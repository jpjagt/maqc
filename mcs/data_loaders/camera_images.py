import pandas as pd
from PIL import Image
from mcs.constants import CAMERA_IMAGES_DIR


def get_content_created_timestamp_of_fpath(fpath):
    exifdata = Image.open(fpath).getexif()
    ts = exifdata.get(306)  # 306 is the tag_id of "DateTime"
    return ts


class CameraImagesDataLoader(object):
    def _get_content_created_timestamps(self, df):
        content_created = df["fpath"].map(
            get_content_created_timestamp_of_fpath
        )
        # the timestamps are formatted like '2022:11:22 15:58:28'
        return pd.to_datetime(content_created, format="%Y:%m:%d %H:%M:%S")

    def load_data(self, data_dir=CAMERA_IMAGES_DIR):
        fpaths = list(data_dir.glob("**/*.jpg"))
        df = pd.DataFrame({"fpath": fpaths})

        def _get_name(fpath):
            return fpath.name

        df["fname"] = df.fpath.map(_get_name)

        df["timestamp"] = self._get_content_created_timestamps(df)
        df = df.set_index("timestamp").sort_index()

        return df
