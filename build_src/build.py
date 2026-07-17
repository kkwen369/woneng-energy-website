# -*- coding: utf-8 -*-
import os, datetime, json
from data import (SITE, NAV, CATEGORIES, PRODUCTS, SOLUTIONS, PROJECTS,
                  CERTS, STATS)
from scraped_products import SCRAPED_PRODUCTS

# Extend with the 43 SKU-level pages scraped from entelechyenergy.com
PRODUCTS = PRODUCTS + SCRAPED_PRODUCTS

def featured_products():
    """Core lines (featured=True) used on home/footer; scraped SKUs default False."""
    return [p for p in PRODUCTS if p.get("featured", True)]

# ---------------- product series grouping ----------------
# Web3Forms endpoint (no backend needed). Replace FORM_KEY with a free key from
# https://web3forms.com — it emails inquiries to SITE["email"]. A mailto fallback
# in main.js guarantees no lead is lost even before the key is set.
FORM_ENDPOINT = "https://api.web3forms.com/form"
FORM_KEY = "YOUR_WEB3FORMS_ACCESS_KEY"

SERIES_RULES = [
    ("all-in-two", "ait", "AIT Split Solar Street Light"),
    ("all-in-one-solar-street-light-bst-aio", "aio", "AIO Solar Street Light"),
    ("solar-flood-light", "flood-f05", "Solar Flood Light F05"),
    ("municipal-led-street-light", "municipal", "Municipal AC LED Street Light"),
    ("solar-street-light-poles", "poles", "Solar Street Light Pole"),
    ("gbet-solar-street-light-poles", "poles", "Solar Street Light Pole"),
    ("light-poles-accessories", "poles", "Solar Street Light Pole"),
    ("clover-solar-security-light", "security", "Solar Security Light"),
    ("solar-wall-light", "wall", "Solar Wall Light"),
    ("dimond-series-solar-wall-light", "wall", "Solar Wall Light"),
    ("solar-post-light", "post", "Solar Post Light"),
    ("solar-decoration-light", "decoration", "Solar Decoration Light"),
    ("solar-garden-spotlight", "spotlight", "Solar Garden Spotlight"),
    ("solar-ground-plug-in", "ground-plug", "Solar Ground Plug-in Light"),
    ("solar-garden-light", "garden-landscape", "Solar Garden & Landscape Light"),
    ("solar-garden-lights", "garden-landscape", "Solar Garden & Landscape Light"),
    ("solar-landscape-lights", "garden-landscape", "Solar Garden & Landscape Light"),
    ("solar-garden-landscape-light", "garden-landscape", "Solar Garden & Landscape Light"),
    ("aio-solar-street-light", "aio", "AIO Solar Street Light"),
    ("ait-solar-street-light", "ait", "AIT Split Solar Street Light"),
    ("solar-flood-light-f05", "flood-f05", "Solar Flood Light F05"),
]
SERIES_ORDER = ["aio", "ait", "flood-f05", "poles", "municipal", "garden-landscape",
                "wall", "post", "decoration", "spotlight", "ground-plug", "security",
                "portable-energy-storage", "solar-power-generator", "solar-hybrid-inverter",
                "powerwall-energy-storage-battery", "rack-mounted-high-voltage-battery",
                "industrial-commercial-bess", "pv-supporting-accessories"]

def classify_series(p):
    s = p["slug"]
    for key, slug, name in SERIES_RULES:
        if key in s:
            return slug, name
    return s, p["name"]

def series_groups():
    groups = {}
    for p in PRODUCTS:
        slug, name = classify_series(p)
        groups.setdefault(slug, {"name": name, "cat": p["cat"], "items": []})
        groups[slug]["items"].append(p)
    out = []
    for slug in SERIES_ORDER:
        if slug in groups:
            out.append((slug, groups[slug]["name"], groups[slug]["cat"], groups[slug]["items"]))
    for slug, g in groups.items():
        if slug not in SERIES_ORDER:
            out.append((slug, g["name"], g["cat"], g["items"]))
    return out

def cat_name_of(cat_id):
    for cname, cid in CATEGORIES:
        if cid == cat_id:
            return cname
    return cat_id

def product_card(p, bp=""):
    chips = "".join(
        f'<span class="pchip"><b>{esc(k)}</b> {esc(v)}</span>' for k, v in key_specs(p))
    return f'''<a class="card pcard" href="{bp}products/{p['slug']}.html">
      <div class="thumb" role="img" aria-label="{esc(p['name'])}" style="background-image:url('{bp}images/products/{os.path.basename(p['img'])}')"><span class="tag">{esc(p['cat_name'].split()[0])}</span></div>
      <div class="body"><h3>{esc(p['name'])}</h3><div class="meta">{esc(p['models'])}</div><div class="pchips">{chips}</div><div class="more">View product →</div></div></a>'''

KEY_SPEC_KEYS = ["Power range", "Power", "Capacity", "Battery", "Protection", "CCT", "LED chips"]
def _short(v, n=24):
    v = str(v)
    return v if len(v) <= n else v[:n-1] + "…"
def key_specs(p):
    chips = [("Model", _short(p["models"], 28))]
    for k, v in p["specs"]:
        if k in KEY_SPEC_KEYS and len(chips) < 4:
            chips.append((k, _short(v)))
        if len(chips) >= 4:
            break
    return chips

