import json
import os
import shutil

def get_info_json_files(directories):
    """
    Given a list of directories, returns a list of file paths ending with 'info.json'.
    
    :param directories: List of directory paths to search in.
    :return: List of file paths ending with 'info.json'.
    """
    json_files = []

    for directory in directories:
        if not os.path.isdir(directory):
            continue  # Skip invalid directories

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith("info.json"):
                    json_files.append(os.path.join(root, file))


    return json_files

json_files = get_info_json_files(["G:\\Videos\\test\\"])

for json_file in json_files:
    with open(json_file, "rt", encoding="utf-8") as f:
        data = json.load(f)
        if "ext" in data:
            media = json_file[:-9]+data["ext"]
            os.system(f"ffmpeg -y -i \"{media}\" -f ffmetadata FFMETADATAFILE")
            if "chapters" in data:

                text = ""
                for d in data["chapters"]:
                    text += f"""
[CHAPTER]
TIMEBASE=1/1000
START={int(d["start_time"]*1000)}
END={int(d["end_time"]*1000)}
title={d["title"]}
"""             
                index = media.rfind('\\')
    
                # If the character is found, slice the string up to that index
                if index != -1:
                    dir = media[:index]+"\\ffmpeg"
                    try:
                        os.mkdir(dir)
                    except FileExistsError:
                        pass
                    output_media = dir+media[index:]
                    with open("FFMETADATAFILE", "a",encoding="utf-8") as myfile:
                        myfile.write(text)
                    os.system(f"ffmpeg -i \"{media}\" -i FFMETADATAFILE -map_metadata 1 -codec copy \"{output_media}\"")
                    os.replace(output_media,media)
                    os.rmdir(dir) #shutil.rmtree(dir)