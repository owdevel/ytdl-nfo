# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-08-07

### Added
- **Local Artwork Downloader (`-dt` / `--download-thumbs`)**: Added automatic local image file detection and downloading module (`ytdl_nfo/artwork.py`). Automatically saves thumbnails, logos, and fanart to local `.jpg`/`.png` files alongside videos for 100% offline Kodi compatibility.
- **Non-Recursive Directory Scanning (`-nr` / `--no-recurse`)**: Added option to scan only the top-level directory without processing subdirectories recursively.
- **Smart Artist Name Cleaner**: Automatically cleans YouTube uploader names (stripping `VEVO`, `Topic`, `Official`, and splitting CamelCase like `DuaLipa` -> `Dua Lipa`) for accurate MusicBrainz / Fanart.tv artist lookups.
- **Kodi Favorites Artwork Compatibility**: Updated `youtube.yaml` and `youtube_musicvideo.yaml` to map `aspect="poster"` and `aspect="thumb"` to the video cover (`thumbnail`), fixing incorrect thumbnail rendering in Kodi's Favorites menu (`favourites.xml`).

## [0.4.0] - 2026-08-06

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
- **Fanart.tv Integration**: Added optional `--fanart-key` / `-fk` CLI parameter and `ytdl_nfo/fanart.py` module to automatically fetch artist logos (`clearlogo`), banners, posters, and background fanart via MusicBrainz + Fanart.tv APIs.

### Changed
- **Dependencies**: Removed unnecessary `setuptools` runtime requirement from `pyproject.toml`.
