# ytdl-nfo : youtube-dl NFO generator

[youtube-dl](https://github.com/ytdl-org/youtube-dl) is an incredibly useful tool for downloading and archiving footage from across the web; however, viewing and organizing these files can be a hassle.

**ytdl-nfo** automates metadata processing so that media files can be easily imported into media centers such as [Plex](https://www.plex.tv/), [Emby](https://emby.media/), [Jellyfin](https://jellyfin.org/), etc. It does this by parsing each `.info.json` file created by youtube-dl (using the `--write-info-json` flag) and generating a Kodi-compatible `.nfo` file.

While this package was originally built for youtube-dl, the goal is to maintain compatibility with related forks, such as [yt-dlp](https://github.com/yt-dlp/yt-dlp).

> :warning: **Warning**: This package is still in early stages and breaking changes may be introduced.

## Installation

### Python 3 pipx (recommended)

[pipx](https://github.com/pipxproject/pipx) is a tool that installs a package and its dependencies in an isolated environment.

1. Install [Python 3.8](https://www.python.org/downloads/) (or later)
2. Install [pipx](https://github.com/pipxproject/pipx)
3. Run `pipx install ytdl-nfo`

### Python 3 pip

1. Install [Python 3.8](https://www.python.org/downloads/) (or later)
2. Installed [pip](https://pip.pypa.io/en/stable/installation/)
3. Run `pip install ytdl-nfo`

### Package from Source

1. Install [Python 3.8](https://www.python.org/downloads/) (or later)
2. Install [Python Poetry](https://python-poetry.org/)
3. Clone the repo using `git clone https://github.com/owdevel/ytdl_nfo.git`
4. Create a dev environment with `poetry install`
5. Build with `poetry build`
6. Install from the `dist` directory with `pip install ./dist/ytdl_nfo-x.x.x.tar.gz`

### Docker

1. Build the image `docker build -t ytdl-nfo:latest .`

## Usage

youtube-dl uses site-specific extractors to collect technical data about a media file. This metadata, along with the extractor ID, are written to a `.info.json` file when the `--write-info-json` flag is used. ytdl-nfo uses a set of YAML configs, located in `ytdl_nfo/configs` to control how metadata from the JSON file is mapped to NFO tags.

If extractor auto-detection fails or you want to override the default, use the `--extractor` option to specify a particular template. The template must be located at `ytdl_nfo/configs/<EXTRACTOR_TEMPLATE_NAME>.yaml`.

```text
python3 -m ytdl_nfo [-h] [--config] [-e EXTRACTOR] [--regex REGEX] [-w] JSON_FILE

positional arguments:
  JSON_FILE             JSON file to convert or directory to process recursively

options:
  -h, --help            show this help message and exit
  --config              Show the path to the config directory
  -e EXTRACTOR, --extractor EXTRACTOR
                        Specify specific extractor
  -r, --regex REGEX     A regular expression used to search for JSON source files
  -w, --overwrite       Overwrite existing NFO files
```

### Examples

```bash
# Display the configuration location
ytdl-nfo --config

# Create a single NFO file using metadata from `great_video.info.json`
ytdl-nfo great_video.info.json

# Create an NFO file for each `.info.json` file located in the `video_folder` directory
# (provided a matching extractor template exists in the `ytdl_nfo/configs` directory)
ytdl-nfo video_folder

# Create a single NFO file using metadata from `great_video.info.json` and the `custom_extractor_name` template
ytdl-nfo --extractor custom_extractor_name great_video.info.json

# If using Docker, the ENTRYPOINT is already running `python3 -m ytdl_nfo`, so you just need to pass a volume and your arguments
docker run -it --rm -v .:/app ytdl-nfo:latest --help
```

## Contributing

This is a small project I started to learn how to use the Python packaging system whilst providing some useful functionality for my home server setup. Issues/Pull Requests and constructive criticism are welcome.

### Development Environment

1. Install [Python 3.8](https://www.python.org/downloads/) (or later)
2. Install [Python Poetry](https://python-poetry.org/)
3. Create a fork of this repo
4. Clone your fork using `git clone git@github.com:<YOUR_USERNAME>/ytdl-nfo.git`
5. Change to the project directory and initialize the environment using poetry

    ```bash
    cd ytdl-nfo
    poetry install
    ```

6. Run the application using `poetry run ytdl-nfo`, or use `poetry shell` to enter the virtual env

## Todo

- [ ] Add try catches to pretty print errors
- [ ] Documentation and templates for creating custom extractors
- [x] Documentation of CLI arguments
- [x] Recursive folder searching
- [x] Add package to pypi
