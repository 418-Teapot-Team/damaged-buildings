import json
from typing import Any

import requests

with open("items_with_tenders.json", "r") as file:
    items = json.load(file)


def get_location(longitude: float, latitude: float) -> dict[str, Any]:
    url = f"https://api.apple-mapkit.com/v1/reverseGeocode?loc={latitude},{longitude}&lang=en-GB"
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJtYXBzYXBpIiwidGlkIjoiMk01MzgyRkRKTiIsImFwcGlkIjoiMk01MzgyRkRKTi5tYXBzLm9yZy5ncHMtY29vcmRpbmF0ZXMiLCJpdGkiOmZhbHNlLCJpcnQiOmZhbHNlLCJpYXQiOjE3NDU3Mzk4ODgsImV4cCI6MTc0NTc0MTY4OCwib3JpZ2luIjoiaHR0cHM6Ly9ncHMtY29vcmRpbmF0ZXMub3JnIn0.3x47I9muKz39R9tzb7zlOP_YlsK_BGFEZz3SA8-RcKI_U8BH3TcjbuCzV75seb0iyFN1qwMExrCQjU1D34Y7jg"
    }
    response = requests.get(url, headers=headers)
    result = response.json()["results"][0]
    return {
        "display_name": ", ".join(result["formattedAddressLines"]),
        "administrative_area": result["administrativeArea"],
        "sub_administrative_area": result.get("subAdministrativeArea"),
        "locality": result["locality"],
        "post_code": result["postCode"],
        "thoroughfare": result.get("thoroughfare"),
        "full_thoroughfare": result.get("fullThoroughfare"),
        "longitude": longitude,
        "latitude": latitude,
    }


cleaned_items = []
for idx, item in enumerate(items, 1):
    print(f"{idx}/{len(items)}")
    cleaned_item = {
        "types": item["impact"],
        "weapon_system": ws[0] if (ws := item["weapon_system"]) else "Unknown",
        "date": item["date"],
        "location": get_location(item["longitude"], item["latitude"]),
        # "latitude": item["latitude"],
        # "longitude": item["longitude"],
        "bellingcat": {
            "id": item["id"],
            "description": item["description"],
            "sources": item["sources"],
        },
        "prozorro_tender": (
            {
                "id": item["tender_id"],
            }
            if item.get("tender_id")
            else None
        ),
    }
    cleaned_items.append(cleaned_item)

with open("cleaned_items.json", "w") as file:
    json.dump(cleaned_items, file, indent=4, ensure_ascii=False)
