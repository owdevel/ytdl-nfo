"""Defines NFOConfig and NFOField classes used to parse an extractor config and generate the NFO XML data."""

from __future__ import annotations

# Standard Libraries
import ast
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from logging import Logger
from logging import getLogger
from typing import Any
from typing import TypedDict
from typing import cast

# Third-party Libraries
from defusedxml.minidom import parseString

logger: Logger = getLogger()


IDENT_SIZE: int = 4
"""The number of spaces to indent nested XML tags when pretty-printing."""

# ============================================================================ #
#                                   Utilities                                  #
# ============================================================================ #


def format_value(template: str, metadata: dict[str, Any]) -> str:
    """Formats the given template string using metadata from the JSON file.

    Args:
        template (str): A format string template
        metadata (dict[str, Any]): Data from the JSON source file, used to populate the field

    Returns:
        str: The formatted string
    """
    # Use a defaultdict to return an empty string, rather than raising a KeyError, if an extractor config references
    # a metadata field that does not exist
    # Reference: https://stackoverflow.com/a/21754294
    metadata_default: dict[str, Any] = defaultdict(lambda: "")
    metadata_default.update(metadata)

    return template.format_map(metadata_default)


# ============================================================================ #
#                                 Type Classes                                 #
# ============================================================================ #


class Converter(TypedDict):
    """Define data types for the 'converter' data structure."""

    data_type: str
    input_format: str
    output_format: str


class NFOFieldType(TypedDict, total=False):
    """Define data types for an NFOConfig field data structure."""

    attrs: dict[str, str]
    converter: Converter
    value: str


class InvalidConfigError(Exception):
    """A custom error class for reporting issues with an extractor config."""


# ============================================================================ #
#                                  Dataclasses                                 #
# ============================================================================ #


class NFOField:
    """A logical representation of a field in an NFO extractor config."""

    attrs: dict[str, str]
    tag_path: str
    value: list[str]

    def __init__(self, tag_path: str, field_info: NFOFieldType, metadata: dict[str, Any]) -> None:
        """Initialize an NFOField object.

        Args:
            tag_path (str): The name of the NFO XML tag to use for the field
            field_info (NFOFieldType): Information about the field (e.g., the value, any attributes to include, and
                an optional converter to apply)
            metadata (dict[str, Any]): Data from the JSON source file, used to populate the field
        """
        self.tag_path = tag_path.rstrip("!")
        self.attrs = field_info.get("attrs", {})

        value: str = format_value(field_info.get("value", ""), metadata)

        # If tag_path ends with a '!', the value should be deserialized to a Python list
        # If the value is empty but supposed to be a list, default to "[]" to prevent the deserializer from breaking
        self.value = ast.literal_eval(value or "[]") if tag_path[-1] == "!" else [value]

        # If a converter is specified, apply it to each element in the value list
        if field_info.get("converter"):
            self.value = [
                self._convert(item=item, **cast(Converter, field_info.get("converter"))) for item in self.value
            ]

    def _convert(self, item: str, data_type: str, input_format: str, output_format: str, *_: str) -> str:
        try:
            if data_type == "date":
                item = datetime.strptime(item, input_format).strftime(output_format)  # noqa: DTZ007
        except ValueError as e:
            logger.error("Conversion error: %s", e)

        return item


class NFOConfig:
    """A logical representation of an NFO extractor config."""

    filename: str = ""
    root_tag: str
    fields: list[NFOField]
    metadata: dict[str, Any]

    def __init__(self, config: dict[str, list[dict[str, str | NFOFieldType]]], metadata: dict[str, Any]) -> None:
        """Initializes an NFOConfig object.

        Args:
            config (dict[str, list[dict[str, str  |  NFOFieldType]]]): The data from an NFO extractor config
            metadata (dict[str, Any]): Data from a JSON source file, used to populate the field of the config
        """
        self._validate(config)

        # Allow the config to specify the name of the NFO output file
        if "_filename" in config:
            self.filename = format_value(str(config["_filename"]), metadata)

        self.metadata = metadata
        self.root_tag = next(key for key in config if not key.startswith("_"))

        # Convert each item beneath the root_tag to an NFOField object for easier processing
        self.fields = [
            NFOField(
                tag_path=tag,
                field_info=field_info if isinstance(field_info, dict) else NFOFieldType(value=field_info),
                metadata=metadata,
            )
            for elem in config[self.root_tag]
            for tag, field_info in elem.items()
        ]

    def _validate(self, config: dict[str, Any]) -> None:
        """Validate the structure of the config.

        Args:
            config (dict[str, Any]): The config data

        Raises:
            InvalidConfigException: If there is no top-level key
            InvalidConfigException: If there is more than one non-metadata top-level key
            InvalidConfigException: If the top-level key does not contain a list of dictionaries
        """
        # Get a list of top-level keys, ignoring metadata keys (i.e., ones starting with '_')
        keys: list[str] = [key for key in config if not key.startswith("_")]
        msg: str

        if len(keys) == 0:
            msg = "No top-level key detected"
            raise InvalidConfigError(msg)

        if len(keys) > 1:
            msg = "Multiple top-level keys detected; only one non-metadata key is supported"
            raise InvalidConfigError(msg)

        root_tag: str = keys[0]

        if isinstance(config[root_tag], list) and any(
            field for field in config[root_tag] if not isinstance(field, dict)
        ):
            msg = "The top-level key does not contain a list of dictionaries"
            raise InvalidConfigError(msg)

    @property
    def xml_str(self) -> str:
        """Generate an XML representation of the JSON data, according to the NFO extractor config.

        Returns:
            str: The NFO XML data
        """
        self.top = ET.Element(self.root_tag)

        # Recursively generate the rest of the NFO XML
        try:
            self._create_child_element(self.top, self.fields, self.metadata)
        except ValueError as e:
            logger.exception(e)

        return parseString(ET.tostring(self.top, encoding="utf-8")).toprettyxml(indent=" " * IDENT_SIZE)

    def _create_child_element(
        self,
        parent_element: ET.Element,
        subtree_data: NFOField | list[NFOField],
        metadata: dict[str, Any],
    ) -> None:
        """A private helper method, recursively called by xml_str(), to generate XML elements.

        Args:
            parent_element (ET.Element): The XML element under which the current tag should be nested
            subtree_data (NFOField | list[NFOField]): Data about the current and any child elements
            metadata (dict[str, Any]): Data from a JSON source file, used to populate element attributes
        """
        # If the subtree_data is a list, recursively process each field
        if isinstance(subtree_data, list):
            for field in subtree_data:
                self._create_child_element(parent_element, field, metadata)
            return

        element: ET.Element = parent_element
        field: NFOField = subtree_data
        tag: str

        # Create any intermediary elements
        for tag in field.tag_path.split(">")[:-1]:
            element = ET.SubElement(element, tag)

        # Create the final ("leaf") element(s)
        parent_element = element
        tag = field.tag_path.split(">")[-1]

        for item in field.value:
            element = ET.SubElement(parent_element, tag)
            element.text = item

            # Add attributes
            for attribute, attr_value in field.attrs.items():
                element.set(attribute, format_value(attr_value, metadata))
