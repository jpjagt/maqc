import fire
import requests
import os
from datetime import date
from mcs.constants import (
    GGD_DATA_DIR,
    GGD_YEARS,
    GGD_COMPONENTS,
)

GGD_LUCHTMEETNET_COMPLETED_YEAR_BASE_URL = (
    "https://data.rivm.nl/data/luchtmeetnet/Vastgesteld-jaar/"
)
GGD_LUCHTMEETNET_CURRENT_YEAR_BASE_URL = (
    "https://data.rivm.nl/data/luchtmeetnet/Actueel-jaar/"
)


def fetch_ggd_data(years=GGD_YEARS):
    current_year = str(date.today().year)
    for year in years:
        write_dir = GGD_DATA_DIR / year
        print(f"writing to {write_dir}")
        os.makedirs(write_dir, exist_ok=True)

        for component in GGD_COMPONENTS:
            filename = year + "_" + component + ".csv"

            if year.startswith(current_year):
                url = GGD_LUCHTMEETNET_CURRENT_YEAR_BASE_URL
            else:
                url = f"{GGD_LUCHTMEETNET_COMPLETED_YEAR_BASE_URL}{year}/"

            url += filename

            print(f"downloading {url}")
            response = requests.get(url)

            if response.status_code != 200:
                continue

            with open(os.path.join(write_dir, filename), "wb") as f:
                f.write(response.content)


if __name__ == "__main__":
    fire.Fire(fetch_ggd_data)
