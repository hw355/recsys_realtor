#!/usr/bin/env python
# coding: utf-8

# # Important features to Home

# In[1]:


import json
import requests
import urllib
import pandas as pd
from fuzzywuzzy import process, fuzz

import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from ipynb.fs.full.Credentials import *


# In[ ]:


DS_dir = currentdir + '/Data_Source'

try:
    os.mkdir(DS_dir, mode = 0o666)

except FileExistsError:
    
    pass


# ## School

# In[2]:


url_school = 'https://services1.arcgis.com/' + HIFLD_key + '/arcgis/rest/services/Public_Schools/FeatureServer/0/query?where=STATE%20%3D%20%27NJ%27%20AND%20COUNTY%20%3D%20%27OCEAN%27&outFields=OBJECTID,NAME,ADDRESS,CITY,STATE,ZIP,COUNTY,LEVEL_,LATITUDE,LONGITUDE&outSR=4326&f=json'
data_school = json.loads(requests.get(url_school).content.decode('utf-8'))
print(json.dumps(data_school, indent = 2))


# In[2]:


pre_school = pd.json_normalize(data_school['features'])
pre_school


# In[3]:


pre_school[['S_ID', 'S_name', 'S_address', 'S_level', 'S_city', 'S_zip', 'S_latitude', 'S_longitude']] = pre_school[['attributes.OBJECTID', 'attributes.NAME', 'attributes.ADDRESS', 'attributes.LEVEL_', 'attributes.CITY', 'attributes.ZIP', 'attributes.LATITUDE', 'attributes.LONGITUDE']]
df_school = pre_school.iloc[:, -8:]
df_school


# In[4]:


# df_school.to_csv('./Data_Source/school.csv', index = False)


# ## City

# In[3]:


where = urllib.parse.quote_plus("""
{
    "State": "NJ",
    "County": "Ocean County"
}
""")
url = 'https://parseapi.back4app.com/classes/US_Zip_Code?count=1&limit=35&order=US_Zip_Code&excludeKeys=Unacceptable_cities,country,Remarks,Timezone&where=%s' % where
headers = {
    'X-Parse-Application-Id': back4app_ID,
    'X-Parse-Master-Key': back4app_key
}

data_city = json.loads(requests.get(url, headers = headers).content.decode('utf-8'))
print(json.dumps(data_city, indent = 2))


# In[5]:


pre_city = pd.json_normalize(data_city['results'])

pre_city['US_Zip_Code'] = '0' + pre_city['US_Zip_Code'].astype(str)
pre_city[['C_ID', 'C_name', 'C_AKA', 'C_zip', 'C_latitude', 'C_longitude', 'C_population']] = pre_city[['objectId', 'Primary_city', 'Acceptable_cities', 'US_Zip_Code', 'Latitude', 'Longitude', 'estimated_population']]
df_city = pre_city.iloc[:,-7:]
df_city


# In[47]:


# df_city.to_csv('./Data_Source/city.csv', index = False)


# In[6]:


city_names = list(df_city['C_name'].unique())
city_names


# ## Fire department

# In[7]:


url_fire = 'https://services1.arcgis.com/' + HIFLD_key + '/arcgis/rest/services/Fire_Station/FeatureServer/0/query?where=STATE%20%3D%20%27NJ%27&outFields=OBJECTID,NAME,ADDRESS,CITY,STATE,ZIPCODE&outSR=4326&f=json'
data_fire = json.loads(requests.get(url_fire).content.decode('utf-8'))
print(json.dumps(data_fire, indent = 2))


# In[8]:


nj_fire = pd.json_normalize(data_fire['features'])
pre_fire = nj_fire[nj_fire['attributes.CITY'].isin(city_names)].copy()


# In[9]:


pre_fire['attributes.ZIPCODE'] = pre_fire[['attributes.ZIPCODE']].apply(lambda x: x.str.slice(0, 5))

pre_fire[['F_ID', 'F_name', 'F_address', 'F_city', 'F_zip', 'F_latitude', 'F_longitude']] = pre_fire[['attributes.OBJECTID', 'attributes.NAME', 'attributes.ADDRESS', 'attributes.CITY', 'attributes.ZIPCODE', 'geometry.y', 'geometry.x']]
df_fire = pre_fire.iloc[:, -7:]
df_fire


# In[54]:


# df_fire.to_csv('./Data_Source/fire.csv', index = False)


# ## Police department

# In[10]:


url_police = 'https://services1.arcgis.com/' + HIFLD_key + '/arcgis/rest/services/Local_Law_Enforcement_Locations/FeatureServer/0/query?where=STATE%20%3D%20%27NJ%27%20AND%20COUNTY%20%3D%20%27OCEAN%27&outFields=OBJECTID,NAME,ADDRESS,CITY,STATE,ZIP,COUNTY,LATITUDE,LONGITUDE&outSR=4326&f=json'
data_police = json.loads(requests.get(url_police).content.decode('utf-8'))
print(json.dumps(data_police, indent = 2))


# In[11]:


pre_police = pd.json_normalize(data_police['features'])
pre_police


# In[12]:


