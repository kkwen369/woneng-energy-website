# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

GEN = r"D:\网站\woneng-energy-website\_gen\all"
OUT = r"D:\网站\woneng-energy-website"

MAP = {
    "HEROHOME": "images/hero-home.webp",
    "HEROFACTORY": "images/hero-factory.webp",
    "HEROPRODUCTS": "images/hero-products.webp",
    "HEROPROJECTS": "images/hero-projects.webp",
    "HEROSOLUTIONS": "images/hero-solutions.webp",
    "PRODAIO": "images/products/aio-street-light.webp",
    "PRODAIT": "images/products/ait-street-light.webp",
    "PRODFLOOD": "images/products/solar-flood-light.webp",
    "PRODGARDEN": "images/products/garden-light.webp",
    "PRODPOLE": "images/products/light-poles.webp",
    "PRODPORTABLE": "images/products/portable-storage.webp",
    "PRODGEN": "images/products/solar-generator.webp",
    "PRODINVERTER": "images/products/hybrid-inverter.webp",
    "PRODPOWERWALL": "images/products/powerwall-battery.webp",
    "PRODRACK": "images/products/rack-battery.webp",
    "PRODBESS": "images/products/bess-system.webp",
    "PRODPV": "images/products/pv-accessories.webp",
    "PROJNIGERIA": "images/projects/nigeria.webp",
    "PROJZAMBIA": "images/projects/zambia.webp",
    "PROJSRILANKA": "images/projects/sri-lanka.webp",
    "PROJDUBAI": "images/projects/dubai.webp",
    "PROJINDONESIA": "images/projects/indonesia.webp",
    "PROJMALAYSIA": "images/projects/malaysia.webp",
}

found = {k: None for k in MAP}
for f in glob.glob(os.path.join(GEN, "*.png")):
    base = os.path.basename(f)
    for k in MAP:
        if base.upper().startswith(k):
            found[k] = f
            break

missing = [k for k, v in found.items() if v is None]
if missing:
    print("MISSING:", missing)
    raise SystemExit(1)

count = 0
for k, src in found.items():
    dst = os.path.join(OUT, MAP[k])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.save(dst, "WEBP", quality=82)
    count += 1
    print("ok", MAP[k], os.path.getsize(dst)//1024, "KB")

print(f"Converted {count} images to WebP.")
