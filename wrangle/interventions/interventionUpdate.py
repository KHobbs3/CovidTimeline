#!/usr/bin/env python
# coding: utf-8

### Processing Interventions


import pandas as pd
from collections import defaultdict
import datetime as dt

# Step 1 ---
import os
os.chdir("CovidTimeline/wrangle/interventions/")

d = defaultdict(list)
d = pd.read_excel('../data/interventions/place-types-concordance.xlsx', sheet_name = 'industries-dict').set_index('industry').transpose().to_dict('records', into=d)

interv = pd.read_csv('../data/interventions/InterventionScan_Nov.csv')



for item in d:
    for key,value in item.items():
        print(key, value)


print("Printing key-terms dictionary................")
d2 = {key: value.split(', ') for key, value in item.items() for item in d} 



# Step 2 ---
print("Labelling intervention data................")
def retrieve_industry(x, dictionary):
    """
    x is a summary description of the policy intervention formatted as a string
    d is a dictionary of industries and keywords associated. values are in a list.
    """
    # set and reset tags
    tags = set()
    
    try:
        for k in dictionary.keys():
            for v in dictionary[k]:
                if x.lower().find(v) > -1:
                    tags.add(k)
    #                 print('found {} in summary, adding {}'.format(v, k))
                    break

    #         print("----\ncurrent tags: {}\n----".format(tags))
    except AttributeError:
        pass
    
    if len(tags) == 0:
        tags.add(None)
    
    return ", ".join(str(e) for e in tags)
    

interv['suggested_industry'] = interv['Intervention summary'].map(lambda x: retrieve_industry(x, d2))



# Step 3 --- 
print("Only retaining Openings, Closures, Restrictions................")
interv = interv.loc[interv['Intervention category'].str.contains("Openings|Closures|Restrictions|Restriction release") == True]


interv.drop(columns = 'Unnamed: 0', inplace = True)
latest = dt.datetime.today().strftime("%Y-%m-%d")
print("Creating file: InterventionScan_Processed_{}.csv".format(latest))

interv.to_csv('../../viz/CovidTimeline/data/input/InterventionScan_Processed_{}.csv'.format(latest), encoding = 'utf-8-sig')
print("Done.")

