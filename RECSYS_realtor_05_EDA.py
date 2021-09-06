#!/usr/bin/env python
# coding: utf-8

# # Exploratory Data Analysis

# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import requests
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib as mat
import matplotlib.pyplot as plt
 
sns.set(color_codes = True)


# In[12]:


city = pd.read_csv('./Data_Source/city.csv')
home = pd.read_csv('./Data_Source/home_ult.csv')
school = pd.read_csv('./Data_Source/school.csv')
fire = pd.read_csv('./Data_Source/fire.csv')
police = pd.read_csv('./Data_Source/police.csv')
crime_data = pd.read_csv('./Data_Source/crime_data.csv')
crime_police = pd.read_csv('./Data_Source/crime_police.csv')
crime_rate = pd.read_csv('./Data_Source/crime_rate.csv')
crime_police_ult = pd.read_csv('./Data_Source/crime_police_ult.csv')
Final = pd.read_csv('./Data_Source/Final.csv')
Final


# ## Horizontal Barchart for missing values

# In[14]:


data_dict = {'City' : city.isna().sum(), 'Home' : home.isna().sum(), 'School' : school.isna().sum(), 
             'Fire' : fire.isna().sum(), 'Police' : police.isna().sum(), 'Crime Data' : crime_data.isna().sum()}

fig, ax = plt.subplots(nrows = 2, ncols = 3, figsize = (8,3))

[x, y] = [0, 0]
for name,data_null in data_dict.items():
    
    if data_null.sum() != 0:
        data_null[data_null != 0].plot(kind='barh', ax = ax[x][y], fontsize = 14).set_title(name, fontsize = 14)
        
        y += 1

fig.suptitle('Missing values in tables', fontsize = 20, ha = 'center', va = 'bottom')

plt.tight_layout()


# In[5]:


city['C_zip'] = city['C_zip'].astype(str)
city.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[ ]:


city.info()


# In[7]:


home['zipcode'] = home['zipcode'].astype(str)
home.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[ ]:


home.info()


# In[7]:


school[['S_ID', 'S_zip']] = school[['S_ID', 'S_zip']].astype(str)
school.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[ ]:


school.info()


# In[8]:


fire[['F_ID', 'F_zip']] = fire[['F_ID', 'F_zip']].astype(str)
fire.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[ ]:


fire.info()


# In[9]:


police[['P_ID', 'P_zip']] = police[['P_ID', 'P_zip']].astype(str)
police.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[ ]:


police.info()


# In[10]:


crime_data.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[8]:


Final[['dist_P (mi.)', 'dist_S (mi.)', 'dist_F (mi.)']].describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[21]:


crime_police_ult[['P_ID', 'P_zip']] = crime_police_ult[['P_ID', 'P_zip']].astype(str)
crime_police_ult.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[20]:


crime_police_ult.nlargest(35,'crime_rate(%)')


# In[15]:


Final.info()


# In[9]:


print(len(home.city.unique()))
home.city.value_counts().nlargest(40)


# In[18]:


Final.nlargest(50,'price')


# ## Boxplot - price

# In[11]:


fig, ax = plt.subplots(figsize = (5,2))
sns.boxplot(x = home['price']).set_title('Distribtion of Price', fontsize = 18, ha = 'center', va = 'bottom')
plt.show()


# ## Histogram - features

# In[11]:


home.features.value_counts().nlargest(5).plot(kind = 'barh', fontsize = 14, 
                                            figsize = (5,2)).set_title('features of Homes in Ocean County',
                                                                      fontsize = 16, ha = 'center', va = 'bottom')

plt.show()


# ## Scatter plot - Price, size, beds, and baths

# In[14]:


fig, ax = plt.subplots(figsize = (7,3))

home.plot(ax = ax, kind = "scatter", x = "beds", y = "baths", 
          s = home['size(sqft)']/100, label = "Home with size(sqft)",
          c = "price", cmap = plt.get_cmap("jet"), vmax = 6000000,
          colorbar = True, alpha = 0.4).set_title('Price, size, beds, and baths of Homes in Ocean County', 
                                                  fontsize = 18, ha = 'center', va = 'bottom')

ax.set_xlabel('Number of beds', fontsize = 14)
ax.set_ylabel('Number of baths', fontsize = 14)

plt.show()


# In[4]:


MB_nj = gpd.read_file('./Maps/map_02/Municipal_Boundaries_of_NJ.shp')

ocean_county = MB_nj[MB_nj['COUNTY'] == 'OCEAN']
ocean_county = ocean_county.to_crs(epsg = 4326)


# In[18]:


