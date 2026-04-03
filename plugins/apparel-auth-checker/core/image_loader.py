"""Image loading utilities: URL sources and local file base64 encoding."""

from __future__ import annotations

import base64
import sys
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

EXTENSION_TO_MEDIA_TYPE: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


@dataclass
class ImageInput:
    """An image ready for inclusion in an Anthropic API message."""
    source_type: str          # "url" or "base64"
    url: str | None           # set when source_type == "url"
    data: str | None          # base64 string when source_type == "base64"
    media_type: str | None    # e.g. "image/jpeg" when source_type == "base64"
    original_source: str      # the original URL or file path string

    def to_api_block(self) -> dict:
        """Return an Anthropic API-compatible image content block."""
        if self.source_type == "url":
            return {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": self.url,
                },
            }
        else:
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": self.media_type,
                    "data": self.data,
                },
            }


def load_image(source: str) -> ImageInput | None:
    """
    Load a single image from a URL or local file path.

    Returns None and prints a warning on failure — callers should skip None entries.
    """
    source = source.strip()

    if source.startswith("http://") or source.startswith("https://"):
        return _load_url(source)
    else:
        return _load_file(source)


def load_images(sources: list[str]) -> list[ImageInput]:
    """
    Batch-load images, skipping any that fail to load.

    Prints warnings to stderr for each failure.
    """
    results: list[ImageInput] = []
    for source in sources:
        img = load_image(source)
        if img is not None:
            results.append(img)
    return results


def _load_url(url: str) -> ImageInput | None:
    """
    Use URL source type directly — the Anthropic API fetches the image.
    Validates the URL is reachable with a HEAD request first.
    """
    try:
        import requests
        resp = requests.head(url, timeout=10, allow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; LegitChecker/1.0)"
        })
        # Accept 200-399 and 405 (Method Not Allowed for HEAD, fallback to URL)
        if resp.status_code < 400 or resp.status_code == 405:
            return ImageInput(
                source_type="url",
                url=url,
                data=None,
                media_type=None,
                original_source=url,
            )
        # If HEAD fails try downloading to validate
        print(f"Warning: URL returned {resp.status_code}: {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Could not reach URL {url}: {e}", file=sys.stderr)
        return None


def _load_file(path_str: str) -> ImageInput | None:
    """Load a local image file and base64-encode it."""
    path = Path(path_str)

    if not path.exists():
        print(f"Warning: File not found: {path_str}", file=sys.stderr)
        return None

    # Detect media type from extension first
    ext = path.suffix.lower()
    media_type = EXTENSION_TO_MEDIA_TYPE.get(ext)

    # Try Pillow for better format detection and validation
    try:
        from PIL import Image as PILImage
        with PILImage.open(path) as img:
            fmt = img.format
            if fmt:
                pil_map = {
                    "JPEG": "image/jpeg",
                    "PNG": "image/png",
                    "GIF": "image/gif",
                    "WEBP": "image/webp",
                }
                media_type = pil_map.get(fmt, media_type)
    except Exception:
        pass  # Fall back to extension-based detection

    if not media_type:
        print(f"Warning: Unsupported image format for file: {path_str}", file=sys.stderr)
        return None

    if media_type not in SUPPORTED_MEDIA_TYPES:
        print(f"Warning: Unsupported media type {media_type} for file: {path_str}", file=sys.stderr)
        return None

    try:
        raw_bytes = path.read_bytes()
        encoded = base64.standard_b64encode(raw_bytes).decode("utf-8")
        return ImageInput(
            source_type="base64",
            url=None,
            data=encoded,
            media_type=media_type,
            original_source=path_str,
        )
    except Exception as e:
        print(f"Warning: Could not read file {path_str}: {e}", file=sys.stderr)
        return None
