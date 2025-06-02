from argparse import ArgumentParser
from pathlib import Path
from tempfile import mkdtemp

from tqdm import tqdm

from video_to_srt import (
    filter_frame_groups,
    group_frames,
    intertitles_to_srt,
    merge_sequences,
    sequence_to_namedtuples,
    video_to_frames,
)


def cli():
    parser = ArgumentParser(
        description="CLI for the intertitle-detector + OCR"
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input video (.mpg) or directory of videos (.mpg)",
    )
    parser.add_argument(
        "-s",
        "--skip",
        action="store_true",
        help="Skip files that already have an .srt file.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Activate Debug mode. Saves intertitle frames for each video.",
    )

    args = parser.parse_args()

    in_file = Path(args.input)

    if not in_file.exists():
        raise FileNotFoundError(f"{in_file} does not exist")
    if in_file.is_dir():
        inputs = [file for file in in_file.iterdir() if not file.is_dir()]
    else:
        inputs = [
            in_file,
        ]

    inputs = [(input, input.with_suffix(".srt")) for input in inputs]

    if args.skip:
        inputs = [input for input in inputs if not input[1].exists()]

    print(f"Found {len(inputs)} files to process")

    for input, output_file in tqdm(inputs, desc="Processing files"):
        pipeline(args.debug, input, output_file)


def pipeline(debug, input, output_file):
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


if __name__ == "__main__":
    cli()
