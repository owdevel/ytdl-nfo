import yaml
import ast
import datetime as dt
import xml.etree.ElementTree as ET
import pkg_resources
from collections import defaultdict
from xml.dom import minidom


class Nfo:
    def __init__(self, extractor, file_path):
        self.data = None
        self.top = None
        try:
            extractor_path = f"configs/{extractor}.yaml"
            with pkg_resources.resource_stream("ytdl_nfo", extractor_path) as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
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
            #!
            print("\\\\\\\\\\\\\\\\\\\data[top_name]")
            print(self.data[top_name])
            print(self.data)
        except ValueError as e:
            print(e)
            return False

        return True

    def __create_child(self, parent, subtree, raw_data):
        # Some .info.json files may not include an upload_date.
        if raw_data.get("upload_date") is None:
            date = dt.datetime.fromtimestamp(raw_data["epoch"])
            raw_data["upload_date"] = date.strftime("%Y%m%d")
        
        # Allow missing keys to give an empty string instead of
        # a KeyError when formatting values
        # https://stackoverflow.com/a/21754294
        format_dict = defaultdict(lambda: "")
        format_dict.update(raw_data)
        #!
        #print("////////////format_dict")
        #print(format_dict)

        # Check if current node is a list
        if isinstance(subtree, list):
            #!
            print("///////////////////IS LIST")
            print(subtree)

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
                children = ast.literal_eval(value.format_map(format_dict))
            else:
                children = [value.format_map(format_dict)]

            if 'convert' in attributes.keys():
                target_type = attributes['convert']
                input_f = attributes['input_f']
                output_f = attributes['output_f']

                for i in range(len(children)):
                    if target_type == 'date':
                        date = dt.datetime.strptime(children[i], input_f)
                        children[i] = date.strftime(output_f)

        # Value only
        else:
            if table:
                children = ast.literal_eval(
                    subtree[child_name].format_map(format_dict))
            else:
                children = [subtree[child_name].format_map(format_dict)]

        # Add the child node(s)
        child_name = child_name.rstrip('!')

        for value in children:
            sub_parent = parent
            sub_name = child_name
            sub_index = sub_name.find('>')
            while sub_index > -1:
                if not table:
                    raise ValueError(f'Error with key {sub_name}: > deliminator can only be used for lists')
                sub_parent = ET.SubElement(sub_parent, sub_name[:sub_index])
                sub_name = sub_name[sub_index + 1:]
                sub_index = sub_name.find('>')

            #!
            if value[0] == '[':
                value = ast.literal_eval(value)
                if isinstance(value, list):   
                    print("////////////////add tree")
                    print(value)
                for v in value:
                    child = ET.SubElement(sub_parent, sub_name)
                    child.text = v

                    # Add attributes
                    if 'attr' in attributes.keys():
                        for attribute, attr_value in attributes['attr'].items():
                            child.set(attribute, attr_value.format_map(format_dict))                    
            
            
            else:
                child = ET.SubElement(sub_parent, sub_name)
                child.text = value

                # Add attributes
                if 'attr' in attributes.keys():
                    for attribute, attr_value in attributes['attr'].items():
                        child.set(attribute, attr_value.format_map(format_dict))

    def print_nfo(self):
        xmlstr = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ")
        print(xmlstr)

    def write_nfo(self, filename):
        #!
        print("/////////////////write_nfo")
        print(self.top)
        xmlstr = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ")
        with open(filename, 'wt', encoding="utf-8") as f:
            f.write(xmlstr)

    def get_nfo(self):
        xmlstr = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ")
        return xmlstr


def get_config(extractor, file_path):
    return Nfo(extractor, file_path)
