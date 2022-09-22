import pandas as pd

from mcs.constants import GGD_DATA_DIR


class GGDDataLoader(object):
    def __init__(self):
        pass

    def _load_station_metadata(self, fpath):
        # tabular data starts on eighth row (headers)
        df = pd.read_csv(
            fpath, sep=";", encoding="latin-1", nrows=7, index_col=False
        )
        # station data starts on fifth column
        df = df.iloc[:, 4:]
        station_code2info = df.set_index("StationsCode")
        return station_code2info

    def _load_data(self, fpath):
        # tabular data starts on eighth row (headers)
        df = pd.read_csv(fpath, sep=";", encoding="latin-1", skiprows=7)
        return df

    def load_for_year(self, year, component):
        fpath = GGD_DATA_DIR / year / f"{year}_{component}.csv"
        return self._load_data(fpath)
