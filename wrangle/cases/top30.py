#!/usr/bin/env python
# coding: utf-8

# Filter COVID-19 shape data to only contain top 30 Population Centres

import geopandas as gpd
import pandas as pd
import datetime as dt

class PopCentres:
    
    def __init__(self, fnc):
        
        self._fnc = fnc
        
    def __call__(self, *args, **kwargs):
        
        return self._fnc(*args, **kwargs)


@PopCentres
def top30():
    shp = gpd.read_file('../../wrangle/data/shapefiles/mergedHR.shp')
    shp.rename(columns = {
        "Health Reg": "Health Region"
    }, inplace = True)
    popcen = pd.read_csv('../../collect/data/POPCTRS/POPCTRS_30.csv')


    # drop unneccessary columns from population centre csv
    popcen_short = popcen.drop(columns = ['POPCTRRAtype', 'POPCTRRAtdwell_2016', 'POPCTRRAurdwell_2016', 'POPCTRRApop_2011',
           'POPCTRRApop_2011a', 'POPCTRRAtdwell_2011a', 'POPCTRRAurdwell_2011a',
           'POPCTRRAarea', 'POPCTRRAadj_2011', 'POPCTRRAir_2011',
           'POPCTRRAir_2016', 'POPCTRRclass', 'POPCTRRApop_2016', 'XPRuid', 'unique'])

    # merge and retain only the top 30 population centres in the covid cases shapefile
    merged = pd.merge(popcen_short, shp, on = 'Health Region', how = 'left')
    
    
    
    # CHECK: HOW MANY POPCTRS WERE INCLUDED
        # There are 31 because I accidentally included Red Deer in the reference file but why not?
    if len(merged.POPCTRRAname.unique())  < 30:
        print("Only retained: {} Pop Centres - \n {}".format(len(merged.POPCTRRAname.unique()), merged.POPCTRRAname.unique()))

        
        
    # Convert and Export
    final = gpd.GeoDataFrame(merged, geometry='geometry')

    
    latest = dt.datetime.today().strftime("%Y-%m-%d")
    print("Creating file: cases_{}.shp".format(latest))
    
    final.to_file('../../viz/CovidTimeline/data/input/cases_{}.shp'.format(latest))

print(top30())

