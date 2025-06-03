import zipfile
from collections import namedtuple
from pathlib import Path
from tempfile import mkdtemp
from typing import Iterable

import cv2
import numpy as np
from ffmpeg import FFmpeg
from jiwer import cer
from tqdm import tqdm

from stum.contours import contour_filter
from stum.tesseract import extract_text

Intertitle = namedtuple("Intertitle", ["idx", "start", "end", "text"])
MSE_THRESHOLD = 10_000


def video_to_frames(video_path, frames_dir):
    frames_path = frames_dir / "frame_%07d.png"
    FFmpeg().input(video_path.absolute()).output(frames_path).execute()


def keep_intertitles(frames_dir):
    for frame in frames_dir.glob("*.png"):
        image = cv2.imread(str(frame))

        if not contour_filter(image):
            frame.unlink()
            continue

        text = extract_text(image)
        if text == "":
            frame.unlink()
            continue

        with open(frame.with_suffix(".txt"), "w") as f:
            f.write(text)


def mse(im1, im2):
    err = np.sum((im1.astype("float") - im2.astype("float")) ** 2)
    err /= float(im1.shape[0] * im1.shape[1])
    return err


def group_frames(frames_dir):
    frames = sorted(frames_dir.glob("*.png"))

    if len(frames) == 0:
        raise FileNotFoundError(f"No frames found in {frames_dir=}")

    grp_cnt = 0
    for idx, frame in enumerate(frames):
        if idx == 0:
            im1 = cv2.imread(str(frame))
            grp_dir = frames_dir / "group_000"
            grp_dir.mkdir()

            frame.rename(grp_dir / frame.name)
            continue

        im2 = cv2.imread(str(frame))
        if detect_scene_change(im1, im2):
            grp_cnt += 1
            grp_dir = frames_dir / f"group_{grp_cnt:03}"
            grp_dir.mkdir()

        frame.rename(grp_dir / frame.name)

        im1 = im2


def detect_scene_change(im1, im2):
    score = mse(im1, im2)
    return score > MSE_THRESHOLD


def filter_frame_groups(group_dirs: Iterable[Path], debug=False):
    def clear_dir(dir_path, debug=False):
        if debug:
            zip_file = dir_path.with_suffix(".zip")
            with zipfile.ZipFile(zip_file, "w") as zf:
                for file in dir_path.iterdir():
                    zf.write(file, arcname=file.name)

        for file in dir_path.iterdir():
            file.unlink()
        dir_path.rmdir()

    for group_dir in group_dirs:
        frames = sorted(group_dir.glob("*.png"))
        middle = int(len(frames) / 2)
        middle_frame = frames[middle]

        image = cv2.imread(str(middle_frame))

        if not contour_filter(image):
            clear_dir(group_dir)
            continue

        text = extract_text(image)
        if text == "":
            clear_dir(group_dir, debug)
            continue

        with open(group_dir / "intertitle.txt", "x") as f:
            f.write(text)


def merge_sequences(frames_dir):
    sequences = sorted([dir for dir in frames_dir.iterdir() if dir.is_dir()])

    for i, seq in enumerate(sequences):
        if i == 0:
            title1 = open(seq / "intertitle.txt").read().strip()
            dir1 = seq
            continue

        title = open(seq / "intertitle.txt").read().strip()
        intertitle_diff = cer(title1, title)

        if intertitle_diff > 0.5:
            continue

        _, longer = sorted([title1, title], key=len)

        open(seq / "intertitle.txt", "w").write(longer)
        for frame in dir1.iterdir():
            if frame.suffix == ".txt":
                frame.unlink()
            elif not frame.suffix == ".png":
                raise Exception("Unexpected file in sequence")
            else:
                frame.rename(seq / frame.name)
        dir1.rmdir()


def sequence_to_namedtuples(frames_dir):
    for idx, grp in enumerate(
        sorted([dir for dir in frames_dir.iterdir() if dir.is_dir()])
    ):
        group_frames = sorted(
            [int(frame.name[6:-4]) for frame in grp.glob("*.png")]
        )
        if len(group_frames) == 1:
            start = end = group_frames[0]
        else:
            start, *_, end = sorted(group_frames)

        text = open(grp / "intertitle.txt").read().strip()

        yield Intertitle(idx=idx, start=start, end=end, text=text)


def frame_nr_to_timestamp(frame_nr, fps=25):
    secs = frame_nr / fps
    h = secs // 3600
    m = (secs // 60) % 60
    s = (secs % 60) // 1
    ms = secs % 1 * 1000
    str_h = str(int(h)).zfill(2)
    str_m = str(int(m)).zfill(2)
    str_s = str(int(s)).zfill(2)
    str_ms = str(int(round(ms))).zfill(3)
    return f"{str_h}:{str_m}:{str_s},{str_ms}"


def intertitle_to_srt(intertitle: Intertitle):
    result = f"{intertitle.idx}\n"
    result += frame_nr_to_timestamp(intertitle.start, fps=25)
    result += " --> "
    result += frame_nr_to_timestamp(intertitle.end, fps=25)
    result += "\n"
    result += f"{intertitle.text.replace('\n', '\t').strip()}"
    return result


def intertitles_to_srt(intertitles: list[Intertitle]):
    intertitles = sorted(intertitles, key=lambda it: it.idx)

    print([it.idx for it in intertitles])

    return "\n\n".join(
        [intertitle_to_srt(intertitle) for intertitle in intertitles]
    )


def pipeline(input: Path, output_file: Path, debug: bool = False):
    """Extracts intertitletexts from a video file and writes them to an SRT.

    Parameters:
    - input (Path): The path to the input video file.
    - output_file (Path): The path where the generated SRT subtitle file will
      be saved.
    - debug (bool, optional): If True, the intermed`iate processing files are
      not deleted and can be used for debugging. Default is False.

    Process:
    1. Extract frames from the input video.
    2. Group frames into sequences of similar frames using Mean Squared Error
       (MSE).
    3. Filter frame groups to keep only those with valid intertitles based on
       contour detection and text extraction.
    4. Merge sequences that have similar intertitle texts.
    5. Convert the remaining intertitles into namedtuples, representing each
       intertitle by its index, start frame number, end frame number, and
       extracted text.
    6. Generate SRT subtitle format from the namedtuple list of intertitles.
    7. Save the generated SRT content to the specified output file.

    The resulting SRT file will have timestamps derived from frame numbers
    using a fixed frames per second (FPS) rate.
    """

    if debug:
        processing_dir = input.with_suffix("")
        processing_dir.mkdir()
    else:
        processing_dir = Path(mkdtemp())
    video_to_frames(input, processing_dir)
    group_frames(processing_dir)
    group_dirs = tqdm(
        [dir for dir in processing_dir.iterdir() if dir.is_dir()],
        desc="Processing groups",
    )

    filter_frame_groups(group_dirs, debug=debug)
    merge_sequences(processing_dir)
    intertitles = sequence_to_namedtuples(processing_dir)
    srt = intertitles_to_srt(intertitles)

    output_file.open("w", encoding="utf-8").write(srt)
