"""Brand-specific authentication knowledge base for the apparel legit checker."""

from dataclasses import dataclass, field


@dataclass
class AuthenticationPoint:
    feature: str
    what_to_look_for: str
    common_fake_tells: list[str]
    photo_angles_needed: list[str]


@dataclass
class BrandProfile:
    name: str
    normalized_name: str
    resale_price_range: tuple[float, float]  # GBP typical legitimate secondary market
    suspicious_low_price: float              # Below this = red flag
    authentication_points: list[AuthenticationPoint]
    reference_description: str               # Injected verbatim into AI prompt


BRAND_PROFILES: dict[str, BrandProfile] = {
    "stone_island": BrandProfile(
        name="Stone Island",
        normalized_name="stone_island",
        resale_price_range=(80, 400),
        suspicious_low_price=35,
        reference_description=(
            "Stone Island is an Italian premium sportswear brand. Their garments are "
            "characterised by a detachable compass rose badge (patch) on the left arm. "
            "The badge uses raised embroidery (not flat print), specific font kerning on "
            "'STONE ISLAND' text around the perimeter, and a compass rose with a needle "
            "in a specific colourway. Zips are branded Lampo or YKK with a Stone Island "
            "pull. Garment tags use a specific font and SKU format starting with numbers "
            "like 7515XXXXXX. Ghost pieces have inner branded linings."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Compass rose badge",
                what_to_look_for="Raised tactile embroidery with depth, accurate compass needle colours, crisp 'STONE ISLAND' text with correct font weight around perimeter",
                common_fake_tells=[
                    "Flat printed badge instead of embroidery",
                    "'STONE ISLAND' text too bold or wrong font",
                    "Compass needle colours inaccurate",
                    "Badge backing fabric wrong colour",
                    "Badge feels plastic/stiff rather than fabric",
                ],
                photo_angles_needed=["Close-up macro of badge front", "Badge from 45 degrees to show texture depth", "Badge reverse showing stitching attachment"],
            ),
            AuthenticationPoint(
                feature="Zip pulls",
                what_to_look_for="Branded Lampo or YKK zips with Stone Island branded pull tab",
                common_fake_tells=["Generic unbranded zip pulls", "Wrong font on branded pulls"],
                photo_angles_needed=["Close-up of main zip pull", "Interior zip tag if present"],
            ),
            AuthenticationPoint(
                feature="Garment label",
                what_to_look_for="Specific font, correct spacing, SKU format (e.g. 7515XXXXXX), Italian or other correct country of manufacture",
                common_fake_tells=["Wrong font on label", "Missing SKU or incorrect format", "Poor print quality on label"],
                photo_angles_needed=["Full interior label including wash care symbols", "Close-up of SKU number"],
            ),
        ],
    ),

    "cp_company": BrandProfile(
        name="CP Company",
        normalized_name="cp_company",
        resale_price_range=(60, 350),
        suspicious_low_price=40,
        reference_description=(
            "CP Company is an Italian luxury sportswear brand known for their goggle "
            "lens accessories integrated into jackets and bags. The lens badge should "
            "be a functional tinted lens (not a plastic imitation). The Metropolis label "
            "and care labels use specific fonts. Serial number labels follow a specific format. "
            "Arm lens pockets are carefully constructed with functional hardware."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Goggle lens badge/accessory",
                what_to_look_for="Functional tinted lens that actually magnifies/filters, quality metal hardware, smooth movement",
                common_fake_tells=[
                    "Plastic non-functional lens imitation",
                    "Lens doesn't tint/filter correctly",
                    "Cheap metal hardware",
                    "Lens integrated awkwardly or asymmetrically",
                ],
                photo_angles_needed=["Goggle lens front", "Goggle lens from side showing depth", "Hardware close-up"],
            ),
            AuthenticationPoint(
                feature="Interior Metropolis label",
                what_to_look_for="Specific CP Company font, correct serial number format, quality print",
                common_fake_tells=["Wrong font", "Serial number format incorrect", "Label quality poor"],
                photo_angles_needed=["Full interior label", "Serial number close-up"],
            ),
        ],
    ),

    "moncler": BrandProfile(
        name="Moncler",
        normalized_name="moncler",
        resale_price_range=(120, 1200),
        suspicious_low_price=80,
        reference_description=(
            "Moncler is a French-Italian luxury down jacket brand. Key authentication "
            "points include the holographic badge on the zip which should show a rainbow "
            "colour shift when tilted, crisp text, and a specific duck logo. Post-2018 "
            "garments have a QR code on the interior label. Zip pulls are branded Moncler "
            "and should not be generic. The chest badge shows a yellow duck with specific "
            "embroidery quality."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Holographic zip badge",
                what_to_look_for="Clear rainbow iridescent colour shift when tilted, crisp 'MONCLER' text, duck logo clearly defined",
                common_fake_tells=[
                    "No colour shift or weak rainbow effect",
                    "Blurry or pixelated text on hologram",
                    "Duck logo poorly defined",
                    "Badge feels cheap or peels at edges",
                ],
                photo_angles_needed=["Hologram badge straight on", "Hologram badge tilted to show colour shift", "Close-up of text on badge"],
            ),
            AuthenticationPoint(
                feature="Interior QR label (2018+ garments)",
                what_to_look_for="Scannable QR code on interior label, code should resolve to Moncler authentication page",
                common_fake_tells=["QR code doesn't scan", "QR code resolves to wrong page", "Label absent on recent piece"],
                photo_angles_needed=["Full interior label showing QR code", "Close-up of QR code"],
            ),
            AuthenticationPoint(
                feature="Branded zip pulls",
                what_to_look_for="Moncler-branded zip pulls, quality metal, correct font on branding",
                common_fake_tells=["Generic unbranded zip pulls", "Cheap-feeling metal"],
                photo_angles_needed=["Zip pull close-up"],
            ),
        ],
    ),

    "canada_goose": BrandProfile(
        name="Canada Goose",
        normalized_name="canada_goose",
        resale_price_range=(150, 900),
        suspicious_low_price=100,
        reference_description=(
            "Canada Goose is a Canadian luxury outerwear brand. Key authentication "
            "features include the arm patch which should be a hologram showing a colour "
            "shift (on newer models), the fur ruff label indicating real vs synthetic fur, "
            "the interior disc badge with serial number, and specific label formats. "
            "The iconic arm patch should not look flat-printed."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Arm hologram patch",
                what_to_look_for="Colour shift when tilted, 'Canada Goose' text crisp, polar bear and maple leaf graphics clear",
                common_fake_tells=[
                    "No colour shift (flat print)",
                    "Blurry graphics or text",
                    "Patch sewn on incorrectly or asymmetrically",
                ],
                photo_angles_needed=["Arm patch straight on", "Arm patch tilted to show any hologram effect"],
            ),
            AuthenticationPoint(
                feature="Interior disc badge and labels",
                what_to_look_for="Serial number disc badge, specific label font, country of manufacture (Canada for most models)",
                common_fake_tells=["Missing disc badge", "Wrong font on labels", "Incorrect country of manufacture"],
                photo_angles_needed=["Interior disc badge", "Main interior label"],
            ),
        ],
    ),

    "supreme": BrandProfile(
        name="Supreme",
        normalized_name="supreme",
        resale_price_range=(50, 2000),
        suspicious_low_price=30,
        reference_description=(
            "Supreme is a New York skateboarding and streetwear brand. The iconic box "
            "logo uses Futura Heavy Oblique font with specific proportions — the 'S' width, "
            "letter spacing, and red box dimensions are all precise. Tags use specific fonts "
            "and the country of manufacture label (usually USA for box logo tees) is a key "
            "check. Stitching on labels should be clean."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Box logo font and proportions",
                what_to_look_for="Futura Heavy Oblique font, correct letter spacing, correct red box dimensions, white text on red",
                common_fake_tells=[
                    "Wrong font (too thin, too thick, or wrong style)",
                    "Incorrect letter spacing",
                    "Red box wrong dimensions",
                    "Text alignment off",
                ],
                photo_angles_needed=["Full box logo front", "Close-up of text on logo"],
            ),
            AuthenticationPoint(
                feature="Interior tag",
                what_to_look_for="Correct Supreme font on tags, country of manufacture correct for the season/item",
                common_fake_tells=["Wrong font on tags", "Wrong country of manufacture"],
                photo_angles_needed=["Full interior tag", "Country of manufacture label"],
            ),
        ],
    ),

    "trapstar": BrandProfile(
        name="Trapstar",
        normalized_name="trapstar",
        resale_price_range=(40, 200),
        suspicious_low_price=25,
        reference_description=(
            "Trapstar is a UK streetwear brand founded in London. Authentication focuses "
            "on woven labels (not heat-transfer on premium pieces), correct font on chest "
            "branding (the 'Trapstar' script), quality of embroidery on logo pieces, and "
            "interior care labels. DHGate fakes often use incorrect font and heat-transfer "
            "labels instead of woven or embroidered labels."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Chest/logo branding",
                what_to_look_for="Correct Trapstar font/script, quality embroidery or print, correct placement",
                common_fake_tells=[
                    "Incorrect font weight or style",
                    "Heat-transfer label where original is embroidered",
                    "Branding placement off-centre",
                    "Print quality poor (cracking, peeling)",
                ],
                photo_angles_needed=["Full chest logo", "Close-up of font details", "Label type (woven vs heat-transfer)"],
            ),
            AuthenticationPoint(
                feature="Interior care/brand label",
                what_to_look_for="Woven label with correct Trapstar branding, correct font, quality stitching",
                common_fake_tells=["Heat-transfer interior label", "Wrong font", "Label poorly attached"],
                photo_angles_needed=["Interior label close-up"],
            ),
        ],
    ),

    "corteiz": BrandProfile(
        name="Corteiz",
        normalized_name="corteiz",
        resale_price_range=(60, 400),
        suspicious_low_price=40,
        reference_description=(
            "Corteiz (CRTZ) is a UK streetwear brand. Key authentication points include "
            "the Alcatraz logo accuracy, correct RTW (Rules The World) label placement, "
            "woven labels with correct font, and specific hang tag details. Corteiz drops "
            "are highly limited so fakes are common. DHGate fakes often have incorrect "
            "logo proportions and wrong label details."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Alcatraz logo / CRTZ branding",
                what_to_look_for="Correct logo proportions, accurate Alcatraz island graphic, correct font on 'CORTEIZ' or 'CRTZ'",
                common_fake_tells=[
                    "Alcatraz graphic proportions wrong",
                    "Font incorrect on branding",
                    "Logo placement incorrect",
                ],
                photo_angles_needed=["Full logo front", "Close-up of logo details"],
            ),
            AuthenticationPoint(
                feature="Woven label / hang tag",
                what_to_look_for="Woven label with correct branding, specific hang tag design for the season",
                common_fake_tells=["Heat-transfer label", "Wrong hang tag design", "Font incorrect on labels"],
                photo_angles_needed=["Interior woven label", "Hang tag (if present)"],
            ),
        ],
    ),

    "nike_jordan": BrandProfile(
        name="Nike / Jordan",
        normalized_name="nike_jordan",
        resale_price_range=(30, 500),
        suspicious_low_price=25,
        reference_description=(
            "Nike and Jordan Brand are US sportswear giants. Swoosh proportions are exact "
            "on genuine items. Jordan Jumpman logo has specific proportions. Tags use "
            "specific fonts with correct spacing. Heel tabs on Jordan 1s have specific "
            "stitching patterns. Sole units have accurate branding. Air units should be "
            "visible where appropriate."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Swoosh / Jumpman logo proportions",
                what_to_look_for="Correct proportions for the specific model, accurate curve on Swoosh, Jumpman in correct pose",
                common_fake_tells=[
                    "Swoosh too fat or too thin",
                    "Jumpman proportions wrong (legs, arms)",
                    "Logo placement incorrect",
                ],
                photo_angles_needed=["Side profile of shoe", "Close-up of logo"],
            ),
            AuthenticationPoint(
                feature="Interior/tongue tag",
                what_to_look_for="Correct Nike/Jordan font, correct sizing and colourway information, correct country of manufacture",
                common_fake_tells=["Wrong font on tags", "Incorrect colourway name", "Low print quality"],
                photo_angles_needed=["Tongue tag", "Interior size label"],
            ),
            AuthenticationPoint(
                feature="Heel tab stitching (Jordan 1)",
                what_to_look_for="Clean stitching on heel tab, correct number of stitches per inch, tab sits correctly",
                common_fake_tells=["Messy or uneven stitching", "Heel tab angle incorrect"],
                photo_angles_needed=["Heel tab close-up", "Heel stitching detail"],
            ),
        ],
    ),

    "adidas_yeezy": BrandProfile(
        name="Adidas / Yeezy",
        normalized_name="adidas_yeezy",
        resale_price_range=(80, 1500),
        suspicious_low_price=40,
        reference_description=(
            "Adidas Yeezy is a collaboration between Adidas and Kanye West. The Boost "
            "sole unit is a key authentication point — real Boost pellets are irregular "
            "and organic-looking, fakes often have too-uniform pellets. The knit upper "
            "pattern is very specific per colourway. Tags follow specific formats. "
            "Three stripes on Adidas items must have correct proportions."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Boost sole pellets",
                what_to_look_for="Irregular, organic-looking pellet shapes, correct colour for the model, right pellet density",
                common_fake_tells=[
                    "Too uniform/identical pellets",
                    "Pellets too large or too small",
                    "Wrong colour on sole unit",
                    "Sole feels too hard or too soft",
                ],
                photo_angles_needed=["Sole unit macro shot", "Heel boost close-up", "Side profile"],
            ),
            AuthenticationPoint(
                feature="Knit pattern (for Yeezy 350/380 etc)",
                what_to_look_for="Correct knit pattern specific to the colourway, accurate stripe placement on Zebra/Beluga etc",
                common_fake_tells=["Pattern repeats at wrong interval", "Stripes too thick or thin for the specific colourway"],
                photo_angles_needed=["Upper close-up showing knit detail", "Side profile of full shoe"],
            ),
        ],
    ),

    "ralph_lauren": BrandProfile(
        name="Ralph Lauren",
        normalized_name="ralph_lauren",
        resale_price_range=(20, 300),
        suspicious_low_price=15,
        reference_description=(
            "Ralph Lauren (Polo Ralph Lauren) is known for the Polo pony embroidery. "
            "The rider's proportions relative to the horse are specific — the rider should "
            "not look too large or too small. The polo mallet angle is consistent. "
            "Tags use specific fonts. Button quality should be high on shirts (genuine "
            "often uses mother-of-pearl or quality resin). Fabric quality is notable."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Polo pony embroidery",
                what_to_look_for="Correct rider-to-horse proportions, polo mallet at correct angle, detailed embroidery with no loose threads",
                common_fake_tells=[
                    "Rider too large relative to horse",
                    "Polo mallet angle wrong",
                    "Embroidery looks flat or pixelated",
                    "Loose or snagged threads",
                    "Wrong placement on garment",
                ],
                photo_angles_needed=["Polo pony embroidery straight on", "Close-up of embroidery detail"],
            ),
            AuthenticationPoint(
                feature="Interior label and font",
                what_to_look_for="Correct Ralph Lauren font, correct country of manufacture, specific label design",
                common_fake_tells=["Wrong font on label", "Incorrect country of manufacture", "Label quality poor"],
                photo_angles_needed=["Interior label", "Wash care label"],
            ),
        ],
    ),

    "north_face": BrandProfile(
        name="The North Face",
        normalized_name="north_face",
        resale_price_range=(30, 300),
        suspicious_low_price=20,
        reference_description=(
            "The North Face is a US outdoor brand. The half-dome logo has specific "
            "proportions. Tags use specific fonts and include specific technical details "
            "about fabric technology (HyVent, GORE-TEX etc). Zip quality should be "
            "YKK branded. Stitching throughout should be consistent and tight."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Half-dome logo",
                what_to_look_for="Correct half-dome proportions, correct font on 'THE NORTH FACE' text, accurate logo placement",
                common_fake_tells=["Half-dome wrong shape", "Font incorrect", "Logo print quality poor"],
                photo_angles_needed=["Front logo close-up"],
            ),
            AuthenticationPoint(
                feature="Tags and technical labelling",
                what_to_look_for="YKK zips, correct fabric technology labels (GORE-TEX, HyVent etc), correct font on all labels",
                common_fake_tells=["Generic non-YKK zips", "Fabric technology labels missing or incorrect"],
                photo_angles_needed=["Main interior label", "Zip pull close-up", "Technical fabric label if present"],
            ),
        ],
    ),

    "salomon": BrandProfile(
        name="Salomon",
        normalized_name="salomon",
        resale_price_range=(40, 200),
        suspicious_low_price=35,
        reference_description=(
            "Salomon is a French outdoor and trail running brand. The 'S' logo has specific "
            "proportions and the 'Salomon' wordmark uses a specific font. The Contagrip sole "
            "unit has a distinctive lug pattern. The tongue label format is specific. "
            "The Quicklace system on running models has a specific mechanism."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="'S' logo and wordmark",
                what_to_look_for="Correct 'S' proportions, correct Salomon font on wordmark, accurate logo placement on tongue/side",
                common_fake_tells=["'S' logo proportions wrong", "Wordmark font incorrect", "Logo quality poor"],
                photo_angles_needed=["Side logo close-up", "Tongue label"],
            ),
            AuthenticationPoint(
                feature="Sole unit (Contagrip)",
                what_to_look_for="Correct lug pattern for the specific model, accurate colourway on sole, Salomon branding on sole",
                common_fake_tells=["Lug pattern doesn't match model", "Sole branding missing or incorrect"],
                photo_angles_needed=["Sole flat lay", "Side profile of sole"],
            ),
        ],
    ),

    "ugg": BrandProfile(
        name="UGG",
        normalized_name="ugg",
        resale_price_range=(30, 200),
        suspicious_low_price=25,
        reference_description=(
            "UGG is an American sheepskin boot brand. Genuine UGGs have the UGG oval "
            "logo on the heel with specific font. The suede texture is a natural sheepskin "
            "which has a natural grain variation — fakes often use uniform synthetic suede. "
            "The inner sole features 'UGG' branding with specific font. The fleece lining "
            "should look natural and fluffy, not synthetic."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="UGG oval heel logo",
                what_to_look_for="Oval UGG logo on heel, correct font, correct proportions, quality embroidery or label",
                common_fake_tells=["Font incorrect on heel logo", "Logo proportions wrong", "Label quality poor"],
                photo_angles_needed=["Heel logo close-up"],
            ),
            AuthenticationPoint(
                feature="Suede texture and sheepskin",
                what_to_look_for="Natural variation in suede grain, natural fluffy sheepskin lining, suede feels like genuine leather",
                common_fake_tells=["Too uniform suede texture (synthetic)", "Lining looks synthetic/plastic", "Suede too stiff"],
                photo_angles_needed=["Suede surface macro shot", "Interior fleece lining", "Side profile"],
            ),
        ],
    ),

    "on_running": BrandProfile(
        name="On Running",
        normalized_name="on_running",
        resale_price_range=(50, 200),
        suspicious_low_price=40,
        reference_description=(
            "On Running is a Swiss performance running brand. The CloudTec sole pods are "
            "the most distinctive feature — each pod has a hollow channel and specific "
            "shape per model. The 'On' logo uses a specific font. The tongue label format "
            "is specific. Fakes often get the CloudTec pod shape wrong."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="CloudTec sole pods",
                what_to_look_for="Correct pod shape for the specific model, hollow channel visible from side, correct pod count and arrangement",
                common_fake_tells=[
                    "Pod shapes too uniform or wrong shape",
                    "Hollow channel not visible or poorly defined",
                    "Wrong number or arrangement of pods",
                ],
                photo_angles_needed=["Sole flat lay", "Side profile showing pod channels", "Heel sole close-up"],
            ),
            AuthenticationPoint(
                feature="'On' logo and tongue label",
                what_to_look_for="Correct 'On' font and logo mark, correct tongue label format with model name and size",
                common_fake_tells=["Logo font incorrect", "Tongue label format wrong"],
                photo_angles_needed=["Side logo close-up", "Tongue label"],
            ),
        ],
    ),

    "adanola": BrandProfile(
        name="Adanola",
        normalized_name="adanola",
        resale_price_range=(15, 80),
        suspicious_low_price=10,
        reference_description=(
            "Adanola is a UK activewear brand. Authentication focuses on the woven label "
            "with correct Adanola font, fabric quality (smooth, quality jersey/lycra), "
            "and branding placement. Fakes may use incorrect font on labels or poor-quality "
            "synthetic fabric instead of the brand's signature material."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="Woven brand label",
                what_to_look_for="Woven 'Adanola' label with correct font, quality stitching attachment, correct placement",
                common_fake_tells=["Heat-transfer label instead of woven", "Wrong font", "Label poorly attached"],
                photo_angles_needed=["Interior label close-up"],
            ),
            AuthenticationPoint(
                feature="Fabric quality",
                what_to_look_for="Smooth, quality jersey or ribbed fabric appropriate to the item, correct weight and opacity",
                common_fake_tells=["Fabric feels cheap or synthetic", "Wrong texture for the item type"],
                photo_angles_needed=["Fabric close-up showing texture"],
            ),
        ],
    ),

    "new_balance": BrandProfile(
        name="New Balance",
        normalized_name="new_balance",
        resale_price_range=(30, 300),
        suspicious_low_price=25,
        reference_description=(
            "New Balance is a US athletic brand. The 'N' logo has specific proportions "
            "per model — the stroke width and angle are precise. Made in USA/UK models "
            "are highly sought after and faked; the country of manufacture label is key. "
            "The sole unit branding and cushioning technology markings should be correct "
            "for the specific model number."
        ),
        authentication_points=[
            AuthenticationPoint(
                feature="'N' logo proportions",
                what_to_look_for="Correct stroke width for the specific model, correct 'N' angle, accurate logo size relative to shoe",
                common_fake_tells=["'N' logo stroke too thin or thick", "Wrong 'N' angle or proportion", "Logo too large or small"],
                photo_angles_needed=["Side profile logo close-up"],
            ),
            AuthenticationPoint(
                feature="Country of manufacture label",
                what_to_look_for="'Made in USA' or 'Made in UK' for premium models, correct label format",
                common_fake_tells=["Wrong country of manufacture on premium models", "Label format incorrect"],
                photo_angles_needed=["Tongue label full shot", "Interior size/country label"],
            ),
        ],
    ),
}


