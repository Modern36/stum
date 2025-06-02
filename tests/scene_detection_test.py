from pathlib import Path

import cv2
import pytest

from stum.video_to_srt import detect_scene_change

test_data_root = Path(__file__).parent / "data"


def get_frame_pairs(pair_dirs):
    for subdir in pair_dirs.iterdir():
        if not subdir.is_dir():
            continue
        images = list(subdir.glob("*.jpeg"))

        assert len(images) == 2
        yield subdir.name, tuple(
            cv2.imread(str(img)) for img in sorted(images)
        )


def changed_scenes_frame_pairs():
    pair_dirs = test_data_root / "scene_detection" / "changed_scene"
    return list(get_frame_pairs(pair_dirs))


def same_scenes_frame_pairs():
    pair_dirs = test_data_root / "scene_detection" / "same_scene"
    return list(get_frame_pairs(pair_dirs))


same_ids, same_data = zip(*same_scenes_frame_pairs())
changed_ids, changed_data = zip(*changed_scenes_frame_pairs())


@pytest.mark.parametrize("same_scenes_frame_pairs", same_data, ids=same_ids)
def test_same_scene(same_scenes_frame_pairs):
    frame1, frame2 = same_scenes_frame_pairs
    assert not detect_scene_change(frame1, frame2)


@pytest.mark.parametrize(
    "same_scenes_frame_pairs", changed_data, ids=changed_ids
)
def test_scene_change(same_scenes_frame_pairs):
    frame1, frame2 = same_scenes_frame_pairs
    assert detect_scene_change(frame1, frame2)
