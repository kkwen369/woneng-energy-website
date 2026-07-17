# -*- coding: utf-8 -*-
"""Generate scraped_products.py from product_scrape.json.

Each of the 43 SKU-level pages from entelechyenergy.com becomes a product dict
using the SAME schema as data.py PRODUCTS, plus featured=False / scraped=True.
Series are grouped so each page gets real, distinct specs; the intro embeds the
specific model name to keep pages content-distinct (duplicate-content mitigation).
"""
import json, os, re

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "..", "product_scrape.json")
# product_scrape.json lives at D:/网站/product_scrape.json
SRC = "D:/网站/product_scrape.json"

with open(SRC, encoding="utf-8") as f:
    RAW = json.load(f)

# ---------------- SERIES DEFINITIONS ----------------
# Each series: cat, cat_name, tagline, intro(name), advantages[(t,d)...], specs[(k,v)...], applications[...]

SERIES = {
    "flood_f05": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="High-power IP66 solar floodlight, 50W–400W.",
        intro=lambda n: (
            f"The {n} is a high-power, IP66-rated solar flood light built for large-area outdoor "
            f"coverage. An upgraded SMD3030 chip set, detachable housing for fast battery swap and a "
            f"built-in charge indicator deliver reliable 120° wide-beam illumination through rain, dust "
            f"and intense sun. Part of Woneng's F05 series (50W–400W) for distributors, EPC contractors "
            f"and project buyers worldwide."
        ),
        advantages=[
            ("IP66 waterproof", "Built for heavy rain, dust and intense sun."),
            ("+20% brightness", "Upgraded SMD3030 chips vs. conventional fixtures."),
            ("High-transmission lens", "PC lens improves light transmission 15–20%."),
            ("6000+ cycles", "3-year full warranty."),
            ("Wide 120° beam", "Large-area coverage, multi control modes."),
        ],
        specs=[
            ("Power range", "50W – 400W (650–3800 lm)"),
            ("LED chips", "SMD3030, 600–828 pcs"),
            ("Battery", "LiFePO4 3.2V, 6000–42000 mAh, 6000 cycles"),
            ("Solar panel", "Monocrystalline 6V 12–50W"),
            ("Protection", "IP66"),
            ("Beam angle", "120°"),
            ("CCT", "3000–6500K"),
            ("Charge / light", "4–6h / 18–24h"),
            ("Working temp.", "-10°C ~ +65°C"),
            ("Warranty", "3 years"),
        ],
        applications=["Stadiums", "Squares", "Construction sites", "Warehouses", "Large outdoor areas"],
    ),
    "flood_rgb": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="Colour-capable RGB solar floodlight, 50W.",
        intro=lambda n: (
            f"The {n} brings colour-capable solar illumination to your project with SMD RGB LED chips "
            f"and a Class A LiFePO4 battery. A high-conversion solar panel keeps it running autonomously — "
            f"ideal for festive, landscape and commercial façade lighting where brand owners and "
            f"distributors need custom-tailored solutions."
        ),
        advantages=[
            ("RGB chips", "SMD3030 / SMD5050 RGB for full-colour output."),
            ("Class A LiFePO4", "Long-life, safe, deep-cycle battery."),
            ("High-conversion panel", "Fast, reliable solar recharge."),
            ("Custom OEM/ODM", "Tailored for brand owners & distributors."),
            ("All-weather", "Built for outdoor duty cycles."),
        ],
        specs=[
            ("Power", "50W RGB"),
            ("LED chips", "SMD3030 / SMD5050 RGB"),
            ("Battery", "Class A LiFePO4"),
            ("Solar panel", "High-conversion monocrystalline"),
            ("Control", "Multi-colour / mode remote"),
            ("Service", "Custom-tailored OEM/ODM"),
        ],
        applications=["Festive lighting", "Landscape", "Commercial façades", "Events", "Brand venues"],
    ),
    "aio_s03": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="All-in-one solar street light, S03 series.",
        intro=lambda n: (
            f"The {n} is an all-in-one solar street light integrating lamp, LiFePO4 battery, solar panel "
            f"and smart controller in a single corrosion-resistant unit. A built-in new LiFePO4 battery "
            f"(2000+ charge cycles), high-brightness 180 lm/W LED chips and intelligent brightness control "
            f"make it a low-maintenance choice for municipal and rural roads, backed by a 3–5 year warranty."
        ),
        advantages=[
            ("New LiFePO4", "2000+ charge cycles, long service life."),
            ("180 lm/W LEDs", "High-brightness, energy-efficient chips."),
            ("Intelligent control", "Auto dimming to save power."),
            ("All-in-one", "Tool-free install, no wiring."),
            ("3–5 yr warranty", "Backed by factory support."),
        ],
        specs=[
            ("LED chips", "High-brightness, 180 lm/W"),
            ("Battery", "New LiFePO4, 2000+ cycles"),
            ("Control", "Intelligent dimming"),
            ("Install", "Integrated, tool-free"),
            ("Warranty", "3–5 years"),
            ("Housing", "Corrosion-resistant"),
        ],
        applications=["Municipal roads", "Rural roads", "Residential parks", "Industrial parks", "Government projects"],
    ),
    "aio_s04": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="High-output all-in-one solar street light, S04 series.",
        intro=lambda n: (
            f"The {n} is a high-output all-in-one solar street light with built-in SMD3030 chips and a "
            f"brand-new LiFePO4 battery. Its corrosion-resistant housing offers excellent heat dissipation "
            f"and IP66 waterproofing, delivering stable all-night performance for roads, parks and "
            f"industrial sites."
        ),
        advantages=[
            ("SMD3030 chips", "High-efficacy, long-life LEDs."),
            ("Brand-new LiFePO4", "Safe, deep-cycle power."),
            ("IP66 waterproof", "Withstands harsh outdoor climate."),
            ("Heat dissipation", "Corrosion-resistant housing."),
            ("All-in-one", "Integrated, easy to deploy."),
        ],
        specs=[
            ("LED chips", "SMD3030"),
            ("Battery", "Brand-new LiFePO4"),
            ("Protection", "IP66"),
            ("Housing", "Corrosion-resistant, fast heat dissipation"),
            ("Type", "All-in-one integrated"),
        ],
        applications=["Municipal roads", "Parks", "Industrial sites", "Rural roads", "Government projects"],
    ),
    "aio_l08": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="High-capacity all-in-one solar street light, L08 series.",
        intro=lambda n: (
            f"The {n} is Woneng's high-capacity all-in-one solar street light featuring SMD5054 chips and a "
            f"brand-new LiFePO4 battery. Corrosion-resistant with excellent heat dissipation and IP65 "
            f"protection, it is engineered for large-area roads and high-demand municipal projects."
        ),
        advantages=[
            ("SMD5054 chips", "High-output, efficient LEDs."),
            ("Brand-new LiFePO4", "Long-life deep-cycle battery."),
            ("IP65 waterproof", "All-weather outdoor duty."),
            ("Heat dissipation", "Corrosion-resistant housing."),
            ("High capacity", "Built for large-area roads."),
        ],
        specs=[
            ("LED chips", "SMD5054"),
            ("Battery", "Brand-new LiFePO4"),
            ("Protection", "IP65"),
            ("Housing", "Corrosion-resistant, fast heat dissipation"),
            ("Type", "All-in-one high-capacity"),
        ],
        applications=["Large-area roads", "Municipal projects", "Industrial parks", "Highways", "Government projects"],
    ),
    "aio_l02": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="Compact all-in-one solar street light, L02 series.",
        intro=lambda n: (
            f"The {n} is a compact all-in-one solar street light using Korea Seoul SMD5730 chips at 160 lm/W. "
            f"With 12–15 nights of lighting on a single charge and a corrosion-resistant, fast "
            f"heat-dissipating body, it is ideal for residential streets, courtyards and small community roads."
        ),
        advantages=[
            ("Seoul SMD5730", "160 lm/W efficacy."),
            ("12–15 nights", "Long lighting on one charge."),
            ("Corrosion-resistant", "Excellent heat dissipation."),
            ("Compact", "Easy to install and maintain."),
            ("All-in-one", "Integrated design."),
        ],
        specs=[
            ("LED chips", "Korea Seoul SMD5730, 160 lm/W"),
            ("Lighting time", "12–15 nights"),
            ("Housing", "Corrosion-resistant, fast heat dissipation"),
            ("Type", "All-in-one compact"),
        ],
        applications=["Residential streets", "Courtyards", "Community roads", "Parks", "Pathways"],
    ),
    "ait_l04": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="Split / modular solar street light, L04 series.",
        intro=lambda n: (
            f"The {n} uses a split / modular solar street light design that separates the panel from the "
            f"lamp for flexible, shaded or angled installation. Super-bright lamp chips, a Class A LiFePO4 "
            f"battery, PWM / intelligent control and a high-conversion solar panel with all-in-one lens "
            f"design deliver stable, maintenance-friendly performance."
        ),
        advantages=[
            ("Flexible split design", "Panel & lamp installed independently."),
            ("Bright chips", "Super-bright lamp chip set."),
            ("Class A LiFePO4", "Safe, long-life battery."),
            ("PWM / intelligent", "Smart charge & control."),
            ("All-in-one lens", "High-conversion panel design."),
        ],
        specs=[
            ("LED", "Super-bright lamp chips"),
            ("Battery", "Class A LiFePO4"),
            ("Control", "PWM intelligent control"),
            ("Solar panel", "High-conversion, all-in-one lens"),
            ("Protection", "IP65"),
            ("Type", "Split / modular"),
        ],
        applications=["Mountain roads", "Courtyards", "Scenic trails", "Outdoor factories", "Projects"],
    ),
    "ait_l03": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="All-in-two (split) solar street light, L03 series.",
        intro=lambda n: (
            f"The {n} is an all-in-two (split) solar street light with built-in SMD3030 chips and a "
            f"brand-new LiFePO4 battery. Corrosion-resistant with excellent heat dissipation and IP66 "
            f"protection, it suits streets, parks and outdoor commercial sites needing flexible panel placement."
        ),
        advantages=[
            ("SMD3030 chips", "High-efficacy LEDs."),
            ("Brand-new LiFePO4", "Long-life deep-cycle battery."),
            ("IP66 waterproof", "All-weather outdoor duty."),
            ("Heat dissipation", "Corrosion-resistant housing."),
            ("Split design", "Flexible panel placement."),
        ],
        specs=[
            ("LED chips", "SMD3030"),
            ("Battery", "Brand-new LiFePO4"),
            ("Protection", "IP66"),
            ("Housing", "Corrosion-resistant, fast heat dissipation"),
            ("Type", "All-in-two (split)"),
        ],
        applications=["Streets", "Parks", "Outdoor commercial sites", "Rural roads", "Projects"],
    ),
    "garden_ggd": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Decorative solar garden light, GGD series.",
        intro=lambda n: (
            f"The {n} is a decorative solar garden light with a built-in LiFePO4 battery (10+ year life), "
            f"die-cast aluminium body and Class A high-conversion solar panel. 2835 LED beads deliver high "
            f"luminous efficiency (145 lm/W) under IP65 protection — perfect for parks, pathways, courtyards "
            f"and landscape projects."
        ),
        advantages=[
            ("LiFePO4 10+ yr", "Built-in long-life battery."),
            ("Die-cast aluminium", "Solid, anti-corrosion body."),
            ("Class A panel", "High solar conversion rate."),
            ("2835 LEDs", "145 lm/W high efficiency."),
            ("IP65 waterproof", "All-weather outdoor use."),
        ],
        specs=[
            ("Battery", "LiFePO4, 10+ year life"),
            ("Body", "Die-cast aluminium, anti-corrosion"),
            ("Solar panel", "Class A, high conversion"),
            ("LED", "2835 beads, 145 lm/W"),
            ("Protection", "IP65"),
        ],
        applications=["Parks", "Gardens", "Pathways", "Courtyards", "Landscape projects"],
    ),
    "garden_spotlight": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Solar garden spotlight, DCD series.",
        intro=lambda n: (
            f"The {n} is a solar garden spotlight with a die-cast aluminium body and Class A high-conversion "
            f"solar panel. SMD5050 LED beads provide high luminous efficiency with IP65 protection, ideal "
            f"for accenting trees, façades and landscape features."
        ),
        advantages=[
            ("Die-cast aluminium", "Solid, anti-corrosion body."),
            ("Class A panel", "High solar conversion rate."),
            ("SMD5050 LEDs", "High luminous efficiency."),
            ("IP65 waterproof", "All-weather outdoor use."),
            ("Accent lighting", "For trees & façades."),
        ],
        specs=[
            ("Body", "Die-cast aluminium, anti-corrosion"),
            ("Solar panel", "Class A, high conversion"),
            ("LED", "SMD5050, high efficiency"),
            ("Protection", "IP65"),
        ],
        applications=["Gardens", "Façades", "Trees", "Landscape features", "Hotels"],
    ),
    "ground_plug": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Solar ground plug-in light, DCD series.",
        intro=lambda n: (
            f"The {n} is a solar ground plug-in light with a die-cast aluminium body and Class A "
            f"high-conversion solar panel. 2835 LED beads deliver efficient, wire-free illumination for "
            f"lawns, paths and garden borders under IP65 protection."
        ),
        advantages=[
            ("Die-cast aluminium", "Solid, anti-corrosion body."),
            ("Class A panel", "High solar conversion rate."),
            ("2835 LEDs", "High luminous efficiency."),
            ("IP65 waterproof", "All-weather outdoor use."),
            ("Wire-free", "Plug-and-play install."),
        ],
        specs=[
            ("Body", "Die-cast aluminium, anti-corrosion"),
            ("Solar panel", "Class A, high conversion"),
            ("LED", "2835 beads, high efficiency"),
            ("Protection", "IP65"),
        ],
        applications=["Lawns", "Paths", "Garden borders", "Driveways", "Pathways"],
    ),
    "landscape_cpd": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Solar landscape lawn lamp, CPD series.",
        intro=lambda n: (
            f"The {n} is a solar landscape lawn lamp with a built-in LiFePO4 battery (10+ year life) and "
            f"die-cast aluminium + PC body. Class A solar panel and SMD LED beads (30–35 pcs) provide "
            f"efficient, IP65-rated lighting for lawns, paths and scenic areas."
        ),
        advantages=[
            ("LiFePO4 10+ yr", "Built-in long-life battery."),
            ("Aluminium + PC", "Solid, anti-corrosion body."),
            ("Class A panel", "High solar conversion rate."),
            ("SMD LEDs", "30–35 pcs, high efficiency."),
            ("IP65 waterproof", "All-weather outdoor use."),
        ],
        specs=[
            ("Battery", "LiFePO4, 10+ year life"),
            ("Body", "Die-cast aluminium + PC, anti-corrosion"),
            ("Solar panel", "Class A, high conversion"),
            ("LED", "30–35 pcs SMD, high efficiency"),
            ("Protection", "IP65"),
        ],
        applications=["Lawns", "Paths", "Scenic areas", "Parks", "Campuses"],
    ),
    "wall_swl": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Lens-integrated solar wall light, SWL series.",
        intro=lambda n: (
            f"The {n} is a lens-integrated solar wall light with a built-in lithium battery (up to 5-year "
            f"life) and multiple lighting modes. PIR motion sensing and IP65 protection make it suited to "
            f"building façades, courtyards, driveways and perimeter walls."
        ),
        advantages=[
            ("Lithium battery", "Up to 5-year life."),
            ("Multi modes", "4 different lighting modes."),
            ("PIR motion", "120° detection."),
            ("IP65 waterproof", "All-weather outdoor use."),
            ("Side lighting", "High luminous efficiency."),
        ],
        specs=[
            ("Battery", "Lithium, up to 5 years"),
            ("Lighting modes", "4 modes"),
            ("Sensor", "PIR motion, 120°"),
            ("LED", "Side-lighting, high efficiency"),
            ("Protection", "IP65"),
        ],
        applications=["Building façades", "Courtyards", "Driveways", "Perimeter walls", "Entrances"],
    ),
    "wall_swl21": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Dimond series solar wall light, SWL-21.",
        intro=lambda n: (
            f"The {n} (Dimond Series) is a solar wall light with 32 LED beads for wide 180° lighting angles "
            f"and high efficiency. Built-in lithium battery (up to 5-year life), PIR motion sensing "
            f"(120°, 5–7 m) and IP65 protection suit residential and commercial façades."
        ),
        advantages=[
            ("32 LED beads", "Wide 180° lighting angle."),
            ("Lithium battery", "Up to 5-year life."),
            ("PIR motion", "120° detection, 5–7 m range."),
            ("IP65 waterproof", "All-weather outdoor use."),
            ("High efficiency", "Up to 180° coverage."),
        ],
        specs=[
            ("LED", "32 beads, 180° angle"),
            ("Battery", "Lithium, up to 5 years"),
            ("Sensor", "PIR motion, 120°, 5–7 m"),
            ("Protection", "IP65"),
        ],
        applications=["Residential façades", "Commercial buildings", "Garages", "Gates", "Courtyards"],
    ),
    "security_swl22": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Clover solar security light, SWL-22.",
        intro=lambda n: (
            f"The {n} (Clover) is a solar security light with 214 LED beads for wide, bright coverage. A "
            f"built-in lithium battery (up to 5-year life), PIR motion sensor (120° detection) and IP65 "
            f"waterproofing secure driveways, yards, warehouses and perimeters."
        ),
        advantages=[
            ("214 LED beads", "Wide, bright lighting coverage."),
            ("Lithium battery", "Up to 5-year life."),
            ("PIR motion", "120° detection."),
            ("IP65 waterproof", "All-weather outdoor use."),
            ("Security focus", "For driveways & perimeters."),
        ],
        specs=[
            ("LED", "214 beads, wide coverage"),
            ("Battery", "Lithium, up to 5 years"),
            ("Sensor", "PIR motion, 120°"),
            ("Protection", "IP65"),
        ],
        applications=["Driveways", "Yards", "Warehouses", "Perimeters", "Parking"],
    ),
    "post_ztd": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Solar post light, ZTD series.",
        intro=lambda n: (
            f"The {n} is a solar post light with a die-cast ABS + PC body and Class A solar panel. Compact "
            f"and corrosion-resistant, it adds safe, automatic dusk-to-dawn lighting to fences, decks, "
            f"pathways and garden posts (IPX4 / IP65 by model)."
        ),
        advantages=[
            ("ABS + PC body", "Die-cast, anti-corrosion."),
            ("Class A panel", "High solar conversion rate."),
            ("Auto dusk-to-dawn", "Hands-free operation."),
            ("Compact", "Easy post mounting."),
            ("Weatherproof", "IPX4 / IP65 by model."),
        ],
        specs=[
            ("Body", "Die-cast ABS + PC, anti-corrosion"),
            ("Solar panel", "Class A, high conversion"),
            ("Protection", "IPX4 / IP65 (by model)"),
            ("Operation", "Auto dusk-to-dawn"),
        ],
        applications=["Fences", "Decks", "Pathways", "Garden posts", "Porches"],
    ),
    "decoration_zsd": dict(
        cat="solar-decor", cat_name="Solar Decorative Lighting Series",
        tagline="Solar decoration light, ZSD series.",
        intro=lambda n: (
            f"The {n} is a solar decoration light with a die-cast ABS + PC body and Class A high-conversion "
            f"solar panel. G45 / S14 LED beads provide warm, efficient accent lighting with IP65 protection "
            f"for gardens, terraces, events and festive scenes."
        ),
        advantages=[
            ("ABS + PC body", "Die-cast, anti-corrosion."),
            ("Class A panel", "High solar conversion rate."),
            ("G45 / S14 LEDs", "Warm accent lighting."),
            ("IP65 waterproof", "All-weather outdoor use."),
            ("Decorative", "For events & scenes."),
        ],
        specs=[
            ("Body", "Die-cast ABS + PC, anti-corrosion"),
            ("Solar panel", "Class A, high conversion"),
            ("LED", "G45 / S14 beads, high efficiency"),
            ("Protection", "IP65"),
        ],
        applications=["Gardens", "Terraces", "Events", "Festive scenes", "Cafés"],
    ),
    "municipal_stl": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="Municipal AC LED street light, STL series.",
        intro=lambda n: (
            f"The {n} is a municipal-grade AC LED street light with two installation options for easy setup. "
            f"IP65 waterproof housing resists heavy rain and storms, die-cast aluminium ensures fast heat "
            f"dissipation, and an isolated / brand power supply is optional for public roads, highways and "
            f"urban projects."
        ),
        advantages=[
            ("Two install options", "Easy to mount."),
            ("IP65 waterproof", "Resists heavy rain & storms."),
            ("Die-cast aluminium", "Fast heat dissipation."),
            ("Isolated PSU", "Brand-driven optional."),
            ("Municipal grade", "For public roads & urban use."),
        ],
        specs=[
            ("Install", "Two mounting options"),
            ("Protection", "IP65 waterproof"),
            ("Housing", "Die-cast aluminium, fast heat dissipation"),
            ("Power supply", "Isolated, brand-driven optional"),
            ("Use", "Public roads, highways, urban"),
        ],
        applications=["Public roads", "Highways", "Urban streets", "City projects", "Industrial zones"],
    ),
    "poles_q235": dict(
        cat="solar-lighting", cat_name="Solar Lighting Series",
        tagline="Q235 steel solar street light poles, 6–12 m.",
        intro=lambda n: (
            f"The {n} are Q235 steel solar street light poles with a 20-year lifespan and no-rust galvanized "
            f"finish. Built for OEM/ODM orders, they pair with Woneng's full street-light range as a top "
            f"China supplier for turnkey road, garden and municipal projects."
        ),
        advantages=[
            ("Q235 steel", "No rust, structural strength."),
            ("20-year lifespan", "Long service life."),
            ("OEM / ODM", "Custom orders welcome."),
            ("Turnkey", "Pairs with full light range."),
            ("Top supplier", "Leading China street-light poles."),
        ],
        specs=[
            ("Material", "Q235 steel, no rust"),
            ("Lifespan", "20 years"),
            ("Service", "OEM / ODM welcome"),
            ("Height", "6–12 m"),
            ("Use", "Road, garden, municipal projects"),
        ],
        applications=["Street lighting", "Garden lighting", "Municipal projects", "Stadium lighting", "Turnkey projects"],
    ),
}

