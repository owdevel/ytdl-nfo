
Open menu
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
            for file in files:
                if file.endswith("info.json"):
                    json_files.append(os.path.join(root, file))

    return json_files

def main(directories):
    json_files = get_info_json_files(directories)

    for json_file in json_files:
        with open(json_file, "rt", encoding="utf-8") as f:
            data = json.load(f)
            if "ext" in data:
                media = json_file[:-9] + data["ext"]
                # Create metadata file
                with open("FFMETADATAFILE", "w", encoding="utf-8") as metadata_file:
                    if "chapters" in data:
                        text = ""
                        for d in data["chapters"]:
                            text += f"""
[CHAPTER]
TIMEBASE=1/1000
START={int(d["start_time"] * 1000)}
END={int(d["end_time"] * 1000)}
title={d["title"]}
"""
                        metadata_file.write(text)

                # Use subprocess to call ffmpeg
                try:
                    subprocess.run(f"ffmpeg -y -i \"{media}\" -f ffmetadata FFMETADATAFILE", check=True)
                    output_media = os.path.join(os.path.dirname(media), "ffmpeg", os.path.basename(media))

                    # Create temporary directory
                    with tempfile.TemporaryDirectory() as temp_dir:
                        output_media = os.path.join(temp_dir, os.path.basename(media))
                        subprocess.run(f"ffmpeg -i \"{media}\" -i FFMETADATAFILE -map_metadata 1 -codec copy \"{output_media}\"", check=True)
                        os.replace(output_media, media)

                except subprocess.CalledProcessError as e:
                    print(f"An error occurred while processing {media}: {e}")

                # Clean up
                if os.path.exists("FFMETADATAFILE"):
                    os.remove("FFMETADATAFILE")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files to add metadata to media files.")
    parser.add_argument('directories', nargs='+', help='List of directories to search for info.json files')

    args = parser.parse_args()
    main(args.directories)