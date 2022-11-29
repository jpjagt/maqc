from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


def create_video(images_df, output_fpath, fps=24):
    print("[create_video] getting fpaths...")
    fpaths = list(images_df.sort_index().fpath.map(str))
    print("[create_video] initing ImageSequenceClip...")
    clip = ImageSequenceClip(fpaths, fps=fps, with_mask=False)
    print("[create_video] writing video file...")
    clip.write_videofile(str(output_fpath))
    print("[create_video] finished.")
