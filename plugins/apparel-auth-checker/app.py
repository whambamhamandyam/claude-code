"""
The Garm Alarm — Hugging Face Spaces / Gradio UI
AI-powered apparel legit checker using Claude Vision.
"""

import os
import sys
import tempfile
from pathlib import Path

import gradio as gr

# Ensure core modules are importable when run from the Space root
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import LegitChecker
from core.brand_profiles import BRAND_PROFILES, get_profile
from core.image_loader import load_images
from core.listing_scraper import ScrapingError, scrape_listing

# ── Brand choices for dropdown ──────────────────────────────────────────────
_BRAND_CHOICES = ["Auto-detect from images"] + [
    p.name for p in BRAND_PROFILES.values()
]
_BRAND_NORM = {"Auto-detect from images": None}
_BRAND_NORM.update({p.name: p.normalized_name for p in BRAND_PROFILES.values()})

# ── Verdict styling ──────────────────────────────────────────────────────────
_VERDICT_STYLE = {
    "AUTHENTIC":   ("✅ AUTHENTIC",   "#1a7a1a", "#e6f4e6"),
    "SUSPICIOUS":  ("⚠️ SUSPICIOUS",  "#7a5a00", "#fff8e1"),
    "LIKELY_FAKE": ("🚨 LIKELY FAKE", "#7a0000", "#fdecea"),
}


def run_check(
    listing_url: str,
    uploaded_images: list,
    brand_choice: str,
    price_str: str,
    progress=gr.Progress(),
) -> tuple:
    """
    Main handler. Returns (verdict_html, details_md, photos_md, status_msg).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            _verdict_html("ERROR", "API key not configured.", "#555", "#eee"),
            "ANTHROPIC_API_KEY is not set. Add it in Space Settings → Secrets.",
            "",
            "❌ Configuration error",
        )

    # Parse price
    price: float | None = None
    if price_str and price_str.strip():
        try:
            price = float(price_str.replace("£", "").replace(",", "").strip())
        except ValueError:
            pass

    brand = _BRAND_NORM.get(brand_choice)
    image_sources: list[str] = []
    platform: str | None = None
    scraped_title: str | None = None

    # ── Source: listing URL ──────────────────────────────────────────────────
    url = listing_url.strip() if listing_url else ""
    if url:
        progress(0.1, desc="Fetching listing…")
        try:
            scraped = scrape_listing(url)
            image_sources = scraped.images
            platform = scraped.platform
            scraped_title = scraped.title
            if price is None and scraped.price is not None:
                price = scraped.price
        except ScrapingError as e:
            if not uploaded_images:
                return (
                    _verdict_html("ERROR", str(e), "#555", "#eee"),
                    str(e),
                    "",
                    "❌ Could not scrape listing — try uploading images directly",
                )
            # Fall through to uploaded images

    # ── Source: uploaded files ───────────────────────────────────────────────
    if uploaded_images and not image_sources:
        for img in uploaded_images:
            if img is not None:
                image_sources.append(str(img))

    if not image_sources:
        return (
            _verdict_html("ERROR", "No images to analyse.", "#555", "#eee"),
            "Please provide a listing URL or upload at least one image.",
            "",
            "❌ No images",
        )

    progress(0.3, desc=f"Analysing {len(image_sources)} image(s) with Claude Vision…")

    try:
        checker = LegitChecker(api_key=api_key)
        report = checker.check(
            image_sources=image_sources,
            brand=brand,
            price=price,
            platform=platform,
            listing_url=url or None,
        )
    except Exception as e:
        return (
            _verdict_html("ERROR", "Analysis failed.", "#555", "#eee"),
            f"Error during analysis: {e}",
            "",
            "❌ Analysis failed",
        )

    progress(1.0, desc="Done")

    # ── Format outputs ───────────────────────────────────────────────────────
    label, fg, bg = _VERDICT_STYLE.get(
        report.verdict, ("⚠️ SUSPICIOUS", "#7a5a00", "#fff8e1")
    )
    verdict_html = _verdict_html(
        label,
        f"Confidence: {report.confidence}%  |  Brand: {report.brand_detected}"
        + (f"  |  Platform: {report.platform.title()}" if report.platform else "")
        + (f"  |  Asking: £{report.price:.2f}" if report.price else ""),
        fg,
        bg,
    )

    details_parts = []

    if report.non_image_flags:
        details_parts.append("### ⚠️ Price Signal")
        for flag in report.non_image_flags:
            details_parts.append(f"- {flag}")
        details_parts.append("")

    if report.positive_indicators:
        details_parts.append("### ✅ Positive Indicators")
        for item in report.positive_indicators:
            details_parts.append(f"- {item}")
        details_parts.append("")

    if report.negative_indicators:
        details_parts.append("### 🚨 Negative Indicators")
        for item in report.negative_indicators:
            details_parts.append(f"- {item}")
        details_parts.append("")

    if report.raw_analysis:
        details_parts.append("### Analysis")
        details_parts.append(report.raw_analysis)

    photos_md = ""
    if report.requested_photos:
        photos_parts = ["### 📸 Ask the seller for these photos\n"]
        for i, photo in enumerate(report.requested_photos, 1):
            photos_parts.append(f"**{i}.** {photo}")
        photos_md = "\n".join(photos_parts)

    title_note = f"*Listing: {scraped_title}*\n\n" if scraped_title else ""
    details_md = title_note + "\n".join(details_parts)

    status = f"✅ Done — {len(image_sources)} image(s) analysed"
    return verdict_html, details_md, photos_md, status


def _verdict_html(label: str, subtitle: str, fg: str, bg: str) -> str:
    return f"""
