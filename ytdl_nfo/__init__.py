import argparse
import os
from .Ytdl_nfo import Ytdl_nfo

def main():

    parser = argparse.ArgumentParser(description='ytdl_nfo, a youtube-dl helper to convert the output of  \'youtube-dl --write-info-json\' to an NFO for use in kodi/plex/etc')
    parser.add_argument('input', metavar='JSON_FILE', type=str, help='Json file to convert or folder to convert in')
    parser.add_argument('--extractor', help='Specify specific extractor')
    args = parser.parse_args()

    if os.path.isfile(args.input):
        file = Ytdl_nfo(args.input)
        file.process()
    else:
        for filename in os.listdir(args.input):
            if filename.endswith('.json'):
                print(f'Processing {filename}')
                file = Ytdl_nfo(os.path.join(args.input,  filename), args.extractor)
                file.process()


__all__ = ['main', 'Ytdl_nfo', 'nfo']