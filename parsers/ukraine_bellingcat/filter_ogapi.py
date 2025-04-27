import json

with open("ogapi.json", "r") as f:
    data = json.load(f)

results = []

for item in data:
    if "Residential" not in item["impact"]:
        continue

    ctx = json.dumps(item).lower()
    if "kyiv" not in ctx and "kiev" not in ctx:
        continue

    results.append(item)


with open("api_residential.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("original:", len(data))
print("filtered:", len(results))
