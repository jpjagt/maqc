from lib2to3.pgen2.pgen import DFAState
from typing import Any
from unicodedata import name
import mcs
import matplotlib.pyplot as plt
from mcs.utils import get_ts_df
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

# #Load relevant data for plots
df = loader.load(2021, "PM25")
df['Einddatumtijd'] =  pd.to_datetime(df['Einddatumtijd'])
df.head(10)


# Create dataframe for plot
df2 = get_ts_df(df)


#plot pm concentration for vondelpark station
start_date_1 = "2021-10-10"
end_date_1 = "2021-10-10"
station_codes = ['NL49014']

df2.loc[start_date_1:end_date_1, station_codes].plot()
plt.show()

#Different date
start_date_2 = "2021-10-11"
end_date_2 = "2021-10-11"

df2.loc[start_date_2:end_date_2, station_codes].plot()
plt.show()

#different date
start_date_2 = "2021-10-11"
end_date_3 = "2021-10-18"

df2.loc[start_date_2:end_date_3, station_codes].plot()
plt.show()


df2.head(10)

print("NL01485:", df['NL01485'].max())

