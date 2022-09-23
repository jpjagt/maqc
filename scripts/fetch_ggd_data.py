import requests
import os
import urllib.request as url
from mcs.constants import (
    GGD_DATA_DIR,
    GGD_YEARS,
    GGD_COMPONENTS,
    GGD_AMSTERDAM_STATION_NAMES,
    GGD_AMSTERDAM_STATION_CODES,
    ROOT_DIR,
)

base_url = "https://data.rivm.nl/data/luchtmeetnet/Vastgesteld-jaar/"
years = [str(i) for i in range(2012, 2022)]

for year in years:
    write_dir = os.path.join(GGD_DATA_DIR, year)
    print("Creating " + write_dir)
    os.makedirs(write_dir, exist_ok=True)
    for component in GGD_COMPONENTS:
        filename = year + "_" + component + ".csv"
        url = base_url + "/" + year + "/" + filename
        response = requests.get(url + filename)
        with open(os.path.join(write_dir, filename), "wb") as f:
            f.write(response.content)
