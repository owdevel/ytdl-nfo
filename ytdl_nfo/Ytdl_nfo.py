import json
import os
import re
from .nfo import get_config


class Ytdl_nfo:
    def __init__(self, file_path, extractor=None, fanart_key=None):
        self.path = file_path
        self.dir = os.path.dirname(file_path)
        self.data = None
        self.filename = None
        self.input_ok = True
        self.extractor = extractor
        self.fanart_key = fanart_key
        
        # Read json data
        if self.input_ok:
            try:
                with open(self.path, "rt", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print(f'Error: Failed to parse JSON in file {self.path}')
                self.input_ok = False

        if self.extractor is None and self.data is not None:
            data_extractor = self.data.get('extractor')
            if isinstance(data_extractor, str):
                self.extractor = re.sub(r'[:?*/\\]', '_', data_extractor.lower())

        if self.path.endswith(".info.json"):
            self.filename = self.path[:-10]
        elif self.data is not None:
            data_filename = self.data.get('_filename')
            if isinstance(data_filename, str):
                self.filename = os.path.splitext(data_filename)[0]
        if self.filename is None:
            self.filename = self.path
        
        if isinstance(self.extractor, str):
            self.nfo = get_config(self.extractor, self.path)
        else:
            self.nfo = None
    
    def process(self):
        if not self.input_ok or self.nfo is None or not self.nfo.config_ok():
            return False
        generated = self.nfo.generate(self.data, fanart_key=self.fanart_key)
        if generated:
            self.write_nfo()
        return generated
    
    def get_nfo_path(self):
        return f'{self.filename}.nfo'
        
    def write_nfo(self):
        if self.nfo is not None and self.nfo.generated_ok():
            nfo_path = self.get_nfo_path()
            self.nfo.write_nfo(nfo_path)

    def print_data(self):
        print(json.dumps(self.data, indent=4, sort_keys=True))

    def get_nfo(self):
        if self.nfo is not None:
            return self.nfo.get_nfo()
        else:
            return None
