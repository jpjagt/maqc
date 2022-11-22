from mcs.constants import UFP_DATA_DIR
import pandas as pd


class UFPDataLoader(object):
    def _extract_start_time(self, fpath):
        # open the file and find starting day and time
        with open(fpath, "r") as f:
            for line in f.readlines():
                if line.startswith("Start: "):
                    return pd.to_datetime(line[7:].strip(), format="%d.%m.%Y %H:%M:%S")

        return None

    def _read_txt(self, fpath):
        df = pd.read_csv(fpath, skiprows=18, sep="\t")
        start_day_time = self._extract_start_time(fpath)
        timestamp = start_day_time + pd.to_timedelta(df["time"] - 1, unit="s")
        df["timestamp"] = timestamp

        df["src_fpath"] = str(fpath)
        df["src_fname"] = fpath.name

        return df

    def _preprocess_data(self, df):
        # preprocess all the data
        # sort by timestamp
        df = df.sort_values("timestamp")
        # if we want, filter out data before 2021
        # df = df.loc[(df["timestamp"] >= 2021)]
        return df

    def load_data(self, experiment_name, device_name):
        # data/ufp/experiment1/device1/2022_01_01/2343_230439.txt
        data_dir = UFP_DATA_DIR / experiment_name / device_name
        dfs = [self._read_txt(fpath) for fpath in data_dir.glob("**/*.txt")]
        df = pd.concat(dfs)
        df = self._preprocess_data(df)
        return df


x = UFPDataLoader()
ufp_df = x.load_data("test", "ufp1")
ufp_df[["timestamp", "src_fname"]].value_counts()
mask = ufp_df.timestamp.duplicated(keep=False)
ufp_df[mask].groupby("timestamp").number.unique().std
