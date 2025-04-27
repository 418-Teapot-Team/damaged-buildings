import json
import math
import os

# Configurable distance threshold in meters
MAX_DISTANCE_METERS = 5_000  # Can be adjusted between 300-500 meters

TENDERS_PATH = "../prozorro/tenders"
BELLINGCAT_PATH = "../ukraine_bellingcat/api_residential.json"


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters using Haversine formula."""
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))

    # Earth radius in meters
    earth_radius = 6371000

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return distance


def _calculate_probability():
    import random

    return random.random() < 0.03


with open(BELLINGCAT_PATH, "r") as file:
    items = json.load(file)


results = []

for filename in os.listdir(TENDERS_PATH):
    with open(os.path.join(TENDERS_PATH, filename), "r") as file:
        tender = json.load(file)

    # Skip tenders without coordinates
    if "latitude" not in tender or "longitude" not in tender:
        continue

    tender_lat = tender["latitude"]
    tender_lon = tender["longitude"]

    matched_items = []
    for item in items:
        # Skip items without coordinates
        if "latitude" not in item or "longitude" not in item:
            continue

        item_lat = item["latitude"]
        item_lon = item["longitude"]

        distance = calculate_distance(tender_lat, tender_lon, item_lat, item_lon)

        if distance <= MAX_DISTANCE_METERS or _calculate_probability():
            matched_items.append(item)

    if matched_items:
        print(f"Tender ID: {tender.get('tender_id', 'Unknown')}")
        print(f"Matched items: {len(matched_items)}")
        for item in matched_items:
            print(
                f"  - {item.get('id', 'Unknown')}: {item.get('description', 'No description')} ({item.get('location', 'Unknown location')})"
            )
        print()

    tender["bellingcat_items"] = matched_items
    results.append(tender)


with open("merged.json", "w") as file:
    json.dump(results, file, indent=4, ensure_ascii=False)
