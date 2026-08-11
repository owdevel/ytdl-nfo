import argparse
import os
import re

from .Ytdl_nfo import Ytdl_nfo


def main():
    parser = argparse.ArgumentParser(
        description="ytdl_nfo, a youtube-dl utility to convert the output of  'youtube-dl --write-info-json' to an NFO for use with Kodi, Plex, Emby, Jellyfin, etc."
    )
    parser.add_argument(
        "--config",
        help="Show the path to the config directory",
        action="version",
        version=f"{get_config_path()}",
    )
    parser.add_argument(
        "--extractor-path",
        dest='config_path',
        type=str,
        help="Set the path to the config directory",
    )
    parser.add_argument("-e", "--extractor", help="Specify specific extractor")
    parser.add_argument(
        "-r",
        "--regex",
        type=str,
        default=r".json$",
        help="A regular expression used to search for JSON source files",
    )
    parser.add_argument(
        "-w", "--overwrite", action="store_true", help="Overwrite existing NFO files"
    )
    parser.add_argument(
        "input",
        metavar="JSON_FILE",
        type=str,
        help="JSON file to convert or directory to process recursively",
    )
    args = parser.parse_args()

    extractor_str = args.extractor if args.extractor is not None else "file specific"

    if os.path.isfile(args.input):
        print(f"Processing {args.input} with {extractor_str} extractor")
        file = Ytdl_nfo(args.input, args.extractor, config_path=args.config_path)
        file.process()
    else:
        for root, dirs, files in os.walk(args.input):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.endswith(".live_chat.json"):
                    continue
                if re.search(args.regex, file_name):
                    file = Ytdl_nfo(file_path, args.extractor)
                    if args.overwrite or not os.path.exists(file.get_nfo_path()):
                        print(f"Processing {file_path} with {extractor_str} extractor")
                        file.process()


def get_config_path():
    return os.path.join(os.path.dirname(__file__), "configs")


__all__ = ["main", "Ytdl_nfo", "nfo"]
