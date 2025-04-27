import json
from pprint import pprint

cleand_teneders = []

with open("merged_tenders.json", "r") as f:
    results = json.load(f)

for item in results:
    pprint(item["awards"])
    cleaned_item = {
        "id": item["tender_id"],
        "title": item["title"],
        "status": "Завершена",
        "expected_cost_uah": item["expected_cost"]["amount"],
        "customer": item["customer"] if item["customer"] else None,
        "awards": item["awards"] or [],
    }
    cleand_teneders.append(cleaned_item)

with open("cleaned_tenders.json", "w") as f:
    json.dump(cleand_teneders, f, indent=4, ensure_ascii=False)
