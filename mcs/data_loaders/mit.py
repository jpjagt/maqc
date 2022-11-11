import pandas as pd

from mcs.constants import MIT_DATA_DIR, MIT_CSV_HEADERS


class MITDataLoader(object):
    def __init__(self):
        pass

    def _read_csv(self, fpath):
        read_csv_kwargs = {
            "header": None,
            "names": MIT_CSV_HEADERS,
            "index_col": False,
        }

        try:
            df = pd.read_csv(fpath, **read_csv_kwargs)
        except pd.errors.ParserError:
            df = pd.read_csv(fpath, **read_csv_kwargs, skiprows=1)

        df["src_fpath"] = str(fpath)
        df["src_fname"] = fpath.name
        return df

    def _preprocess_data(self, df):
        # filter out the summary rows
        df = df[df["is_summary"] == 0]

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        # some timestamps might be from 1999; we only want data from this year
        # and later
        df = df[df["timestamp"].dt.year > 2021]

        # it's a UTC timestamp, and we're UTC+1
        df["timestamp"] += pd.DateOffset(hours=1)

        for col in df.columns:
            if "bin" in col:
                df[col] = df[col].astype("float")

        # TODO:
        # - humidity normalization (or filtering)
        # - zeroed out column
        # - if all values are the same in a row
        # - check sanjana's data cleaning script for more

        return df

    def load_data(self, experiment_name, device_name):
        data_dir = MIT_DATA_DIR / experiment_name / device_name
        dfs = [self._read_csv(fpath) for fpath in data_dir.glob("**/*.CSV")]
        df = pd.concat(dfs)
        df = self._preprocess_data(df)
        return df
