import pandas as pd

from mcs.utils import query_yes_no
from mcs.constants import (
    CAMERA_IMAGES_DIR,
    CAMERA_LABEL_TASKS,
    IMG_LABELS_CSV_FPATH,
    CAMERA_INTERVAL,
)


# IMG_20221114_231436_00_150
def fnames2timestamps(fnames):
    ftimes = fnames.str.split("_").str[1:3].str.join("_")
    start = pd.to_datetime(ftimes, format="%Y%m%d_%H%M%S")
    offsets = fnames.str.rsplit("_").str[-1].str.split(".").str[0].astype(int)
    date_offsets = pd.Series(
        [
            pd.DateOffset(seconds=(CAMERA_INTERVAL * offset))
            for offset in offsets
        ]
    )
    timestamps = (
        start + date_offsets + pd.DateOffset(hours=1)  # UTC to our timezone
    )
    return timestamps


def create_camera_images_csv():
    if IMG_LABELS_CSV_FPATH.exists():
        query_yes_no("do you want to overwrite the existing csv?")

    fnames = sorted([fp.name for fp in CAMERA_IMAGES_DIR.glob("*.jpg")])
    df = pd.DataFrame({"fname": fnames})
    df["timestamp"] = fnames2timestamps(df.fname)
    df = df.set_index("timestamp").between_time("05:30", "18:00")
    df = df.sort_index().reset_index()
    df[CAMERA_LABEL_TASKS] = None
    df.to_csv(IMG_LABELS_CSV_FPATH, index=False)
    print("new empty camera images csv created")


if __name__ == "__main__":
    create_camera_images_csv()
