import fire

from mcs.data_loaders import CameraImagesDataLoader
from mcs.constants import CAMERA_DIR
from mcs.camera import create_video


def create_video_from_images(
    output_fname, fps=24, start_time="06:15", end_time="17:30"
):
    output_fpath = CAMERA_DIR / f"{output_fname}.mp4"
    images_df = CameraImagesDataLoader().load_data()
    images_df = images_df.between_time(start_time, end_time)
    create_video(images_df, output_fpath, fps=fps)


if __name__ == "__main__":
    fire.Fire(create_video_from_images)
