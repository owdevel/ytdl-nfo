# ytdl-nfo : youtube-dl NFO generator

[youtube-dl](https://github.com/ytdl-org/youtube-dl) is an incredibly useful resource to download and archive footage from across the web. Viewing and organising these files however can be a bit of a hassle.

**ytdl-nfo** takes the `--write-info-json` output from youtube-dl and parses it into Kodi-compatible .nfo files. The aim is to prepare and move files so as to be easily imported into media centers such as Plex, Emby, Jellyfin, etc. 

**Warning**
This package is still in early stages and breaking changes may be introduced.

## Installation
Requirements: Python 3.6
### Python 3 pipx (recommended)
[pipx](https://github.com/pipxproject/pipx) is tool that installs a package and its dependiencies in an isolated environment. This is useful to not affect existing packages or installs. Visit their [github page](https://github.com/pipxproject/pipx) to learn more and for installation instructions.

1. Ensure Python 3.6 and [pipx](https://github.com/pipxproject/pipx) is installed
2. Run the following command to install with pipx
``` bash
pipx install git+https://github.com/owdevel/ytdl_nfo.git
```

### Python 3 pip
1. Ensure Python 3.6 is installed
2. Run the following command to install with pip
```bash
pip install git+https://github.com/owdevel/ytdl_nfo.git
```

### Manual
1. Ensure Python 3.6 is installed
2. Clone the repo using `git clone https://github.com/owdevel/ytdl_nfo.git`
3. Cd into the directory
4. Install requirements using pip `pip install -r requirements.txt`


## Usage
### Automatic
Run `ytdl-nfo JSON_FILE` replacing `JSON_FILE` with either the path to the file you wish to convert, or a folder containing files to convert. The tool will automatically take any files ending with `.json` and convert them to `.nfo` using the included extractor templates.

#### Examples
Convert a single file
```bash
ytdl-nfo great_video.info.json
```

Convert a directory with json files
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
- [ ] Recursive folder searching
- [ ] Documentation and templates for creating custom extractors
- [ ] Add package to pypi

## Authors Note
This is a small project I started to learn how to use python packaging system whilst providing some useful functionality for my home server setup. Feel free to contact me at owdevel@gmail.com with any feedback, suggestions or criticisms. Hope you have a great day :).