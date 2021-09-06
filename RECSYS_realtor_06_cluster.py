#!/usr/bin/env python
# coding: utf-8

# # Get clusters from Final.csv

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import requests
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib as mat
import matplotlib.pyplot as plt
import os
 
sns.set(color_codes = True)


# In[ ]:


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
DS_dir = currentdir + '/Data_Source'

try:
    os.mkdir(DS_dir, mode = 0o666)

except FileExistsError:
    
    pass


# In[2]:


Final = pd.read_csv('./Data_Source/Final.csv')
Final[['zipcode', 'S_zip', 'F_zip', 'P_zip']] = Final[['zipcode', 'S_zip', 'F_zip', 'P_zip']].astype(str)
Final


# In[3]:


Final.info()


# In[4]:


Final.iloc[:,:13].describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[5]:


Final[['dist_P (mi.)', 'dist_S (mi.)', 'dist_F (mi.)']].describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[6]:


from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
column_trans_s = ColumnTransformer([('bed_int', MinMaxScaler(), ['beds']),
                                    ('bath_int', MinMaxScaler(), ['baths']),
                                    ('size(sqft)_num', MinMaxScaler(),['size(sqft)']),
                                    ('longitude_num', MinMaxScaler(),['longitude']),
                                    ('latitude_long_num', MinMaxScaler(),['latitude']),
                                    ('dist_P (mi.)_num', MinMaxScaler(),['dist_P (mi.)']),
                                    ('dist_S (mi.)_num', MinMaxScaler(),['dist_S (mi.)']),
                                    ('dist_F (mi.)_num', MinMaxScaler(),['dist_F (mi.)']),
                                    ('crime_num', MinMaxScaler(),['crime_rate(%)']),
                                    ('popden_int', MinMaxScaler(),['POPDEN2010 (per sq. mi.)']),
                                    ('text', TfidfVectorizer(use_idf = True, stop_words = 'english'),'features')
                                   ], remainder = 'drop')

token = column_trans_s.fit_transform(Final)
token


# In[7]:


token.shape


# ## Cosine Similarity

# In[8]:


from sklearn.metrics.pairwise import cosine_similarity

cos_sim = cosine_similarity(token)
cos_sim


# ## DBSCAN

# In[9]:


from sklearn.cluster import DBSCAN
model_DB = DBSCAN(eps = 0.01, min_samples = 30, metric = 'cosine').fit(cos_sim)
labels = model_DB.labels_

unique, counts = np.unique(labels, return_counts = True)
print(dict(zip(unique, counts)))


# In[10]:


labels


# In[11]:


_vars = Final.columns.tolist()
_vars = _vars[:5] + ['latitude'] + ['longitude'] + ['dist_P (mi.)'] + ['dist_S (mi.)'] + ['dist_F (mi.)'] + _vars[-2:] + ['features'] 
_vars


# In[12]:


F = Final[_vars].copy()
F.insert(5, 'cluster', labels, True)
F


# In[13]:


# F.to_csv('./Data_Source/Final_clustered.csv', index = False)


# ## Comparison of clusters

# In[14]:


F = pd.read_csv('./Final with cluster.csv')


# In[13]:


sns.set()

PairGrid = sns.PairGrid(F[(F['cluster'] == 0) | (F['cluster'] == 1)], vars = _vars[2:-1], hue = 'cluster', 
                        diag_sharey = False, corner = True)
PairGrid.map_lower(sns.scatterplot, s = 50, edgecolor = 'white', alpha = 0.5)
PairGrid.map_diag(sns.histplot)
PairGrid.add_legend()

PairGrid.fig.suptitle('An overview of the comparison of clusters', fontsize = 56, ha = 'center', va = 'baseline')
plt.show()


# In[14]:


sns.set(font_scale = 2)
fig, ax = plt.subplots(figsize = (8,10))

sns.histplot(data = F[(F['cluster'] == 0) | (F['cluster'] == 1)], 
             y = 'features', hue = 'cluster')

plt.title('Comparison of clusters in features', fontsize = 20, ha = 'center', va = 'bottom')
plt.show()


# In[43]:


F['g_features'] = "not specified"
F.loc[F['features'].str.contains("single_story"), 'g_features'] = "*, single_story"
F.loc[F['features'].str.contains("two_or_more_stories"), 'g_features'] = "*, two_or_more_stories"
F[['cluster', 'features', 'g_features']]


# In[44]:


sns.set(font_scale = 2)
fig, ax = plt.subplots(figsize = (15,5))

