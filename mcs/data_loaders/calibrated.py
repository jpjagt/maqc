import pandas as pd

from mcs.constants import CALIBRATED_DATA_DIR


class CalibratedDataLoader(object):
    def __init__(self, experiment_name):
        self._experiment_name = experiment_name
        self._dir = CALIBRATED_DATA_DIR / self._experiment_name

    def write_data(self, name, data):
        fpath = self._dir / f"{name}.csv"
        fpath.parent.mkdir(exist_ok=True, parents=True)
        data.index.names = ["timestamp", "sensor_name"]
        data.reset_index().to_csv(fpath, index=False)

    def load_data(self, name):
        fpath = self._dir / f"{name}.csv"
        if not fpath.exists():
            raise ValueError(
                f"this file doesn't exist: {fpath}. "
                "did you maybe forgot to run scripts/write_calibrated_data.py?"
            )
        return pd.read_csv(fpath, index_col=["timestamp", "sensor_name"])
