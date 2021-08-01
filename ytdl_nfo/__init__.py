import argparse
import os
import re
from .Ytdl_nfo import Ytdl_nfo

def main():

    parser = argparse.ArgumentParser(description='ytdl_nfo, a youtube-dl helper to convert the output of  \'youtube-dl --write-info-json\' to an NFO for use in kodi/plex/etc')
    parser.add_argument('input', metavar='JSON_FILE', type=str, help='Json file to convert or folder to convert in')
    parser.add_argument('-e', '--extractor', help='Specify specific extractor')
    parser.add_argument('-w', '--overwrite', action="store_true", help='Overwrite existing NFO files')
    parser.add_argument('--regex', type=str, help='Specify regex search string to match files', default=r".json$")
    parser.add_argument('--config', help='Prints the path to the config directory', action='version', version=f'{get_config_path()}')
    args = parser.parse_args()

    extractor_str = args.extractor if args.extractor != None else "file specific"

    if os.path.isfile(args.input):
        print(f'Processing {args.input} with {extractor_str} extractor')
        file = Ytdl_nfo(args.input, args.extractor)
        file.process()
        file.write_nfo()
    else:
        print(f"Processing Folder {args.input}")
        for filename in os.listdir(args.input):
            if re.search(args.regex, filename):
                print(f'Processing {filename} with {extractor_str} extractor')
                file = Ytdl_nfo(os.path.join(args.input,  filename), args.extractor)
                file.process()
                file.write_nfo()

def get_config_path():
    return os.path.join(os.path.dirname(__file__), 'configs')


__all__ = ['main', 'Ytdl_nfo', 'nfo']