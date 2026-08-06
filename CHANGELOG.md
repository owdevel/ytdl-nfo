# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-08-06

### Fixed
- **Python 3.12+ / 3.14 Compatibility**: Replaced deprecated `pkg_resources` with Python standard library `importlib.resources.files` in `ytdl_nfo/nfo.py`.
- **UTF-8 Character Encoding**: Explicitly added `encoding="utf-8"` declaration in generated XML headers (`<?xml version="1.0" encoding="utf-8"?>`) and binary writing to fix special character corruption (e.g. em-dash `—`, `€`, accents).
- **Kodi Rating Display**: Fixed star ratings not displaying in Kodi v17+ by implementing full `<ratings><rating ...><value>...</value></rating></ratings>` XML container and integer `<userrating>` format.
- **Safe List and Date Parsing**: Added error handling for missing or empty JSON metadata fields (`ast.literal_eval` and `strptime`) to prevent crashes during NFO generation.

### Added
- **Official YouTube Thumbnails**: Included `<thumb>` tag mapped to `{thumbnail}` in `youtube.yaml`.
- **Automatic Rating Calculation**: Scaled rating scores from `average_rating` or `like_count`/`view_count` ratios into a standard 10-point scale.
- **Dynamic Audio Language Normalization**: Mapped language codes dynamically to 3-letter ISO 639-2 format (`spa`, `eng`, `ita`, `fra`, `deu`, etc.) leaving unspecified fields clean.
- **New Extractor `youtube_musicvideo`**: Added new extractor configuration (`ytdl_nfo/configs/youtube_musicvideo.yaml`) to output `<musicvideo>` root XML tags.

### Changed
- **Dependencies**: Removed unnecessary `setuptools` runtime requirement from `pyproject.toml`.
