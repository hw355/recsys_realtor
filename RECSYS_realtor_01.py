#!/usr/bin/env python
# coding: utf-8

# # Content-based Engines for the for-sale Homes using Python

# In[1]:


import numpy as np
import pandas as pd
import requests
import json
import urllib
import datetime as dt

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


# ## Data Collection

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

data_cities = json.loads(requests.get(url, headers = headers).content.decode('utf-8'))
print(json.dumps(data_cities, indent = 2))


# In[4]:


df_cities = pd.json_normalize(data_cities['results'])
city_names = list(df_cities['Primary_city'].unique())
city_names


# In[12]:


api_key = Realtor_API_KEY_2

features = ['single_story', 'two_or_more_stories', 'garage_1_or_more', 'garage_2_or_more', 'basement']


# In[17]:


def getHome(api_key, cities, state, features):
    table = []
    url = "https://realtor.p.rapidapi.com/properties/v2/list-for-sale"
    
    for city in cities:
        for feature in features:
            querystring = {"city":city,
                           "limit":"200",
                           "offset":"0",
                           "beds_min":"1",
                           "baths_min":"1",
                           "sqft_min":"1",
                           "state_code":state,
                           "features":feature
                          }

            headers = {
                'x-rapidapi-key': api_key,
                'x-rapidapi-host': "realtor.p.rapidapi.com"
                }
            try:
        
                response = requests.request("GET", url, headers = headers, params = querystring)

                print(city, feature, len(response.json()['properties']))

                if len(response.json()['properties']) > 0:
                    for item in response.json()['properties']:
                        item['city'] = item['address']['city']
                        item['line'] = item['address']['line']
                        item['zipcode'] = item['address']['postal_code']
                        item['state'] = item['address']['state_code']
                        item['longitude'] = item['address']['lon']
                        item['latitude'] = item['address']['lat']
                        item['size(sqft)'] = item['building_size']['size']
                        item['features'] = feature
                        data = pd.DataFrame.from_dict(item, orient = 'index').T
                        row = data[['property_id', 'price', 'beds', 'baths', 'size(sqft)',
                                    'line', 'city', 'state', 'zipcode', 
                                    'longitude', 'latitude', 'features', 'last_update']]

                        table.append(row)
            except len(response.json()['properties']) == 0:
                continue

    table = pd.concat(table, axis = 0, ignore_index = True, sort = False)
    
    table['price'] = table['price'].astype(int)
    table['price'].describe().apply(lambda x: format(x, 'f'))
    table['size(sqft)'] = table['size(sqft)'].astype(int)
    table['size(sqft)'].describe().apply(lambda x: format(x, 'f'))
    table['longitude'] = table['longitude'].astype(float)
    table['latitude'] = table['latitude'].astype(float)
    table['beds'] = table['beds'].astype(int)
    table['baths'] = table['baths'].astype(int)
    table['last_update'] = pd.to_datetime(table['last_update'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
    table['zipcode'] = table['zipcode'].astype('category')
    table['features'] = table['features'].astype('category')
        
    return table


# In[18]:


df_home = getHome(api_key, city_names, 'NJ', features)
df_home


# In[19]:


# df_home.to_csv('./Data_Source/home.csv', index = False)


# In[ ]:


df_home.info()
df_home.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# ## Clean Data

# In[1]:


pre_home = pd.read_csv('./Data_Source/home.csv').drop_duplicates().reset_index(drop = True)
pre_home['last_update'] = pd.to_datetime(pre_home['last_update'])
pre_home['days_ago'] = (np.datetime64(dt.date.today()) - 
                        pre_home[['last_update']].values.astype('datetime64[D]')).astype(int)
pre_home


# In[2]:


cols = pre_home.columns[5:7].tolist() + ['features']
Home_1 = pre_home.groupby(cols).agg({'days_ago':min, 'price':min}).reset_index()
Home_1


# In[3]:


Home_1[Home_1.duplicated(cols)]


# In[4]:


Home_2 = Home_1.groupby(['line', 'city'])['features'].agg(lambda column: ", ".join(column)).reset_index(name = "features")
Home_2


# In[5]:


cols = Home_1.columns[:2].tolist() + Home_1.columns[-2:].tolist()
Home = Home_1[cols].merge(Home_2).sort_values('price').drop_duplicates(subset = Home_2.columns[:2].tolist(),
                                                                       keep = 'first').reset_index(drop = True)
Home


# In[6]:


home_ult = pre_home.iloc[:,:-3].merge(Home, how = 'right').drop_duplicates(subset = Home.columns[:2].tolist(),
                                                                           keep = 'first').reset_index(drop = True)
home_ult


# In[7]:


pre_home[['line']][~pre_home['line'].isin(list(home_ult['line']))]


# In[8]:


home_ult[home_ult.duplicated(['line'])]


# In[9]:


# home_ult.to_csv('./Data_Source/home_ult.csv', index = False)

