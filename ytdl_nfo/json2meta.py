import json

with open("c.json", "rt", encoding="utf-8") as f:
   data = json.load(f)
for d in data["chapters"]:
    print(d["start_time"],d["title"],d["end_time"])