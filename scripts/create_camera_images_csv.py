import fire

from mcs.utils import query_yes_no
from mcs.data_loaders import CameraImagesDataLoader
from mcs.constants import (
    CAMERA_LABEL_TASKS,
    IMG_LABELS_CSV_FPATH,
)


def create_camera_images_csv(start_time="06:15", end_time="16:45"):
    if IMG_LABELS_CSV_FPATH.exists():
        query_yes_no("do you want to overwrite the existing csv?")

    df = CameraImagesDataLoader().load_data()
    df = df.between_time(start_time, end_time).reset_index()
    df[CAMERA_LABEL_TASKS] = None
    df.to_csv(IMG_LABELS_CSV_FPATH, index=False)
    print("new empty camera images csv created")


if __name__ == "__main__":
    fire.Fire(create_camera_images_csv)
