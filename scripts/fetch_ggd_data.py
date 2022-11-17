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



def get_data_for(years, base_url, current_year=False):
    for year in years:
        write_dir = os.path.join(GGD_DATA_DIR, year)
        print("Creating " + write_dir)
        os.makedirs(write_dir, exist_ok=True)
        for component in GGD_COMPONENTS:

            filename = year + "_" + component + ".csv"
            if current_year:
                url = base_url + filename
            else:
                url = base_url + year + "/" + filename
            print(url)
            response = requests.get(url)
            with open(os.path.join(write_dir, filename), "wb") as f:
                f.write(response.content)

# get_data_for(
#     years = [year for year in GGD_YEARS if not year.startswith("2022")],
#     base_url = "https://data.rivm.nl/data/luchtmeetnet/Vastgesteld-jaar/",
# )

get_data_for(
    years = [year for year in GGD_YEARS if year.startswith("2022")],
    base_url = "https://data.rivm.nl/data/luchtmeetnet/Actueel-jaar/",
    current_year=True
)