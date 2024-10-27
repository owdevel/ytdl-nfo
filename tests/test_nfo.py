from __future__ import annotations

# Standard Libraries
from typing import Any

# Third-party Libraries
import pytest

# Internal Libraries
from ytdl_nfo.nfo import NFOConfig
from ytdl_nfo.nfo import NFOField


@pytest.fixture
def sample_config() -> dict[str, list[dict[str, Any]]]:
    return {
        "episodedetails": [
            {"genre!": "{categories}"},
            {"actor>name!": "{cast}"},
            {"really>nested>actor>name>list!": "{cast}"},
            {"this>should>be>invalid": "{upload_date}"},
            {"normal": "{upload_date}"},
            {
                "converted>date": {
                    "convert": "date",
                    "input_format": "%Y%m%d",
                    "output_format": "%Y-%m-%d",
                    "value": "{upload_date}",
                }
            },
            {
                "nested>date!": {
                    "convert": "date",
                    "input_format": "%Y%m%d",
                    "output_format": "%Y-%m-%d",
                    "value": "{nested_dates}",
                }
            },
        ]
    }


@pytest.fixture
def sample_metadata() -> dict[str, Any]:
    return {"cast": ["Scientist", "Engineer"], "categories": ["Science", "Technology"], "upload_date": "20241015"}


def check_lists_equal(list_1: list[str], list_2: list[str]) -> bool:
    """Check if two lists are equal."""
    return len(list_1) == len(list_2) and sorted(list_1) == sorted(list_2)


class TestNFO:
    def test_nfoconfig(self, sample_config: dict[str, list[dict[str, Any]]], sample_metadata: dict[str, Any]) -> None:
        cfg = NFOConfig(sample_config, sample_metadata)

        assert cfg.root_tag == "episodedetails"

        assert isinstance(cfg.fields[0], NFOField)
        assert cfg.fields[0].tag_path == "genre"

        genres: str | list[str] = cfg.fields[0].value
        assert isinstance(genres, list)
        assert check_lists_equal(genres, ["Science", "Technology"])

        assert isinstance(cfg.fields[1], NFOField)

        actors: str | list[str] = cfg.fields[1].value
        assert cfg.fields[1].tag_path == "actor>name"
        assert isinstance(actors, list)
        assert check_lists_equal(actors, ["Scientist", "Engineer"])
