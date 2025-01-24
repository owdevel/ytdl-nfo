import yaml
import ast
import datetime as dt
import xml.etree.ElementTree as ET
import pkg_resources
from collections import defaultdict
from xml.dom import minidom
import string

class Nfo:
    def __init__(self, extractor, file_path):
        self.data = None    #initiate from yaml file.
        self.top = None     #top level node
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

        # Some .info.json files may not include an upload_date.
        if raw_data.get("upload_date") is None:
            date = dt.datetime.fromtimestamp(raw_data["epoch"])
            raw_data["upload_date"] = date.strftime("%Y%m%d")
        
        # Allow missing keys to give an empty string instead of
        # a KeyError when formatting values
        # https://stackoverflow.com/a/21754294
        format_dict = defaultdict(lambda: "")
        format_dict.update(raw_data)

        # Recursively generate the rest of the NFO
        try:
            self.__create_child(self.top, self.data[top_name], format_dict)
        except ValueError as e:
            print(e)
            return False

        return True

    def __create_child(self, parent, subtree, format_dict):
        # Check if current node is a list
        if isinstance(subtree, list):

            # Process individual nodes
            for child in subtree:
                self.__create_child(parent, child, format_dict)
            return

        # Process data in child node
        child_name = list(subtree.keys())[0]
        table = child_name[-1] == '!'

        attributes = {}
        children = []

        # Check if attributes are present
        if isinstance(subtree[child_name], dict):
            attributes = subtree[child_name]
            children = self.interpret_child(format_dict,subtree[child_name]['value'])
 
            if 'convert' in attributes.keys():
                target_type = attributes['convert']
                input_f = attributes['input_f']
                output_f = attributes['output_f']

                if target_type == 'date':
                    date = dt.datetime.strptime(children, input_f)
                    children = date.strftime(output_f)
        # Value only
        else:
            children = self.interpret_child(format_dict, subtree[child_name])
        
        # Add the child node(s)
        child_name = child_name.rstrip('!')
        sub_parent = parent
        child_name_list = child_name.split('>') 
        sub_name = child_name_list[-1]
        for cnl in child_name_list[:-1]:
            sub_parent = ET.SubElement(sub_parent, cnl)
        
        # If type of 'value' is list, repeat to create SubElement
        if isinstance(children, list):
            for c in children:
                self.creat_ET_node(sub_parent, sub_name, attributes, format_dict, c)
        else:
            self.creat_ET_node(sub_parent, sub_name, attributes, format_dict, children)
    
    def interpret_child(self, format_dict, value):
        children=[]
        formatter = string.Formatter()
        for literal_text, field_name, format_spec, conversion in formatter.parse(value):
                # if there's a field, use it as a key
                if field_name is not None:

                    # When empty field_names are given.
                    if field_name == '':
                        raise ValueError('')

                    elif field_name.isdigit():
                        raise ValueError('')

                    else:
                        children = format_dict[field_name]
        return children
    
    def creat_ET_node(self, sub_parent, sub_name, attributes, format_dict, text):
        child = ET.SubElement(sub_parent, sub_name)
        child.text = text
        # Add attributes
        if 'attr' in attributes.keys():
            for attribute, attr_value in attributes['attr'].items():
                child.set(attribute, attr_value.format_map(format_dict))

    def print_nfo(self):
        xmlstr = minidom.parseString(ET.tostring(
            self.top, 'utf-8')).toprettyxml(indent="    ")
        print(xmlstr)

    def write_nfo(self, filename):
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
