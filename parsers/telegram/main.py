import asyncio
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import html2text
import requests
from bs4 import BeautifulSoup


class TelegramScraper:
    def __init__(self, post_url: str, cache_dir: str = "cache/telegram") -> None:
        self.postURL = post_url
        self.urlSplit = self.postURL.split(",")
        self.urlList = [entry + "?embed=1&mode=tme" for entry in self.urlSplit]
        self.imageUrls = []
        self.videoUrls = []
        self.content = ""
        self.dateTime = None
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36 TelegramBot (like TwitterBot)"
        }
        self.cache_dir = cache_dir

    def _get_cache_path(self) -> Path:
        """Generate a cache file path for the current URL."""
        # Create a hash of the URL for the filename
        url_hash = hashlib.md5(self.postURL.encode()).hexdigest()
        cache_path = Path(self.cache_dir) / f"{url_hash}.json"
        return cache_path

    def _read_from_cache(self) -> Optional[Dict[str, Any]]:
        """Try to read data from cache."""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    # Add a note to indicate this came from cache
                    cached_data["_from_cache"] = True
                    return cached_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading cache: {e}", file=sys.stderr)
        return None

    def _save_to_cache(self, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        # Ensure cache directory exists
        cache_dir_path = Path(self.cache_dir)
        cache_dir_path.mkdir(parents=True, exist_ok=True)

        cache_path = self._get_cache_path()
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error writing to cache: {e}", file=sys.stderr)

    def html_to_text(self, html):
        h = html2text.HTML2Text()
        h.body_width = 0  # Disable line wrapping
        h.ignore_links = True  # Ignore hyperlinks
        h.ignore_emphasis = True  # Ignore bold and italic formatting
        h.ignore_images = True  # Ignore images
        h.protect_links = True  # Protect hyperlinks from being stripped out
        h.unicode_snob = True  # Use Unicode characters instead of ASCII
        h.wrap_links = False  # Disable link wrapping

        text = h.handle(html)
        text = re.sub(r"\*+", "", text)  # Remove asterisks
        text = re.sub(
            r"^[ \t]*[\\`]", "", text, flags=re.MULTILINE
        )  # Remove leading \ or `
        return text

    def format_as_json(self):
        """Format the scraped data as JSON in the requested format."""
        media_list = []

        # Add images to media list
        for img_url in self.imageUrls:
            media_list.append({"type": "image", "url": img_url})

        # Add videos to media list
        for video_url in self.videoUrls:
            media_list.append({"type": "video", "url": video_url})

        # Create the JSON object
        json_data = {
            "text": self.content,
            "link": self.postURL,
            "media": media_list,
            "created_at": self.dateTime.isoformat() if self.dateTime else None,
        }

        return json_data

    async def run(self):
        # First, try to get from cache
        cached_data = self._read_from_cache()
        if cached_data:
            return cached_data

        def append_image_urls(url_list):
            for div in url_list:
                style = div.get("style", "")
                match = re.search(r"background-image:url\('(.*)'\)", style)
                if match:
                    bg_image_url = match.group(1)
                    self.imageUrls.append(bg_image_url)

        def append_video_urls(link_html):
            # Method 1: Try to extract video sources safely using string matching
            html_str = str(link_html)

            # Find video tags with src attributes
            video_src_matches = re.findall(r'<video[^>]*src="([^"]+)"', html_str)
            for src in video_src_matches:
                if src and src not in self.videoUrls:
                    self.videoUrls.append(src)

            # Find source tags with video type
            video_source_matches = re.findall(
                r'<source[^>]*type="video/[^"]*"[^>]*src="([^"]+)"', html_str
            )
            for src in video_source_matches:
                if src and src not in self.videoUrls:
                    self.videoUrls.append(src)

            # Find Telegram data-video attributes (specific to Telegram's embed format)
            data_video_matches = re.findall(r'data-video="([^"]+)"', html_str)
            for src in data_video_matches:
                if src and src not in self.videoUrls:
                    self.videoUrls.append(src)

            # Method 2: Use BeautifulSoup's select method which is more reliable
            try:
                # Look for video sources using CSS selectors
                for selector in [
                    "video[src]",
                    'source[type="video/mp4"]',
                    'source[type="application/x-mpegURL"]',
                    "div[data-video]",
                ]:
                    elements = link_html.select(selector)
                    for el in elements:
                        src = None
                        if selector == "div[data-video]":
                            src = el.get("data-video")
                        else:
                            src = el.get("src")

                        if src and src not in self.videoUrls:
                            self.videoUrls.append(src)
            except Exception as e:
                print(
                    f"Error extracting videos with CSS selectors: {e}", file=sys.stderr
                )

        try:
            for link in self.urlList:
                link_req = requests.get(url=link, headers=self.headers)
                link_req.raise_for_status()
                link_html = BeautifulSoup(link_req.text, "html.parser")

                # Extract content - using correct BS4 syntax with attrs parameter
                content_element = link_html.find(
                    "div",
                    attrs={
                        "class": "tgme_widget_message_text js-message_text",
                        "dir": "auto",
                    },
                )
                self.content = (
                    self.html_to_text(str(content_element)) if content_element else ""
                )

                # Extract date/time
                date_str = ""
                meta_element = link_html.find(
                    "span", attrs={"class": "tgme_widget_message_meta"}
                )
                if meta_element:
                    # Use regular expressions to extract datetime from the meta_element string
                    meta_html = str(meta_element)
                    time_pattern = r'<time class="datetime" datetime="([^"]+)"'
                    time_match = re.search(time_pattern, meta_html)
                    if time_match:
                        date_str = time_match.group(1)

                if date_str:
                    try:
                        self.dateTime = datetime.datetime.fromisoformat(date_str)
                    except ValueError:
                        try:
                            self.dateTime = datetime.datetime.strptime(
                                date_str, "%Y-%m-%dT%H:%M:%S%z"
                            )
                        except ValueError:
                            print(
                                f"Warning: Could not parse date: {date_str}",
                                file=sys.stderr,
                            )

                # Find images and videos - using correct BS4 syntax
                img_ct = link_html.find_all(
                    "a", attrs={"class": "tgme_widget_message_photo_wrap"}
                )
                append_image_urls(img_ct)
                append_video_urls(link_html)

            # Output the JSON data
            json_data = self.format_as_json()
            # Save to cache
            self._save_to_cache(json_data)
            return json_data

        except requests.exceptions.RequestException as err:
            print(f"Error: {err}", file=sys.stderr)
            return None


async def scrape_telegram_posts(
    urls: List[str], cache_dir: str = "cache/telegram"
) -> List[Dict[str, Any]]:
    """
    Entrypoint function to scrape multiple Telegram posts.

    Args:
        urls: List of Telegram post URLs to scrape
        cache_dir: Directory to use for caching results

    Returns:
        List of dictionaries containing post data
    """
    results = []

    for url in urls:
        try:
            scraper = TelegramScraper(url, cache_dir=cache_dir)
            post_data = await scraper.run()
            if post_data:
                results.append(post_data)
        except Exception as e:
            print(f"Error scraping URL {url}: {e}", file=sys.stderr)

    return results


async def main():
    """Simple demo of the TelegramScraper functionality."""
    # Define a default cache directory
    cache_dir = "cache/telegram"

    # Ensure cache directory exists
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    # Get the URL from user input
    post_url = input("Please enter the Telegram post URL: ")

    # Create the scraper and run it
    scraper = TelegramScraper(post_url, cache_dir=cache_dir)
    post_data = await scraper.run()

    # Output the result
    if post_data:
        print(json.dumps(post_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
