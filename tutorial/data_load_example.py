import mcs
from mcs.data_loaders import ggd
from mcs import plot
from mcs.constants import (
    GGD_DATA_DIR,
    GGD_YEARS,
    GGD_COMPONENTS,
    GGD_AMSTERDAM_STATION_NAMES,
    GGD_AMSTERDAM_STATION_CODES,
)

loader = ggd.GGDDataLoader()

df = loader.load(2017, "CO")
print(df)
