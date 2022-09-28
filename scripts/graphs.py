from unicodedata import name
import mcs
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
from mcs.data_loaders import ggd
from mcs import plot
from mcs.constants import (
    GGD_DATA_DIR,
    GGD_YEARS,
    GGD_COMPONENTS,
    GGD_AMSTERDAM_STATION_NAMES,
    GGD_AMSTERDAM_STATION_CODES,
    GGD_AMSTERDAM_STATIONS 
)

loader = ggd.GGDDataLoader()

#Load relevant data for plots
df = loader.load(2021, "PM25")
df['Einddatumtijd'] =  pd.to_datetime(df['Einddatumtijd'])

# print(GGD_AMSTERDAM_STATIONS)
df2 = pd.DataFrame(GGD_AMSTERDAM_STATIONS, columns = ['code', 'name']) 
print(df2)
 #Extract station code for corresponding station name 
df3 = df2.set_index('name', inplace=True)

def getstationcode(name, df):
     inputid = input(name)
     try:
         return df.loc[str(inputid), 'code']
     except:
         return 'No such station'
      
getstationcode('Amsterdam-Vondelpark',df3)

name_index = df.idx['name'==name]
name_code = df['code'].iloc[name_index]

#Select date&station to plot
SV = df.iloc[:,0:6]
bitmask = (SV['Einddatumtijd'] >= '2021-10-10') & (SV['Einddatumtijd'] < '2021-10-11')
SV_okt = SV[bitmask]

print(SV_okt)

plt.plot('Einddatumtijd', 'NL01485', data=SV_okt)
plt.show()