def inquiry_form(bp="", title="New Inquiry"):
    """Shared inquiry form wired to Web3Forms (see FORM_KEY). Includes a honeypot."""
    return f'''<form class="inquiry-form" action="{FORM_ENDPOINT}" method="POST" data-web3>
      <input type="hidden" name="access_key" value="{FORM_KEY}">
      <input type="hidden" name="subject" value="Woneng Inquiry — {esc(title)}">
      <input type="hidden" name="from_name" value="Woneng Website">
      <input type="text" name="company_website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="form-grid">
        <div class="field"><label>Name *</label><input name="name" required placeholder="Your full name"></div>
        <div class="field"><label>Company *</label><input name="company" required placeholder="Your company name"></div>
        <div class="field"><label>Email *</label><input type="email" name="email" required placeholder="you@company.com"></div>
        <div class="field"><label>WhatsApp / Phone</label><input name="phone" placeholder="+234 … / phone number"></div>
        <div class="field"><label>Product / Category</label><input id="f-product" name="product" placeholder="e.g. AIO Solar Street Light"></div>
        <div class="field"><label>Target Market</label><input name="market" placeholder="e.g. Nigeria"></div>
        <div class="field full"><label>Quantity &amp; Project Need</label><textarea name="message" placeholder="Tell us your quantity, project type and timeline..."></textarea></div>
        <div class="field full"><button class="btn btn-lg" type="submit">Send Inquiry</button></div>
      </div>
      <div class="form-ok">✓ Thank you! Our international team will reply within 24 hours.</div>
    </form>'''


OUT = os.path.join(os.path.dirname(__file__), "..")
BASE_URL = SITE.get("base_url", "https://" + SITE["domain"]).rstrip("/")
def w(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def jsonld(data):
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'

def org_ld():
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE["brand_full"],
        "alternateName": SITE["brand"],
        "url": BASE_URL + "/",
        "logo": BASE_URL + "/images/hero-home.webp",
        "email": SITE["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["address"],
            "addressCountry": "CN",
        },
        "contactPoint": [{
            "@type": "ContactPoint",
            "telephone": SITE["whatsapp"].replace(" ", ""),
            "contactType": "sales",
            "areaServed": "Worldwide",
        }],
    }

def website_ld():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE["brand"],
        "url": BASE_URL + "/",
        "publisher": {"@type": "Organization", "name": SITE["brand_full"]},
    }

