import mcs
from mcs.data_loaders.mit import MITDataLoader
from mcs import plot
from mcs.constants import (
    GGD_DATA_DIR,
    MIT_DATA_DIR,
    MIT_CSV_HEADERS,
    GGD_YEARS,
    GGD_COMPONENTS,
    GGD_AMSTERDAM_STATION_NAMES,
    GGD_AMSTERDAM_STATION_CODES,
    BINSIZES,
)
import pandas as pd
import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

loader = MITDataLoader()
df1 = loader.load_data("midway", "ams1")
# df2 = loader.load_data("midway", "ams2")
df3 = loader.load_data("midway", "ams3")
df4 = loader.load_data("midway", "ams4")

df1 = df1["2022-11-07":]
# df2 = df2["2022-11-07":]
df3 = df3["2022-11-07":]
df4 = df4["2022-11-07":]

# Checking when sensors where turned on
# plot.plot_timestamps_of_mit_sensor(df1, "ams1")
# plt.show()

# plot.plot_timestamps_of_mit_sensor(df2, "ams2")
# plt.show()

# plot.plot_timestamps_of_mit_sensor(df3, "ams3")
# plt.show()

# plot.plot_timestamps_of_mit_sensor(df4, "ams4")
# plt.show()

plot.plot_line([df1, df3, df4], "PM25", outliers=False)
