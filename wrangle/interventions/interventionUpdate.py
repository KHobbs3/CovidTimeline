#!/usr/bin/env python
# coding: utf-8

# ### Processing Interventions
# 
# * **Step 1:** Create dictionary of key words (see industries-dict tab in place-types-concordance.xlsx for keywords used to identify industry).
# * **Step 2:** Add `Industry` tags.
# * **Step 3:** Filter interventions so that only "Closures, Openings, Restrictions, and Restriction releases" are retained.
# 
# Tags were validated by comparing manually labelled entries with suggested tags. Mismatches were either attributed to incorrect/redundant/inapplicable keywords or manual tags.

import pandas as pd
import datetime as dt


# Step 1 ---
d = dict()
d = pd.read_excel('data/interventions/place-types-concordance.xlsx', sheet_name = 'industries-dict').set_index('industry').transpose().to_dict('records', into=d)

interv = pd.read_excel('data/interventions/master_closures_openings.xlsx', sheet_name = "top30")


d2 = {key: value.split(', ') for key, value in d[0].items()} 


# Step 2 ---
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
    #             print('checking for {}'.format(v))
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
interv = interv.loc[interv['Intervention category'].str.contains("Openings|Closures|Restrictions|Restriction release") == True]



latest = dt.datetime.today().strftime("%Y-%m-%d")
print("Creating file: InterventionScan_Processed_{}.csv".format(latest))
interv.to_csv('../viz/CovidTimeline/data/input/InterventionScan_Processed_{}.csv'.format(latest), encoding = 'utf-8-sig')