def breadcrumb_ld(items):
    """items = list of (name, rel_url)."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "name": n, "item": BASE_URL + "/" + u}
            for i, (n, u) in enumerate(items)
        ],
    }

# ---------------- shared chrome ----------------
def head(title, desc, kw, bp="", url="", og_image="", og_type="website", json_ld=None):
    canonical = BASE_URL + "/" + url if url else BASE_URL + "/"
    ogimg = (BASE_URL + "/" + og_image) if og_image else (BASE_URL + "/images/hero-home.webp")
    jld = ""
    if json_ld:
        jld = "".join(jsonld(d) for d in json_ld) if isinstance(json_ld, list) else jsonld(json_ld)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(kw)}">
<meta name="author" content="{esc(SITE['brand_full'])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(SITE['brand_full'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ogimg}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{ogimg}">
{jld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{bp}css/style.css">
</head>'''

def header(active="", bp=""):
    items = ""
    for label, href in NAV:
        cls = " active" if href == active else ""
        items += f'<li><a class="{cls.strip()}" href="{bp}{href}">{esc(label)}</a></li>\n'
    return f'''<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{bp}index.html">
      <span class="logo">W</span>
      <span>Woneng<small>SOLAR &amp; STORAGE</small></span>
    </a>
    <button class="nav-toggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="nav-links">
      {items}
    </ul>
    <div class="nav-cta">
      <a class="btn" href="#" data-inquiry="Request a Quote" data-inquiry-title="Request a Bulk Quote">Get a Quote</a>
    </div>
  </div>
</header>'''

def footer(bp=""):
    prod_links = "".join(
        f'<li><a href="{bp}products/{p["slug"]}.html">{esc(p["name"])}</a></li>' for p in featured_products()[:6])
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="brand" href="{bp}index.html"><span class="logo">W</span><span>Woneng<small>SOLAR &amp; STORAGE</small></span></a>
      <p>Zhaoqing Woneng High-Tech Co., Ltd. — solar lighting &amp; energy storage manufacturer. Factory direct, wholesale and OEM/ODM for global B2B distributors and EPC contractors.</p>
    </div>
    <div class="foot-col">
      <h4>Products</h4>
      <ul>{prod_links}</ul>
    </div>
    <div class="foot-col">
      <h4>Company</h4>
      <ul>
        <li><a href="{bp}about.html">About Us</a></li>
        <li><a href="{bp}factory.html">Factory &amp; Capacity</a></li>
        <li><a href="{bp}certifications.html">Certifications</a></li>
        <li><a href="{bp}projects.html">Projects</a></li>
        <li><a href="{bp}solutions.html">Solutions</a></li>
        <li><a href="{bp}contact.html">Contact</a></li>
      </ul>
    </div>
    <div class="foot-col foot-contact">
      <h4>Contact</h4>
      <ul>
        <li><span class="mi">✉</span><span>{esc(SITE['email'])}</span></li>
        <li><span class="mi">☎</span><span>WhatsApp: {esc(SITE['whatsapp'])}</span></li>
        <li><span class="mi">⌖</span><span>{esc(SITE['address'])}</span></li>
      </ul>
    </div>
  </div>
  <div class="wrap foot-bottom">
    <span>© <span id="year"></span> {esc(SITE['brand_full'])}. All rights reserved.</span>
    <span>Factory Direct · Wholesale · OEM/ODM · Global Export</span>
  </div>
</footer>'''

WHATSAPP_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.99 6.45 17.5 2 12.04 2zm5.8 14.14c-.25.69-1.45 1.32-1.99 1.36-.53.04-1.07.24-3.6-.75-2.99-1.14-4.9-4.05-5.05-4.24-.15-.19-1.18-1.57-1.18-3 0-1.42.75-2.12 1.01-2.41.26-.29.57-.36.76-.36.19 0 .38 0 .55.01.18.01.41-.07.64.49.25.59.84 2.03.91 2.18.07.15.12.32.02.52-.1.19-.15.31-.29.48-.15.18-.31.39-.45.53-.15.15-.3.31-.13.6.17.29.74 1.22 1.59 1.98 1.09.97 2.01 1.27 2.3 1.41.29.14.46.12.63-.07.18-.19.74-.86.94-1.16.2-.3.4-.25.67-.15.28.1 1.77.84 2.07 1 .3.16.5.24.57.37.08.14.08.79-.17 1.48z"/></svg>'

def inquiry_float():
    wa = SITE['whatsapp'].replace("+", "")
    return f'''<div class="inquiry-float">
  <a class="fab inquiry" href="#" data-inquiry="Request a Quote" data-inquiry-title="Request a Bulk Quote"><span class="lbl">Get a Quote</span>✉</a>
  <a class="fab whatsapp" href="https://wa.me/{wa}" target="_blank" rel="noopener"><span class="lbl">WhatsApp</span>{WHATSAPP_SVG}</a>
</div>'''

def inquiry_modal(bp=""):
    return f'''<div class="modal-back" id="inquiryModal">
  <div class="modal">
    <div class="modal-head"><h3 id="inquiryModalTitle">Request a Quote</h3><button class="modal-close" aria-label="Close">×</button></div>
    <div class="modal-body">
      {inquiry_form(bp, "Request a Quote")}
    </div>
  </div>
</div>'''

def scripts(bp=""):
    return f'<script src="{bp}js/main.js"></script>'

def page(title, desc, kw, body, active="", bp="", banner=None, breadcrumb=None,
          og_image="", og_type="website", json_ld=None, url=""):
    """Full page assembly. banner=(eyebrow,title,sub) for inner pages."""
    h = ""
    if banner:
        eyebrow, btitle, bsub = banner
        bc = ""
        if breadcrumb:
            bc = f'<div class="wrap breadcrumb">{breadcrumb}</div>'
        h = f'''<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('{bp}images/hero-factory.webp')"></div>
  <div class="pagebanner-inner">
    <div class="wrap">
      {bc}
      <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">{esc(eyebrow)}</div>
      <h1>{esc(btitle)}</h1>
      <p>{esc(bsub)}</p>
    </div>
  </div>
</section>'''
    return (head(title, desc, kw, bp, url=url, og_image=og_image,
                 og_type=og_type, json_ld=json_ld) +
            '<body>' + header(active, bp) + h + body +
            inquiry_float() + inquiry_modal(bp) +
            footer(bp) + scripts(bp) + '</body></html>')

# ---------------- HOME ----------------
def build_home():
    prod_cards = ""
    for p in featured_products():
        prod_cards += f'''<a class="card pcard" href="products/{p['slug']}.html">
          <div class="thumb" role="img" aria-label="{esc(p['name'])}" style="background-image:url('images/products/{os.path.basename(p['img'])}')"><span class="tag">{esc(p['cat_name'].split()[0])}</span></div>
          <div class="body">
            <h3>{esc(p['name'])}</h3>
            <div class="meta">{esc(p['models'])}</div>
            <div class="more">View product →</div>
          </div></a>'''

    adv = [
        ("Factory Direct", "Own standardized plant in Zhaoqing — wholesale pricing, no middle layer."),
        ("15+ Years Export", "Deep experience serving distributors, EPC contractors and governments."),
        ("Africa Focused", "Heat, dust and unstable-grid ready products for Nigeria & Africa."),
        ("OEM / ODM", "Private label, engineering customization and global logistics."),
    ]
    adv_cards = "".join(f'<div class="card"><div class="ic">◆</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in adv)

    stats = "".join(f'<div class="b"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in STATS)

    proj_cards = ""
    for p in PROJECTS[:3]:
        proj_cards += f'''<a class="card pcard" href="projects.html">
          <div class="thumb" style="background-image:url('images/projects/{os.path.basename(p['img'])}')"></div>
          <div class="body"><h3>{esc(p['country'])}</h3><div class="meta">{esc(p['title'])}</div><div class="more">View project →</div></div></a>'''

    markets = ["Nigeria", "Zambia", "South Africa", "Kenya", "Ghana", "Sri Lanka", "Indonesia", "Malaysia", "UAE", "Philippines"]

    body = f'''
<section class="hero">
  <div class="hero-bg" style="background-image:url('images/hero-home.webp')"></div>
  <div class="hero-inner">
    <div class="wrap">
      <div class="eyebrow">Global B2B Solar &amp; Energy Storage Manufacturer</div>
      <h1>Reliable Solar Lighting &amp; Energy Storage for Africa &amp; the World</h1>
      <p class="lead">Woneng delivers factory-direct solar street lights, flood lights and LiFePO4 energy storage systems — engineered for harsh climates, built for distributors, EPC contractors and government projects worldwide.</p>
      <div class="hero-actions">
        <a class="btn btn-lg" href="#" data-inquiry="Request a Quote" data-inquiry-title="Request a Bulk Quote">Get a Bulk Quote</a>
        <a class="btn btn-lg btn-light" href="products.html">Explore Products</a>
      </div>
      <div class="hero-stats">{stats}</div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <div class="eyebrow">Core Product Lines</div>
      <h2>Solar Lighting &amp; Energy Storage, End to End</h2>
      <p>From AIO street lights to container BESS — one supplier for your full project bill of materials.</p>
    </div>
    <div class="grid grid-3">{prod_cards}</div>
    <div class="center" style="margin-top:34px"><a class="btn btn-ghost" href="products.html">View All Products</a></div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="section-head"><div class="eyebrow">Why Woneng</div><h2>A B2B Partner, Not a Reseller</h2></div>
    <div class="grid grid-4">{adv_cards}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div>
        <div class="eyebrow" style="color:var(--blue);font-weight:700;letter-spacing:2px;text-transform:uppercase;font-size:13px">Global Export Capacity</div>
        <h2>Standardized Production. Stable Supply. Worldwide Delivery.</h2>
        <p>Our Zhaoqing facility runs complete production, testing and QC flows with an annual output of 50,000 self-developed batteries. We support batch wholesale, project customization and OEM/ODM with one-stop global logistics.</p>
        <ul class="flist">
          <li><strong>50,000</strong> nano-magnesium-silicon batteries produced per year</li>
          <li><strong>ISO + CE + RoHS + IEC</strong> certified manufacturing</li>
          <li><strong>OEM / ODM</strong> private label &amp; engineering customization</li>
          <li><strong>Global delivery</strong> to Africa, SE Asia, Middle East &amp; beyond</li>
        </ul>
        <a class="btn" href="factory.html" style="margin-top:14px">See Our Factory</a>
      </div>
      <div class="media" style="background-image:url('images/hero-factory.webp')"></div>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="section-head"><div class="eyebrow">Markets We Serve</div><h2>Built for Africa, Ready for the World</h2>
      <p>We focus on Africa's off-grid demand and expand across emerging markets.</p></div>
    <div class="logos">{"".join(f'<span class="lg">{m}</span>' for m in markets)}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head"><div class="eyebrow">Proven Deliveries</div><h2>Global Project References</h2></div>
    <div class="grid grid-3">{proj_cards}</div>
    <div class="center" style="margin-top:30px"><a class="btn btn-ghost" href="projects.html">All Projects</a></div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="cta">
      <h2>Ready to Quote Your Solar or Storage Project?</h2>
      <p>Tell us your market, quantity and application — get a factory-direct proposal in 24 hours.</p>
      <div class="hero-actions">
        <a class="btn btn-lg btn-light" href="#" data-inquiry="Request a Quote" data-inquiry-title="Request a Bulk Quote">Start Inquiry</a>
        <a class="btn btn-lg btn-light" href="https://wa.me/{SITE['whatsapp'].replace('+','')}" target="_blank" rel="noopener">WhatsApp Us</a>
      </div>
    </div>
  </div>
</section>
'''
    return page("Woneng — Solar Street Lights & Energy Storage Manufacturer | Factory Direct",
                "Woneng is a B2B manufacturer of solar street lights, solar flood lights and LiFePO4 energy storage systems. Factory direct wholesale, OEM/ODM, Africa & Nigeria off-grid solar solutions.",
                "solar street light, solar energy storage, Nigeria solar street light, Africa off-grid solar system, solar flood light, Powerwall battery, Woneng",
                body, active="index.html", url="index.html",
                og_image="images/hero-home.webp",
                json_ld=[org_ld(), website_ld()])

# ---------------- ABOUT ----------------
def build_about():
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-factory.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>About Us</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">About Woneng</div>
    <h1>A Trusted New-Energy Export Partner</h1>
    <p>15 years of solar manufacturing &amp; export experience, delivering reliable PV and storage solutions to global B2B clients.</p>
  </div></div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Who We Are</h2>
        <p>Zhaoqing Woneng High-Tech Co., Ltd. is an international export enterprise dedicated to the new-energy photovoltaic and energy-storage industry, integrating independent R&amp;D, standardized production, global sales and customized solution services.</p>
        <p>Based in Zhaoqing, Guangdong — a core manufacturing base for new-energy equipment in South China — we own standardized production workshops and a complete industrial-chain supply network.</p>
        <ul class="flist">
          <li>Focus on <strong>off-grid power, C&amp;I storage, home backup and outdoor PV lighting</strong></li>
          <li>Long-term partnerships with <strong>distributors, EPC contractors and government buyers</strong></li>
          <li>Strategy: <strong>global layout with Africa as the core market</strong></li>
        </ul>
      </div>
      <div class="media" style="background-image:url('images/hero-factory.webp')"></div>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="section-head"><div class="eyebrow">What We Do</div><h2>Core Product System</h2></div>
    <div class="grid grid-3">
      <div class="card"><div class="ic">☀</div><h3>PV + Storage Integrated</h3><p>Custom hybrid solutions for off-grid areas solving unstable power and shortage.</p></div>
      <div class="card"><div class="ic">⌂</div><h3>Residential Storage</h3><p>Compact, safe, durable home storage for daily use, backup and remote supply.</p></div>
      <div class="card"><div class="ic">⚙</div><h3>C&amp;I Storage</h3><p>Large-capacity systems balancing peaks/valleys and cutting power cost.</p></div>
      <div class="card"><div class="ic">💡</div><h3>Solar LED Street Light</h3><p>Integrated, weather-resistant, high-efficacy lighting for municipal and rural use.</p></div>
      <div class="card"><div class="ic">🔋</div><h3>Self-developed Battery</h3><p>Nano-magnesium-silicon cells, 50,000/yr, extreme-temp resilient.</p></div>
      <div class="card"><div class="ic">🔌</div><h3>Supporting Equipment</h3><p>Chargers, distribution control and full PV+storage closed loop.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="stats-band"><div class="wrap" style="padding:0">
      {''.join(f'<div class="b"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v,l in STATS)}
    </div></div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="split rev">
      <div>
        <h2>Our Vision</h2>
        <p>Upholding <strong>"Quality Oriented, Innovation Driven, Global Win-Win"</strong>, Woneng is committed to building a professional and international new-energy export brand.</p>
        <p>We continuously iterate technologies, enrich our product matrix and deepen core overseas markets — providing efficient, reliable and inclusive green-energy solutions as a long-term, trustworthy partner.</p>
        <a class="btn" href="contact.html">Work With Us</a>
      </div>
      <div class="media tall" style="background-image:url('images/hero-factory.webp')"></div>
    </div>
  </div>
</section>
'''
    return page("About Woneng — Solar & Energy Storage Manufacturer | Zhaoqing Woneng",
                "Zhaoqing Woneng High-Tech Co., Ltd. is a B2B new-energy exporter with 15 years of solar manufacturing and export experience, focused on Africa and global off-grid markets.",
                "about Woneng, solar manufacturer China, Zhaoqing Woneng, solar street light factory, energy storage manufacturer",
                body, active="about.html", url="about.html",
                og_image="images/hero-factory.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("About Us", "about.html")]), org_ld()])

# ---------------- PRODUCTS INDEX ----------------
def build_products_index():
    groups = series_groups()
    # category filter buttons
    cats = [("all", "All Products")] + [(cid, cname) for cname, cid in CATEGORIES]
    filter_btns = "".join(
        f'<button class="chip-filter{" active" if cid == "all" else ""}" data-cat="{cid}">{esc(cname)}</button>'
        for cid, cname in cats)
    body_groups = ""
    for i, (slug, name, cat, items) in enumerate(groups):
        cards = "".join(product_card(p) for p in items)
        open_attr = "open" if i < 2 else ""
        body_groups += f'''<details class="series" {open_attr} data-cat="{esc(cat)}">
          <summary><div class="series-head">
            <h2>{esc(name)}</h2>
            <span class="series-meta">
              <span class="tag">{esc(cat_name_of(cat).split()[0])}</span>
              <span class="count">{len(items)} model{"s" if len(items) != 1 else ""}</span>
              <span class="expand">+ expand</span>
            </span>
          </div></summary>
          <div class="grid grid-3">{cards}</div>
        </details>'''
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-products.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>Products</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Product Center</div>
    <h1>Solar Lighting &amp; Energy Storage Products</h1>
    <p>Browse by product series — click a series to see all models, specs and inquiry pages.</p>
  </div></div>
</section>
<section><div class="wrap">
  <div class="cat-filter">{filter_btns}</div>
  <div class="series-list">{body_groups}</div>
  <div class="cta" style="margin-top:28px">
    <h2>Can't find the exact model?</h2>
    <p>We do OEM/ODM and project customization. Send us your spec sheet.</p>
    <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="Custom OEM/ODM Request" data-inquiry-title="Custom OEM/ODM Request">Request Custom Build</a></div>
  </div>
</div></section>
'''
    return page("Products — Solar Street Lights & Energy Storage | Woneng",
                "Woneng product catalog by series: AIO/split solar street lights, solar flood lights, garden & decorative lights, portable & container storage, hybrid inverters, Powerwall and rack batteries, PV accessories.",
                "solar street light, solar flood light, portable energy storage, hybrid inverter, Powerwall battery, rack battery, BESS, PV accessories, Woneng products",
                body, active="products.html", url="products.html",
                og_image="images/hero-products.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Products", "products.html")]), org_ld()])

# ---------------- PRODUCT DETAIL ----------------
def build_product(p):
    slug = p["slug"]
    chips = "".join(f'<span class="keychip"><b>{esc(k)}</b> {esc(v)}</span>' for k, v in key_specs(p))
    adv = "".join(f'<li><span class="ck">✓</span><div><b>{esc(t)}</b><p>{esc(d)}</p></div></li>' for t, d in p["advantages"])
    spec_rows = "".join(f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in p["specs"])
    app_chips = "".join(f'<span class="chip">{esc(a)}</span>' for a in p["applications"])
    # series switcher — all models in the same series
    sslug = classify_series(p)[0]
    sibs = [x for x in PRODUCTS if classify_series(x)[0] == sslug]
    switcher = ""
    for x in sibs:
        if x["slug"] == slug:
            switcher += f'<span class="sw active" aria-current="true">{esc(x["models"])}</span>'
        else:
            switcher += f'<a class="sw" href="{x["slug"]}.html">{esc(x["models"])}</a>'
    rel = [x for x in sibs if x["slug"] != slug][:3]
    if not rel:  # fall back to same-category if series has only one model
        rel = [x for x in PRODUCTS if x["cat"] == p["cat"] and x["slug"] != slug][:3]
    rel_cards = "".join(product_card(x, bp="../") for x in rel)
    sol_link = SOLUTIONS[0]
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('../images/hero-products.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../products.html">Products</a><span>/</span>{esc(p['name'])}</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">{esc(p['cat_name'])}</div>
    <h1>{esc(p['name'])}</h1>
    <p>{esc(p['tagline'])}</p>
  </div></div>
</section>

<section><div class="wrap">
  <div class="psplit">
    <div class="pmedia" role="img" aria-label="{esc(p['name'])}" style="background-image:url('../images/products/{os.path.basename(p['img'])}')"></div>
    <div class="pinfo">
      <div class="keychips">{chips}</div>
      <h2 class="pname">{esc(p['name'])}</h2>
      <p class="ptag">{esc(p['tagline'])}</p>
      <p class="pintro">{esc(p['intro'])}</p>
      <div class="pactions">
        <a class="btn btn-lg" href="#" data-inquiry="{esc(p['name'])}" data-inquiry-title="Quote: {esc(p['name'])}">Get a Quote</a>
        <a class="btn btn-lg btn-ghost" href="../downloads/Solar-Light-Catalog-2026.pdf" target="_blank" rel="noopener">Download Catalog (PDF)</a>
      </div>
    </div>
  </div>
</div></section>

<section class="section-alt"><div class="wrap">
  <div class="switcher">
    <span class="sw-label">Models in this series:</span>
    <div class="sw-row">{switcher}</div>
  </div>
</div></section>

<section><div class="wrap">
  <h2 class="h-sm">Key Advantages</h2>
  <ul class="adv-compact">{adv}</ul>
</div></section>

<section class="section-alt"><div class="wrap"><div class="split">
  <div>
    <details class="specs" open>
      <summary>Technical Specifications</summary>
      <p class="muted">Typical parameters — customizable for project requirements.</p>
      <table class="spectable"><tbody>{spec_rows}</tbody></table>
    </details>
  </div>
  <div>
    <h2 class="h-sm">Applications</h2>
    <div class="chips" style="margin:12px 0 20px">{app_chips}</div>
    <a class="btn" href="../solutions/{sol_link['slug']}.html">See Matching Solution →</a>
  </div>
</div></div></section>

{('<section><div class="wrap"><div class="section-head"><div class="eyebrow">Related</div><h2>From the Same Series</h2></div><div class="grid grid-3">'+rel_cards+'</div></div></section>') if rel_cards else ''}

<section class="section-alt"><div class="wrap"><div class="cta">
  <h2>Quote {esc(p['name'])} for Your Project</h2>
  <p>Tell us quantity, market and timeline — factory-direct pricing in 24h.</p>
  <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="{esc(p['name'])}" data-inquiry-title="Quote: {esc(p['name'])}">Request Quote</a></div>
</div></div></section>
'''
    p_url = f"products/{slug}.html"
    canonical = BASE_URL + "/" + p_url
    product_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["name"],
        "image": [BASE_URL + "/" + p["img"]],
        "description": p["intro"],
        "brand": {"@type": "Brand", "name": SITE["brand_full"]},
        "category": p["cat_name"],
        "model": p["models"],
        "additionalProperty": [
            {"@type": "PropertyValue", "name": k, "value": v} for k, v in p["specs"]
        ],
        "offers": {
            "@type": "Offer",
            "availability": "https://schema.org/InStock",
            "priceCurrency": "USD",
            "seller": {"@type": "Organization", "name": SITE["brand_full"]},
        },
    }
    bc_ld = breadcrumb_ld([("Home", "index.html"), ("Products", "products.html"), (p["name"], p_url)])
    return page(f"{p['name']} — {p['cat_name']} | Woneng",
                f"{p['name']} by Woneng: {p['tagline']} Models {p['models']}. Factory-direct B2B pricing, OEM/ODM, global export.",
                f"{p['name']}, {p['cat_name']}, Woneng, solar, Nigeria, Africa, wholesale, OEM",
                body, active="products.html", bp="../", url=p_url,
                og_image=p["img"], json_ld=[bc_ld, product_ld])

# ---------------- SOLUTIONS ----------------
def build_solutions_index():
    cards = ""
    for s in SOLUTIONS:
        cards += f'''<a class="card pcard" href="solutions/{s['slug']}.html">
          <div class="thumb" style="background-image:url('{s['img']}')"></div>
          <div class="body"><h3>{esc(s['title'])}</h3><div class="meta">B2B solution</div><div class="more">View solution →</div></div></a>'''
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-solutions.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>Solutions</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Solutions</div>
    <h1>Solar &amp; Storage Solutions for Real Demand</h1>
    <p>Engineered for off-grid Africa, municipal lighting, residential and industrial scenarios.</p>
  </div></div>
</section>
<section><div class="wrap"><div class="grid grid-3">{cards}</div></div></section>
'''
    return page("Solutions — Off-grid Solar & Storage for Africa & Industry | Woneng",
                "Woneng B2B solutions: Africa off-grid solar, municipal street lighting, residential PV+storage, C&I storage, outdoor lighting, Nigeria local and rural Africa solar.",
                "Africa off-grid solar solution, Nigeria solar solution, municipal solar lighting, residential PV storage, industrial energy storage, Woneng solutions",
                body, active="solutions.html", url="solutions.html",
                og_image="images/hero-solutions.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Solutions", "solutions.html")]), org_ld()])

def build_solution(s):
    simg = "../" + s['img']
    pts = "".join(f'<li><strong>{esc(x)}</strong></li>' if False else f'<li>{esc(x)}</li>' for x in s["points"])
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('{simg}')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../solutions.html">Solutions</a><span>/</span>{esc(s['title'])}</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Solution</div>
    <h1>{esc(s['title'])}</h1>
    <p>{esc(s['lead'])}</p>
  </div></div>
</section>
<section><div class="wrap">
  <div class="split">
    <div class="media" style="background-image:url('{simg}')"></div>
    <div>
      <h2>What's Included</h2>
      <ul class="flist">{pts}</ul>
      <div style="margin-top:18px;display:flex;gap:12px;flex-wrap:wrap">
        <a class="btn btn-lg" href="#" data-inquiry="{esc(s['title'])}" data-inquiry-title="Solution Inquiry: {esc(s['title'])}">Discuss My Project</a>
        <a class="btn btn-lg btn-ghost" href="../products.html">Browse Products</a>
      </div>
    </div>
  </div>
</div></section>
<section class="section-alt"><div class="wrap"><div class="cta">
  <h2>Plan Your {esc(s['title'].split(' Solution')[0])} Deployment</h2>
  <p>Share your site, load and budget — we design the system and quote factory-direct.</p>
  <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="{esc(s['title'])}" data-inquiry-title="Solution Inquiry: {esc(s['title'])}">Start Inquiry</a></div>
</div></div></section>
'''
    s_url = f"solutions/{s['slug']}.html"
    return page(f"{s['title']} | Woneng",
                f"{s['title']}: {s['lead']} Woneng B2B solar & storage solutions for Africa and global markets.",
                f"{s['title']}, Woneng solution, Nigeria, Africa, solar, off-grid",
                body, active="solutions.html", bp="../", url=s_url,
                og_image=s["img"], og_type="article",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Solutions", "solutions.html"), (s["title"], s_url)]), org_ld()])

# ---------------- PROJECTS ----------------
def build_projects():
    cards = ""
    for p in PROJECTS:
        chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in p["scope"])
        cards += f'''<div class="proj">
          <div class="pic" style="background-image:url('images/projects/{os.path.basename(p['img'])}')"></div>
          <div class="info">
            <div class="loc">{esc(p['country'])}</div>
            <h3>{esc(p['title'])}</h3>
            <p>{esc(p['desc'])}</p>
            <div class="chips">{chips}</div>
          </div></div>'''
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-projects.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>Projects</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Global References</div>
    <h1>Overseas Project Cases</h1>
    <p>Real deployments across Africa, the Middle East and Asia — proof of delivery capability.</p>
  </div></div>
</section>
<section><div class="wrap">{cards}
  <div class="cta" style="margin-top:14px">
    <h2>Your Project Could Be Next</h2>
    <p>From single village to city-scale — we deliver and support worldwide.</p>
    <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="Project Collaboration" data-inquiry-title="Project Collaboration">Talk to Our Team</a></div>
  </div>
</div></section>
'''
    return page("Projects — Global Solar & Storage Deployments | Woneng",
                "Woneng overseas projects: Nigeria, Zambia, Sri Lanka, Dubai, Indonesia and Malaysia solar street lighting, storage and micro-grid deployments.",
                "solar project Nigeria, Zambia solar, Dubai solar storage, Sri Lanka lighting, Indonesia microgrid, Woneng projects",
                body, active="projects.html", url="projects.html",
                og_image="images/hero-projects.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Projects", "projects.html")]), org_ld()])

# ---------------- FACTORY ----------------
def build_factory():
    feats = [
        ("Standardized Workshops", "Complete production, testing and QC flows under one roof."),
        ("Self-developed Battery", "Nano-magnesium-silicon cells, 50,000 units/year, extreme-temp."),
        ("R&D Team", "In-house engineers for product and solution innovation."),
        ("QC System", "Traceable quality, certified environmental compliance."),
        ("OEM / ODM", "Private label, engineering customization, flexible MOQ."),
        ("Global Logistics", "Factory-direct supply, worldwide delivery & overseas support."),
    ]
    fcards = "".join(f'<div class="card"><div class="ic">◆</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for t, d in feats)
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-factory.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>Factory &amp; Capacity</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Factory &amp; Capacity</div>
    <h1>Standardized Production, Stable Supply</h1>
    <p>Zhaoqing manufacturing base with full-chain solar &amp; storage production capability.</p>
  </div></div>
</section>

<section><div class="wrap">
  <div class="split">
    <div>
      <h2>Production &amp; Capacity</h2>
      <p>Our standardized workshops and mature supply chain support large-scale, stable mass production. The core battery project has passed official environmental assessment and production filing.</p>
      <ul class="flist">
        <li><strong>50,000</strong> self-developed batteries produced annually</li>
        <li>Complete <strong>production, testing and QC</strong> processes</li>
        <li><strong>Traceable</strong> product quality &amp; certified management</li>
      </ul>
    </div>
    <div class="media" style="background-image:url('images/hero-factory.webp')"></div>
  </div>
</div></section>

<section class="section-alt"><div class="wrap">
  <div class="section-head"><div class="eyebrow">Capabilities</div><h2>What Our Factory Delivers</h2></div>
  <div class="grid grid-3">{fcards}</div>
</div></section>

<section><div class="wrap">
  <div class="stats-band"><div class="wrap" style="padding:0">
    {''.join(f'<div class="b"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v,l in STATS)}
  </div></div>
</div></section>

<section class="section-alt"><div class="wrap"><div class="cta">
  <h2>Need OEM / ODM or Bulk Supply?</h2>
  <p>Send your spec or brand requirements — we handle selection, design, factory supply and logistics.</p>
  <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="OEM/ODM & Bulk Supply" data-inquiry-title="OEM/ODM & Bulk Supply">Request Partnership</a></div>
</div></div></section>
'''
    return page("Factory & Capacity — Woneng Solar & Storage Manufacturing",
                "Woneng Zhaoqing factory: standardized workshops, 50,000 batteries/year, R&D, QC, OEM/ODM and global logistics for B2B solar and storage supply.",
                "solar factory China, energy storage manufacturer, OEM ODM solar, Woneng factory, battery production",
                body, active="factory.html", url="factory.html",
                og_image="images/hero-factory.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Factory & Capacity", "factory.html")]), org_ld()])

# ---------------- CERTIFICATIONS ----------------
def build_certs():
    cards = ""
    for name, std, desc in CERTS:
        cards += f'''<div class="card cert"><div class="badge">{esc(name[:4])}</div><h3>{esc(name)}</h3><div class="muted small">{esc(std)}</div><p class="small" style="margin-top:8px">{esc(desc)}</p></div>'''
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-products.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>Certifications</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Certifications</div>
    <h1>Certified &amp; Compliant</h1>
    <p>Full certification set to back your procurement and import confidence.</p>
  </div></div>
</section>
<section><div class="wrap">
  <div class="section-head"><div class="eyebrow">Quality &amp; Compliance</div><h2>International Certifications</h2>
    <p>Woneng products carry the certifications required for global B2B trade and import.</p></div>
  <div class="grid grid-4">{cards}</div>
  <div class="cta" style="margin-top:24px">
    <h2>Need Certificate Copies for Tender?</h2>
    <p>We provide full documentation packs for distributors and project bidding.</p>
    <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="Certification Documents" data-inquiry-title="Certification Documents Request">Request Documents</a></div>
  </div>
</div></section>
'''
    return page("Certifications — Woneng ISO/CE/RoHS/IEC Certified",
                "Woneng holds ISO9001, ISO14001, ISO45001, IATF16949, CE, RoHS, IEC, MSDS, UN38.3 and offers OEM/ODM customization for global B2B solar and storage trade.",
                "solar certification, CE RoHS IEC, ISO9001 solar, Woneng certified, battery MSDS UN38.3",
                body, active="certifications.html", url="certifications.html",
                og_image="images/hero-products.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Certifications", "certifications.html")]), org_ld()])

# ---------------- CONTACT ----------------
def build_contact():
    wa = SITE['whatsapp'].replace("+", "")
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-projects.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="breadcrumb"><a href="index.html">Home</a><span>/</span>Contact</div>
    <div class="eyebrow" style="color:#BBD6F2;letter-spacing:2px;text-transform:uppercase;font-size:13px;font-weight:700;margin:6px 0">Contact</div>
    <h1>Let's Build Your Project</h1>
    <p>Reach our international team for quotes, OEM/ODM and project support.</p>
  </div></div>
</section>

<section><div class="wrap">
  <div class="split">
    <div>
      <h2>Contact Information</h2>
      <ul class="flist">
        <li><strong>Email:</strong> {esc(SITE['email'])}</li>
        <li><strong>WhatsApp:</strong> {esc(SITE['whatsapp'])}</li>
        <li><strong>Factory:</strong> {esc(SITE['address'])}</li>
        <li><strong>Business:</strong> R&amp;D, production &amp; global export of PV systems, storage and LED street lights</li>
      </ul>
      <div style="margin-top:18px"><a class="btn btn-lg" href="https://wa.me/{wa}" target="_blank" rel="noopener">Chat on WhatsApp</a></div>
    </div>
    <div class="card">
      <h3>Send an Inquiry</h3>
      {inquiry_form(bp="", title="Website Contact")}
    </div>
  </div>
</div></section>
'''
    return page("Contact Woneng — Solar & Storage Manufacturer | Get a Quote",
                "Contact Woneng for solar street lights, flood lights and energy storage. Email, WhatsApp, factory address and B2B inquiry form for quotes and OEM/ODM.",
                "contact Woneng, solar manufacturer contact, request solar quote, Nigeria solar supplier, Woneng email",
                body, active="contact.html", url="contact.html",
                og_image="images/hero-projects.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Contact", "contact.html")]), org_ld()])

# ---------------- SEO FILES ----------------
def build_seo():
    # (path, priority, changefreq)
    pages = [
        ("index.html", 1.0, "daily"),
        ("products.html", 0.9, "weekly"),
        ("solutions.html", 0.9, "weekly"),
        ("about.html", 0.8, "monthly"),
        ("projects.html", 0.8, "monthly"),
        ("factory.html", 0.8, "monthly"),
        ("certifications.html", 0.7, "monthly"),
        ("contact.html", 0.6, "yearly"),
    ]
    for p in PRODUCTS:
        pages.append((f"products/{p['slug']}.html", 0.7, "weekly"))
    for s in SOLUTIONS:
        pages.append((f"solutions/{s['slug']}.html", 0.7, "weekly"))
    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f'  <url><loc>{BASE_URL}/{p}</loc><lastmod>{today}</lastmod>'
        f'<changefreq>{cf}</changefreq><priority>{pr}</priority></url>'
        for p, pr, cf in pages)
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>'''
    w("sitemap.xml", sitemap)
    w("robots.txt", f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml
""")

