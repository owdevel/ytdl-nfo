import yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom

class Nfo:
    def __init__(self, extractor):
        with open('./ytdl_nfo/configs/youtube.yml','r') as f:
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
        child = ET.SubElement(parent, child_name)

        # Check if attributes are present
        if isinstance(subtree[child_name], dict):
            for attribute, value in subtree[child_name].items():
                # Set text if value
                if attribute == 'value':
                    child.text = value.format(**raw_data)
                else:
                    child.set(attribute, value.format(**raw_data))
        # Value only
        else:
            child.text = subtree[child_name].format(**raw_data)

    def print_nfo(self):
        xmlstr = minidom.parseString(ET.tostring(self.top, 'utf-8')).toprettyxml(indent="    ")
        print(xmlstr)

    def write_nfo(self, filename):
        xmlstr = minidom.parseString(ET.tostring(self.top, 'utf-8')).toprettyxml(indent="    ")
        with open(filename, 'w') as f:
            f.write(xmlstr)



def get_config(extractor):
   return Nfo(extractor)
