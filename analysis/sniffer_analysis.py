import mcs
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns 
import matplotlib.dates as mdates
from mcs.data_loaders import sniffer


loader = sniffer.SNIFFERdataloader()
df = loader.load_data('snifferdata11-11_184')
df2 = loader.load_data('snifferdata11-11_321')

#Set time range for plots 
data = df.loc[((df[['time']] < '2022-11-11 14:40:00').all(axis=1) 
& (df[['time']] > '2022-11-11 13:30:00').all(axis=1))]


#create variables for plots
x1 = data['time']
y1 = data['pm2_5']
y2 = data['pm1_0']
y3 = data['pm10']

#plot pm values over time
sns.set()
fig, ax = plt.subplots()
ax.plot(x1, y3, label = 'PM 10', alpha = 0.8)
ax.plot(x1, y2, label = 'PM 1', alpha = 0.8)
ax.plot(x1, y1, label = 'PM 2.5', alpha = 0.8)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

plt.ylabel('μm/m³')
plt.xlabel('time')
plt.title('Snifferbike PM measurements 11-11-2022')
plt.legend()
plt.show()


