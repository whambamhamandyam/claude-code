"""
Platform-specific listing scrapers for Vinted, Depop, and eBay.

Strategy: requests + HTML/JSON parsing (no headless browser needed).
- Vinted:  Parses __NEXT_DATA__ JSON embedded in page source
- Depop:   Parses application/ld+json structured data + og:image fallback
- eBay:    Parses og:image tags + image carousel elements

Run as a standalone test:
    python -m core.listing_scraper https://www.vinted.co.uk/items/12345
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

_SESSION = requests.Session()
_SESSION.headers.update(_BROWSER_HEADERS)


@dataclass
class ScrapedListing:
    platform: str
    images: list[str] = field(default_factory=list)
    price: float | None = None
    title: str | None = None
    listing_url: str = ""


class ScrapingError(Exception):
    pass


def scrape_listing(url: str) -> ScrapedListing:
    """
    Auto-detect platform from URL and extract images, price, and title.

    Raises ScrapingError if the platform is unsupported or no images found.
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if "vinted.co.uk" in host or "vinted.com" in host or "vinted.fr" in host:
        platform = "vinted"
    elif "depop.com" in host:
        platform = "depop"
    elif "ebay.co.uk" in host or "ebay.com" in host:
        platform = "ebay"
    else:
        raise ScrapingError(
            f"Unsupported platform: {host}. "
            "Supported: vinted.co.uk, depop.com, ebay.co.uk/ebay.com. "
            "You can also provide image URLs or file paths directly."
        )

    html = _fetch_html(url)

    listing: ScrapedListing
    if platform == "vinted":
        listing = _scrape_vinted(url, html)
    elif platform == "depop":
        listing = _scrape_depop(url, html)
    else:
        listing = _scrape_ebay(url, html)

    # Fallback: og:image if primary method found nothing
    if not listing.images:
        listing.images = _extract_og_images(html)

    # Second fallback: JSON-LD
    if not listing.images:
        listing.images = _extract_json_ld_images(html)

    if not listing.images:
        raise ScrapingError(
            f"Could not extract images from {platform} listing. "
            "The listing may be private, removed, or the page structure has changed. "
            "Try providing image URLs or file paths directly."
        )

    return listing


