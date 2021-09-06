#!/usr/bin/env python
# coding: utf-8

# # Duplicate examples in Home dataset

# In[1]:


import pandas as pd
import numpy as np
import datetime as dt


# In[34]:


pre_home = pd.read_csv('./Data_Source/home.csv').drop_duplicates().reset_index(drop = True)
pre_home['last_update'] = pd.to_datetime(pre_home['last_update'])
pre_home['days_ago'] = (np.datetime64(dt.date.today()) - 
                        pre_home[['last_update']].values.astype('datetime64[D]')).astype(int)
pre_home


# ## duplicated prices

# In[69]:


Home_1 = pre_home[['price', 'line', 'city']].drop_duplicates()
Home_1[Home_1.duplicated(['line', 'city'])].sort_values(['line', 'city']).head()


# ## duplicated IDs

# In[67]:


Home_1 = pre_home[['property_id', 'latitude', 'line', 'city']].drop_duplicates()
Home_1[Home_1.duplicated(['line', 'city'])].sort_values(['line', 'city']).head()


# ## duplicated coordinates

# In[65]:


pre_home[['longitude', 'latitude', 'line', 'city']][(pre_home['line'] == '9 Molly Ct') | (pre_home['line'] == '51 Melanie Way')].drop_duplicates()


# ## duplicated features

# In[68]:


pre_home[['features', 'line', 'city']][(pre_home['line'] == '30 South St') | (pre_home['line'] == '5 Madras Ct')].drop_duplicates()

