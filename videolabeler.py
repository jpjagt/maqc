import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk

from PIL import ImageTk, Image
from mcs.constants import (
    CAMERA_IMAGES_DIR,
    IMG_LABELS_CSV_FPATH,
    CAMERA_LABEL_TASKS,
)

DEFAULT = object()


def update_text(text_obj, text):
    text_obj.config(text=text)
    text_obj.text = text


class Window(tk.Tk):
    display_interval = 1.4  # seconds

    def __init__(self, images_df, task_name=None):
        self._images_df = images_df
        self._current_index = 0

        if task_name is not None and task_name not in self._images_df:
            raise ValueError(
                "task name is not a column in images_df. "
                "maybe you mistyped the task, or maybe the csv "
                "needs to be regenerated?"
            )

        self._task_name = (
            self._prompt_task() if task_name is None else task_name
        )

        self._images_df = self._images_df[
            self._images_df[self._task_name].isna()
        ]

        super().__init__()

        self.geometry("1250x800")

        self._init_tk()

    def _init_tk(self):
        self.title("senseable construction timelapse labeling")

        # self.button = tk.Button(
        #     text="Start playing", command=self._loop_through_images
        # )
        # self.button.pack()

        self._header = tk.Label(
            font=("Arial", 18), text=f"labeling task: {self._task_name}"
        )

        self._current_img_text = tk.Label(font=("Arial", 13))
        self._current_label_text = tk.Label(font=("Arial", 13))
        self._control_tip_text = tk.Label(font=("Arial", 11))

        self.image_label = tk.Label()

        self._header.pack()
        self._current_img_text.pack()
        self._current_label_text.pack()
        self._control_tip_text.pack()
        self.image_label.pack(fill="both", expand="yes")

        self.bind("<Key>", self._pressed_key)

        self._is_playing = False
        self._active_label = None
        self._update(active_label=None, is_playing=False)
        self._display_next_image(initial_display=True)

    def _update(self, active_label=DEFAULT, is_playing=DEFAULT):
        if active_label is not DEFAULT:
            print("updating active_label to", active_label)
            self._active_label = active_label
            update_text(
                self._current_label_text,
                f"current label: {self._active_label}",
            )

        if is_playing is not DEFAULT:
            print("updating is_playing to", is_playing)
            started_playing = not self._is_playing and is_playing
            self._is_playing = is_playing
            control_tip_text = (
                "hit a key (0-5) to start playing"
                if not is_playing
                else "hit spacebar to pause"
            )
            update_text(self._control_tip_text, control_tip_text)

            if started_playing:
                self._display_next_image()

    def _display_image(self, img_info):
        update_text(self._current_img_text, img_info.timestamp)

        fpath = CAMERA_IMAGES_DIR / img_info.fname
        # fpath = CAMERA_IMAGES_DIR / "2022-11-14-140009.jpg"
        img = ImageTk.PhotoImage(Image.open(fpath).resize((1200, 800)))
        self.image_label.configure(image=img)
        self.image_label.image = img
        # self.img.pack()
        # ?label_name here

    def _display_next_image(self, initial_display=False):
        if not self._is_playing and not initial_display:
            return

        i = self._current_index + 1

        if i >= len(self._images_df):
            return

        row = self._images_df.iloc[i]

        self._display_image(row)
        self._current_index = i

        self._set_label_in_df()

        if not initial_display:
            self.after(
                int(self.display_interval * 1000), self._display_next_image
            )

    def _pressed_key(self, event):
        key = event.char
        print("key pressed: ", key)

        key2action = {
            "0": lambda: self._update(is_playing=True, active_label=0),
            "1": lambda: self._update(is_playing=True, active_label=1),
            "2": lambda: self._update(is_playing=True, active_label=2),
            "3": lambda: self._update(is_playing=True, active_label=3),
            "4": lambda: self._update(is_playing=True, active_label=4),
            "5": lambda: self._update(is_playing=True, active_label=5),
            " ": lambda: self._update(is_playing=False),
        }

        if key not in key2action:
            print("invalid key", key)
            return

        action = key2action[key]
        action()

    def _set_label_in_df(self):
        index = self._images_df.index[self._current_index]
        self._images_df.loc[index, self._task_name] = self._active_label

    def _prompt_task(self):
        print("available tasks:")
        for task in CAMERA_LABEL_TASKS:
            if task in self._images_df:
                pct = round((1 - self._images_df[task].isna().mean()) * 100, 0)
                print(task, f"({pct}% completed)")
        while True:
            user_task = input("enter name of task: ")
            if user_task in self._images_df:
                return user_task

    def _save_images_df(self, fpath):
        self._images_df.to_csv(fpath, index=False)


if __name__ == "__main__":
    images_df = pd.read_csv(
        IMG_LABELS_CSV_FPATH, parse_dates=["timestamp"], index_col=False
    )
    window = Window(images_df)
    window.mainloop()
    # when it's over, save the csv
    window._save_images_df(fpath=IMG_LABELS_CSV_FPATH)
