#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import datetime as dt
import schedule


class Cases:
    
    def __init__(self, fnc):
        
        self._fnc = fnc
        
    def __call__(self, *args, **kwargs):
        
        return self._fnc(*args, **kwargs)

    

@Cases
def update_cases():
    daily = pd.read_csv('https://raw.githubusercontent.com/ishaberry/Covid19Canada/master/timeseries_hr/cases_timeseries_hr.csv')

    # convert to datetime object
    daily.date_report = daily.date_report.map(lambda x: dt.datetime.strptime(x, '%d-%m-%Y'))

    # only grab from July 20, 2020 onwards
    print("Retaining everything on and after july 20, 2020.")
    july20 = daily.loc[daily.date_report >= "2020-07-20"]
    
    # resample to weekly & export
    july20.groupby(['province','health_region']).resample('W-Mon', on = 'date_report').sum().to_csv('data/weekly_ts.csv')

    # export daily cases too
    daily.to_csv("data/daily_ts.csv")
    
    # print latest update
    latest = dt.datetime.today().strftime("%Y-%m-%d")
    return "Latest case data call: {}".format(latest)

# schedule.every().monday.do(update_cases)


print(update_cases())

