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

### Build a Docker Image

1. Install [Docker](https://docs.docker.com/engine/install/)
2. Clone the repo using `git clone https://github.com/owdevel/ytdl_nfo.git`
3. Build the Docker image

    ```bash
    docker build -t ytdl-nfo:local .
    ```

### Package from Source

1. Install [Python 3.8](https://www.python.org/downloads/) (or later)
2. Install [Python Poetry](https://python-poetry.org/)
3. Clone the repo using `git clone https://github.com/owdevel/ytdl_nfo.git`
4. Create a dev environment with `poetry install`
5. Build with `poetry build`
6. Install from the `dist` directory with `pip install ./dist/ytdl_nfo-x.x.x.tar.gz`

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
```

#### Docker

```bash
# 'PATH_TO_MEDIA_FILES' must be relative to 'PATH_CONTAINING_MEDIA_FILES'
docker run --rm -v '<PATH_CONTAINING_MEDIA_FILES>:/mnt' ytdl-nfo '/mnt/<PATH_TO_MEDIA_FILES>'
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

### Custom Extractor Configs

Extractor configs define how data from an `.info.json` file should be mapped (and possibly converted) to NFO XML
elements. They are written in YAML and located in the `ytdl_nfo/configs` directory.

Each extractor config is a dictionary with a single top-level key that maps to a list of dictionaries (referred to here as "Fields"). Metadata about the generated NFO file (e.g., file name) can be specified using top-level keys prefixed with an underscore (e.g., `_filename`).

Each Field contains a single key, which can be either a literal XML tag or a list of nested XML tags (separated by `>`). The associated value can be either a string or a dictionary. If the value is a dictionary, it must contain a key named `value` that maps to a string. Regardless of how the `value` string is specified, it will be treated as a Python format string, with the contents of the `.info.json` file passed in as the arguments. If the key ends with an exclamation point (`!`), the formatted string will be parsed as a list.

Value dictionaries support two additional keys, `attrs` and `converter`, each of which maps to another dictionary. The value of each key in `attrs` will be formatted and the pair will be added to the XML element as attributes, while the `converter` dictionary specifies a `data_type`, as well as other arguments required for the conversion process. Currently, `date` is the only supported converter type, and it takes `input_format` and `output_format` as parameters.

#### Example

Given an `.info.json` file containing the following:

```json
{
    "cast": [
        "Actor 1",
        "Actor 2"
    ],
    "categories": [
        "Science",
        "Technology"
    ],
    "nested_dates": [
        "20240719",
        "20240813",
        "20241004"
    ],
    "upload_date": "20241026"
}
```

and this extractor config:

```yaml
_filename: 'episode'
episodedetails:
  - genre!: '{categories}'
  - actor>name!: '{cast}'
  - really>nested>actor>name>list!: '{cast}'
  - normal: '{upload_date}'
  - converted>date:
      converter:
        data_type: 'date'
        input_format: '%Y%m%d'
        output_format: '%Y-%m-%d'
      value: '{upload_date}'
  - nested>date!:
      converter:
        data_type: 'date'
        input_format: '%Y%m%d'
        output_format: '%Y-%m-%d'
      value: '{nested_dates}'
```

ytdl-nfo will generate an NFO file named `episode.nfo` with the following contents in the same directory as the JSON file.

```xml
<?xml version="1.0" ?>
<episodedetails>
    <genre>Science</genre>
    <genre>Technology</genre>
    <actor>
        <name>Actor 1</name>
        <name>Actor 2</name>
    </actor>
    <really>
        <nested>
            <actor>
                <name>
                    <list>Actor 1</list>
                    <list>Actor 2</list>
                </name>
            </actor>
        </nested>
    </really>
    <normal>20241026</normal>
    <converted>
        <date>2024-10-26</date>
    </converted>
    <nested>
        <date>2024-07-19</date>
        <date>2024-08-13</date>
        <date>2024-10-04</date>
    </nested>
</episodedetails>
```

## Todo

- [ ] Add try catches to pretty print errors
- [x] Documentation and templates for creating custom extractors
- [x] Documentation of CLI arguments
- [x] Recursive folder searching
- [x] Add package to pypi
