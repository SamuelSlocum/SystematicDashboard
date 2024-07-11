#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 18 15:57:33 2024

@author: samuelslocum
"""

import urllib.request
import requests
import simplejson as json
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import datetime as dt
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
    USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay, \
    USLaborDay, USThanksgivingDay

#These are the data transformations available to the user
transform = {0:lambda x: x,
             1:lambda x: x.diff(),
             2:lambda x: x.diff().diff(),
             3:lambda x: np.log(x),
             4:lambda x: np.log(x).diff()}


#Create a custom calendar for US trading days.
class USTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]

usb = CustomBusinessDay(calendar = USTradingCalendar())


#MAIN FUNCTION
#This takes in a FRED series name and user parameters and it returns a dataframe of pont-in-time data for each date. 
#The value for each point in time is the standard deviation from the mean computed over 10 years (2500 trading days)
def PullFredFinance(request):

    request_json = request.get_json()
    args = ['series_id','transform','startdate','enddate']
    var = {}
    
    for arg in args:
        if request.args and arg in request.args:
            var[arg] = request.args.get(arg)
        elif request_json and arg in request_json:
            var[arg] = request_json[arg]
        else:
            pass
            #return {"values":'ERR!0'}
        
    #Make a request to the FRED api
    base_url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'api_key':'17b08c5ed791161868eba22d0febc1f9',
        'series_id': var['series_id'],
        'file_type': 'json',
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    #unpack the data and transform it.
    df = pd.DataFrame(data['observations'])
    df = df[['date', 'value', 'realtime_start', 'realtime_end']]
    df['date'] = pd.to_datetime(df['date'])
    df['realtime_start'] = pd.to_datetime(df['realtime_start'])
    df['value'] = df['value'].apply(lambda x: float(x) if x!='.' else np.nan)
    sign = np.sign(var['transform'])
    df = (sign*df[['date','value']].set_index('date')).resample(usb).last().shift(1)
    
    #Compute a z-score based in the last 10 year.
    stdized = (df-df.ffill().rolling(2500).mean())/df.ffill().rolling(2500).std()
    
    #This is just going to be all dates, so we can Vlookup on tradeable days and the alignment will be easy.
    dates = pd.date_range(var['startdate'],var['enddate'])
    
    #Create an empty dataframe with the proper dates and join in the relevant data
    empty = pd.DataFrame([],index=dates)
    Pit_vals = empty.join(stdized).ffill()
    Pit_vals = (100*Pit_vals).round(2)

    output = {"values":list(Pit_vals.values.reshape(-1))}
    
    return json.dumps(output, ignore_nan=True)



