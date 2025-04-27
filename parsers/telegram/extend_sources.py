import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from main import TelegramScraper

# Define fixed paths
CACHE_DIR = "cache/telegram"
INPUT_FILE = "../cleaning/cleaned_items.json"
OUTPUT_FILE = "../telegram/extended_sources.json"

# Ensure cache directory exists
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

# Load the input data
with open(INPUT_FILE, "r") as f:
    items = json.load(f)


async def main():
    for idx, item in enumerate(items, start=1):
        print(f"{idx}/{len(items)}:", item["bellingcat"]["id"])
        extended_sources = []
        for link in item["bellingcat"]["sources"]:
            if link.startswith("https://t.me/"):
                scraper = TelegramScraper(link, cache_dir=CACHE_DIR)
                post_data = await scraper.run()

                if post_data:  # Check if post data was successfully retrieved
                    # Check if post came from cache
                    cache_status = (
                        "CACHED" if post_data.get("_from_cache") else "FETCHED"
                    )
                    print(f"  - {cache_status}: {link}")

                    # Remove the cache indicator flag before storing
                    if "_from_cache" in post_data:
                        del post_data["_from_cache"]

                    extended_sources.append(post_data)
                else:
                    print(f"  - FAILED: {link}")

        item["sources_extended"] = extended_sources

    # Create output directory if it doesn't exist
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the output file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(items, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
