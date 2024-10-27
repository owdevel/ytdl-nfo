"""Parses command-line interface (CLI) arguments and invoke the NFO generator for each specified or matching file."""

from __future__ import annotations

# Standard Libraries
import logging
import re
from argparse import ArgumentParser
from argparse import Namespace
from pathlib import Path

from .nfo_generator import NFOGenerator

# ---------------------------------- Logging --------------------------------- #
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-7s] - %(message)s"))

logging.basicConfig(level=logging.NOTSET, handlers=[console_handler])
logger: logging.Logger = logging.getLogger(__name__)


def parse_arguments() -> Namespace:
    """Parse command-line interface (CLI) arguments.

    Returns:
        Namespace: An argparse Namespace object containing the values of command-line arguments
    """
    parser: ArgumentParser = ArgumentParser(
        prog="ytdl-nfo",
        description="A utility for converting metadata, saved using the youtube-dl '--write-info-json' flag, to an "
        "NFO file compatible with Kodi, Plex, Emby, Jellyfin, etc.",
    )
    parser.add_argument(
        "--show-config-dir",
        action="version",
        version=str(Path(__file__) / "configs"),
        help="Show the path to the config directory",
    )
    parser.add_argument(
        "-e",
        "--extractor",
        help="The extractor config to use; allows overriding the extractor specified in the JSON file",
    )
    parser.add_argument(
        "-r",
        "--regex",
        type=str,
        default=r".+\.info\.json$",
        help="A regular expression used to search for JSON info files",
    )
    parser.add_argument("-w", "--overwrite", action="store_true", help="Overwrite existing NFO files")
    parser.add_argument(
        "input",
        metavar="JSON_FILE_PATH",
        nargs="+",
        type=Path,
        help="One or more JSON files or directories to process; directories will be processed recursively",
    )
    return parser.parse_args()


def main() -> None:
    """Parse CLI arguments and invoke the NFO generator for each specified or matching file."""
    args: Namespace = parse_arguments()

    for path in args.input:
        if path.is_file():
            NFOGenerator(json_file=path, extractor_name=args.extractor, overwrite=args.overwrite)
        elif path.is_dir():
            for file in path.rglob("*"):
                if file.name.endswith(".live_chat.json"):
                    continue

                if re.match(args.regex, file.name):
                    NFOGenerator(json_file=file, extractor_name=args.extractor, overwrite=args.overwrite)
        else:
            logger.error("Path Not Found: %s", str(path))


__all__: list[str] = ["main", "NFOGenerator"]
