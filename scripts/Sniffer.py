#import snifferplot as sp
from shutil import get_archive_formats
import pandas as pd
import os 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from pandas.api.types import is_numeric_dtype

print(os.getcwd())

# x is file name; particle is particulate matter you wish to plot (pm2_5, pm10, pm1_0), 
# maxvalue is maximal value of you the particle you wish to plot. 
x = '/home/mitch182/code/measuring-construction-sites/data/Sniffer/2022_10_20_snifferbike.maq+321.csv'  
df = pd.read_csv(x)

#explore large and low values to get indication of time of pollution
df.nlargest(n=10, columns=['pm10', 'pm1_0', 'pm2_5'])
df.nsmallest(n=10, columns=['pm10', 'pm1_0', 'pm2_5'])

#set time column to pandas datetime format
df['time'] =  pd.to_datetime(df['time'])

print(df)


# Search for highest values in all numerical 
# columns and put in dataframe
dfs = []

for col in df.columns:
    top_values = []
    if is_numeric_dtype(df[col]):
        top_values = df[col].nlargest(n=10)
        dfs.append(pd.DataFrame({col: top_values}).reset_index(drop=True))
pd.concat(dfs, axis=1)


#Plot pm concentrations over time
#df['time'] = pd.Series(range(len(df)))

myfmt= md.DateFormatter('%H:%M')
plot = df.set_index('time').plot(y = ['pm1_0', 'pm2_5', 'pm10'],
rot= 70, ylabel= 'μg/m3')
plot.xaxis.set_major_formatter(myfmt) #apply Hour Minute format to xticks

#plot pm concentrations with humidity and temperature
myfmt= md.DateFormatter('%H:%M')
plot = df.set_index('time').plot(y = ['rh', 'pm2_5','t'],
rot= 70, ylabel= 'pm2.5 = μg/m3')
plot.xaxis.set_major_formatter(myfmt) #apply Hour Minute format to xticks



