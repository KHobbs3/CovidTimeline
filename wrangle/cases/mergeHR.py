#!/usr/bin/env python
# coding: utf-8

# # Merging a shapefile of Canada's health region boundaries with COVID-19 Case timeseries data
# 
# ---
# 
# ### Data output:
# Shapefile of Health Regions in Canada and their associated weekly COVID-19 data.



import pandas as pd
import geopandas as gpd
from datetime import datetime

class Merge:
    
    def __init__(self, fnc):
        
        self._fnc = fnc
        
    def __call__(self, *args, **kwargs):
        
        return self._fnc(*args, **kwargs)
          



@Merge
def mergeHR():


    weekly = pd.read_csv('CovidTimeline/collect/data/weekly_ts.csv')
    hr = gpd.read_file('CovidTimeline//collect/data/hr_boundaries/RegionalHealthBoundaries.shp')


    # Cleaning

    # Step 1 --- drop territories from case and shape data
    prov_cases = weekly.set_index('province').drop(['NWT', 'Yukon', 'Nunavut'], axis = 0).reset_index()

    # Step 2 --- set up clean name cols
    prov_cases['clean_name'] = prov_cases.health_region
    hr['clean_name'] = hr.ENGNAME

    # Step 3 --- clean names to match
    prov_cases.clean_name.replace({
        r'\s\(.*\)': ''}, 
        inplace = True)

    prov_cases.clean_name.replace({
        ',': '',
        '-':' '}, 
        regex = True, inplace = True)


    # Step 3b --- fix ambiguities in case file
    ### for case data
    prov_cases.loc[(prov_cases.clean_name == 'Northern') & (prov_cases.province == 'Manitoba'), 'clean_name'] = 'Northern Regional Health Authority'
    prov_cases.loc[(prov_cases.clean_name == 'Northern') & (prov_cases.province == 'BC'), 'clean_name'] = 'Northern Health'

    prov_cases.loc[(prov_cases.clean_name == 'Central') & (prov_cases.province == 'NL'), 'clean_name'] = 'Central Regional Health Authority'
    prov_cases.loc[(prov_cases.clean_name == 'Central') & (prov_cases.province == 'Alberta'), 'clean_name'] =  'Central Zone'

    prov_cases.loc[(prov_cases.clean_name == 'South') & (prov_cases.province == 'Alberta'), 'clean_name'] = 'South Zone'
    prov_cases.loc[(prov_cases.clean_name == 'North') & (prov_cases.province == 'Alberta'), 'clean_name'] = 'North Zone'

    prov_cases.loc[(prov_cases.clean_name == 'Eastern') & (prov_cases.province == 'NL'), 'clean_name'] = 'Eastern Regional Health Authority'
    prov_cases.loc[(prov_cases.clean_name == 'Eastern') & (prov_cases.province == 'Ontario'), 'clean_name'] = 'The Eastern Ontario'

    # change health region name as well to differentiate 
    prov_cases.loc[(prov_cases.clean_name == 'Eastern Regional Health Authority') & (prov_cases.province == 'NL'), 'health_region'] = 'Eastern Regional Health Authority'


    prov_cases.loc[(prov_cases.clean_name == 'Western') & (prov_cases.province == 'NL'), 'clean_name'] = 'Western Regional Health Authority'


    ### for health regions data
    hr.clean_name.replace({
          # General
          'Région du ' : '',
          'Région de la ' : '',
          'Région des ' : '',
          'Région de ' : '',
          ' Regional Health Unit' : '',
          ' Health Unit' : '',
          'City of ' : '',
        ',': '',
        '-':' ',

           # Specific
        'Calgary Zone' : 'Calgary',
        'Edmonton Zone' : 'Edmonton',
        'Peterborough County–City': 'Peterborough',
        'Vancouver  Coastal Health': 'Vancouver Coastal',
        'Vancouver Island Health': 'Island',
        'Interior Health' : 'Interior',
        'Fraser Health':'Fraser',
        'The District of Algoma': 'Algoma',
        'Brant County': 'Brant',
        ' District':'',
        'Huron Perth Public':'Huron Perth',
        'Sudbury and':'Sudbury',
        'Niagara Regional Area':'Niagara',
        'Southern Health—Santé Sud':'Southern Health',
        'Renfrew County and':'Renfrew',
        'Hastings and Prince Edward Counties':'Hastings Prince Edward',
        'Prairie Mountain Health':'Prairie Mountain'
    }, 
        regex = True, inplace = True)

    hr.clean_name.replace({
        'Windsor Essex County':'Windsor Essex',
    'Kingston Frontenac and Lennox and Addington':'Kingston Frontenac Lennox & Addington',
        'Mauricie et du Centre du Québec':'Mauricie',
        'Haliburton Kawartha Pine Ridge':'Haliburton Kawartha Pineridge',
        'Gaspésie—Îles de la Madeleine':'Gaspésie Îles de la Madeleine',
        'Saguenay—Lac Saint Jean':'Saguenay',
        "l'Abitibi Témiscamingue":'Abitibi Témiscamingue',
         "l'Estrie":'Estrie',
         "l'Outaouais":'Outaouais',
        'Interlake Eastern Regional Health Authority':'Interlake Eastern',
        'Labrador Grenfell Regional Health Authority':'Labrador Grenfell',
        'Winnipeg Regional Health Authority':'Winnipeg'
    }, 
        inplace = True)



    # Step 3c --- aggregate zones in shapefile as was done by UofT researches in case ts
    hr.clean_name.replace({
        # SK -- Far North
        'Far North Central':'Far North',
        'Far North East':'Far North',
        'Far North West':'Far North',

        # SK -- South
        'South East':'South',
        'South West':'South',
        'South Central':'South',

        # SK -- Central
        'Central West':'Central',
        'Central East':'Central',

        # SK -- North
        'North East':'North',
        'North West':'North',
        'North Central':'North'


    }, inplace = True)



    # Step 4 --- merge
    print("Merging case data with health regions.")
    merge = pd.merge(prov_cases, hr, on = 'clean_name')

    # check missing names
    hr_missing = list(set(hr.clean_name.unique()) - set(merge.clean_name.unique()))
    cases_missing = list(set(prov_cases.clean_name.unique()) - set(merge.clean_name.unique()))
    
    if len(hr_missing) > 3 or len(cases_missing) > 1:
        print('Missing from HR: {}\nMissing from Cases: {}'.format(len(hr_missing), len(cases_missing)))
        print(sorted(hr_missing), sorted(cases_missing))             

    # Tidy & Export
    # convert to shapefile
    shp = gpd.GeoDataFrame(merge, geometry='geometry')

    # drop unneccessary columns
    shp2 = shp.drop(columns = ['TotalPop20',
           'Pop0to4_20', 'Pop5to9_20', 'Pop10to14_', 'Pop15to19_', 'Pop20to24_',
           'Pop25to29_', 'Pop30to34_', 'Pop35to39_', 'Pop40to44_', 'Pop45to49_',
           'Pop50to54_', 'Pop55to59_', 'Pop60to64_', 'Pop65to69_', 'Pop70to74_',
           'Pop75to79_', 'Pop80to84_', 'Pop85Older', 'AverageAge', 'MedianAge_',
           'Last_Updat','NewCases7D', 'PopUnder20', 'Pop20to49', 'Pop50to69', 'Pop70to84',
           'PopOver85'])



    # extract dates after july 20, 2020
    shp2.date_report = shp2.date_report.astype(str)
    shp2.to_file('CovidTimeline/wrangle/data/shapefiles/mergedHR.shp')

print(mergeHR())