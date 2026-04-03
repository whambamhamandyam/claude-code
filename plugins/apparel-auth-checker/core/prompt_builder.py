"""
Constructs the Claude API messages for apparel authentication analysis.

The strategy:
- System prompt: expert persona + brand-specific knowledge + JSON output contract
- User message: labelled image blocks interleaved with a task text block
- Price and platform signals injected as context (not hard rules)
"""

from __future__ import annotations

from core.brand_profiles import BrandProfile, list_brand_names
from core.image_loader import ImageInput

_JSON_OUTPUT_SCHEMA = """\
You MUST respond in this exact JSON format and nothing else:
{
  "verdict": "AUTHENTIC" | "SUSPICIOUS" | "LIKELY_FAKE",
  "confidence": <integer 0-100>,
  "brand_detected": "<brand name as seen in the images, or 'Unknown'>",
  "positive_indicators": ["<specific visual observation>", ...],
  "negative_indicators": ["<specific visual observation>", ...],
  "requested_photos": ["<description of a specific photo to request from seller>", ...],
  "analysis": "<3-5 sentence narrative summary>"
}

Verdict definitions:
- AUTHENTIC: Multiple strong positive indicators, no significant red flags
- SUSPICIOUS: Mixed signals; authenticity cannot be confirmed or denied — more photos needed
- LIKELY_FAKE: One or more definitive fake indicators present

Rules:
- confidence reflects certainty in your verdict (not probability of authenticity)
- If image quality is too poor to assess any features, set verdict SUSPICIOUS, confidence 20
- requested_photos should list 1-4 specific close-up shots that would resolve uncertainty
- positive_indicators and negative_indicators must cite specific visual evidence from the images
- Do NOT hedge excessively — buyers need clear, actionable guidance
- Respond with valid JSON only. Do not wrap in markdown code fences."""


def build_system_prompt(brand_profile: BrandProfile | None) -> str:
    """Build the system prompt with expert persona and optional brand knowledge."""
    known_brands = ", ".join(list_brand_names()).replace("_", " ").title()

    base = (
        "You are an expert apparel authenticator with over 10 years of experience "
        "identifying counterfeit goods on UK secondary market platforms (Vinted, Depop, eBay). "
        "You are specifically familiar with DHGate and AliExpress replica products that flood "
        "these platforms, and you know the exact tells that distinguish genuine items from fakes.\n\n"
        f"You can authenticate items from these brands: {known_brands}.\n\n"
        "Be direct and specific. Cite exact visual evidence for every claim. "
        "Buyers need clear guidance — do not hedge unnecessarily.\n\n"
    )

    if brand_profile:
        brand_section = _build_brand_section(brand_profile)
        return base + brand_section + "\n\n" + _JSON_OUTPUT_SCHEMA
    else:
        generic = (
            "No specific brand has been provided. Identify the brand from visible logos, "
            "labels, and branding in the images, then apply your authentication expertise "
            "for that brand. Look for:\n"
            "- Logo accuracy and font consistency\n"
            "- Label quality and correct formatting\n"
            "- Hardware quality (zips, buttons, buckles)\n"
            "- Stitching consistency and quality\n"
            "- Overall construction quality vs known DHGate replica quality\n\n"
        )
        return base + generic + _JSON_OUTPUT_SCHEMA


def _build_brand_section(profile: BrandProfile) -> str:
    """Format brand-specific authentication knowledge for injection into system prompt."""
    lines = [
        f"You are authenticating: {profile.reference_description}\n",
        f"Key authentication points for {profile.name}:",
    ]

    for point in profile.authentication_points:
        lines.append(f"\n  [{point.feature}]")
        lines.append(f"  What to look for: {point.what_to_look_for}")
        lines.append("  Common DHGate fake tells:")
        for tell in point.common_fake_tells:
            lines.append(f"    - {tell}")

    lines.append(f"\nLegitimate resale range on UK secondary market: "
                 f"£{profile.resale_price_range[0]}–£{profile.resale_price_range[1]}")
    lines.append(f"Suspicious if priced below: £{profile.suspicious_low_price}")

    return "\n".join(lines)


def build_user_message_blocks(
    images: list[ImageInput],
    brand_profile: BrandProfile | None,
    price: float | None,
    platform: str | None,
) -> list[dict]:
    """
    Build the user message content array for the Anthropic API.

    Structure: interleaved label-text + image blocks, followed by task text.
    All images in one message so Claude reasons holistically across them.
    """
    content: list[dict] = []
    n = len(images)

    for i, img in enumerate(images, 1):
        content.append({"type": "text", "text": f"Image {i} of {n}:"})
        content.append(img.to_api_block())

    # Build the task instruction with context signals
    task_parts = [
        f"Analyse the {n} image{'s' if n > 1 else ''} above for authenticity."
    ]

    if price is not None and brand_profile is not None:
        low, high = brand_profile.resale_price_range
        pct_below = ((low - price) / low * 100) if price < low else 0
        price_line = f"\nPRICE SIGNAL: Seller is asking £{price:.2f}. "
        price_line += f"Genuine {brand_profile.name} items typically sell for £{low}–£{high} on UK secondary market. "
        if price < brand_profile.suspicious_low_price:
            price_line += (
                f"⚠ This price (£{price:.2f}) is BELOW the suspicious threshold of "
                f"£{brand_profile.suspicious_low_price}. "
                f"That is {pct_below:.0f}% below the minimum typical resale price. "
                "Factor this into your assessment but do not let price alone determine the verdict — "
                "genuine items are sometimes sold cheaply by owners who need quick cash."
            )
        elif price < low:
            price_line += f"This price is somewhat below the typical range but not impossibly low."
        else:
            price_line += "This price is within the expected range for a genuine item."
        task_parts.append(price_line)
    elif price is not None:
        task_parts.append(f"\nPRICE SIGNAL: Seller is asking £{price:.2f}.")

    if platform:
        platform_notes = {
            "vinted": "Platform: Vinted. Common issues: DHGate fakes listed as 'genuine', new accounts with no reviews selling premium items at low prices.",
            "depop": "Platform: Depop. Common issues: Heavily filtered/edited photos hiding fake details, stock photos mixed with real shots.",
            "ebay": "Platform: eBay. Common issues: Photos may be stock images, look for seller feedback and item location.",
        }
        note = platform_notes.get(platform.lower())
        if note:
            task_parts.append(f"\n{note}")

    task_parts.append("\nProvide your authentication assessment in the required JSON format.")
    content.append({"type": "text", "text": "\n".join(task_parts)})

    return content
