import yaml
import ast
import datetime as dt
import xml.etree.ElementTree as ET
import pkg_resources
from xml.dom import minidom

class Nfo:
    def __init__(self, extractor):
        with pkg_resources.resource_stream("ytdl_nfo", f"configs/{extractor}.yaml") as f:
            self.data = yaml.load(f, Loader=yaml.FullLoader)

    def generate(self, raw_data):

        # There should only be one top level node
        top_name = list(self.data.keys())[0]
        self.top = ET.Element(top_name)

        # Recursively generate the rest of the NFO
        self.__create_child(self.top, self.data[top_name], raw_data)

    def __create_child(self, parent, subtree, raw_data):

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
                children = ast.literal_eval(value.format(**raw_data))
            else:
                children = [value.format(**raw_data)]

            if 'convert' in attributes.keys():
                target_type = attributes['convert']
                input_f=attributes['input_f']
                output_f=attributes['output_f']

                for i in range(len(children)):
                    if target_type == 'date':
                        date = dt.datetime.strptime(children[i], input_f)
                        children[i] = date.strftime(output_f)


        # Value only
        else:
            if table:
                children = ast.literal_eval(subtree[child_name].format(**raw_data))
            else:
                children = [subtree[child_name].format(**raw_data)]

        # Add the child node(s)
        child_name = child_name.rstrip('!')

        for value in children:
            child = ET.SubElement(parent, child_name)
            child.text = value

            # Add attributes
            if 'attr' in attributes.keys():
                for attribute, attr_value in attributes['attr'].items():
                    child.set(attribute, attr_value.format(**raw_data))


    def print_nfo(self):
        xmlstr = minidom.parseString(ET.tostring(self.top, 'utf-8')).toprettyxml(indent="    ")
        print(xmlstr)

    def write_nfo(self, filename):
        xmlstr = minidom.parseString(ET.tostring(self.top, 'utf-8')).toprettyxml(indent="    ")
        with open(filename, 'wt', encoding="utf-8") as f:
            f.write(xmlstr)
    
    def get_nfo(self):
        xmlstr = minidom.parseString(ET.tostring(self.top, 'utf-8')).toprettyxml(indent="    ")
        return xmlstr



def get_config(extractor):
   return Nfo(extractor)
