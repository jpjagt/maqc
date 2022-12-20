import pandas as pd
from datetime import datetime

from mcs.constants import (
    MIT_DATA_DIR,
    MIT_CSV_HEADERS,
    MIT_NUMERIC_COLUMNS,
)
from mcs import utils


def print_rows_removal(mask, reason):
    frac = mask.sum() / mask.shape[0]
    print(
        "[MITDataLoader] filtered out "
        f"{mask.sum()}/{mask.shape[0]} ({round(frac * 100, 2)}%) rows "
        f"where {reason}"
    )


class MITDataLoader(object):
    def __init__(self):
        pass

    def _read_csv(self, fpath):
        read_csv_kwargs = {
            "header": None,
            "names": MIT_CSV_HEADERS,
            "index_col": False,
            "na_values": ["na"],
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
        df = df[df["is_summary"] == 0].copy()

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        for numeric_col in ["PM1", "PM10", "PM25"]:
            df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")

        for col in df.columns:
            if "bin" in col:
                df[col] = df[col].astype("float")

        # some timestamps might be from 1999; we only want data from last year
        # and later
        this_year = datetime.now().year
        before_this_year = df["timestamp"].dt.year < this_year
        df = df[~before_this_year]
        print_rows_removal(
            before_this_year, f"timestamp is from before {this_year}"
        )

        # it's a UTC timestamp, and we're UTC+1
        df["timestamp"] += pd.DateOffset(hours=1)

        # round to the nearest 5 seconds
        df["timestamp"] = df["timestamp"].dt.round("5s")

        non_numeric_columns = [
            col
            for col in df.columns
            if col not in MIT_NUMERIC_COLUMNS and col != "timestamp"
        ]
        # then also make sure we're taking the mean of any measurements which
        # are now rounded to the same timestamp by resampling. we do this with
        # a pd.Grouper to prevent non-numeric columns to be lost in the
        # resampling
        df = (
            df.groupby(
                [pd.Grouper(freq="5s", key="timestamp"), *non_numeric_columns]
            )
            .mean()
            .reset_index()
        )

        utils.set_timestamp_related_cols(df, src_col="timestamp")

        # set the timestamp as the index
        df = df.set_index("timestamp").sort_index()

        # TODO:
        # - humidity normalization (or filtering)
        # - zeroed out column
        # - if all values are the same in a row
        # - check sanjana's data cleaning script for more
        # filter out all columns where latitude and longitude are zero

        # filter out when lat/lng are zero
        coords_are_zero = (
            df[["latitude", "longitude"]].astype(float) == 0
        ).all(axis=1)
        df = df[~coords_are_zero]
        print_rows_removal(coords_are_zero, "coordinates were zero")

        # filter out when data_is_valid is False
        data_is_invalid = ~df["data_is_valid"].astype(bool)
        df = df[~data_is_invalid]
        print_rows_removal(data_is_invalid, "data_is_valid (OPC) was False")

        duplicate_indices = df.index.duplicated(keep="first")
        df = df[~duplicate_indices]
        print_rows_removal(duplicate_indices, "timestamp was duplicate")

        return df

    def load_data(self, experiment_name, sensor_name):
        if isinstance(sensor_name, (list, tuple)):
            return self._load_data_for_multiple_sensors(
                experiment_name, sensor_name
            )

        print(f"[MITDataLoader] loading {experiment_name}/{sensor_name}")
        data_dir = MIT_DATA_DIR / experiment_name / sensor_name
        if not data_dir.exists():
            raise ValueError(
                "the directory for the given experiment and device does not exist"
            )
        dfs = [self._read_csv(fpath) for fpath in data_dir.glob("**/*.CSV")]
        df = pd.concat(dfs)
        df = self._preprocess_data(df)
        return df

    def _load_data_for_multiple_sensors(self, experiment_name, sensor_names):
        df = pd.concat(
            {
                name: self.load_data(experiment_name, name)
                for name in sensor_names
            },
            names=["sensor_name", "timestamp"],
        )
        return df
