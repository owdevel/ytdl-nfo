import json
import os
import shutil
import subprocess
import tempfile
import argparse

def get_info_json_files(directories):
    """
    Given a list of directories, returns a list of file paths ending with 'info.json'.
    
    :param directories: List of directory paths to search in.
    :return: List of file paths ending with 'info.json'.
    """
    json_files = []
    for directory in directories:
        if not os.path.isdir(directory):
            print(f"Skipping invalid directory: {directory}")
            continue  # Skip invalid directories
        for root, _, files in os.walk(directory):
            json_files.extend(os.path.join(root, file) for file in files if file.endswith("info.json"))
    return json_files

def create_metadata_file(json_file, media_file):
    """
    Creates a metadata file for the given media file.
    
    :param json_file: Path to the JSON file.
    :param media_file: Path to the media file.
    :return: Path to the metadata file.
    """
    with open(json_file, "rt", encoding="utf-8") as f:
        data = json.load(f)
    if "chapters" in data:
        #Instead of creating a temporary file manually, we use tempfile.NamedTemporaryFile to create a temporary file with a unique name.
        metadata_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        for chapter in data["chapters"]:
            metadata_file.write(f"""
[CHAPTER]
TIMEBASE=1/1000
START={int(chapter["start_time"] * 1000)}
END={int(chapter["end_time"] * 1000)}
title={chapter["title"]}
""")
        metadata_file.close()
        return metadata_file.name
    return None

def add_metadata_to_media_file(media_file, metadata_file):
    """
    Adds metadata to the given media file.
    
    :param media_file: Path to the media file.
    :param metadata_file: Path to the metadata file.
    """
    try:
        subprocess.run(f"ffmpeg -y -i \"{media_file}\" -f ffmetadata {metadata_file}", check=True)
        output_media = os.path.join(os.path.dirname(media_file), "ffmpeg", os.path.basename(media_file))
        with tempfile.TemporaryDirectory() as temp_dir:
            output_media = os.path.join(temp_dir, os.path.basename(media_file))
            subprocess.run(f"ffmpeg -i \"{media_file}\" -i {metadata_file} -map_metadata 1 -codec copy \"{output_media}\"", check=True)
            os.replace(output_media, media_file)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while processing {media_file}: {e}")

def main(directories):
    json_files = get_info_json_files(directories)
    for json_file in json_files:
        with open(json_file, "rt", encoding="utf-8") as f:
            data = json.load(f)
        if "ext" in data:
            media_file = json_file[:-9] + data["ext"]
            metadata_file = create_metadata_file(json_file, media_file)
            if metadata_file:
                add_metadata_to_media_file(media_file, metadata_file)
                os.remove(metadata_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files to add metadata to media files.")
    parser.add_argument('directories', nargs='+', help='List of directories to search for info.json files')
    args = parser.parse_args()
    main(args.directories)