<div style="
    background:{bg};
    border:2px solid {fg};
    border-radius:12px;
    padding:20px 24px;
    font-family:sans-serif;
">
  <div style="font-size:2rem;font-weight:800;color:{fg};letter-spacing:-0.5px">{label}</div>
  <div style="font-size:0.95rem;color:#444;margin-top:6px">{subtitle}</div>
</div>
"""


# ── Build UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="The Garm Alarm",
    theme=gr.themes.Default(
        primary_hue="slate",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    ),
    css="""
        .gradio-container { max-width: 860px !important; margin: auto; }
        footer { display: none !important; }
    """,
) as demo:

    gr.Markdown(
        """
# 🚨 The Garm Alarm
### AI-powered legit checker for Vinted, Depop & eBay
Paste a listing URL or upload images. Detects DHGate fakes using Claude Vision.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            listing_url = gr.Textbox(
                label="Listing URL",
                placeholder="https://www.vinted.co.uk/items/12345  or  depop.com/...  or  ebay.co.uk/...",
                lines=1,
            )
        with gr.Column(scale=1):
            brand_choice = gr.Dropdown(
                label="Brand",
                choices=_BRAND_CHOICES,
                value="Auto-detect from images",
            )

    with gr.Row():
        uploaded_images = gr.File(
            label="Or upload images directly (alternative to URL)",
            file_count="multiple",
            file_types=["image"],
        )

    with gr.Row():
        price_input = gr.Textbox(
            label="Asking price (£)",
            placeholder="e.g. 45.00",
            scale=1,
        )
        check_btn = gr.Button("🔍 Run Legit Check", variant="primary", scale=2)

    status_bar = gr.Textbox(label="Status", interactive=False, max_lines=1)

    verdict_out = gr.HTML(label="Verdict")

    with gr.Row():
        with gr.Column():
            details_out = gr.Markdown(label="Findings")
        with gr.Column():
            photos_out = gr.Markdown(label="Photos to request")

    gr.Markdown(
        """
---
**Supported brands:** Stone Island · CP Company · Moncler · Canada Goose · Supreme ·
Trapstar · Corteiz · Nike/Jordan · Adidas/Yeezy · Ralph Lauren · North Face ·
Salomon · UGG · On Running · Adanola · New Balance

*Powered by [Claude](https://anthropic.com). Not a substitute for expert authentication.*
        """,
        elem_id="footer-note",
    )

    check_btn.click(
        fn=run_check,
        inputs=[listing_url, uploaded_images, brand_choice, price_input],
        outputs=[verdict_out, details_out, photos_out, status_bar],
    )

    listing_url.submit(
        fn=run_check,
        inputs=[listing_url, uploaded_images, brand_choice, price_input],
        outputs=[verdict_out, details_out, photos_out, status_bar],
    )


if __name__ == "__main__":
    demo.launch()
