import os
import json
import nfo

class Ytdl_nfo:
    def __init__(self, file_path, extractor=None):
        self.path = file_path
        self.dir = os.path.dirname(file_path)

        # Read json data
        with open(self.path, 'r') as f:
            self.data = json.load(f)

        self.extractor = extractor
        if extractor is None:
            self.extractor = self.data['extractor'].lower()

        self.filename = os.path.splitext(self.data['_filename'])[0]
        self.nfo = nfo.get_config(self.extractor)

    def process(self):
        self.nfo.generate(self.data)
        #self.nfo.print_nfo()
        self.nfo.write_nfo(os.path.join(self.dir, f'{self.filename}.nfo'))

    def print_data(self):
        print(json.dumps(self.data, indent=4, sort_keys=True))


