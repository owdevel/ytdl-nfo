# ytdl-nfo : youtube-dl NFO generator

[youtube-dl](https://github.com/ytdl-org/youtube-dl) is an incredibly useful resource to download and archive footage from across the web. Viewing and organising these files however can be a bit of a hassle.

**ytdl-nfo** takes the `--write-info-json` output from youtube-dl and parses it into Kodi-compatible .nfo files. The aim is to prepare and move files so as to be easily imported into media centers such as Plex, Emby, Jellyfin, etc. 

**Warning**
This package is still in early stages and breaking changes may be introduced.
### NOTE: youtube-dl derivatives
This package was originally built for youtube-dl, however the aim is to be compatible with related forks as well. Currently these are:
- [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)


## Installation
Requirements: Python 3.8
### Python 3 pipx (recommended)
[pipx](https://github.com/pipxproject/pipx) is tool that installs a package and its dependencies in an isolated environment.

1. Ensure Python 3.8 and [pipx](https://github.com/pipxproject/pipx) is installed
2. Install with `pipx install ytdl-nfo`

### Python 3 pip
1. Ensure Python 3.8 is installed
2. Install with `pip install ytdl-nfo`

### Package from source
1. Ensure Python 3.8 and [Python Poetry](https://python-poetry.org/) is installed
2. Clone the repo using `git clone https://github.com/owdevel/ytdl_nfo.git`
3. Create a dev environment with `poetry install`
3. Build with `poetry build`
4. Install from the `dist` directory with `pip install ./dist/ytdl_nfo-x.x.x.tar.gz`

### Development Environment
1. Perform steps 1-3 of package from source
2. Run using `poetry run ytdl-nfo` or use `poetry shell` to enter the virtual env


## Usage
### Automatic
Run `ytdl-nfo JSON_FILE` replacing `JSON_FILE` with either the path to the file you wish to convert, or a folder containing files to convert. The tool will automatically take any files ending with `.json` and convert them to `.nfo` using the included extractor templates.

#### Examples
Convert a single file
```bash
ytdl-nfo great_video.info.json
```

Convert a directory and all sub directories with `.info.json` files
```bash
ytdl-nfo video_folder
```

### Manual
ytdl-nfo uses a set of YAML configs to determine the output format and what data comes across. This is dependent on the extractor flag which is set by youtube-dl. Should this fail to be set or if a custom extractor is wanted there is the `--extractor` flag. ytdl-nfo will then use extractor with the given name as long as it is in the config directory with the format `custom_extractor_name.yaml`.

```bash
ytdl-nfo --extractor custom_extractor_name great_video.info.json
```

#### Config Location
Run the following command to get the configuration location.
```bash
ytdl-nfo --config
```

## Extractors
Issues/Pull Requests are welcome to add more youtube-dl supported extractors to the repo.

### Custom Extractors
Coming Soon...

## Todo
- [ ] Add try catches to pretty print errors
- [ ] Documentation and templates for creating custom extractors
- [ ] Documentation of CLI arguments
- [x] Recursive folder searching
- [x] Add package to pypi

## Authors Note
This is a small project I started to learn how to use python packaging system whilst providing some useful functionality for my home server setup.
Issues/pull requests and constructive criticism is welcome.
