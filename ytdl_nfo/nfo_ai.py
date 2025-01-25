import yaml
import ast
import datetime as dt
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
import string

class Nfo:
    """
    Class to generate and manage NFO (XML) files from raw data using YAML configurations.
    """
    def __init__(self, extractor, file_path):
        self.data = None  # Loaded from YAML configuration file.
        self.top = None  # Root XML element.
        
        try:
            extractor_path = f"configs/{extractor}.yaml"
            with pkg_resources.resource_stream("ytdl_nfo", extractor_path) as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            print(f"Error: No config available for extractor {extractor} in file {file_path}")

    def config_ok(self):
        """Check if the configuration is successfully loaded."""
        return self.data is not None

    def generated_ok(self):
        """Check if the NFO XML has been generated."""
        return self.top is not None

    def generate(self, raw_data):
        """
        Generate the NFO (XML) structure from raw data.
        """
        try:
            top_name = list(self.data.keys())[0]
            self.top = ET.Element(top_name)

            if "upload_date" not in raw_data:
                raw_data["upload_date"] = dt.datetime.fromtimestamp(raw_data["epoch"]).strftime("%Y%m%d")

            format_dict = defaultdict(str, raw_data)
            self.__create_child(self.top, self.data[top_name], format_dict)
            return True
        except Exception as e:
            print(f"Error during generation: {e}")
            return False

    def __create_child(self, parent, subtree, format_dict):
        """
        Recursively create child XML nodes.
        """
        if isinstance(subtree, list):
            for child in subtree:
                self.__create_child(parent, child, format_dict)
            return

        child_name, child_data = next(iter(subtree.items()))
        is_table = child_name.endswith("!")
        attributes = {}
        children = []

        if isinstance(child_data, dict):
            attributes = child_data
            children = self.__interpret_value(format_dict, child_data.get("value", ""))

            if "convert" in attributes:
                children = self.__apply_conversion(children, attributes)
        else:
            children = self.__interpret_value(format_dict, child_data)

        self.__add_child_nodes(parent, child_name.rstrip("!"), attributes, children, format_dict)

    def __interpret_value(self, format_dict, value):
        """
        Interpret and format values based on format_dict.
        """
        formatter = string.Formatter()
        for _, field_name, _, _ in formatter.parse(value):
            if field_name:
                return format_dict[field_name]
        return ""

    def __apply_conversion(self, value, attributes):
        """
        Apply type conversion if specified in attributes.
        """
        target_type = attributes.get("convert")
        input_format = attributes.get("input_f")
        output_format = attributes.get("output_f")

        if target_type == "date":
            date = dt.datetime.strptime(value, input_format)
            return date.strftime(output_format)

        return value

    def __add_child_nodes(self, parent, child_name, attributes, children, format_dict):
        """
        Add XML child nodes to the parent.
        """
        sub_parent = parent
        for part in child_name.split(">")[:-1]:
            sub_parent = ET.SubElement(sub_parent, part)

        final_name = child_name.split(">")[-1]

        if isinstance(children, list):
            for child in children:
                self.__create_element(sub_parent, final_name, attributes, child, format_dict)
        else:
            self.__create_element(sub_parent, final_name, attributes, children, format_dict)

    def __create_element(self, parent, name, attributes, text, format_dict):
        """
        Create and append an XML element.
        """
        element = ET.SubElement(parent, name)
        element.text = text

        for attr, attr_value in attributes.get("attr", {}).items():
            element.set(attr, attr_value.format_map(format_dict))

    def write_nfo(self, filename):
        """
        Write the NFO XML to a file.
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.get_nfo())

    def get_nfo(self):
        """
        Return the NFO XML as a pretty-printed string.
        """
        return minidom.parseString(ET.tostring(self.top, "utf-8")).toprettyxml(indent="    ")

    def print_nfo(self):
        """
        Print the NFO XML to the console.
        """
        print(self.get_nfo())


def get_config(extractor, file_path):
    """
    Factory function to initialize Nfo object.
    """
    return Nfo(extractor, file_path)
