import os
import json
from .nfo import get_config


class Ytdl_nfo:
    def __init__(self, file_path, extractor=None):
        self.path = file_path
        self.dir = os.path.dirname(file_path)
        self.data = None
        self.filename = None
        self.input_ok = True
        
        # Read json data
        if self.input_ok:
            try:
                with open(self.path, "rt", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print(f'Error: Failed to parse JSON in file {self.path}')
                self.input_ok = False

        self.extractor = extractor
        if extractor is None and self.data is not None:
            data_extractor = self.data.get('extractor')
            if isinstance(data_extractor, str):
                self.extractor = data_extractor.lower()

        if file_path.endswith(".info.json"):
            self.filename = file_path[:-10]
        elif self.data is not None:
            data_filename = self.data.get('_filename')
            if isinstance(data_filename, str):
                self.filename = os.path.splitext(data_filename)[0]
        if self.filename is None:
            self.filename = file_path
        
        if isinstance(self.extractor, str):
            self.nfo = get_config(self.extractor)
        else:
            self.nfo = None
    
    def process(self):
        if not self.input_ok or self.nfo is None or not self.nfo.config_ok():
            return False
        self.nfo.generate(self.data)
        self.write_nfo()
        return True

    def write_nfo(self):
        if self.nfo is not None and self.nfo.generated_ok():
            self.nfo.write_nfo(f'{self.filename}.nfo')

    def print_data(self):
        print(json.dumps(self.data, indent=4, sort_keys=True))

    def get_nfo(self):
        if self.nfo is not None:
            return self.nfo.get_nfo()
        else:
            return None