def _fetch_html(url: str) -> str:
    """Fetch the page HTML with browser-like headers."""
    try:
        resp = _SESSION.get(url, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except requests.HTTPError as e:
        raise ScrapingError(f"HTTP error fetching listing: {e}")
    except requests.RequestException as e:
        raise ScrapingError(f"Network error fetching listing: {e}")


def _scrape_vinted(url: str, html: str) -> ScrapedListing:
    """
    Vinted embeds listing data in a __NEXT_DATA__ JSON script tag.
    Parse photos[].full_size_url and price.amount from the JSON tree.
    """
    listing = ScrapedListing(platform="vinted", listing_url=url)

    match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not match:
        return listing

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return listing

    # Navigate into the Next.js page props — structure varies by Vinted version
    # Try common paths
    item = (
        _deep_get(data, "props", "pageProps", "item")
        or _deep_get(data, "props", "pageProps", "initialData", "item")
        or _deep_get(data, "props", "initialProps", "pageProps", "item")
    )

    if item:
        # Extract photos
        photos = item.get("photos") or item.get("photos_for_view") or []
        for photo in photos:
            for key in ("full_size_url", "url", "large_url", "thumb_url"):
                img_url = photo.get(key)
                if img_url and img_url not in listing.images:
                    listing.images.append(img_url)
                    break

        # Extract price
        price_obj = item.get("price") or item.get("price_numeric")
        if isinstance(price_obj, dict):
            try:
                listing.price = float(price_obj.get("amount", 0))
            except (ValueError, TypeError):
                pass
        elif isinstance(price_obj, (int, float)):
            listing.price = float(price_obj)

        # Extract title
        listing.title = item.get("title") or item.get("description", "")[:80]

    return listing


def _scrape_depop(url: str, html: str) -> ScrapedListing:
    """
    Depop embeds listing data in application/ld+json structured data.
    Also tries og:image as a supplementary source.
    """
    listing = ScrapedListing(platform="depop", listing_url=url)

    soup = BeautifulSoup(html, "html.parser")

    # Try JSON-LD first (most reliable on Depop)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, AttributeError):
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            item_type = item.get("@type", "")
            if item_type in ("Product", "ItemPage", "Thing"):
                # Images can be string, list of strings, or list of ImageObject
                images = item.get("image") or []
                if isinstance(images, str):
                    images = [images]
                for img in images:
                    if isinstance(img, dict):
                        img_url = img.get("url") or img.get("contentUrl")
                    else:
                        img_url = img
                    if img_url and img_url not in listing.images:
                        listing.images.append(img_url)

                # Price
                offers = item.get("offers") or {}
                if isinstance(offers, list) and offers:
                    offers = offers[0]
                if isinstance(offers, dict):
                    try:
                        listing.price = float(offers.get("price", 0) or 0)
                    except (ValueError, TypeError):
                        pass

                listing.title = item.get("name") or item.get("description", "")[:80]
                break

    # Supplement with og:image if needed
    if not listing.images:
        listing.images = _extract_og_images(html)

    return listing


def _scrape_ebay(url: str, html: str) -> ScrapedListing:
    """
    eBay listing image extraction.
    Tries: JSON-LD → og:image → image carousel meta tags.
    """
    listing = ScrapedListing(platform="ebay", listing_url=url)

    soup = BeautifulSoup(html, "html.parser")

    # eBay embeds some data in a script with icep_ or __NEXT_DATA__
    # Simplest reliable approach: og:image + image gallery
    listing.images = _extract_og_images(html)

    # Also try to find high-res images in eBay's image gallery pattern
    # eBay uses data-zoom-src or data-src attributes on image tags
    for img in soup.find_all("img", attrs={"data-zoom-src": True}):
        src = img.get("data-zoom-src")
        if src and src not in listing.images:
            listing.images.append(src)

    for img in soup.find_all("img", attrs={"data-src": True}):
        src = img.get("data-src")
        if src and "ebayimg" in src and src not in listing.images:
            listing.images.append(src)

    # Title from og:title or h1
    og_title = soup.find("meta", property="og:title")
    if og_title:
        listing.title = og_title.get("content", "")

    # Price — look for itemprop="price"
    price_el = soup.find(itemprop="price")
    if price_el:
        try:
            listing.price = float(price_el.get("content", 0) or 0)
        except (ValueError, TypeError):
            pass

    return listing


def _extract_og_images(html: str) -> list[str]:
    """Extract og:image meta tag values from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for tag in soup.find_all("meta", property="og:image"):
        content = tag.get("content")
        if content and content not in images:
            images.append(content)
    return images


def _extract_json_ld_images(html: str) -> list[str]:
    """Extract images from all JSON-LD script tags in the page."""
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, AttributeError):
            continue
        _collect_images_from_json(data, images)
    return images


def _collect_images_from_json(obj: object, out: list[str]) -> None:
    """Recursively collect image URLs from a JSON object."""
    if isinstance(obj, str):
        if obj.startswith("http") and any(ext in obj.lower() for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
            if obj not in out:
                out.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            _collect_images_from_json(item, out)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            if key in ("image", "url", "contentUrl", "thumbnailUrl"):
                _collect_images_from_json(val, out)
            elif isinstance(val, (dict, list)):
                _collect_images_from_json(val, out)


def _deep_get(obj: dict, *keys: str) -> object | None:
    """Safely navigate nested dicts."""
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m core.listing_scraper <listing_url>")
        sys.exit(1)

    test_url = sys.argv[1]
    print(f"Scraping: {test_url}")
    try:
        result = scrape_listing(test_url)
        print(f"Platform: {result.platform}")
        print(f"Title:    {result.title}")
        print(f"Price:    £{result.price}" if result.price else "Price:    not found")
        print(f"Images ({len(result.images)}):")
        for i, img_url in enumerate(result.images, 1):
            print(f"  {i}. {img_url}")
    except ScrapingError as err:
        print(f"Error: {err}")
        sys.exit(1)
