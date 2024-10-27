"""Defines the NFOGenerator class."""

from __future__ import annotations

# Standard Libraries
import json
import logging
import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Any

# Third-party Libraries
import pkg_resources
from yaml import safe_load

# Internal Libraries
from ytdl_nfo.nfo import InvalidConfigError
from ytdl_nfo.nfo import NFOConfig

if TYPE_CHECKING:
    # Standard Libraries
    from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


# YouTube timestamps appear to use Pacific Standard Time (PST)
# Reference: https://support.google.com/youtube/answer/1270709?hl=en#:~:text='Published%20on'%20date%20on%20watch%20page
PST = timezone(timedelta(hours=-8))


class NFOGenerator:
    """Defines a class used to generate Kodi-compatible NFO files."""

    def __init__(self, json_file: Path, *, extractor_name: str | None = None, overwrite: bool = False) -> None:
        """Initialize an NFOGenerator object.

        Args:
            json_file (Path): The JSON file to process
            extractor_name (str | None, optional): The specific extractor config to use; defaults to None
            overwrite (bool, optional): Whether to overwrite existing NFO files; defaults to False
        """
        nfo_config: NFOConfig
        self.json_file: Path = json_file

        # ---------------------------- Load JSON Metadata ---------------------------- #

        try:
            # Read metadata from the JSON source file
            metadata: dict[str, Any] = json.loads(json_file.read_text(encoding="utf-8"))

            if "epoch" in metadata:
                # Ensure upload_date is set
                metadata.setdefault(
                    "upload_date", datetime.fromtimestamp((metadata["epoch"]), tz=PST).strftime("%Y%m%d")
                )
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from: %s", str(json_file))
            return

        # ------------------------ Set / Update Extractor Name ----------------------- #

        # Override default extractor name, if set via CLI argument
        if not isinstance((extractor_name := extractor_name or metadata.get("extractor")), str):
            logger.error("Expected extractor name to be a string but was a '%s'", type(extractor_name))
            return

        # Normalize the extractor name
        extractor_name = re.sub(r"[:?*/\\]", "_", extractor_name.lower())

        logger.info("Processing '%s' with '%s' extractor", str(json_file), extractor_name)

        # --------------------------- Initialize NFO Config -------------------------- #

        try:
            # Read the extractor config from the package resources
            extractor_path: str = f"configs/{extractor_name}.yaml"

            with pkg_resources.resource_stream("ytdl_nfo", extractor_path) as f:
                nfo_config = NFOConfig(safe_load(f), metadata)
        except FileNotFoundError:
            logger.error("No NFO config found for extractor '%s'", extractor_name)
            return
        except InvalidConfigError as e:
            logger.error("Invalid extractor config: %s", e)
            return

        # Set the NFO file name based on the '_filename' metadata attribute or the JSON file name
        self.nfo_filename: str = nfo_config.filename or self.default_nfo_name

        # Abort if NFO file exists and overwrite was not specified
        if self.nfo_path.exists() and not overwrite:
            logger.debug("Skipping %s; NFO file already exists, and 'overwrite' is disabled", str(self.nfo_path))
            return

        # ---------------------- Generate and Write the NFO File --------------------- #

        self.nfo_path.write_text(nfo_config.xml_str, encoding="utf-8")
        logger.info("Finished writing '%s'", str(self.nfo_path))

    @property
    def default_nfo_name(self) -> str:
        """Generate a default NFO file name by stripping extensions from the JSON file path.

        Returns:
            str: The name of the JSON file, minus any suffixes
        """
        # Handle the most common case where the suffix is the default '.info.json'
        if self.json_file.name.endswith(".info.json"):
            return self.json_file.name[:-10]

        # Otherwise, try to auto-detect and strip any suffixes
        # Note: This was removed as the default because it will replace part of the filename if the name contains
        # periods and no spaces (e.g., if the `--restrict-filenames` flag was used)
        suffixes: str = "".join(self.json_file.suffixes)

        return self.json_file.name[: len(suffixes) * -1]

    @property
    def nfo_path(self) -> Path:
        """Generates the NFO output file path.

        NFO files will be placed next to the source JSON file.

        Returns:
            Path: The NFO output file path
        """
        return self.json_file.with_name(f"{self.nfo_filename}.nfo")
