import pandas as pd
import time
import tkinter as tk

from PIL import ImageTk, Image
from mcs.constants import DATA_DIR

CAMERA_IMAGES_DIR = DATA_DIR / "camera" / "images"
CAMERA_DIR = DATA_DIR / "camera"
img_labels_fpath = CAMERA_DIR / "img_labels.csv"
img_labels_fpath_template = CAMERA_DIR / "img_labels_template.csv"
IMAGES_DF = pd.read_csv(img_labels_fpath_template, parse_dates=["timestamp"])

"""def create_csv(csvfile):
    with open("img_labels.csv", "w") as csvfile:
        filewriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        filewriter.writerow(
            [
                "Index",
                "img_timestamp",
                "ntrucks_right_half_img",
                "ntrucks_left_half_img"
            ] 
        )
"""


class Window(tk.Tk):
    interval = 2  # milliseconds

    def __init__(self, label_name):
        super().__init__()

        self.geometry("1250x800")

        self._label_name = label_name

        self._images_df = IMAGES_DF
        self._images_df = self._images_df[self._images_df[self._label_name].isna()]

        self.title("senseable construction timelapse labeling")
        self.button = tk.Button(text="Start playing", command=self._loop_through_images)

        self.button.pack()

        self.image_label = tk.Label()
        self.image_label.pack(fill="both", expand="yes")

        self.bind("<Key>", self._pressed_key)

    def _display_image(self, img_timestamp):
        img_timestamp_str = img_timestamp.strftime("%Y-%m-%d-%H%M%S")
        print("displaying image", img_timestamp_str)
        fpath = CAMERA_IMAGES_DIR / f"{img_timestamp_str}.jpg"
        # fpath = CAMERA_IMAGES_DIR / "2022-11-14-140009.jpg"
        img = ImageTk.PhotoImage(Image.open(fpath).resize((1200, 800)))
        self.image_label.configure(image=img)
        self.image_label.image = img
        # self.img.pack()
        # ?label_name here

    def _loop_through_images(self, i=0):
        if i >= len(self._images_df):
            return

        row = self._images_df.iloc[i]

        self._display_image(row.timestamp)
        self._current_index = i

        self.after(self.interval * 1000, self._loop_through_images, i + 1)

    def _pressed_key(self, event):
        key = event.char
        print("key pressed: ", key)

        key2number = {
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            # " ": TO DO play/pauze on spacebar press
        }

        if key not in key2number:
            print("invalid key", key)
            return

        self._images_df.loc[self._current_index, self._label_name] = key2number[key]

    def _save_images_df(self, fpath):
        self._images_df.to_csv(fpath)


# Start the event loop.
window = Window("ntrucks_right_half_img")
window.mainloop()
window._save_images_df(fpath=img_labels_fpath)