sns.histplot(data = F[(F['cluster'] == 0) | (F['cluster'] == 1)], 
             y = 'g_features', hue = 'cluster')

plt.title('Comparison of clusters in the number of stories', fontsize = 20, ha = 'center', va = 'bottom')
plt.show()


# In[15]:


sns.set()

fig, ax = plt.subplots(nrows = 1, ncols = 3, figsize = (15,3))
for x in _vars[2:5]:
    sns.histplot(ax = ax[(_vars.index(x)-2)%3], data = F[(F['cluster'] == 0) | (F['cluster'] == 1)], 
                 x = x, hue = 'cluster')
fig.suptitle('Detailed comparison of clusters in beds, baths, and size', fontsize = 20, ha = 'center', va = 'bottom')
plt.tight_layout()

PairGrid_1 = sns.PairGrid(F[(F['cluster'] == 0) | (F['cluster'] == 1)], vars = _vars[2:5], 
                          hue = 'cluster', diag_sharey = False, corner = True)
PairGrid_1.map_lower(sns.scatterplot, s = 50, edgecolor = 'white', alpha = 0.5)
PairGrid_1.add_legend()

PairGrid_1.fig.suptitle('PairGrid of the comparison of clusters in beds, baths, and size', fontsize = 20, ha = 'center', va = 'baseline')
plt.show()


# In[16]:


sns.set()

fig, ax = plt.subplots(nrows = 1, ncols = 3, figsize = (15,3))
for x in _vars[7:10]:
    sns.histplot(ax = ax[(_vars.index(x)-7)%3], data = F[(F['cluster'] == 0) | (F['cluster'] == 1)], 
                 x = x, hue = 'cluster')

fig.suptitle('Detailed comparison of clusters in distance to facilities', fontsize = 20, ha = 'center', va = 'bottom')
plt.tight_layout()


# In[17]:


MB_nj = gpd.read_file('./Municipal_Boundaries_of_NJ.shp')

ocean_county = MB_nj[MB_nj['COUNTY'] == 'OCEAN']
ocean_county = ocean_county.to_crs(epsg = 4326)


# In[18]:


ocean = gpd.read_file('./OceanCountyParcels.shp')
ocean = ocean.to_crs(epsg = 4326)


# ## Visualize clusters on the map

# In[19]:


fig, ax = plt.subplots(figsize = (12, 15))
ax.set_aspect('equal')

ocean.plot(ax = ax, color = 'white', 
           edgecolor = 'grey', alpha = 0.15).set_title('Homes, Police Stations, and Crime Rate in Ocean County',
                                                       fontsize = 20, ha = 'center', va = 'bottom')

ocean_county.plot(ax = ax, color = 'white', edgecolor = 'grey', 
                  alpha = 0.15).set_title('Clusters of homes in Ocean County',
                                          fontsize = 20, ha = 'center', va = 'bottom')

F[F['cluster'] == 0].plot(ax = ax, kind = "scatter", x = 'longitude', y = 'latitude',
                  s = Final['size(sqft)']/30, label = 'cluster 0',
                  color = 'skyblue', edgecolors = 'blue', alpha = 0.5,
                  marker = 'X')

F[F['cluster'] == 1].plot(ax = ax, kind = "scatter", x = 'longitude', y = 'latitude',
                  s = Final['size(sqft)']/30, label = 'cluster 1',
                  color = 'peachpuff', edgecolors = 'darkorange', alpha = 0.5,
                  marker = '*')

plt.show()


# ## Evaluation

# In[12]:


from sklearn.metrics import silhouette_score

silhouette_score(cos_sim, labels, metric = 'cosine')


# In[15]:


from sklearn.metrics import calinski_harabasz_score

calinski_harabasz_score(cos_sim, labels)


# In[17]:


clustered_Final = Final.merge(F)
clustered_Final


# ## Get Top-N Recommendations

# In[59]:


def getRecommendations(propertyID, cities, N):

    house = clustered_Final[clustered_Final['property_id'] == propertyID]

    print('Based on your choice:')
    display(house)

    cluster_user = house['cluster'].values[0]

    print('\n\n\n')
    print(f'We recommend you TOP {N} houses:')
    print(f'in these municipalities{cities}')
    display(clustered_Final[(clustered_Final['cluster'] == cluster_user) & (clustered_Final['city'].isin(cities)) & ~(clustered_Final['property_id'] == propertyID)].sort_values('price').head(N))


# In[61]:


getRecommendations('M5001559427', ['Manchester', 'Manahawkin', 'Toms River'], 5)

