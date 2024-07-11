#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 13:22:34 2024

@author: samuelslocum
"""


import urllib.request
import requests
import simplejson as json
import numpy as np
import pandas as pd

#These are the data transformations available to the user.
transform = {0:lambda x: x,
             1:lambda x: x.diff(),
             2:lambda x: x.diff().diff(),
             3:lambda x: np.log(x),
             4:lambda x: np.log(x).diff()}

#HELPER FUNCTIONS
#This function transforms the data so that we have a set of historic data for each of the point-in-time dates.
def PIT(df):
    PIT = df.reset_index().set_index(['date','realtime_start']).unstack()['value'].transpose().ffill()
    return PIT


#MAIN FUNCTION
#This takes in a FRED series name and user parameters and it returns a dataframe of pont-in-time data for each date. 
#The value for each point in time is the standard deviation from the mean computed over 10 years.
def PullFredEcon(request):

    request_json = request.get_json()
    args = ['series_id','transform','startdate','enddate']
    var = {}
    
    #unpack the arguments from the request
    for arg in args:
        if request.args and arg in request.args:
            var[arg] = request.args.get(arg)
        elif request_json and arg in request_json:
            var[arg] = request_json[arg]
        else:
            pass
            #return {"values":'ERR!0'}
        
    #Make a request from the FRED API.
    base_url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'api_key':'17b08c5ed791161868eba22d0febc1f9',
        'series_id': var['series_id'],
        'file_type': 'json',
        'realtime_start': '2002-01-01',  # Start date for real-time period
        'realtime_end': '9999-12-31'     # End date for real-time period
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    #unpack the series and put them in a form where we can extract point-in-time data at each date.
    df = pd.DataFrame(data['observations'])
    df = df[['date', 'value', 'realtime_start', 'realtime_end']]
    df['date'] = pd.to_datetime(df['date'])
    df['realtime_start'] = pd.to_datetime(df['realtime_start'])
    df['value'] = df['value'].apply(lambda x: float(x) if x!='.' else np.nan)
    df = df[['date','value','realtime_start']]
    PIT_frame = PIT(df)
    
    #This is just going to be all dates, so we can Vlookup on tradeable days and the alignment will be easy.
    dates = pd.date_range(var['startdate'],var['enddate'])
    dates_big = pd.date_range('2000-01-01',var['enddate'])
    
    #Apply the chosen transform and standardize the data so that each PIT is in units of standard deviations relative to the last 10 years.
    tcode = np.abs(var['transform'])
    sign = np.sign(var['transform'])
    T1 = sign*transform[tcode](PIT_frame.transpose())
    T1 = T1.resample("M").last()
    T2 = ((T1-T1.rolling(120).mean())/T1.rolling(120).std()).ffill()
    Pit_vals = T2.iloc[-1,:]
    Pit_vals.index.name='date'
    ddf = pd.DataFrame([],index=dates_big)
    Pit_vals = ddf.join(Pit_vals).ffill().loc[dates]
    Pit_vals = (100*Pit_vals).round(2)

    output = {"values":list(Pit_vals.values.reshape(-1))}
    
    return json.dumps(output, ignore_nan=True)