def get_profile(brand_hint: str | None) -> BrandProfile | None:
    """Fuzzy-match a brand name hint to a profile. Returns None if not found."""
    if not brand_hint:
        return None

    normalised = brand_hint.lower().strip().replace(" ", "_").replace("-", "_")

    # Direct match
    if normalised in BRAND_PROFILES:
        return BRAND_PROFILES[normalised]

    # Alias map for common shorthand
    aliases: dict[str, str] = {
        "si": "stone_island",
        "stone": "stone_island",
        "cp": "cp_company",
        "cp_co": "cp_company",
        "goose": "canada_goose",
        "cg": "canada_goose",
        "sup": "supreme",
        "trap": "trapstar",
        "crtz": "corteiz",
        "nike": "nike_jordan",
        "jordan": "nike_jordan",
        "aj": "nike_jordan",
        "yeezy": "adidas_yeezy",
        "adidas": "adidas_yeezy",
        "polo": "ralph_lauren",
        "rl": "ralph_lauren",
        "tnf": "north_face",
        "north_face": "north_face",
        "on": "on_running",
        "nb": "new_balance",
        "uggs": "ugg",
    }

    if normalised in aliases:
        return BRAND_PROFILES[aliases[normalised]]

    # Substring search
    for key, profile in BRAND_PROFILES.items():
        if normalised in key or key in normalised:
            return profile
        if normalised in profile.name.lower():
            return profile

    return None


def list_brand_names() -> list[str]:
    """Return all available normalised brand names."""
    return list(BRAND_PROFILES.keys())
