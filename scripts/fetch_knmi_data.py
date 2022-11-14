import requests
from mcs.constants import KNMI_DATA_DIR
import zipfile
from io import BytesIO


def get_data_for():
    url = "https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_240.zip"
    response = requests.get(url)
    #unzip that bad boy
    zippy = zipfile.ZipFile(BytesIO(response.content))
    KNMI_DATA_DIR.mkdir(exist_ok=True)
    fpath = KNMI_DATA_DIR
    zippy.extractall(fpath)

if __name__ == '__main__':
    get_data_for()


