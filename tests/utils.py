from pathlib import Path

import cv2


def image_paths(image_dir):
    return image_dir.glob("**/*.jpeg")


test_data_root = Path(__file__).parent / "data"


intertitles = test_data_root / "intertitles"


def get_text_intertitle_pairs():
    for image in image_paths(intertitles):
        with open(image.with_suffix(".txt"), "r", encoding="utf-8") as f:
            yield image.name, (f.read(), cv2.imread(str(image)))


other_frames = test_data_root / "other_frames"


def get_text_badsintertitles_pairs():
    for image in image_paths(other_frames / "error_titles"):
        with open(image.with_suffix(".txt"), "r", encoding="utf-8") as f:
            yield image.name, (f.read(), cv2.imread(str(image)))