def classify(slug):
    s = slug.lower()
    if "flood" in s and "rgb" in s:
        return "flood_rgb"
    if "flood" in s:
        return "flood_f05"
    if "aio-100100p-s03" in s or "aio-6060p-s03" in s or "aio-8080p-s03" in s or "ait-6030p-s03" in s:
        return "aio_s03"
    if "2520p-s04" in s:
        return "aio_s04"
    if "6000w-l08" in s:
        return "aio_l08"
    if "aio-l02" in s:
        return "aio_l02"
    if "aio-200w-l04" in s or "ait-100w-l04" in s:
        return "ait_l04"
    if "ait-300w-l03" in s:
        return "ait_l03"
    if "ggd" in s:
        return "garden_ggd"
    if "dcd-003" in s or "garden-spotlight" in s:
        return "garden_spotlight"
    if "dcd001" in s or "ground-plug" in s:
        return "ground_plug"
    if "cpd" in s:
        return "landscape_cpd"
    if "swl-19-20" in s or "swl-t18b" in s:
        return "wall_swl"
    if "swl-21" in s or "dimond" in s:
        return "wall_swl21"
    if "swl-22" in s or "clover" in s:
        return "security_swl22"
    if "ztd" in s:
        return "post_ztd"
    if "zsd" in s:
        return "decoration_zsd"
    if "stl" in s:
        return "municipal_stl"
    if "pole" in s or "gbet" in s:
        return "poles_q235"
    return "flood_f05"

