#!/usr/bin/env python3
"""
Apparel Authenticity Checker — CLI entry point.

Paste a listing URL (Vinted, Depop, eBay) or provide image paths/URLs directly.

Usage:
    # From a listing URL (auto-scrapes all images):
    python3 checker.py https://www.vinted.co.uk/items/12345

    # From a listing URL with hints:
    python3 checker.py https://www.vinted.co.uk/items/12345 --brand stone_island --price 28

    # From direct image files or URLs:
    python3 checker.py front.jpg back.jpg label.jpg --brand moncler --price 120

    # JSON output for scripting:
    python3 checker.py https://www.depop.com/products/xyz --output json

Exit codes:
    0  AUTHENTIC
    1  SUSPICIOUS
    2  LIKELY_FAKE
    3  Error
"""

import argparse
import sys
from urllib.parse import urlparse

from core.analyzer import AuthReport, LegitChecker
from core.brand_profiles import list_brand_names
from core.listing_scraper import ScrapingError, scrape_listing
from core.report_formatter import format_json_report, format_text_report


_LISTING_HOSTS = {
    "vinted.co.uk", "vinted.com", "vinted.fr",
    "depop.com",
    "ebay.co.uk", "ebay.com",
}

_VERDICT_EXIT_CODES = {
    "AUTHENTIC": 0,
    "SUSPICIOUS": 1,
    "LIKELY_FAKE": 2,
}


def _is_listing_url(value: str) -> bool:
    """Return True if the string looks like a supported platform listing URL."""
    try:
        parsed = urlparse(value)
        host = parsed.netloc.lower().lstrip("www.")
        return any(host.endswith(h) for h in _LISTING_HOSTS) and bool(parsed.path.strip("/"))
    except Exception:
        return False


def build_parser() -> argparse.ArgumentParser:
    brands = list_brand_names()
    parser = argparse.ArgumentParser(
        prog="checker.py",
        description="AI-powered apparel legit check using Claude Vision.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available brands: {', '.join(brands)}",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="URL_OR_IMAGE",
        help=(
            "Vinted/Depop/eBay listing URL (auto-scrapes images), "
            "or one or more image URLs/file paths."
        ),
    )
    parser.add_argument(
        "--brand",
        metavar="BRAND",
        default=None,
        help=(
            "Brand name hint for targeted authentication. "
            f"Options: {', '.join(brands)}. "
            "If omitted, Claude auto-detects from images."
        ),
    )
    parser.add_argument(
        "--price",
        metavar="GBP",
        type=float,
        default=None,
        help="Asking price in GBP (used as a signal; auto-extracted from listing URL if available).",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format. Default: text.",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-6",
        help="Claude model to use. Default: claude-opus-4-6.",
    )
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        default=None,
        help="Anthropic API key. Overrides ANTHROPIC_API_KEY env var.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Determine if input is a listing URL or direct images
    first_input = args.inputs[0]
    listing_url: str | None = None
    image_sources: list[str] = []
    price: float | None = args.price
    platform: str | None = None

    if len(args.inputs) == 1 and _is_listing_url(first_input):
        # Single listing URL — scrape it
        listing_url = first_input
        if args.output == "text":
            print(f"Fetching listing: {listing_url} ...", file=sys.stderr)

        try:
            scraped = scrape_listing(listing_url)
        except ScrapingError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 3

        image_sources = scraped.images
        platform = scraped.platform

        # Use scraped price only if --price not explicitly provided
        if price is None and scraped.price is not None:
            price = scraped.price

        if args.output == "text" and scraped.title:
            print(f"Listing: {scraped.title}", file=sys.stderr)
        if args.output == "text":
            print(f"Found {len(image_sources)} image(s) on {platform.title()}.", file=sys.stderr)
    else:
        # Direct image URLs or file paths
        image_sources = args.inputs
        # Detect platform from any listing URL-like input in the list
        for inp in args.inputs:
            if _is_listing_url(inp):
                host = urlparse(inp).netloc.lower()
                if "vinted" in host:
                    platform = "vinted"
                elif "depop" in host:
                    platform = "depop"
                elif "ebay" in host:
                    platform = "ebay"
                break

    if not image_sources:
        print("Error: No images to analyse.", file=sys.stderr)
        return 3

    # Run the check
    try:
        checker = LegitChecker(api_key=args.api_key, model=args.model)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3

    if args.output == "text":
        print("Analysing images with Claude Vision ...", file=sys.stderr)

    try:
        report: AuthReport = checker.check(
            image_sources=image_sources,
            brand=args.brand,
            price=price,
            platform=platform,
            listing_url=listing_url,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"Unexpected error during analysis: {e}", file=sys.stderr)
        return 3

    # Output
    if args.output == "json":
        print(format_json_report(report))
    else:
        print(format_text_report(report))

    return _VERDICT_EXIT_CODES.get(report.verdict, 1)


if __name__ == "__main__":
    sys.exit(main())
