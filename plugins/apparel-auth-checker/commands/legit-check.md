---
description: AI-powered authenticity check on an apparel listing from Vinted, Depop, or eBay
argument-hint: "<listing_url_or_image> [--brand BRAND] [--price PRICE] [--output text|json]"
---

Run an AI-powered legit check on an apparel listing using Claude Vision.

**Usage:**

```
/legit-check <listing_url>
/legit-check <listing_url> --brand stone_island --price 28
/legit-check image1.jpg image2.jpg --brand moncler
```

**What it does:**
1. If given a Vinted/Depop/eBay URL, automatically extracts all listing images
2. Sends images to Claude Vision with brand-specific authentication knowledge
3. Returns a verdict: AUTHENTIC / SUSPICIOUS / LIKELY FAKE with confidence %
4. Lists specific findings and photos to request from the seller

**Requirements:** `ANTHROPIC_API_KEY` must be set in your environment.

**Setup (first time):**
```bash
cd $CLAUDE_PLUGIN_ROOT
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

Please run the legit check with the following command and display the full output:

```bash
cd "$CLAUDE_PLUGIN_ROOT" && python3 checker.py $ARGUMENTS
```

If the command fails because dependencies are not installed, run:
```bash
cd "$CLAUDE_PLUGIN_ROOT" && pip install -r requirements.txt --quiet && python3 checker.py $ARGUMENTS
```

Display the output exactly as returned. If the verdict is LIKELY FAKE or SUSPICIOUS, suggest the user ask the seller for the specific photos listed in the "REQUEST THESE PHOTOS FROM SELLER" section.
