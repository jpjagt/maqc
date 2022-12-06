"""
time - number of seconds since start of experiment
number - number concentration
diam - average particle diameter
LDSA - lung deposited surface area
surface - total surface area
mass - Particle mass (<0.3 um)
A1
A2
idiff
HV
EM1
EM2
DV
T
RH
P
flow
bat
Ipump
error
PWMpump
"""

from mcs.constants import UFP_DATA_DIR
import pandas as pd

from mcs import utils

DEVICE_NAME2NOF_SECONDS_OFFSET = {"sensor1": 32, "sensor2": 0}


class UFPDataLoader(object):
    def _extract_start_time(self, fpath):
        # open the file and find starting day and time
        with open(fpath, "r") as f:
            for line in f.readlines():
                if line.startswith("Start: "):
                    return pd.to_datetime(
                        line[7:].strip(), format="%d.%m.%Y %H:%M:%S"
                    )

        return None

    def _read_txt(self, fpath):
        df = pd.read_csv(fpath, skiprows=18, sep="\t")
        start_day_time = self._extract_start_time(fpath)
        timestamp = start_day_time + pd.to_timedelta(df["time"] - 1, unit="s")
        df["timestamp"] = timestamp

        df["src_fpath"] = str(fpath)
        df["src_fname"] = fpath.name

        return df

    def _preprocess_data(self, df, device_name):
        # preprocess all the data
        # sort by timestamp
        df = df.sort_values("timestamp")
        # if we want, filter out data before 2021
        # df = df.loc[(df["timestamp"] >= 2021)]
        if device_name in DEVICE_NAME2NOF_SECONDS_OFFSET:
            df["timestamp"] = df["timestamp"] + pd.Timedelta(
                seconds=DEVICE_NAME2NOF_SECONDS_OFFSET[device_name]
            )

        # round to the nearest 5 seconds
        df["timestamp"] = df["timestamp"].dt.round("5s")

        non_numeric_columns = [
            col
            for col in df.columns
            if not pd.api.types.is_numeric_dtype(df[col])
            and col != "timestamp"
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

        df = df.set_index("timestamp")
        return df

    def load_data(self, experiment_name, device_name):
        # example path: data/ufp/2022_11_25/sensor1/...
        data_dir = UFP_DATA_DIR / experiment_name / device_name
        dfs = [self._read_txt(fpath) for fpath in data_dir.glob("**/*.txt")]
        df = pd.concat(dfs)
        df = self._preprocess_data(df, device_name)
        return df
