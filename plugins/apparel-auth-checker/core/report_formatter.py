"""
Formats an AuthReport into terminal text or JSON output.
"""

from __future__ import annotations

import json

from core.analyzer import AuthReport

_VERDICT_CONFIG = {
    "AUTHENTIC":    {"banner": "AUTHENTIC",    "bar": "="},
    "SUSPICIOUS":   {"banner": "SUSPICIOUS",   "bar": "-"},
    "LIKELY_FAKE":  {"banner": "LIKELY FAKE",  "bar": "!"},
}

_WIDTH = 62


def format_text_report(report: AuthReport) -> str:
    """Render a human-readable terminal report."""
    lines: list[str] = []

    cfg = _VERDICT_CONFIG.get(report.verdict, _VERDICT_CONFIG["SUSPICIOUS"])
    banner_text = f"  VERDICT: {cfg['banner']}   |   Confidence: {report.confidence}%  "
    bar_char = cfg["bar"]
    border = bar_char * _WIDTH

    lines.append(f"\n+{border}+")
    lines.append(f"|{banner_text.center(_WIDTH)}|")
    lines.append(f"+{border}+")
    lines.append("")

    # Metadata line
    meta_parts = [f"Brand: {report.brand_detected}", f"Images analysed: {report.images_analyzed}"]
    if report.platform:
        meta_parts.append(f"Platform: {report.platform.title()}")
    lines.append("  " + "   |   ".join(meta_parts))

    # Price signal
    if report.price is not None:
        lines.append(f"  Asking price: £{report.price:.2f}")

    if report.non_image_flags:
        lines.append("")
        for flag in report.non_image_flags:
            lines.append(f"  ⚠  {flag}")

    # Positive indicators
    if report.positive_indicators:
        lines.append("")
        lines.append("POSITIVE INDICATORS:")
        for item in report.positive_indicators:
            lines.append(f"  + {item}")

    # Negative indicators
    if report.negative_indicators:
        lines.append("")
        lines.append("NEGATIVE INDICATORS:")
        for item in report.negative_indicators:
            lines.append(f"  ✗ {item}")

    # Photos to request
    if report.requested_photos:
        lines.append("")
        lines.append("REQUEST THESE PHOTOS FROM SELLER:")
        for i, photo in enumerate(report.requested_photos, 1):
            lines.append(f"  {i}. {photo}")

    # Full analysis
    if report.raw_analysis:
        lines.append("")
        lines.append("FULL ANALYSIS:")
        # Word-wrap at ~78 chars
        words = report.raw_analysis.split()
        line_buf = "  "
        for word in words:
            if len(line_buf) + len(word) + 1 > 78:
                lines.append(line_buf)
                line_buf = f"  {word}"
            else:
                line_buf = f"{line_buf} {word}" if line_buf.strip() else f"  {word}"
        if line_buf.strip():
            lines.append(line_buf)

    lines.append("")
    return "\n".join(lines)


def format_json_report(report: AuthReport) -> str:
    """Serialize AuthReport to a clean JSON string."""
    data = {
        "verdict": report.verdict,
        "confidence": report.confidence,
        "brand_detected": report.brand_detected,
        "positive_indicators": report.positive_indicators,
        "negative_indicators": report.negative_indicators,
        "requested_photos": report.requested_photos,
        "non_image_flags": report.non_image_flags,
        "analysis": report.raw_analysis,
        "images_analyzed": report.images_analyzed,
        "listing_url": report.listing_url,
        "price": report.price,
        "platform": report.platform,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
