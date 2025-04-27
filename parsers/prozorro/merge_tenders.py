import json
import os

results = []

for filename in os.listdir("tenders"):
    with open(f"tenders/{filename}", "r") as f:
        data = json.load(f)
        results.append(data)

with open("merged_tenders.json", "w") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

