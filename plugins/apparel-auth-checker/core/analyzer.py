"""
Core orchestrator: LegitChecker class and AuthReport dataclass.

Uses the Anthropic API (claude-opus-4-6 with vision) to analyse apparel images.
Streaming is used for potentially long responses; the final message is collected
via get_final_message().
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Literal

import anthropic

from core.brand_profiles import BrandProfile, get_profile
from core.image_loader import ImageInput, load_images
from core.prompt_builder import build_system_prompt, build_user_message_blocks

DEFAULT_MODEL = "claude-opus-4-6"
MAX_IMAGES_PER_REQUEST = 20


@dataclass
class AuthReport:
    verdict: Literal["AUTHENTIC", "SUSPICIOUS", "LIKELY_FAKE"]
    confidence: int
    brand_detected: str
    positive_indicators: list[str] = field(default_factory=list)
    negative_indicators: list[str] = field(default_factory=list)
    requested_photos: list[str] = field(default_factory=list)
    non_image_flags: list[str] = field(default_factory=list)
    raw_analysis: str = ""
    images_analyzed: int = 0
    listing_url: str | None = None
    price: float | None = None
    platform: str | None = None


class LegitChecker:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Export your Anthropic API key and try again:\n"
                "  export ANTHROPIC_API_KEY='sk-ant-...'"
            )
        self.client = anthropic.Anthropic(api_key=key)
        self.model = model

    def check(
        self,
        image_sources: list[str],
        brand: str | None = None,
        price: float | None = None,
        platform: str | None = None,
        listing_url: str | None = None,
    ) -> AuthReport:
        """
        Perform a full authenticity check.

        Args:
            image_sources: List of image URLs or local file paths.
            brand:         Brand name hint (e.g. 'stone_island'). Optional.
            price:         Asking price in GBP. Optional.
            platform:      Listing platform ('vinted', 'depop', 'ebay'). Optional.
            listing_url:   Original listing URL for reference. Optional.

        Returns:
            AuthReport with verdict, confidence, and detailed findings.
        """
        brand_profile = get_profile(brand)

        # Load images
        images = load_images(image_sources)
        if not images:
            raise ValueError(
                "No images could be loaded. Check that URLs are accessible "
                "and file paths exist."
            )

        # Cap at API limit
        if len(images) > MAX_IMAGES_PER_REQUEST:
            print(
                f"Note: {len(images)} images provided; analysing first {MAX_IMAGES_PER_REQUEST}.",
                file=sys.stderr,
            )
            images = images[:MAX_IMAGES_PER_REQUEST]

        # Build API messages
        system_prompt = build_system_prompt(brand_profile)
        user_content = build_user_message_blocks(images, brand_profile, price, platform)

        # Call API with streaming (avoids timeout on long vision responses)
        raw_json = self._call_api_streaming(system_prompt, user_content)

        # Parse the JSON response
        report = self._parse_response(raw_json, images, price, platform, listing_url, brand_profile)

        # Append non-image flags (price signal)
        if price is not None and brand_profile is not None:
            low = brand_profile.resale_price_range[0]
            if price < brand_profile.suspicious_low_price:
                pct = int((low - price) / low * 100)
                report.non_image_flags.append(
                    f"Price £{price:.2f} is {pct}% below market minimum "
                    f"(£{low}) for genuine {brand_profile.name}"
                )

        return report

    def _call_api_streaming(self, system_prompt: str, user_content: list[dict]) -> str:
        """
        Call the Claude API using streaming and return the complete text response.
        Streaming avoids HTTP timeouts on large vision payloads.
        """
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_content}
            ],
            thinking={"type": "adaptive"},
        ) as stream:
            final = stream.get_final_message()

        # Extract the text content block (skip thinking blocks)
        for block in final.content:
            if block.type == "text":
                return block.text

        return ""

    def _parse_response(
        self,
        raw_text: str,
        images: list[ImageInput],
        price: float | None,
        platform: str | None,
        listing_url: str | None,
        brand_profile: BrandProfile | None,
    ) -> AuthReport:
        """
        Parse the Claude JSON response into an AuthReport.
        Two-pass: direct json.loads() first, regex extraction fallback.
        """
        parsed: dict = {}

        # Pass 1: direct parse
        try:
            parsed = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            pass

        # Pass 2: extract JSON block from potential markdown fences or surrounding text
        if not parsed:
            match = re.search(r'\{[^{}]*"verdict"[^{}]*\}', raw_text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

        # Pass 3: broader extraction
        if not parsed:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

        if not parsed:
            # Absolute fallback: return a SUSPICIOUS verdict with raw text
            return AuthReport(
                verdict="SUSPICIOUS",
                confidence=20,
                brand_detected=brand_profile.name if brand_profile else "Unknown",
                raw_analysis=raw_text[:500],
                images_analyzed=len(images),
                listing_url=listing_url,
                price=price,
                platform=platform,
                non_image_flags=["Could not parse AI response — treat as inconclusive"],
            )

        verdict_raw = parsed.get("verdict", "SUSPICIOUS").upper()
        if verdict_raw not in ("AUTHENTIC", "SUSPICIOUS", "LIKELY_FAKE"):
            verdict_raw = "SUSPICIOUS"

        return AuthReport(
            verdict=verdict_raw,  # type: ignore[arg-type]
            confidence=int(parsed.get("confidence", 50)),
            brand_detected=parsed.get("brand_detected", "Unknown"),
            positive_indicators=parsed.get("positive_indicators", []),
            negative_indicators=parsed.get("negative_indicators", []),
            requested_photos=parsed.get("requested_photos", []),
            non_image_flags=[],
            raw_analysis=parsed.get("analysis", ""),
            images_analyzed=len(images),
            listing_url=listing_url,
            price=price,
            platform=platform,
        )
