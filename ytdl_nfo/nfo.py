import yaml
import ast
import datetime as dt
import xml.etree.ElementTree as ET
import importlib.resources
from collections import defaultdict
from xml.dom import minidom


class Nfo:
    def __init__(self, extractor, file_path):
        self.data = None
        self.top = None
        try:
            config_file = importlib.resources.files("ytdl_nfo").joinpath("configs", f"{extractor}.yaml")
            with config_file.open("rb") as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
        except (FileNotFoundError, ModuleNotFoundError):
            print(f"Error: No config available for extractor {extractor} in file {file_path}")
    
    def config_ok(self):
        return self.data is not None
    
    def generated_ok(self):
        return self.top is not None
    
    def generate(self, raw_data):

        # There should only be one top level node
        top_name = list(self.data.keys())[0]
        self.top = ET.Element(top_name)

        # Recursively generate the rest of the NFO
        try:
            self.__create_child(self.top, self.data[top_name], raw_data)
        except ValueError as e:
            print(e)
            return False

        return True

    def __create_child(self, parent, subtree, raw_data):
        # Some .info.json files may not include an upload_date.
        if raw_data.get("upload_date") is None and raw_data.get("epoch") is not None:
            date = dt.datetime.fromtimestamp(raw_data["epoch"])
            raw_data["upload_date"] = date.strftime("%Y%m%d")
        
        # Calculate rating and userrating if missing
        if raw_data.get("rating") is None:
            if raw_data.get("average_rating") is not None:
                try:
                    avg = float(raw_data["average_rating"])
                    raw_data["rating"] = round(avg * 2, 1) if avg <= 5 else round(avg, 1)
                except (ValueError, TypeError):
                    raw_data["rating"] = 8.0
            elif raw_data.get("like_count") is not None and raw_data.get("dislike_count") is not None:
                try:
                    likes = float(raw_data["like_count"])
                    dislikes = float(raw_data["dislike_count"])
                    total = likes + dislikes
                    if total > 0:
                        raw_data["rating"] = round((likes / total) * 10, 1)
                    else:
                        raw_data["rating"] = 8.0
                except (ValueError, TypeError, ZeroDivisionError):
                    raw_data["rating"] = 8.0
            elif raw_data.get("like_count") is not None and raw_data.get("view_count") is not None:
                try:
                    likes = float(raw_data["like_count"])
                    views = float(raw_data["view_count"])
                    if views > 0:
                        ratio = (likes / views) * 100
                        raw_data["rating"] = min(10.0, max(5.0, round(5.0 + ratio * 1.5, 1)))
                    else:
                        raw_data["rating"] = 8.0
                except (ValueError, TypeError, ZeroDivisionError):
                    raw_data["rating"] = 8.0
            else:
                raw_data["rating"] = 8.0

        if raw_data.get("userrating") is None:
            try:
                r_val = float(raw_data["rating"])
                raw_data["userrating"] = str(int(round(r_val)))
                raw_data["rating"] = f"{r_val:.1f}"
            except (ValueError, TypeError):
                raw_data["userrating"] = "8"
                raw_data["rating"] = "8.0"
        
        # Calculate audio_language if missing
        if raw_data.get("audio_language") is None:
            lang = raw_data.get("language")
            if not lang and isinstance(raw_data.get("subtitles"), dict) and len(raw_data["subtitles"]) > 0:
                lang = list(raw_data["subtitles"].keys())[0]
            
            if lang:
                l_code = str(lang).lower().split("-")[0].split("_")[0]
                ISO_MAP = {
                    "es": "spa", "spa": "spa",
                    "en": "eng", "eng": "eng",
                    "it": "ita", "ita": "ita",
                    "fr": "fra", "fre": "fra", "fra": "fra",
                    "de": "deu", "ger": "deu", "deu": "deu",
                    "pt": "por", "por": "por",
                    "ru": "rus", "rus": "rus",
                    "ja": "jpn", "jpn": "jpn",
                    "zh": "zho", "chi": "zho", "zho": "zho",
                    "nl": "nld", "dut": "nld", "nld": "nld",
                    "pl": "pol", "pol": "pol",
                    "sv": "swe", "swe": "swe",
                    "ko": "kor", "kor": "kor"
                }
                raw_data["audio_language"] = ISO_MAP.get(l_code, l_code)
            else:
                raw_data["audio_language"] = ""

        # Allow missing keys to give an empty string instead of
        # a KeyError when formatting values
        # https://stackoverflow.com/a/21754294
        format_dict = defaultdict(lambda: "")
        format_dict.update(raw_data)

        # Check if current node is a list
        if isinstance(subtree, list):

            # Process individual nodes
            for child in subtree:
                self.__create_child(parent, child, raw_data)
            return

        # Process data in child node
        child_name = list(subtree.keys())[0]

        table = child_name[-1] == '!'

        attributes = {}
        children = []

        # Check if attributes are present
        if isinstance(subtree[child_name], dict):
            attributes = subtree[child_name]
            value = subtree[child_name]['value']

            # Set children if value flag
            if table:
                val_str = value.format_map(format_dict)
                if val_str:
                    try:
                        children = ast.literal_eval(val_str)
                    except (ValueError, SyntaxError):
                        children = []
                else:
                    children = []
            else:
                children = [value.format_map(format_dict)]

            if 'convert' in attributes.keys():
                target_type = attributes['convert']
                input_f = attributes['input_f']
                output_f = attributes['output_f']

                for i in range(len(children)):
                    if target_type == 'date':
                        if children[i]:
                            try:
                                date = dt.datetime.strptime(children[i], input_f)
                                children[i] = date.strftime(output_f)
                            except ValueError:
                                children[i] = ""
                        else:
                            children[i] = ""

        # Value only
        else:
            if table:
                val_str = subtree[child_name].format_map(format_dict)
                if val_str:
                    try:
                        children = ast.literal_eval(val_str)
                    except (ValueError, SyntaxError):
                        children = []
                else:
                    children = []
            else:
                children = [subtree[child_name].format_map(format_dict)]

        # Add the child node(s)
        child_name = child_name.rstrip('!')

        for value in children:
            sub_parent = parent
            sub_name = child_name
            sub_index = sub_name.find('>')
            while sub_index > -1:
                p_name = sub_name[:sub_index]
                existing = sub_parent.find(p_name)
                if existing is not None and not table:
                    sub_parent = existing
                else:
                    sub_parent = ET.SubElement(sub_parent, p_name)
                sub_name = sub_name[sub_index + 1:]
                sub_index = sub_name.find('>')

            child = ET.SubElement(sub_parent, sub_name)
            child.text = str(value)

            # Add attributes
            if 'attr' in attributes.keys():
                for attribute, attr_value in attributes['attr'].items():
                    child.set(attribute, attr_value.format_map(format_dict))

            if 'parent_attr' in attributes.keys():
                for attribute, attr_value in attributes['parent_attr'].items():
                    sub_parent.set(attribute, attr_value.format_map(format_dict))

    def print_nfo(self):
        xmlbytes = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ", encoding="utf-8")
        print(xmlbytes.decode("utf-8"))

    def write_nfo(self, filename):
        xmlbytes = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ", encoding="utf-8")
        with open(filename, 'wb') as f:
            f.write(xmlbytes)

    def get_nfo(self):
        xmlbytes = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ", encoding="utf-8")
        return xmlbytes.decode("utf-8")


def get_config(extractor, file_path):
    return Nfo(extractor, file_path)
