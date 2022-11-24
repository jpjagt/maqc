from mcs.constants import UFP_DATA_DIR
import pandas as pd
from datetime import timedelta

TIMECOMPENSATION = {"sensor1": 32, "sensor2": 0}


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

    def _preprocess_data(self, df, devicename):
        # preprocess all the data
        # sort by timestamp
        df = df.sort_values("timestamp")
        # if we want, filter out data before 2021
        # df = df.loc[(df["timestamp"] >= 2021)]
        if devicename in TIMECOMPENSATION.keys():
            df["timestamp"] = df["timestamp"] + pd.Timedelta(
                seconds=TIMECOMPENSATION[devicename]
            )
        df = df.set_index("timestamp")
        return df

    def load_data(self, experiment_name, device_name):
        # data/ufp/experiment1/device1/2022_01_01/2343_230439.txt
        data_dir = UFP_DATA_DIR / experiment_name / device_name
        dfs = [self._read_txt(fpath) for fpath in data_dir.glob("**/*.txt")]
        df = pd.concat(dfs)
        df = self._preprocess_data(df, device_name)
        return df
