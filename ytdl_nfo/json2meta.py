import json
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