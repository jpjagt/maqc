import pandas as pd
import time
import tkinter as tk

from mcs.constants import DATA_DIR

CAMERA_IMAGES_DIR = DATA_DIR / "camera" / "images"

IMAGES_DF = pd.read_csv(DATA_DIR / "camera" / "img_labels.csv")

# index: 0
# fpath:
# img_timestamp:
# ntrucks:
# ntrucks_in_right_half_of_image
# ntrucks_in_left_half_of_image


class Window(tk.Tk):
    interval = 2  # seconds
    image_freq = 60

    def __init__(self, label_name):
        super().__init__()

        self._label_name = label_name

        self._images_df = IMAGES_DF
        self._images_df = self._images_df[
            self._images_df[self._label_name].isna()
        ]

        self.title("senseable construction timelapse labeling")

        self.button = tk.Button(text="start playing")
        self.button.bind("", self._loop_through_images)
        self.button.pack()

        self.bind("<Key>", self._pressed_key)

    def _get_current_image_timestamp(self):
        start_date = pd.to_datetime("2022-11-15 12:00:00")
        current_img_timestamp = start_date + TimeDelta(
            seconds=self.img_index * self.image_freq
        )
        return current_img_timestamp

    def _display_image(self, img_timestamp):
        img_timestamp_str = img_timestamp.strftime("%Y-%m-%d-%H:%M:%S")
        fpath = CAMERA_IMAGES_DIR / f"{img_timestamp}.jpg"
        # TODO

    def _loop_through_images(self):
        for i, row in self._images_df.iterrows():
            time.sleep(self.interval)
            self._display_image(row.timestamp)
            self._current_index = i

    def _pressed_key(self, event):
        key = event.char
        print("key pressed: ", key)

        # TODO: play/pause on spacebar press

        key2number = {
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
        }

        if key not in key2number:
            print("invalid key", key)
            return

        self._images_df.loc[
            self._current_index, self._label_name
        ] = key2number[key]


# Start the event loop.
window = Window()
window.mainloop()
