import pytest
from jiwer import cer

from video_to_srt import (
    filter_frame_groups,
    group_frames,
    intertitles_to_srt,
    merge_sequences,
    sequence_to_namedtuples,
    video_to_frames,
)


def two_decimal_cer(text_1, text2):
    return round(cer(text_1, text2), 2)


@pytest.fixture(scope="session")
def target_srt1(system_os):
    if system_os.startswith("macOS"):
        return """0
00:00:00,080 --> 00:00:00,560
(stmsx FILMINDUSTRIS VECKOREVY 1930

FÖRNÄMLIG VISIT.

Londons Lordmayor med sin
officiella uppvaktning landstiger
i Göteborg.

1
00:00:00,600 --> 00:00:00,720
Göteborg, 1 sept. 1930.
Londons Lordmayor
Sir William Waterlow

anländer till Göteborg med
”Suecia” och mottages
av landshövdingen."""
    elif system_os.startswith("Linux"):
        return """0
00:00:00,080 --> 00:00:00,560
é%svmsx FILMINDUSTRIS VECKOREVY 1930

FÖRNÄMLIG VISIT.

Londons Lordmayor med sin
officiella uppvaktning landstiger
i Göteborg.

1
00:00:00,600 --> 00:00:00,720
Göteborg, 1 sept. 1930.
Londons Lordmayor
Sir William Waterlow\n
anländer till Göteborg med
”Suecia” och mottages
av landshövdingen.

""".strip()


class TestVideoToFrames:
    def test_frame_extraction(self, video1, frames1):
        video_to_frames(video1, frames1)

        assert 250 == len(list(frames1.glob("*.png")))

    def test_group_by_similarity(self, frames1):

        group_frames(frames1)
        assert 5 == len([d for d in frames1.iterdir() if d.is_dir()])

    def test_filter_groups(self, frames1):
        group_dirs = (dir for dir in frames1.iterdir() if dir.is_dir())

        filter_frame_groups(group_dirs)
        sequences = [d for d in frames1.iterdir() if d.is_dir()]
        assert 3 == len(sequences)
        for grp_dir in sequences:
            assert 1 == len(list(grp_dir.glob("*.txt")))
            assert 1 <= len(list(grp_dir.glob("*.png")))

    def test_merge_sequences(self, frames1):
        merge_sequences(frames1)
        sequences = [d for d in frames1.iterdir() if d.is_dir()]
        assert 2 == len(sequences)
        for grp_dir in sequences:
            assert 1 == len(list(grp_dir.glob("*.txt")))
            assert 1 <= len(list(grp_dir.glob("*.png")))

    def test_first_sequence(self, frames1, target_cer):
        named_tuples = sequence_to_namedtuples(frames1)

        # There are two intertitles
        first, _ = list(named_tuples)

        assert (first.idx, first.start, first.end) == (0, 2, 14)

        assert (
            two_decimal_cer(
                first.text,
                (
                    "SF FILMINDUSTRIS VECKOREVY 1930\n\n"
                    "FÖRNÄMLIG VISIT.\n\n"
                    "Londons Lordmayor med sin\n"
                    "officiella uppvaktning landstiger\n"
                    "i Göteborg.\n"
                ),
            )
            <= target_cer
        )

    def test_second_sequence(self, frames1, target_cer):
        named_tuples = sequence_to_namedtuples(frames1)

        # There are two intertitles
        _, second = list(named_tuples)

        assert (second.idx, second.start, second.end) == (1, 15, 18)

        assert (
            two_decimal_cer(
                second.text,
                (
                    "Göteborg, 1 sept. 1930.\n"
                    "Londons Lordmayor\n"
                    "Sir William Waterlow\n\n"
                    "anländer till Göteborg med\n"
                    "”Suecia” och mottages\n"
                    "av landshövdingen.\n"
                ),
            )
            <= target_cer
        )

    def test_srt_maker(self, frames1, target_srt1):
        intertitles = list(sequence_to_namedtuples(frames1))
        assert len(intertitles) == 2
        srt = intertitles_to_srt(intertitles)

        assert srt == target_srt1
        # Using the exact output from the OCR for convenience.