def model_code(name):
    m = re.search(r"BST-[\w/-]+", name)
    if m:
        return m.group(0)
    # fallback: strip trailing
    return name

out = []
for item in RAW:
    slug = item["slug"]
    name = item["name"]
    series_key = classify(slug)
    ser = SERIES[series_key]
    code = model_code(name)
    d = {
        "slug": slug,
        "name": name,
        "cat": ser["cat"],
        "cat_name": ser["cat_name"],
        "tagline": ser["tagline"],
        "models": code,
        "models_full": [code],
        "img": item["img_local"],
        "intro": ser["intro"](name),
        "advantages": [list(a) for a in ser["advantages"]],
        "specs": [list(s) for s in ser["specs"]],
        "applications": list(ser["applications"]),
        "featured": False,
        "scraped": True,
    }
    out.append(d)

import pprint
header = (
    "# -*- coding: utf-8 -*-\n"
    "\"\"\"Auto-generated scraped product entries (43 SKU pages).\n\n"
    "Generated by gen_scraped.py from product_scrape.json. Each entry matches the\n"
    "data.py PRODUCTS schema and is flagged featured=False / scraped=True so it is\n"
    "excluded from the home/footer highlights but listed in the products index and\n"
    "given its own SEO'd detail page.\n"
    "\"\"\"\n\n"
    "SCRAPED_PRODUCTS = "
)
body = pprint.pformat(out, indent=1, width=96, sort_dicts=False)
text = header + body + "\n"
dst = os.path.join(HERE, "scraped_products.py")
with open(dst, "w", encoding="utf-8") as f:
    f.write(text)

print("Wrote", len(out), "scraped products to", dst)
