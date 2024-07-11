#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 14:02:57 2024

@author: samuelslocum
"""


import urllib.request
import requests
import simplejson as json
import numpy as np
import pandas as pd

#This is the menu of transforms that can be made
transform = {0:lambda x: x,
             1:lambda x: x.diff(),
             2:lambda x: x.diff().diff(),
             3:lambda x: np.log(x),
             4:lambda x: np.log(x).diff()}

#This takes a request on the form of a json blob and computes positioning of a trading strategy based on the provided signal and transform parameters.

#signal -- An array of signal values to trade based off of.
#transform -- Which transform to apply to the signal
#rollWindow -- Compute a z-score for the signal based on a window of size rollWindow. If this is set to 0, no z-score transform will be applied.
#lowThresh/highThresh -- The signal will only activiate if it is in the range of [lowThresh, highThresh]

def RunStrategy(request):
    
    request_json = request.get_json()
    
    args = ['signal','transform','rollWindow','lowThresh','highThresh']
    var = {}
    
    #unpack the json
    for arg in args:
        if request.args and arg in request.args:
            var[arg] = request.args.get(arg)
        elif request_json and arg in request_json:
            var[arg] = request_json[arg]
        else:
            pass
            #return {"values":'ERR!0'}

    #transform the signal using the given transform, rolling, and thresholds.
    Signal = transform[var['transform']](pd.DataFrame(var["signal"]))[0]
    Signal.replace('', np.nan,inplace=True)
    
    if var['rollWindow']>0:
        Position = ((Signal-Signal.rolling(var['rollWindow']).mean())/Signal.rolling(var['rollWindow']).std()).apply(lambda x: np.sign(x) if np.abs(x)>var['lowThresh'] and np.abs(x)<var['highThresh'] else 0)
    else: 
        Position = (Signal).apply(lambda x: np.sign(x) if np.abs(x)>var['lowThresh'] and np.abs(x)<var['highThresh'] else 0)
        
    out = [int(x) for x in list(Position.values)]
        
    output = {"values":out}
    return json.dumps(output, ignore_nan=True)




