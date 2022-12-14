import pandas as pd

from mcs.constants import CALIBRATED_DATA_DIR
from mcs.background_levels import set_cols_without_bg


class CalibratedDataLoader(object):
    def __init__(self, experiment_name):
        self._experiment_name = experiment_name
        self._dir = CALIBRATED_DATA_DIR / self._experiment_name

    def write_data(self, name, data):
        fpath = self._dir / f"{name}.csv"
        fpath.parent.mkdir(exist_ok=True, parents=True)
        data.index.names = ["sensor_name", "timestamp"]
        data.reset_index().to_csv(fpath, index=False)

    def load_data(self, name):
        fpath = self._dir / f"{name}.csv"
        if not fpath.exists():
            raise ValueError(
                f"this file doesn't exist: {fpath}. "
                "did you maybe forgot to run scripts/write_calibrated_data.py?"
            )

        df = pd.read_csv(
            fpath,
            index_col=["sensor_name", "timestamp"],
            parse_dates=["timestamp"],
        )
        df = df.unstack(level=0)
        set_cols_without_bg(
            df,
            {
                "pm25_calibrated": "PM25",
                "no2_calibrated": "NO2",
                "pm25_uncalibrated": "PM25",
                "no2_uncalibrated": "NO2",
            },
        )
        df = df.stack().swaplevel()

        return df