pre_police[['P_ID', 'P_name', 'P_address', 'P_city', 'P_zip', 'P_latitude', 'P_longitude']] = pre_police[['attributes.OBJECTID', 'attributes.NAME', 'attributes.ADDRESS', 'attributes.CITY', 'attributes.ZIP', 'attributes.LATITUDE', 'attributes.LONGITUDE']]
df_police = pre_police.iloc[:, -7:]
df_police = df_police.append([df_police[df_police['P_name'] == 'LONG BEACH TOWNSHIP POLICE DEPARTMENT'].copy()], ignore_index = True)
df_police.at[34, 'P_name'] = 'BARNEGAT LIGHT POLICE DEPARTMENT'
df_police


# In[17]:


# df_police.to_csv('./Data_Source/police.csv', index = False)


# In[13]:


url_crime_station = 'https://api.usa.gov/crime/fbi/sapi/api/agencies/byStateAbbr/NJ?API_KEY=' + FBI_NJ_key
data_crime_station = json.loads(requests.get(url_crime_station).content.decode('utf-8'))
print(json.dumps(data_crime_station, indent = 2))


# In[14]:


df_crime_station = pd.json_normalize(data_crime_station['results'])
df_crime_station = df_crime_station[df_crime_station['county_name'] == 'OCEAN']
df_crime_station['agency_name'] = df_crime_station['agency_name'].str.upper()
df_crime_station


# In[20]:


# df_crime_station.to_csv('./Data_Source/crime_data_pt1_station.csv', index = False)


# In[15]:


station_codes = list(df_crime_station.ori)
station_codes


# In[16]:


def getRecord(station_codes):
    allRecord = []
    for station_code in station_codes:
        url_crime_record = 'https://api.usa.gov/crime/fbi/sapi/api/summarized/agencies/' + station_code + '/offenses/2015/2019?API_KEY=' + FBI_NJ_key
        data_crime_record = json.loads(requests.get(url_crime_record).content.decode('utf-8'))
        df_crime_record = pd.json_normalize(data_crime_record['results'])
        
        agg_crime_record = df_crime_record.groupby('offense').agg({'actual':'sum'}).T
        agg_crime_record['case_number'] = agg_crime_record.iloc[:, -12:-1].sum(axis=1)
        agg_crime_record['ori'] = station_code

        allRecord.append(agg_crime_record)
    
    allRecord = pd.concat(allRecord, axis = 0, ignore_index = True, sort = False)
    cols = allRecord.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    allRecord = allRecord[cols]
    
    return allRecord


# In[17]:


df_crime_record = getRecord(station_codes)
df_crime_record


# In[24]:


# df_crime_record.to_csv('./Data_Source/crime_data_pt2_record.csv', index = False)


# In[18]:


df_crime_data = pd.merge(df_crime_station[['ori', 'agency_name']], df_crime_record, on = "ori")
df_crime_data


# In[26]:


# df_crime_data.to_csv('./Data_Source/crime_data.csv', index = False)


# ## Merge Police department with Crime record

# In[41]:


def getFuzzyMatch(df_police, df_crime_data):
    df_crime_data['dummy'] = True
    df_police['dummy'] = True
    
    pre_crime_police = pd.merge(df_police, df_crime_data, on = 'dummy')
    pre_crime_police.drop('dummy', axis = 1, inplace = True)
    
    cols = pre_crime_police.columns.tolist()
    col = cols[:4] + cols[7:] + cols[4:7]
    pre_crime_police = pre_crime_police[col]
   
    pre_crime_police['Token_Set_Ratio'] = pre_crime_police[['agency_name', 'P_name']].apply(lambda x:fuzz.token_set_ratio(x.agency_name, x.P_name), axis = 1)
    pre_crime_police['Rank_Token_Set_Ratio'] = pre_crime_police.groupby('agency_name')['Token_Set_Ratio'].rank(ascending = False, method = 'dense')

    pre_crime_police['Token_Sort_Ratio'] = pre_crime_police[['agency_name','P_name']].apply(lambda x:fuzz.token_sort_ratio(x.agency_name, x.P_name), axis = 1)
    pre_crime_police['Rank_Token_Sort_Ratio'] = pre_crime_police.groupby('agency_name')['Token_Sort_Ratio'].rank(ascending = False, method = 'dense')

    pre_crime_police = pre_crime_police.loc[(pre_crime_police.Rank_Token_Set_Ratio == 1) & (pre_crime_police.Token_Set_Ratio > 70) & ((pre_crime_police.Token_Sort_Ratio == 100) | ((pre_crime_police.Token_Sort_Ratio < 90) & (pre_crime_police.Token_Sort_Ratio > 80)) | (pre_crime_police.Token_Sort_Ratio < 70))]
    crime_police = pre_crime_police.iloc[:,:-4]
    
    return crime_police


# In[42]:


df_crime_police = getFuzzyMatch(df_police, df_crime_data)
df_crime_police


# In[40]:


df_crime_police = getFuzzyMatch(df_police, df_crime_data)
df_crime_police[df_crime_police['P_name'] == 'TOMS RIVER POLICE DEPARTMENT']


# In[52]:


# df_crime_police.to_csv('./Data_Source/crime_police.csv', index = False)

