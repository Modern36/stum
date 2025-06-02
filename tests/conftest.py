import platform
from pathlib import Path
from tempfile import mkdtemp

import cv2
import pytest

from tests.utils import other_frames

from .utils import (
    get_text_badsintertitles_pairs,
    get_text_intertitle_pairs,
    image_paths,
    intertitles,
    test_data_root,
)


def get_images(image_dir):
    for image in image_paths(image_dir):
        yield cv2.imread(str(image))


@pytest.fixture(scope="function")
def white_intertitles():
    intetitle_dir = intertitles / "white_background"
    return get_images(intetitle_dir)


@pytest.fixture(scope="function")
def black_intertitles():
    black_intertitles_dir = intertitles / "black_background"
    return get_images(black_intertitles_dir)


@pytest.fixture(scope="function")
def not_intertitles():
    not_intertitle_dir = other_frames / "not_intertitles"
    return get_images(not_intertitle_dir)


@pytest.fixture(scope="function")
def error_titles():
    return get_text_badsintertitles_pairs()


@pytest.fixture(scope="function")
def texts_and_intertitle():
    return get_text_intertitle_pairs()


@pytest.fixture(scope="function")
def contour_false_positive():
    false_positive_dir = other_frames / "contour_false_positives"
    return get_images(false_positive_dir)


@pytest.fixture(scope="function")
def black_frames():
    black_frames_dir = other_frames / "black_frames"
    return get_images(black_frames_dir)


@pytest.fixture(scope="function")
def video1():
    return test_data_root / "video" / "SF681.1.10s.mpg"


@pytest.fixture(scope="class")
def frames1():
    return Path(mkdtemp())


@pytest.fixture(scope="session")
def system_os():
    """Get the current operating system"""
    return platform.platform()


@pytest.fixture(scope="session")
def target_cer(system_os):
    """Load target CER based on the OS"""
    if system_os.startswith("macOS"):
        return 0.07
    elif system_os.startswith("Linux"):
        return 0.06
