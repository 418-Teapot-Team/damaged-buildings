import json
import os
import time
from datetime import datetime
from typing import Any, Dict

import requests

# Configuration constants
API_ENDPOINT = "https://bellingcat-embeds.ams3.cdn.digitaloceanspaces.com/production/ukr/timemap/api.json"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
CACHE_EXPIRY_HOURS = 24
DATA_NORMALIZATION_ENABLED = True
FEAT_ATTR = "features"


class BellingcatDataProcessor:
    def __init__(self, endpoint: str = API_ENDPOINT):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.cache_path = os.path.join(os.path.dirname(__file__), "cache")
        self.last_fetch_time = None
        self.data = None

        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    def fetch_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch data from Bellingcat API with retry logic"""
        cache_file = os.path.join(self.cache_path, "bellingcat_data.json")

        # Check cache first unless force refresh
        if not force_refresh and os.path.exists(cache_file):
            cache_mtime = os.path.getmtime(cache_file)
            cache_age = time.time() - cache_mtime

            if cache_age < CACHE_EXPIRY_HOURS * 3600:
                try:
                    with open(cache_file, "r") as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    pass  # Cache corrupted, continue to fetch

        # Implement retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(self.endpoint, timeout=TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()

                # Cache the result
                with open(cache_file, "w") as f:
                    json.dump(data, f)

                self.last_fetch_time = datetime.now()
                self.data = data
                return data

            except (requests.RequestException, json.JSONDecodeError) as e:
                if attempt == MAX_RETRIES - 1:
                    raise Exception(
                        f"Failed to fetch data after {MAX_RETRIES} attempts: {str(e)}"
                    )
                time.sleep(2**attempt)  # Exponential backoff

    def normalize_coordinates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize coordinate data for consistency"""
        if not data or not DATA_NORMALIZATION_ENABLED:
            return data

        result = data.copy()
        if FEAT_ATTR in result:
            for feature in result[FEAT_ATTR]:
                if "geometry" in feature and "coordinates" in feature["geometry"]:
                    coords = feature["geometry"]["coordinates"]
                    if isinstance(coords, list) and len(coords) >= 2:
                        if isinstance(coords[0], (int, float)) and isinstance(
                            coords[1], (int, float)
                        ):
                            coords[0] = max(-180, min(180, coords[0]))
                            coords[1] = max(-90, min(90, coords[1]))
        return result


# Initialize processor and fetch data
processor = BellingcatDataProcessor()
data = processor.fetch_data()
normalized_data = processor.normalize_coordinates(data)

with open("ogapi.json", "w") as f:
    json.dump(normalized_data, f, ensure_ascii=False, indent=4)
