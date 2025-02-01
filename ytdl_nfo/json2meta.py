import json

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

#ffmpeg -i INPUT.mp4 -f ffmetadata FFMETADATAFILE
with open("c.json", "rt", encoding="utf-8") as f:
   data = json.load(f)
   
text = ""
for d in data["chapters"]:
    print(d["start_time"],d["title"],d["end_time"])
    
    text += f"""
[CHAPTER]
TIMEBASE=1/1000
START={int(d["start_time"]*1000)}
END={int(d["end_time"]*1000)}
title={d["title"]}
"""

with open("ffmetadata", "a") as myfile:
    myfile.write(text)

#ffmpeg -i INPUT.mp4 -i FFMETADATAFILE -map_metadata 1 -codec copy OUTPUT.mp4