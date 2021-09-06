#!/usr/bin/env python
# coding: utf-8

# # Get derived data and merge data sets

# In[7]:


import pandas as pd
import geopandas as gpd
import numpy as np
from fuzzywuzzy import process, fuzz
import os


# In[ ]:


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
DS_dir = currentdir + '/Data_Source'

try:
    os.mkdir(DS_dir, mode = 0o666)

except FileExistsError:
    
    pass


# ## Get Crime Rate(%)

# In[2]:


def getCrimeRate(crime_police, ocean):
    crime_police['dummy'] = True
    ocean_block = ocean[['NAME','POP2010']].copy()
    ocean_block[['dummy']] = True
    
    pre_crime_police = pd.merge(crime_police, ocean_block, on = 'dummy')
    pre_crime_police.drop('dummy', axis = 1, inplace = True)

    pre_crime_police['Token_Set_Ratio'] = pre_crime_police[['P_name', 'NAME']].apply(lambda x:fuzz.token_set_ratio(x.P_name, x.NAME), axis = 1)
    pre_crime_police['Rank_Token_Set_Ratio'] = pre_crime_police.groupby('P_name')['Token_Set_Ratio'].rank(ascending = False, method = 'dense')
   
    pre_crime_police = pre_crime_police.loc[(pre_crime_police.Rank_Token_Set_Ratio == 1) & (pre_crime_police.Token_Set_Ratio > 60)]
    pre_crime_police.insert(19, 'crime_rate(%)', pre_crime_police['case_number']/pre_crime_police['POP2010']*20)
    pre_crime_police = pre_crime_police.iloc[:,:-2]
    
    crime_police = pd.merge(ocean_county, pre_crime_police,  how='right', left_on = ['NAME','POP2010'], right_on = ['NAME','POP2010'])
    
    return crime_police


# In[5]:


MB_nj = gpd.read_file('./Maps/map_02/Municipal_Boundaries_of_NJ.shp')

ocean_county = MB_nj[MB_nj['COUNTY'] == 'OCEAN']
ocean_county = ocean_county.to_crs(epsg = 4326)


# In[8]:


crime_police = pd.read_csv('./Data_Source/crime_police.csv')
crime_rate = getCrimeRate(crime_police, ocean_county)
crime_rate


# In[11]:


# crime_rate.to_csv('./Data_Source/crime_rate.csv', index = False)


# In[9]:


crime_rate.columns


# In[10]:


cols = crime_rate.columns.tolist()
cols = ['P_ID', 'P_name', 'P_address', 'P_city', 'ori', 'agency_name', 'NAME'] + cols[-4:-3] + ['POPDEN2010'] + cols[-3:]
crime_police_ult = crime_rate[cols].copy()
crime_police_ult.rename(columns = {'NAME':'mun_name', 'POPDEN2010': 'POPDEN2010 (per sq. mi.)'}, inplace = True)
crime_police_ult

crime_police_ult.nlargest(35,'POPDEN2010 (per sq. mi.)')


# In[ ]:


#crime_police_ult.to_csv('./Data_Source/crime_police_ult.csv', index = False)


# ## Merge data sets to get Final.csv

# In[5]:


home = pd.read_csv('./Data_Source/home_ult.csv')
school = pd.read_csv('./Data_Source/school.csv')
fire = pd.read_csv('./Data_Source/fire.csv')
police = pd.read_csv('./Data_Source/crime_police_ult.csv')


# In[6]:


home


# In[7]:


school


# In[8]:


fire


# In[9]:


police


# In[22]:


def getClosetFacilities(Home, facilities):
    
    DF = []
    DF_all = []
    
    for f in facilities:
        
        facility = pd.DataFrame(f)
    
        Match = Home.merge(facility.iloc[:,-3:], how = "left", left_on = 'zipcode', right_on = facility.columns[-3][0:2] + 'zip')
        Match['dist_' + Match.columns[-1][0:1] + ' (mi.)'] = (((Match['longitude'] - 
                                                                 Match[Match.columns[-2][0:2] + 'longitude'])*54.6)**2 +
                                                                ((Match['latitude'] - 
                                                                 Match[Match.columns[-2][0:2] + 'latitude'])*69)**2)**0.5

        Same_zip_dist = Match[Match.iloc[:,-1].notnull()].groupby('property_id').agg({Match.columns[-1]:min}).reset_index()
        Match_same_zip = Match.merge(Same_zip_dist, how = 'right')

        _null = Match[Match.iloc[:,-1].isnull()].iloc[:,:13].reset_index(drop = True)
        Crs_diff_zip = _null.merge(facility.iloc[:,-3:], how = 'cross')
        Crs_diff_zip['dist_' + Match.columns[-2][0:1] + ' (mi.)'] = (((Crs_diff_zip['longitude'] - 
                                                                        Crs_diff_zip[Match.columns[-2][0:2] + 'longitude'])*54.6)**2 +
                                                                       ((Crs_diff_zip['latitude'] -
                                                                        Crs_diff_zip[Match.columns[-2][0:2] + 'latitude'])*69)**2)**0.5

        Diff_zip_dist = Crs_diff_zip.groupby('property_id').agg({Match.columns[-1]:min}).reset_index()
        Match_diff_zip = Crs_diff_zip.merge(Diff_zip_dist, how = 'right')
        
        
        DF = pd.concat([Match_same_zip, Match_diff_zip]).reset_index(drop = True)
        
        if len(DF_all) == 0:
            DF_all = DF
        
        else:
            DF_all = DF_all.merge(DF)

    return DF_all


# In[23]:


Facilities = [police, school, fire]


# In[24]:


near_all = getClosetFacilities(home, Facilities)
near_all


# In[25]:


Final = near_all.merge(police.iloc[:,-5:])
Final


# In[26]:


Final.info()


# In[27]:


#Final.to_csv('./Data_Source/Final.csv', index = False)

