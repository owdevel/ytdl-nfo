import argparse
import os
from .Ytdl_nfo import Ytdl_nfo

def main():

    parser = argparse.ArgumentParser(description='ytdl_nfo, a youtube-dl helper to convert the output of  \'youtube-dl --write-info-json\' to an NFO for use in kodi/plex/etc')
    parser.add_argument('input', metavar='JSON_FILE', type=str, help='Json file to convert or folder to convert in')
    parser.add_argument('-e', '--extractor', help='Specify specific extractor')
    parser.add_argument('-w', '--overwrite', action="store_true", help='Overwrite existing NFO files')
    parser.add_argument('--config', help='Prints the path to the config directory', action='version', version=f'{get_config_path()}')
    args = parser.parse_args()

    if os.path.isfile(args.input):
        print(f'Processing {args.input} with extractor {args.extractor}')
        file = Ytdl_nfo(args.input, args.extractor)
        file.process()
    else:
        for root, dirs, files in os.walk(args.input):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.endswith('.info.json'):
                    if args.overwrite or not os.path.exists(file_path[:-10] + ".nfo"):
                        print(f'Processing {file_path} with extractor {args.extractor}')
                        file = Ytdl_nfo(file_path, args.extractor)
                        file.process()

def get_config_path():
    return os.path.join(os.path.dirname(__file__), 'configs')


__all__ = ['main', 'Ytdl_nfo', 'nfo']