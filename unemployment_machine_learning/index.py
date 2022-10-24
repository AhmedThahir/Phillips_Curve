#!/usr/bin/env python
# coding: utf-8

# # Importing Libaries

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


import matplotlib.pyplot as plt
get_ipython().run_line_magic('config', "InlineBackend.figure_formats = ['svg'] # makes everything svg by default")
get_ipython().run_line_magic('matplotlib', 'inline')

import seaborn as sns
sns.set_theme() # affects all matplotlib and seaborn plots
plt.style.use('ggplot')


# In[3]:


import plotly.express as px
import plotly.graph_objs as go

import plotly.io as pio
pio.templates.default = "ggplot2"
pio.renderers.default = "notebook"
# injects plotly.js into the notebook for offline plotly
# but only works for the first save, for some reason


# In[4]:


from fredapi import Fred
fred = Fred(api_key="ee01755ad12aff2d809e022069706883")


# # Importing Data

# ## SPF
# 
# > An Excel workbook with multiple worksheets. Each worksheet holds the time series of mean forecasts for the level of a different variable. The first two columns list the year and quarter in which the survey was conducted. The remaining columns give the mean forecasts for all quarterly and annual horizons, as described below
# ~ SPF Documentation

# In[5]:


spf_unrate = (
    pd.read_excel(
        "ds/us/survey_of_professional_forecasters_mean_responses.xlsx",
        parse_dates = True
    )
)
spf_unrate


# In[6]:


earliest_year = spf_unrate["YEAR"].iloc[0]


# In[7]:


spf_unrate = spf_unrate.set_index(spf_unrate['YEAR'].astype(str) + 'Q' + spf_unrate['QUARTER'].astype(str))
spf_unrate.index.name="PERIOD"

spf_unrate = spf_unrate.drop(["YEAR", "QUARTER"], axis=1)
spf_unrate


# # FRED Unemployment Rate
# 
# Starting from the earliest year of SPF
# (Why unnecessarily load everything?)

# In[8]:


fred_unrate = (
    pd.DataFrame(
        data = fred.get_series(
            "UNRATE",
            observation_start = str(earliest_year) + "-01-01"
        ),
        columns = ["UNRATE"]
    )
)
fred_unrate.index.name = 'DATE'

fred_unrate


# ## Resampling the Data to Quarterly Mean

# In[9]:


fred_unrate.index = fred_unrate.index.to_period('Q')
fred_unrate = fred_unrate.groupby("DATE").mean()
fred_unrate.index.name="PERIOD"
fred_unrate


# # Visualization

# In[10]:


fig = go.Figure().update_layout(
  # Title and Subtitle
  title = dict(
    text =
        "Unemployment Rate over the Years" +
        "<br><sup>" + "(Interactive Graph)" + "</sup>",
    x = 0.08,
    y = 0.90
  ),
  
  # axes titles
  xaxis_title = "Period",
  yaxis_title = "Unemployment Rate",
  
  hovermode = "x unified",
  
  # legend
  showlegend = True,
  legend = dict(
    orientation = 'h',
    
    # positioning
    yanchor = "bottom",
    y = 1,
    xanchor = "left",
    x = 0
  )
)

fig.add_trace(go.Scattergl(
    x = fred_unrate.index.astype(str),
    y = fred_unrate[fred_unrate.columns[0]],
    name = "FRED (Actual)"    
))

fig.add_trace(go.Scattergl(
    x = spf_unrate.index.astype(str),
    y = spf_unrate["UNEMP1"],
    name = "SPF (Forecast)"
))

fig.show(config = dict(
      doubleClickDelay = 400,
      displayModeBar = False,
      showTips = False
))