# ---------------- BUILD ALL ----------------
def main():
    w("index.html", build_home())
    w("about.html", build_about())
    w("products.html", build_products_index())
    for p in PRODUCTS:
        w(f"products/{p['slug']}.html", build_product(p))
    w("solutions.html", build_solutions_index())
    for s in SOLUTIONS:
        w(f"solutions/{s['slug']}.html", build_solution(s))
    w("projects.html", build_projects())
    w("factory.html", build_factory())
    w("certifications.html", build_certs())
    w("contact.html", build_contact())
    build_seo()
    # copy downloadable catalogs
    import shutil
    dl_src = {
        "Solar-Light-Catalog-2026.pdf": r"D:/网站/Solar Light Catalog 2026.pdf",
        "Solar-System-Brochure-2026.pdf": r"D:/网站/2026.5 Solar System Brochure.pdf",
    }
    dl_dir = os.path.join(OUT, "downloads")
    os.makedirs(dl_dir, exist_ok=True)
    for dst_name, src_path in dl_src.items():
        if os.path.exists(src_path):
            shutil.copy(src_path, os.path.join(dl_dir, dst_name))
    # copy assets
    for f in ["style.css", "main.js"]:
        src = os.path.join(os.path.dirname(__file__), "assets", f)
        dst = os.path.join(OUT, "css" if f.endswith(".css") else "js", f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
    print("Built", len(PRODUCTS) + len(SOLUTIONS) + 10, "pages + sitemap/robots")

if __name__ == "__main__":
    main()
