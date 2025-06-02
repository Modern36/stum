from argparse import ArgumentParser
from pathlib import Path

from tqdm import tqdm

from stum.video_to_srt import pipeline


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
        pipeline(
            input,
            output_file,
            debug=args.debug,
        )


if __name__ == "__main__":
    cli()
