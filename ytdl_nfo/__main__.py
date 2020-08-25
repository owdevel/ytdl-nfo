#!/usr/bin/env python

import argparse
from Ytdl_nfo import Ytdl_nfo

def main():

    parser = argparse.ArgumentParser(description='ytdl_nfo')
    parser.add_argument('input', metavar='JSON_FILE', type=str, help='Json file path')
    args = parser.parse_args()

    file = Ytdl_nfo(args.input)
    file.process()


if __name__=='__main__':
    main()
