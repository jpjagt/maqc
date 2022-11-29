import fire

from mcs.camera import label_images
from mcs.constants import (
    IMG_LABELS_CSV_FPATH,
)


if __name__ == "__main__":
    if not IMG_LABELS_CSV_FPATH.exists():
        raise RuntimeError(
            "you first need to run scripts/create_camera_images_csv.py. "
            "this script will create the .csv file which is used by the image "
            "labeling tool."
        )
    fire.Fire(label_images)
