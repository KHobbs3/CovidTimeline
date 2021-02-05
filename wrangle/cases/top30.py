#!/usr/bin/env python
# coding: utf-8

# # Filter COVID-19 shape data to only contain top 30 Population Centres
# 
# ### Data sources:
# * [Population Centres](https://geosuite.statcan.gc.ca/geosuite/en/index#self) (POPCTRS_30.csv)
# * [Reference Guide](https://www150.statcan.gc.ca/n1/pub/82-402-x/2017001/rm-cr-eng.htm) for linking population centres to health regions
# * [Ontario Government](http://www.health.gov.on.ca/en/common/system/services/phu/locations.aspx) 
# * [Quebec Health Regions](https://www.msss.gouv.qc.ca/en/reseau/regions-sociosanitaires-du-quebec/)
# 
# ### Data input:
# * POPCTRS (POPCTRS_30.csv)
# * Merged health regions shapefile with case data (mergedHR-MMMDD.shp)
# 
# ### Procedure:
# * **Step 1:** Processing population centres (POPCTRS)
#     * POPCTRS were sorted according to descending `POPCTRRApop_2016` and the top 30 entries were retained.
#     * The Reference Guide, Ontario Government, and Quebec Government sources were used to identify which health region a population centre belongs to. This along with the province abbreviation/naming convention used in the COVID-19 time series by the COVID Open Data Working Group were manually inputted into the POPCTRS_30 CSV file.
# * **Step 2:** Merge top 30 POPCTRS with the shapefile on health region name 



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
    shp = gpd.read_file('CovidTimeline/wrangle/data/shapefiles/mergedHR.shp')
    popcen = pd.read_csv('CovidTimeline/collect/data/POPCTRS/POPCTRS_30.csv')


    # drop unneccessary columns from population centre csv
    popcen_short = popcen.drop(columns = ['POPCTRRAtype', 'POPCTRRAtdwell_2016', 'POPCTRRAurdwell_2016', 'POPCTRRApop_2011',
           'POPCTRRApop_2011a', 'POPCTRRAtdwell_2011a', 'POPCTRRAurdwell_2011a',
           'POPCTRRAarea', 'POPCTRRAadj_2011', 'POPCTRRAir_2011',
           'POPCTRRAir_2016', 'POPCTRRclass', 'POPCTRRApop_2016', 'XPRuid', 'unique'])

    # merge and retain only the top 30 population centres in the covid cases shapefile
    merged = pd.merge(popcen_short, shp, on = 'health_reg', how = 'left')
    
    
    
    # CHECK: HOW MANY POPCTRS WERE INCLUDED
        # There are 31 because I accidentally included Red Deer in the reference file but why not?
    if len(merged.POPCTRRAname.unique())  < 30:
        print("Only retained: {} Pop Centres - \n {}".format(len(merged.POPCTRRAname.unique()), merged.POPCTRRAname.unique()))

        
        
    # Convert and Export
    final = gpd.GeoDataFrame(merged, geometry='geometry')

    latest = dt.datetime.today().strftime("%Y-%m-%d")
    print("Creating file: cases_{}.shp".format(latest))
    
    final.to_file('CovidTimeline/viz/CovidTimeline/data/input/cases_{}.shp'.format(latest))
    
print(top30())

