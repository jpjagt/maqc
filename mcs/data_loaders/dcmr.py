import pandas as pd

from mcs.constants import DCMR_DATA_DIR


class DCMRDataLoader(object):
    def _load_pm25_10sec(self, experiment_dir):
        df = pd.read_excel(
            experiment_dir / "pm25-10sec.xlsx",
            skiprows=1,
        ).rename(
            columns={
                "494SDM - PM2.5.L": "PM25",
                "J335 S49": "timestamp",
            }
        )
        df.timestamp = pd.to_datetime(df.timestamp)
        df = df.set_index("timestamp")
        return df

    def load_10sec_data(self, experiment_name):
        experiment_dir = DCMR_DATA_DIR / experiment_name
        df = self._load_pm25_10sec(experiment_dir)
        return df

    def _load_hourly(self, experiment_dir, fname, usecols, col_rename):
        df = pd.read_excel(
            experiment_dir / fname, index_col=0, usecols=usecols
        ).rename(columns=col_rename)
        # the first and last row are garbage
        df = df.iloc[1:-1]

        df.index = pd.to_datetime(df.index)
        df.index.name = "timestamp"

        return df.astype(float)

    def _load_no2_hourly(self, experiment_dir):
        return self._load_hourly(
            experiment_dir,
            "no2-hourly.xlsx",
            usecols="A,B",
            col_rename={
                "494SDM\n494 NO2": "no2",
            },
        )

    def _load_pm_hourly(self, experiment_dir):
        return self._load_hourly(
            experiment_dir,
            "pm-hourly.xlsx",
            usecols="A,B,C",
            col_rename={
                "494SDM\n494 PM2,5 * factor": "PM25",
                "494SDM\n494 PM10 * factor": "PM10",
            },
        )

    def load_hourly_data(self, experiment_name):
        experiment_dir = DCMR_DATA_DIR / experiment_name
        df = self._load_no2_hourly(experiment_dir)
        df = df.merge(
            self._load_pm_hourly(experiment_dir),
            left_index=True,
            right_index=True,
        )
        return df