ocean = gpd.read_file('./Maps/map_01/OceanCountyParcels.shp')
ocean = ocean.to_crs(epsg = 4326)


# ## Map: Homes, Police Stations, and Crime Rate in Ocean County

# In[81]:


fig, ax = plt.subplots(figsize = (12,15))
ax.set_aspect('equal')

ocean.plot(ax = ax, color = 'white', 
           edgecolor = 'grey', alpha = 0.15).set_title('Homes, Police Stations, and Crime Rate in Ocean County',
                                                       fontsize = 20, ha = 'center', va = 'bottom')

crime_rate.plot(ax = ax, column = 'crime_rate(%)', cmap ='jet', vmax = 6, 
                linewidth = 0.8, edgecolor = 'black', alpha = 0.5)

home.plot(ax = ax, kind = "scatter", x = "longitude", y = "latitude", 
          s = home['size(sqft)']/120, label = "Home with size(sqft)",
          c = "price", cmap = plt.get_cmap("jet"), vmax = 6000000,
          colorbar = True, alpha = 0.4)

crime_police.plot(ax = ax, kind = "scatter", x = "P_longitude", y = "P_latitude",
                  s = 90, label = "Police Station",
                  color = 'gold', edgecolors = 'darkorange',
                  marker = 'p')

crime_rate.nsmallest(5,'crime_rate(%)').apply(lambda x: ax.annotate(s = x.NAME,
                                                                    xy = x.geometry.centroid.coords[0],
                                                                    ha = 'right', fontsize = 16,
                                                                    arrowprops = dict(facecolor = 'skyblue', shrink = 0.05),
                                                                    bbox = dict(boxstyle = "round,pad=0.1", fc = "skyblue"))
                                              ,axis = 1)

crime_rate.nlargest(5,'crime_rate(%)').apply(lambda x: ax.annotate(s = x.NAME,
                                                                   xy = x.geometry.centroid.coords[0],
                                                                   ha = 'left', fontsize = 16,
                                                                   arrowprops = dict(facecolor = 'lightcoral', shrink = 0.05),
                                                                   bbox = dict(boxstyle = "round,pad=0.1", fc = "lightcoral"))
                                             ,axis = 1)

ax.set_xlabel('Longitude', fontsize = 14)
ax.set_ylabel('Latitude', fontsize = 14)

plt.show()


# ## Map: Homes, Schools, and Fire Stations in Ocean County

# In[26]:


fig, ax = plt.subplots(figsize = (12,15))
ax.set_aspect('equal')

ocean.plot(ax = ax, color = 'white', 
           edgecolor = 'grey', alpha = 0.15).set_title('Homes, Schools, and Fire Stations in Ocean County',
                                                       fontsize = 20, ha = 'center', va = 'bottom')

crime_rate.plot(ax = ax, column = 'POP2010', cmap ='jet', vmax = 40000, 
                linewidth = 0.8, edgecolor = 'black', alpha = 0.5)

home.plot(ax = ax, kind = "scatter", x = "longitude", y = "latitude", 
          s = home['size(sqft)']/120, label = "Home with size(sqft)",
          c = "price", cmap = plt.get_cmap("jet"), vmax = 6000000,
          colorbar = True, alpha = 0.4)

school.plot(ax = ax, kind = "scatter", x = "S_longitude", y = "S_latitude",
            s = 90, label = "School",
            color = 'lime', edgecolors = 'white', alpha = 0.6,
            marker = 's')

fire.plot(ax = ax, kind = "scatter", x = "F_longitude", y = "F_latitude",
          s = 100, label = "Fire Station",
          color = 'magenta', edgecolors = 'white', alpha = 0.7,
          marker = 'd')

crime_rate.nsmallest(5,'POP2010').apply(lambda x: ax.annotate(s = x.NAME,
                                                              xy = x.geometry.centroid.coords[0],
                                                              ha = 'left', fontsize = 16, alpha = 0.8,
                                                              arrowprops = dict(facecolor = 'skyblue', shrink = 0.05),
                                                              bbox = dict(boxstyle = "round,pad=0.1", fc = "skyblue"))
                                        ,axis = 1)

crime_rate.nlargest(5,'POP2010').apply(lambda x: ax.annotate(s = x.NAME,
                                                             xy = x.geometry.centroid.coords[0],
                                                             ha = 'right', fontsize = 16, alpha = 0.8,
                                                             arrowprops = dict(facecolor = 'lightcoral', shrink = 0.05),
                                                             bbox = dict(boxstyle = "round,pad=0.1", fc = "lightcoral"))
                                       ,axis = 1)

ax.set_xlabel('Longitude', fontsize = 14)
ax.set_ylabel('Latitude', fontsize = 14)

plt.show()

