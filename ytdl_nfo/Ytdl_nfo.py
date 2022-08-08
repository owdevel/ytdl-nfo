import os
import json
from .nfo import get_config


class Ytdl_nfo:
    def __init__(self, file_path, extractor=None):
        self.path = file_path
        self.dir = os.path.dirname(file_path)

        # Read json data
        with open(self.path, "rt", encoding="utf-8") as f:
            self.data = json.load(f)

        self.extractor = extractor
        if extractor is None:
            self.extractor = self.data['extractor'].lower()

        if file_path.endswith(".info.json"):
            self.filename = file_path[:-10]
        else:
            self.filename = os.path.splitext(self.data['_filename'])[0]

        self.nfo = get_config(self.extractor)

    def process(self):
        self.nfo.generate(self.data)

    def write_nfo(self):
        self.nfo.write_nfo(f'{self.filename}.nfo')

    def print_data(self):
        print(json.dumps(self.data, indent=4, sort_keys=True))

    def get_nfo(self):
        return self.nfo.get_nfo()
