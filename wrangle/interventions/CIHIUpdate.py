#!/usr/bin/env python
# coding: utf-8

# # Updating Master Intervention list with CIHI releases


import pandas as pd
from collections import defaultdict

old = pd.read_excel('../data/interventions/CIHI_closures_openings.xlsx', sheet_name = "top30")
new = pd.read_excel("../data/interventions/covid-19-intervention-scan-data-tables-en-web.xlsx", sheet_name = "Intervention scan", skiprows = [0,1])
popctrs = pd.read_csv('../../collect/data/POPCTRS/POPCTRS_30.csv')

# Filter for closures and openings only - after july 22
new2 = new.loc[new['Intervention type'].str.contains("Closures|Openings")]


# Step 1 --- Filter after (and including) last update
cutoff = input("Enter the final date of the previous release (YYYY-MM-DD): ")
new3 = new2.loc[new2['Date implemented'].astype(str) >= cutoff]

    # Filter provinces/territories that don't contain top30 POPCTRS
keep = 'Ont.|Alta.|B.C.|Que.|N.S.|Sask.|N.L.|Man.|N.B.'
new4 = new3[new3.Jurisdiction.str.contains(keep,na=False)]
print("{} new entries for the top 30 POPCTRS since {}".format(len(new4), cutoff))

# Step 2 --- Make reference DataFrame
d = popctrs.groupby(['Province', 'health_reg'])['health_reg'].count().to_dict()
reference = pd.DataFrame(d, index =[0]).transpose().reset_index().drop(columns = [0])
reference.columns = ['Jurisdiction', 'health_region']



# Step 3 ---
# Separate those at regional/municipal level from the rest 
regional = new4.loc[(new3.Level == "Regional") | (new4.Level == "Municipal")]
rest = new4.loc[(new3.Level != "Regional") | (new4.Level != "Municipal")]
print("{} new regional entries, {} new provincial/territorial".format(len(regional), len(rest)))

# Merge provincial/territorial and federal with reference
out = pd.merge(reference, rest, how = 'right')



# Step 4a ---
# Create a reference dictionary using keywords
print("Creating reference dictionary using keywords................")
hrs = defaultdict(list)
hrs = pd.read_excel('data/interventions/place-types-concordance.xlsx', sheet_name = 'popctrs-dict').set_index('health_reg').transpose().to_dict('records', into=hrs)

for item in hrs:
    for key,value in item.items():
        print(key, value.split(', '))

hrs2 = {key: value.split(', ') for key, value in item.items() for item in hrs} 


# Generate suggested HRs using reference dictionary
def retrieve_hr(x, dictionary):
    """
    x is a summary description of the policy intervention formatted as a string
    d is a dictionary of industries and keywords associated
    """
    # set and reset tags
    tags = set()
    try:
        for k in dictionary.keys():
            for v in dictionary[k]:
                if x.lower().find(v) > -1:
                    tags.add(k)
                    print('found {} in summary, adding {}'.format(v, k))
                    break

    #         print("----\ncurrent tags: {}\n----".format(tags))
    except AttributeError:
        pass
    
    if len(tags) == 0:
        tags.add(None)
    
    print("Found {} in summary".format(", ".join(str(e) for e in tags)))

    response = input("Type 'yes' to add to health regions, otherwise type 'no'.")
    if response == 'yes':
        return ", ".join(str(e) for e in tags)
    elif response == 'no':
        return None

print("Generating suggested HRs using reference dict................")
regional['Intervention summary'].map(lambda x: retrieve_hr(x, hrs2))



# Step 4b ---
# Manually add health regions
print("Manually adding health regions................")
regional['health_region'] = "Capitale-Nationale"
regional = pd.concat([regional, regional]).reset_index()
regional.loc[1, "health_region"] = 'Montréal'

# Re-concatenate and add to old
final = pd.concat([old, out, regional]).reset_index().drop(columns = 'index')

# Step 5 --- Clean & Export
print("Exporting as InterventionScan_Nov.csv ................")
final.drop(columns= 'level_0').to_csv('../data/interventions/InterventionScan_Nov.csv', encoding = "utf-8-sig")
print("WARNING: Validate this file by hand.")

