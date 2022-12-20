import pandas as pd

from mcs.constants import CAMERA_DIR


class CameraImageLabelsDataLoader(object):
    def load_data(self, fname="img_labels"):
        fpath = CAMERA_DIR / f"{fname}.csv"
        df = pd.read_csv(
            fpath, parse_dates=["timestamp"], index_col=False, sep=None
        )

        return df
