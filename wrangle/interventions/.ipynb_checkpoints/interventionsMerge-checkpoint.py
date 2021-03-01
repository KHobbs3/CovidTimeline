#!/usr/bin/env python
# coding: utf-8
# %%

# ## Merging data collected...
# 1. MASTER: Manual collection and CIHI - curate to only July 20, 2020.
# 2. Government Ontario
# 
# 
# **Step 1:** standardize column names
# 
# **Step 2:** standardize intervention type and health regions for Ontario data
# 
# **Step 3:** filter PHUs in Ontario
# 
# **Step 4:** add summary and category to Ontario data
# 
# **Step 5:** Concat, clean, export
# 
# ---

# %%


import pandas as pd


# %%
on = pd.read_csv("https://data.ontario.ca/dataset/cbb4d08c-4e56-4b07-9db6-48335241b88a/resource/ce9f043d-f0d4-40f0-9b96-4c8a83ded3f6/download/response_framework.csv")


standards = pd.read_excel("../data/interventions/standardized-restrictions.xlsx", 
                        sheet_name = "on")


# Standardize columns
on.rename(columns = {
    "Reporting_PHU": "Health Region",
    "Status_PHU" : "Type",
    "start_date" : "Implemented",
    "end_date" : "Expired"
},  inplace = True)


on.Type.replace({
    "Prevent": "Green - Prevent",
    "Protect": "Yellow - Protect",
    "Restrict": "Orange - Restrict",
    "Control": "Red - Control",
    "Lockdown": "Grey - Lockdown"
}, inplace = True)


on["Health Region"].replace({
    'Durham Region Health Department': "Durham",
    'Halton Region Health Department' : "Halton",
    'Hamilton Public Health Services' : "Hamilton",
    'Kingston, Frontenac and Lennox & Addington Public Health': "Kingston Frontenac Lennox & Addington",
    'Middlesex-London Health Unit' : "Middlesex-London",
    'Niagara Region Public Health Department': "Niagara",
    'Ottawa Public Health': "Ottawa",
    'Region of Waterloo, Public Health': "Waterloo",
    'Simcoe Muskoka District Health Unit': "Simcoe Muskoka",
    'Toronto Public Health': "Toronto",
   'Wellington-Dufferin-Guelph Public Health': 'Wellington Dufferin Guelph',
   'Windsor-Essex County Health Unit': "Windsor Essex",

}, inplace = True)


on["Jurisdiction"] = "Ont."
on["Source"] = "https://data.ontario.ca/dataset/cbb4d08c-4e56-4b07-9db6-48335241b88a/resource/ce9f043d-f0d4-40f0-9b96-4c8a83ded3f6/download/response_framework.csv"
on["Source type"] = "Ontario Data Catalogue"


# Filter
keep_PHU = ['Durham', 'Halton', 'Hamilton', 
           'Kingston Frontenac Lennox & Addington', 
           'Middlesex-London', 'Niagara', 'Ottawa',
            'Waterloo', 'Simcoe Muskoka', 
            'Toronto', 'Wellington Dufferin Guelph', 'Windsor Essex'
           ]

on_filt = on.loc[(on["Health Region"].str.contains("|".join(keep_PHU))) & (on["Type"] != "Other")]

on_filt.head(2)


# %%
print("Adding summaries to gov Ontario data...")

stds = pd.read_excel("../data/interventions/standardized-restrictions.xlsx", 
                        sheet_name = "on").set_index("Level")["Summary"].to_dict()

def summary(x):
    """
    x is Type series from on_filt
    maps summary based on previous type
    """
    try:
        return stds[x]

    except KeyError:
        return None


on_filt["Summary"] = on_filt.Type.map(summary)


# %%

print("Adding categories to gov Ontario data...")
def cat(x):
    """
    x is Type series from on_filt
    maps summary based on type
    """  
    if x == "Stay-at-home" or x == "Yellow - Protect" or x == "Orange - Restrict":
        return "Restrictions"
    elif x == "Green - Prevent":
        return "Openings"
    elif x == "Grey - Lockdown":
        return "Closures"
    else:
        return None


on_filt["Category"] = on_filt.Type.map(cat)


conversions = pd.read_excel("../data/interventions/standardized-restrictions.xlsx", 
                        sheet_name = "on").set_index("Level")["Number"].to_dict()



cat2 = []
    
def cat_fill(temp):
    """
    df is dataframe from on_filt
    maps summary based on PREVIOUS type.
    fills in blanks for Category.
    """

    # iter the entries within PHU
    idx = len(temp)
    for i in range(0,idx):
        if i == 0:
            previous_key = temp.iloc[0]["Type"]
            previous = conversions[previous_key]
            cat2.append(None)
        else:
            previous_key = temp.iloc[i-1]["Type"]
            current_key = temp.iloc[i]["Type"]

            previous = conversions[previous_key]
            current = conversions[current_key]

            # if going LOWER in restrictions
            if previous > current:
                cat2.append("Openings")
            else:
                cat2.append("Closures")
                

for p in keep_PHU:
    
    # section by PHU
    temp = on_filt.loc[on_filt["Health Region"] == p]
    
    try:
        cat_fill(temp)
    except KeyError:
        pass

    
on_filt["cat_fill"] = cat2
on_filt["Category"].fillna(on_filt["cat_fill"], inplace = True)
on_filt.drop(columns = ["cat_fill"], inplace = True)


# %%
# MANUAL --------
manual = pd.read_excel("../data/interventions/master_closures_openings.xlsx", sheet_name = "top30")

manual.rename(columns = {
    "Jurisdiction ": "Jurisdiction",
    "Date implemented" : "Implemented",
    "Intervention type": "Type",
    "Intervention category" : "Category",
    "Intervention summary" : "Summary",
    "Primary source\n(news release or specific resource)": "Source"
}, inplace = True)

# Filter Category, Type and Date
manual_filt = manual.loc[(manual.Category.str.contains("Openings|Closures|Restrictions|Restriction release") == True) 
                         & (manual.Implemented.astype(str) > "2020-07-20")]
manual_filt = manual_filt.loc[~manual_filt.Type.str.contains("education|daycare")]
manual_filt.head(2)


# %%


# Concat, clean, and export
df = pd.concat([manual_filt, on_filt])
df.drop(columns = ['Secondary source', 'Reporting_PHU_id', 'PHU_url', 
                   'Date announced', 'Indigenous \npopulation group'], 
       inplace = True)

print("Exporting master.csv...")
df.to_csv("../data/interventions/master.csv")

