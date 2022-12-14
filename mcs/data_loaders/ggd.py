import pandas as pd
import numpy as np
import itertools

from mcs.constants import (
    GGD_DATA_DIR,
    GGD_YEARS,
    GGD_COMPONENTS,
    GGD_AMSTERDAM_STATION_NAMES,
    GGD_AMSTERDAM_STATION_CODES,
)


def get_station_codes_from_columns(columns):
    return [
        col
        for col in columns
        if isinstance(col, str) and len(col) == 7 and col.startswith("NL")
    ]


class GGDDataLoader(object):
    def __init__(self):
        pass

    def _get_skiprows(self, fpath):
        fname = fpath.name
        return {"2020_NH3.csv": 8, "2021_NH3.csv": 6}.get(fname, 0)

    def _load_station_metadata(self, fpath):
        print(f"[GGDDataLoader] reading metadata from {fpath}")

        try:
            df = pd.read_csv(
                fpath,
                sep=";",
                encoding="latin-1",
                nrows=6,
                index_col=False,
                skiprows=self._get_skiprows(fpath),
            )
        except FileNotFoundError:
            return None
        # station data starts on fifth column
        df = df.iloc[:, 4:]

        if "StationsCode" not in df:
            return None

        station_code2info = df.set_index("StationsCode").T

        def _get_lat_lng(val):
            if pd.isna(val):
                return [np.nan, np.nan]
            return [float(v) for v in val.strip("(").strip(")").split(",")]

        station_code2info[["lat", "lng"]] = (
            station_code2info["Latitude,Longitude"]
            .map(_get_lat_lng)
            .values.tolist()
        )

        return station_code2info

    def _load_data(self, fpath):
        print(f"[GGDDataLoader] reading {fpath}")

        # tabular data starts on eighth row (headers)
        skiprows = 7 + self._get_skiprows(fpath)

        try:
            df = pd.read_csv(
                fpath, sep=";", encoding="latin-1", skiprows=skiprows
            )
        except FileNotFoundError:
            return None

        df.columns = df.columns.str.strip()

        # always ETC / GMT+1
        df["Begindatumtijd"] = pd.to_datetime(
            df["Begindatumtijd"], errors="coerce"
        )
        df["Einddatumtijd"] = pd.to_datetime(
            df["Einddatumtijd"], errors="coerce"
        )

        return df

    def _preprocess_data(self, df):
        station_codes = get_station_codes_from_columns(df.columns)

        # set the ts col as the index, and get just the station measurements
        df = df.set_index("Begindatumtijd")[station_codes]
        # make sure the data is chronological
        df = df.sort_index()
        # remove duplicate timestamps
        df = df[~df.index.duplicated()]
        # make sure we have a row for every hour
        df = df.asfreq("H")

        # # fill missing values using ffill
        # df[station_codes] = df[station_codes].ffill()

        return df

    def load(self, year, component):
        fpath = GGD_DATA_DIR / str(year) / f"{year}_{component}.csv"
        df = self._load_data(fpath)
        if df is not None:
            df["year"] = year
            df["component"] = component
        return df

    def load_station_metadata(self, year, component):
        fpath = GGD_DATA_DIR / str(year) / f"{year}_{component}.csv"
        metadata_df = self._load_station_metadata(fpath)
        if metadata_df is not None:
            metadata_df["year"] = year
            metadata_df["component"] = component
        return metadata_df

    def _get_all_year_component_combinations(self):
        return itertools.product(GGD_YEARS, GGD_COMPONENTS)

    def load_all(self, component, all_stations=False):
        dfs = [self.load(year, component) for year in GGD_YEARS]
        df = pd.concat([df for df in dfs if df is not None])

        if not all_stations:
            # filter the columns on the relevant StationsCodes
            columns = [
                "year",
                "Component",
                "Bep.periode",
                "Eenheid",
                "Begindatumtijd",
                "Einddatumtijd",
            ]

            columns += list(set(df.columns) & set(GGD_AMSTERDAM_STATION_CODES))
            df = df[columns]

        return self._preprocess_data(df)

    def load_all_station_metadata(
        self, all_stations=False, keep_all_unique=False
    ):
        metadata_dfs = [
            self.load_station_metadata(year, component)
            for year, component in self._get_all_year_component_combinations()
        ]
        metadata_df = pd.concat([df for df in metadata_dfs if df is not None])

        if not all_stations:
            metadata_df = metadata_df[
                metadata_df.Stationsnaam.isin(GGD_AMSTERDAM_STATION_NAMES)
            ]

        if keep_all_unique:
            # keep all the stations with slightly different info
            metadata_df = metadata_df.drop_duplicates()
        else:
            # only keep the latest occurrence of the StationsCode
            metadata_df = metadata_df[
                ~metadata_df.index.duplicated(keep="last")
            ].drop(columns=["year", "component"])

        return metadata_df
