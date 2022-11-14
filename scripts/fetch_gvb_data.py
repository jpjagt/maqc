import requests
import json
from mcs.constants import GVB_DATA_DIR

dataset_name2url = {
    "hdvries-away-2022": "https://maps.gvb.nl/api/v1/stop-timetables/stop-00065-hugo-de-vrieslaan-line-19-away-diemen-sniep-20220828-20221210.json",
    "hdvries-return-2022": "https://maps.gvb.nl/api/v1/stop-timetables/stop-00066-hugo-de-vrieslaan-line-19-return-station-sloterdijk-20220828-20221210.json",
}


def fetch_data(name, url):
    data = requests.get(url).json()

    KNMI_DATA_DIR.mkdir(exist_ok=True)
    fpath = GVB_DATA_DIR / f"{name}.json"

    with open(fpath, "w") as f:
        f.write(json.dumps(data))


if __name__ == "__main__":
    for dataset_name, url in dataset_name2url.items():
        fetch_data(dataset_name, url)
