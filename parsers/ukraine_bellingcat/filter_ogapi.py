import json

with open("ogapi.json", "r") as f:
    data = json.load(f)

results = []

for item in data:
    if "Residential" in item["impact"]:
        results.append(item)


with open("api_residential.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("original:", len(data))
print("filtered:", len(results))
