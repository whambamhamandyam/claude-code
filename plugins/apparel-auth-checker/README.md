# Apparel Authenticity Checker

AI-powered legit check for apparel on Vinted, Depop, and eBay. Paste a listing URL and get an instant authenticity verdict powered by Claude Vision.

DHGate and AliExpress replica products have flooded UK secondary market platforms. This tool uses Claude's vision capabilities with brand-specific authentication knowledge to identify fakes.

## Quick Start

```bash
# Install dependencies
cd plugins/apparel-auth-checker
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Check a listing URL
python3 checker.py https://www.vinted.co.uk/items/12345

# With brand and price hints
python3 checker.py https://www.vinted.co.uk/items/12345 --brand stone_island --price 28
```

## Usage

```
python3 checker.py URL_OR_IMAGE [URL_OR_IMAGE ...] [OPTIONS]

positional arguments:
  URL_OR_IMAGE    Vinted/Depop/eBay listing URL, image URL(s), or local file path(s)

options:
  --brand BRAND   Brand hint for targeted analysis (see supported brands below)
  --price GBP     Asking price in GBP (auto-extracted from listing URL if available)
  --output FORMAT Output format: text (default) or json
  --model MODEL   Claude model (default: claude-opus-4-6)
  --api-key KEY   Anthropic API key (overrides ANTHROPIC_API_KEY env var)
```

### Examples

```bash
# Vinted listing — auto-scrapes all photos
python3 checker.py https://www.vinted.co.uk/items/12345

# Depop with brand hint
python3 checker.py https://www.depop.com/products/username-item --brand moncler

# eBay with price
python3 checker.py https://www.ebay.co.uk/itm/123456789 --brand canada_goose --price 85

# Direct image files (e.g. photos sent by seller over DM)
python3 checker.py front.jpg tag.jpg badge_close.jpg --brand stone_island --price 45

# JSON output for scripting
python3 checker.py https://www.vinted.co.uk/items/12345 --output json | jq .verdict
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | AUTHENTIC |
| `1`  | SUSPICIOUS |
| `2`  | LIKELY FAKE |
| `3`  | Error |

Useful for shell scripting:
```bash
python3 checker.py "$URL" && echo "Looks good" || echo "Be careful"
```

## Supported Brands

| Brand | `--brand` value |
|-------|-----------------|
| Stone Island | `stone_island` |
| CP Company | `cp_company` |
| Moncler | `moncler` |
| Canada Goose | `canada_goose` |
| Supreme | `supreme` |
| Trapstar | `trapstar` |
| Corteiz | `corteiz` |
| Nike / Jordan | `nike_jordan` |
| Adidas / Yeezy | `adidas_yeezy` |
| Ralph Lauren | `ralph_lauren` |
| The North Face | `north_face` |
| Salomon | `salomon` |
| UGG | `ugg` |
| On Running | `on_running` |
| Adanola | `adanola` |
| New Balance | `new_balance` |

If `--brand` is omitted, Claude auto-detects the brand from the images.

## Sample Output

```
+==============================================================+
|         VERDICT: LIKELY FAKE   |   Confidence: 82%          |
+==============================================================+

  Brand: Stone Island   Images analysed: 4   Platform: Vinted
  Asking price: £28.00
  ⚠  Price £28.00 is 69% below market minimum (£80) for genuine Stone Island

POSITIVE INDICATORS:
  + Overall garment construction appears well-made
  + Colourway matches known genuine product

NEGATIVE INDICATORS:
  ✗ Badge compass rose appears flat printed, not embroidered
  ✗ "STONE ISLAND" text on badge uses incorrect font weight (too bold)
  ✗ Zip pull is unbranded generic (genuine items use Lampo or YKK)

REQUEST THESE PHOTOS FROM SELLER:
  1. Close-up macro of badge front (compass rose centred)
  2. Badge reverse showing stitching/attachment method
  3. Full interior label including wash care symbols
  4. Zip pull close-up

FULL ANALYSIS:
  The badge in image 1 shows a flat printed compass rose rather than
  the raised tactile embroidery present on genuine Stone Island pieces.
  The "STONE ISLAND" text weight is noticeably heavier than authentic
  examples. Combined with generic zip pulls and a price 69% below the
  minimum typical resale value, this listing displays multiple indicators
  consistent with a DHGate replica.
```

## Testing the Scraper

Test image extraction without using the API:

```bash
python3 -m core.listing_scraper https://www.vinted.co.uk/items/12345
```

## Platform Notes

- **Vinted**: Scrapes `__NEXT_DATA__` JSON embedded in page source
- **Depop**: Parses `application/ld+json` structured data
- **eBay**: Parses Open Graph image tags and image carousel elements
- **Fallback**: All platforms fall back to `og:image` meta tags

If a platform changes its page structure, scraping may fail. In that case, download the listing images manually and pass them as file paths.

## How It Works

1. The listing URL is fetched and images are extracted
2. All images are sent to Claude Vision in a single API call (holistic analysis)
3. The system prompt injects brand-specific authentication knowledge:
   - Exact fake tells known for DHGate replicas of that brand
   - Authentication points (badge, labels, hardware, materials)
   - Market price context
4. Claude returns a structured JSON verdict
5. The verdict is formatted and displayed with actionable next steps
