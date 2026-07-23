# -*- coding: utf-8 -*-
"""Woneng Energy — site builder with SEO + UX improvements (2026-07 rebuild)."""
import os, datetime, json
from data import (SITE, NAV, CATEGORIES, PRODUCTS, SOLUTIONS, PROJECTS,
                  CERTS, STATS)
from scraped_products import SCRAPED_PRODUCTS

PRODUCTS = PRODUCTS + SCRAPED_PRODUCTS

def featured_products():
    return [p for p in PRODUCTS if p.get("featured", True)]

FORM_ENDPOINT = "https://api.web3forms.com/form"
FORM_KEY = "YOUR_WEB3FORMS_ACCESS_KEY"  # TODO: replace with real key from web3forms.com

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

# ---------- FAQ data for SEO ----------
FAQ_ITEMS = [
    ("What is the minimum order quantity (MOQ)?", "Our standard MOQ varies by product. For solar street lights, the MOQ is typically 50–100 units. For energy storage systems, MOQ is 10–20 units. We also support sample orders for initial evaluation — contact us for your specific product."),
    ("What payment methods do you accept?", "We accept T/T (bank transfer), L/C (letter of credit), PayPal, and Western Union. For first orders, 30% deposit + 70% before shipment is standard. Long-term partners may negotiate flexible terms."),
    ("What is the lead time / delivery time?", "Standard production lead time is 15–30 days depending on order quantity and product type. Custom OEM/ODM orders may take 30–45 days. We ship from Guangzhou/Shenzhen port to worldwide destinations."),
    ("Do you provide OEM/ODM services?", "Yes. We offer full OEM/ODM service including private-label branding, custom packaging, engineering modification, and project-specific design. Our R&D team supports you from concept to mass production."),
    ("What certifications do your products carry?", "Our products are certified with ISO 9001, ISO 14001, CE (multiple directives), and comply with international standards. We provide full documentation packs for tender/bidding purposes."),
    ("What warranty do you offer?", "All Woneng products carry a 3-year full-machine warranty. LiFePO4 batteries are rated for 6000+ cycles (10+ year service life). We provide after-sales support and replacement parts worldwide."),
    ("How do you handle shipping to Africa?", "We ship via sea freight (FCL or LCL) from Guangzhou/Shenzhen to major African ports including Lagos, Dar es Salaam, Mombasa, and Accra. We also support air freight for urgent orders. Delivery time is typically 25–40 days by sea."),
    ("Can I get a sample before bulk order?", "Yes, we welcome sample orders for quality evaluation. Sample pricing is available with fast delivery via air freight. Sample costs are refundable against your first bulk order."),
]

def inquiry_form(bp="", title="New Inquiry", product="", suffix=""):
    product_value = esc(product) if product else ""
    product_attr = f' value="{product_value}"' if product_value else ""
    s = esc(suffix) if suffix else ""
    id_pre = f"f-{s}-" if s else "f-"
    return f'''<form class="inquiry-form" action="{FORM_ENDPOINT}" method="POST" data-web3>
      <input type="hidden" name="access_key" value="{FORM_KEY}">
      <input type="hidden" name="subject" value="Woneng Inquiry — {esc(title)}">
      <input type="hidden" name="from_name" value="Woneng Website">
      <input type="text" name="company_website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true" style="display:none">
      <div class="form-grid">
        <div class="field"><label for="{id_pre}name">Name *</label><input id="{id_pre}name" name="name" required placeholder="Your full name"></div>
        <div class="field"><label for="{id_pre}company">Company *</label><input id="{id_pre}company" name="company" required placeholder="Your company name"></div>
        <div class="field"><label for="{id_pre}email">Email *</label><input id="{id_pre}email" type="email" name="email" required placeholder="you@company.com"></div>
        <div class="field"><label for="{id_pre}phone">WhatsApp / Phone</label><input id="{id_pre}phone" name="phone" placeholder="+234 … / phone number"></div>
        <div class="field"><label for="{id_pre}product">Product / Category</label><input id="{id_pre}product" name="product" placeholder="e.g. AIO Solar Street Light"{product_attr}></div>
        <div class="field"><label for="{id_pre}market">Target Market</label><input id="{id_pre}market" name="market" placeholder="e.g. Nigeria"></div>
        <div class="field full"><label for="{id_pre}msg">Quantity &amp; Project Need</label><textarea id="{id_pre}msg" name="message" placeholder="Tell us your quantity, project type and timeline..."></textarea></div>
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
        "logo": BASE_URL + "/favicon.svg",
        "email": SITE["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["address"],
            "addressLocality": "Zhaoqing",
            "addressRegion": "Guangdong",
            "addressCountry": "CN",
        },
        "contactPoint": [{
            "@type": "ContactPoint",
            "telephone": SITE["whatsapp"].replace(" ", ""),
            "contactType": "sales",
            "areaServed": "Worldwide",
            "availableLanguage": ["English", "Chinese"],
        }],
        "sameAs": [v for k, v in [
            ("linkedin", SITE.get("linkedin", "")),
            ("youtube", SITE.get("youtube", "")),
            ("fb", SITE.get("fb", "")),
        ] if v],
    }

def website_ld():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE["brand"],
        "url": BASE_URL + "/",
        "publisher": {"@type": "Organization", "name": SITE["brand_full"]},
        "potentialAction": {
            "@type": "SearchAction",
            "target": BASE_URL + "/products.html?q={search_term_string}",
            "query-input": "required name=search_term_string",
        },
    }

def faq_ld():
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQ_ITEMS
        ],
    }

def breadcrumb_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "name": n, "item": BASE_URL + "/" + u}
            for i, (n, u) in enumerate(items)
        ],
    }

# ---------- Cookie consent banner ----------
COOKIE_BANNER = '''<div class="cookie-banner" id="cookieBanner">
  <div class="wrap">
    <p>We use cookies to improve your experience and analyze site traffic. By continuing, you agree to our <a href="privacy.html">Privacy Policy</a>.</p>
    <button class="btn btn-sm" onclick="document.getElementById('cookieBanner').style.display='none';localStorage.setItem('cookieOk','1')">Accept</button>
  </div>
</div>'''

# ---------- Skip-to-content link ----------
SKIP_LINK = '<a href="#main" class="skip-link">Skip to content</a>'

# ---------- Shared chrome ----------
def head(title, desc, kw, bp="", url="", og_image="", og_type="website", json_ld=None):
    canonical = BASE_URL + "/" + url if url else BASE_URL + "/"
    ogimg = (BASE_URL + "/" + og_image) if og_image else (BASE_URL + "/images/hero-home.webp")
    jld = ""
    if json_ld:
        jld = "".join(jsonld(d) for d in json_ld) if isinstance(json_ld, list) else jsonld(json_ld)
    favicon_bp = bp if bp else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="keywords" content="{esc(kw)}">
<meta name="author" content="{esc(SITE['brand_full'])}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<link rel="icon" type="image/svg+xml" href="{favicon_bp}favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{favicon_bp}favicon-32.png">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(SITE['brand_full'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ogimg}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{ogimg}">
<meta name="twitter:site" content="@woneng_energy">
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
      <span class="logo" aria-hidden="true">W</span>
      <span>Woneng<small>SOLAR &amp; STORAGE</small></span>
    </a>
    <button class="nav-toggle" aria-label="Open navigation menu"><span></span><span></span><span></span></button>
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
    social_links = ""
    if SITE.get("linkedin"):
        social_links += f'<li><a href="{esc(SITE["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a></li>'
    if SITE.get("youtube"):
        social_links += f'<li><a href="{esc(SITE["youtube"])}" target="_blank" rel="noopener">YouTube</a></li>'
    if SITE.get("fb"):
        social_links += f'<li><a href="{esc(SITE["fb"])}" target="_blank" rel="noopener">Facebook</a></li>'
    social_html = f'<div class="foot-col"><h4>Follow Us</h4><ul>{social_links}</ul></div>' if social_links else ""
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="brand" href="{bp}index.html"><span class="logo" aria-hidden="true">W</span><span>Woneng<small>SOLAR &amp; STORAGE</small></span></a>
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
        <li><a href="{bp}news.html">News</a></li>
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
    {social_html}
  </div>
  <div class="wrap foot-bottom">
    <span>&copy; <span id="year"></span> {esc(SITE['brand_full'])}. All rights reserved. <a href="{bp}privacy.html" style="color:#7E8FA1">Privacy Policy</a></span>
    <span>Factory Direct &middot; Wholesale &middot; OEM/ODM &middot; Global Export</span>
  </div>
</footer>'''

WHATSAPP_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.99 6.45 17.5 2 12.04 2zm5.8 14.14c-.25.69-1.45 1.32-1.99 1.36-.53.04-1.07.24-3.6-.75-2.99-1.14-4.9-4.05-5.05-4.24-.15-.19-1.18-1.57-1.18-3 0-1.42.75-2.12 1.01-2.41.26-.29.57-.36.76-.36.19 0 .38 0 .55.01.18.01.41-.07.64.49.25.59.84 2.03.91 2.18.07.15.12.32.02.52-.1.19-.15.31-.29.48-.15.18-.31.39-.45.53-.15.15-.3.31-.13.6.17.29.74 1.22 1.59 1.98 1.09.97 2.01 1.27 2.3 1.41.29.14.46.12.63-.07.18-.19.74-.86.94-1.16.2-.3.4-.25.67-.15.28.1 1.77.84 2.07 1 .3.16.5.24.57.37.08.14.08.79-.17 1.48z"/></svg>'

def inquiry_widget(bp=""):
    """Right-side slide-out inquiry panel with vertical tab."""
    wa = SITE['whatsapp'].replace("+", "")
    tab_icon = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
    return f'''<div class="drawer-overlay" id="drawerOverlay" aria-hidden="true"></div>
<div class="inquiry-drawer" id="inquiryDrawer" aria-hidden="true">
  <div class="drawer-head">
    <div>
      <div class="drawer-title">Click Here To Get Free Quote</div>
      <div class="drawer-sub">Factory-direct pricing in 24 hours</div>
    </div>
    <button class="drawer-close" aria-label="Close quote panel">×</button>
  </div>
  <div class="drawer-body">
    {inquiry_form(bp, "Request a Quote", suffix="drawer")}
  </div>
</div>
<a class="inquiry-tab" href="#" id="inquiryTab" aria-label="Open quote form">
  <span class="tab-icon" aria-hidden="true">{tab_icon}</span>
  <span class="tab-text">Get Free Quote</span>
</a>
<a class="whatsapp-tab" href="https://wa.me/{wa}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">
  {WHATSAPP_SVG}
</a>'''

def scripts(bp="", needs_supabase=False):
    s = f'<script src="{bp}js/main.js"></script>'
    if needs_supabase:
        s = f'<script src="{bp}js/supabase-config.js"></script><script src="{bp}js/site-supabase.js"></script>' + s
    return s

def page(title, desc, kw, body, active="", bp="", banner=None, breadcrumb=None,
          og_image="", og_type="website", json_ld=None, url="", needs_supabase=False):
    """Full page assembly."""
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
      <div class="eyebrow">{esc(eyebrow)}</div>
      <h1>{esc(btitle)}</h1>
      <p>{esc(bsub)}</p>
    </div>
  </div>
</section>'''
    # Cookie banner: show only if localStorage doesn't have cookieOk
    cookie_script = '''<script>if(!localStorage.getItem('cookieOk'))document.getElementById('cookieBanner').style.display='flex';</script>'''
    return (head(title, desc, kw, bp, url=url, og_image=og_image,
                 og_type=og_type, json_ld=json_ld) +
            '<body>' + SKIP_LINK + header(active, bp) +
            '<main id="main">' + h + body + '</main>' +
            inquiry_widget(bp) +
            COOKIE_BANNER + cookie_script +
            footer(bp) + scripts(bp, needs_supabase) + '</body></html>')

# ---------- FAQ section (used on home) ----------
def faq_section():
    items = "".join(
        f'<div class="acc"><button>{esc(q)}</button><div class="pane"><p>{esc(a)}</p></div></div>'
        for q, a in FAQ_ITEMS)
    return f'''<section class="section-alt">
  <div class="wrap">
    <div class="section-head"><div class="eyebrow">Common Questions</div><h2>Frequently Asked Questions</h2></div>
    <div class="faq-list">{items}</div>
  </div>
</section>'''

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

    ADV_ICONS = {
        "factory": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20h20"/><path d="M5 20v-8l6-4 6 4v8"/><path d="M11 20v-6"/><path d="M15 20v-6"/></svg>',
        "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2"/><path d="M12 21v2"/><path d="M4.22 4.22l1.42 1.42"/><path d="M18.36 18.36l1.42 1.42"/><path d="M1 12h2"/><path d="M21 12h2"/><path d="M4.22 19.78l1.42-1.42"/><path d="M18.36 5.64l1.42-1.42"/></svg>',
        "wrench": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    }
    adv = [
        ("factory", "Factory Direct", "Own standardized plant in Zhaoqing — wholesale pricing, no middle layer."),
        ("globe", "Team 15+ Years", "Deep industry experience serving distributors, EPC contractors and governments."),
        ("sun", "Africa Focused", "Heat, dust and unstable-grid ready products for Nigeria &amp; Africa."),
        ("wrench", "OEM / ODM", "Private label, engineering customization and global logistics."),
    ]
    adv_cards = "".join(f'<div class="card adv"><div class="ic">{ADV_ICONS[k]}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for k, t, d in adv)

    stats = "".join(f'<div class="b"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in STATS)

    proj_cards = ""
    for p in PROJECTS[:3]:
        proj_cards += f'''<a class="card pcard" href="projects.html">
          <div class="thumb" style="background-image:url('images/projects/{os.path.basename(p['img'])}')"></div>
          <div class="body"><h2>{esc(p['country'])}</h2><div class="meta">{esc(p['title'])}</div><div class="more">View project →</div></div></a>'''

    markets = ["Nigeria", "Zambia", "South Africa", "Kenya", "Ghana", "Sri Lanka", "Indonesia", "Malaysia", "UAE", "Philippines"]

    # Trade info strip
    trade_info = '''<div class="trade-strip"><div class="wrap">
  <div class="trade-items">
    <div class="trade-item"><strong>MOQ:</strong> 50–100 units (samples available)</div>
    <div class="trade-item"><strong>Payment:</strong> T/T, L/C, PayPal, Western Union</div>
    <div class="trade-item"><strong>Lead Time:</strong> 15–30 days standard</div>
    <div class="trade-item"><strong>Shipping:</strong> Sea freight FCL/LCL from Guangzhou</div>
  </div>
</div></div>'''

    # Homepage bottom inquiry section: contact info (left) + embedded form (right)
    email = SITE['email']
    wa = SITE['whatsapp'].replace("+", "")
    address = SITE['address']
    email_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/></svg>'
    pin_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
    home_inquiry = f'''
<section class="home-inquiry">
  <div class="wrap">
    <div class="inquiry-wrap">
      <div class="inquiry-info">
        <div class="eyebrow">Talk To Our Team</div>
        <h2>Get a Factory-Direct Quote Today</h2>
        <p>Reach our export team by email, WhatsApp or the form — we respond within 24 hours with pricing, specs and shipping options tailored to your market.</p>
        <div class="contact-item">
          <span class="ci" aria-hidden="true">{email_svg}</span>
          <div><b>Email</b><span><a href="mailto:{email}">{email}</a></span></div>
        </div>
        <div class="contact-item">
          <span class="ci" aria-hidden="true">{WHATSAPP_SVG}</span>
          <div><b>WhatsApp</b><span><a href="https://wa.me/{wa}" target="_blank" rel="noopener">+{wa}</a></span></div>
        </div>
        <div class="contact-item">
          <span class="ci" aria-hidden="true">{pin_svg}</span>
          <div><b>Factory Address</b><span>{esc(address)}</span></div>
        </div>
      </div>
      <div class="inquiry-form-card">
        {inquiry_form(bp="", title="Homepage Inquiry", suffix="contact")}
      </div>
    </div>
  </div>
</section>
'''

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

{trade_info}

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
          <li><strong>ISO 9001 + ISO 14001 + CE</strong> certified manufacturing</li>
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

{faq_section()}

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

{home_inquiry}
'''
    return page("Woneng — Solar Street Lights & Energy Storage Manufacturer | Factory Direct",
                "Woneng is a B2B manufacturer of solar street lights, solar flood lights and LiFePO4 energy storage systems. Factory direct wholesale, OEM/ODM, Africa & Nigeria off-grid solar solutions. MOQ 50 units, T/T L/C PayPal payment, 15-30 day lead time.",
                "solar street light manufacturer, solar energy storage, Nigeria solar street light, Africa off-grid solar system, solar flood light, Powerwall battery, Woneng, factory direct, OEM ODM solar, wholesale solar lighting",
                body, active="index.html", url="index.html",
                og_image="images/hero-home.webp",
                json_ld=[org_ld(), website_ld(), faq_ld()],
                needs_supabase=True)

# ---------------- ABOUT ----------------
def build_about():
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-factory.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">Established 2023 · Team 15+ Years</div>
    <h1>A Trusted New-Energy Export Partner</h1>
    <p>A team with 15+ years of solar industry experience, now delivering reliable PV and storage solutions through Woneng.</p>
  </div></div>
</section>

<section>
  <div class="wrap">
    <div class="split">
      <div>
        <h2>Who We Are</h2>
        <p>Zhaoqing Woneng High-Tech Co., Ltd. (established 2023) is an international export enterprise dedicated to the new-energy photovoltaic and energy-storage industry, integrating independent R&amp;D, standardized production, global sales and customized solution services.</p>
        <p>Our core team brings over 15 years of combined experience in solar manufacturing, export operations and overseas project delivery. Based in Zhaoqing, Guangdong — a core manufacturing base for new-energy equipment in South China — we own standardized production workshops and a complete industrial-chain supply network.</p>
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
    <div class="stats-band"><div class="wrap">
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
                "Zhaoqing Woneng High-Tech Co., Ltd. (est. 2023) — a B2B new-energy exporter built on 15+ years of team solar industry experience, focused on Africa and global off-grid markets.",
                "about Woneng, solar manufacturer China, Zhaoqing Woneng, solar street light factory, energy storage manufacturer, Woneng company profile",
                body, active="about.html", url="about.html",
                og_image="images/hero-factory.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("About Us", "about.html")]), org_ld()])

# ---------------- PRODUCTS INDEX ----------------
def build_products_index():
    groups = series_groups()
    cats = [("all", "All Products")] + [(cid, cname) for cname, cid in CATEGORIES]
    filter_btns = "".join(
        f'<button class="chip-filter{" active" if cid == "all" else ""}" data-cat="{cid}">{esc(cname)}</button>'
        for cid, cname in cats)
    body_groups = ""
    for i, (slug, name, cat, items) in enumerate(groups):
        cards = "".join(product_card(p) for p in items)
        # Only first series open, rest collapsed for UX
        open_attr = " open" if i == 0 else ""
        body_groups += f'''<details class="series"{open_attr} data-cat="{esc(cat)}">
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
    <div class="eyebrow">Product Series</div>
    <h1>Solar Lighting &amp; Energy Storage Products</h1>
    <p>Browse by product series — click a series to see all models, specs and inquiry pages.</p>
  </div></div>
</section>
<section><div class="wrap">
  <div class="cat-filter">{filter_btns}</div>
  <div class="series-list">{body_groups}</div>
  <div class="trade-strip" style="margin-top:28px"><div class="wrap">
    <div class="trade-items">
      <div class="trade-item"><strong>MOQ:</strong> 50–100 units (samples available)</div>
      <div class="trade-item"><strong>Payment:</strong> T/T, L/C, PayPal</div>
      <div class="trade-item"><strong>Lead Time:</strong> 15–30 days</div>
      <div class="trade-item"><strong>Shipping:</strong> Sea freight FCL/LCL</div>
    </div>
  </div></div>
  <div class="cta" style="margin-top:28px">
    <h2>Can't find the exact model?</h2>
    <p>We do OEM/ODM and project customization. Send us your spec sheet.</p>
    <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="Custom OEM/ODM Request" data-inquiry-title="Custom OEM/ODM Request">Request Custom Build</a></div>
  </div>
</div></section>
'''
    return page("Products — Solar Street Lights & Energy Storage | Woneng",
                "Woneng product catalog by series: AIO/split solar street lights, solar flood lights, garden & decorative lights, portable & container storage, hybrid inverters, Powerwall and rack batteries, PV accessories. MOQ 50 units.",
                "solar street light, solar flood light, portable energy storage, hybrid inverter, Powerwall battery, rack battery, BESS, PV accessories, Woneng products, buy solar street light wholesale",
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
    # MOQ + trade info box
    trade_box = '''<div class="trade-box">
  <h3>Trade Information</h3>
  <table class="spectable"><tbody>
    <tr><th>MOQ</th><td>50–100 units (sample orders available)</td></tr>
    <tr><th>Payment</th><td>T/T, L/C, PayPal, Western Union</td></tr>
    <tr><th>Lead Time</th><td>15–30 days (standard); 30–45 days (OEM/ODM)</td></tr>
    <tr><th>Shipping</th><td>Sea freight FCL/LCL from Guangzhou/Shenzhen</td></tr>
    <tr><th>Warranty</th><td>3 years full machine; 6000+ cycles battery life</td></tr>
    <tr><th>Port</th><td>Guangzhou / Shenzhen</td></tr>
  </tbody></table>
</div>'''
    sslug = classify_series(p)[0]
    sibs = [x for x in PRODUCTS if classify_series(x)[0] == sslug]
    switcher = ""
    for x in sibs:
        if x["slug"] == slug:
            switcher += f'<span class="sw active" aria-current="true">{esc(x["models"])}</span>'
        else:
            switcher += f'<a class="sw" href="{x["slug"]}.html">{esc(x["models"])}</a>'
    rel = [x for x in sibs if x["slug"] != slug][:3]
    if not rel:
        rel = [x for x in PRODUCTS if x["cat"] == p["cat"] and x["slug"] != slug][:3]
    rel_cards = "".join(product_card(x, bp="../") for x in rel)
    sol_link = SOLUTIONS[0]
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('../images/hero-products.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">{esc(p['cat_name'])}</div>
    <h1>{esc(p['name'])}</h1>
    <p>{esc(p['tagline'])}</p>
  </div></div>
</section>
<div class="breadcrumbs-bar"><div class="wrap"><a href="../index.html">Home</a><span>/</span><a href="../products.html">Products</a><span>/</span>{esc(p['name'])}</div></div>

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
    {trade_box}
  </div>
</div></div></section>

<section><div class="wrap">
  <h2 class="h-sm">Applications</h2>
  <div class="chips" style="margin:12px 0 20px">{app_chips}</div>
  <a class="btn" href="../solutions/{sol_link['slug']}.html">See Matching Solution →</a>
</div></section>

{('<section class="section-alt"><div class="wrap"><div class="section-head"><div class="eyebrow">Related</div><h2>From the Same Series</h2></div><div class="grid grid-3">'+rel_cards+'</div></div></section>') if rel_cards else ''}

<section class="section-alt"><div class="wrap">
  <div class="inquiry-card">
    <div class="section-head center" style="margin-bottom:24px">
      <div class="eyebrow">Get a Quote</div>
      <h2>Send an Inquiry</h2>
      <p>Tell us quantity, market and timeline — factory-direct pricing in 24h.</p>
    </div>
    {inquiry_form(bp="../", title=f"Quote: {p['name']}", product=p['name'], suffix="page")}
  </div>
</div></section>
'''
    p_url = f"products/{slug}.html"
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
            "priceSpecification": {
                "@type": "PriceSpecification",
                "priceCurrency": "USD",
                "minPrice": "0",
                "valueAddedTaxIncluded": False,
            },
            "eligibleQuantity": {
                "@type": "QuantitativeValue",
                "minValue": 50,
                "unitCode": "C62",
            },
            "seller": {"@type": "Organization", "name": SITE["brand_full"]},
        },
    }
    bc_ld = breadcrumb_ld([("Home", "index.html"), ("Products", "products.html"), (p["name"], p_url)])
    return page(f"{p['name']} — {p['cat_name']} | Woneng",
                f"{p['name']} by Woneng: {p['tagline']} Models {p['models']}. Factory-direct B2B pricing, OEM/ODM, global export. MOQ 50 units, 3-year warranty.",
                f"{p['name']}, {p['cat_name']}, Woneng, solar, Nigeria, Africa, wholesale, OEM, buy solar street light, {p['models']}",
                body, active="products.html", bp="../", url=p_url,
                og_image=p["img"], json_ld=[bc_ld, product_ld])

# ---------------- SOLUTIONS ----------------
def build_solutions_index():
    cards = ""
    for s in SOLUTIONS:
        cards += f'''<a class="card pcard" href="solutions/{s['slug']}.html">
          <div class="thumb" style="background-image:url('{s['img']}')"></div>
          <div class="body"><h2>{esc(s['title'])}</h2><div class="meta">B2B solution</div><div class="more">View solution →</div></div></a>'''
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-solutions.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">B2B Solutions</div>
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
    pts = "".join(f'<li>{esc(x)}</li>' for x in s["points"])
    # Add recommended products from the solution's category
    # Find matching products based on solution keywords
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('{simg}')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">Solution</div>
    <h1>{esc(s['title'])}</h1>
    <p>{esc(s['lead'])}</p>
  </div></div>
</section>
<div class="breadcrumbs-bar"><div class="wrap"><a href="../index.html">Home</a><span>/</span><a href="../solutions.html">Solutions</a><span>/</span>{esc(s['title'])}</div></div>
<section><div class="wrap">
  <div class="split">
    <div class="media" style="background-image:url('{simg}')"></div>
    <div>
      <h2>What's Included</h2>
      <ul class="flist">{pts}</ul>
      <div class="trade-strip" style="margin-top:18px"><div class="wrap" style="padding:16px 20px">
        <div class="trade-items">
          <div class="trade-item"><strong>MOQ:</strong> Project-based</div>
          <div class="trade-item"><strong>Payment:</strong> T/T, L/C</div>
          <div class="trade-item"><strong>Design:</strong> Free system sizing</div>
        </div>
      </div></div>
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
                f"{s['title']}: {s['lead']} Woneng B2B solar & storage solutions for Africa and global markets. Free system design, factory-direct quote.",
                f"{s['title']}, Woneng solution, Nigeria, Africa, solar, off-grid, solar solution provider",
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
            <h2>{esc(p['title'])}</h2>
            <p>{esc(p['desc'])}</p>
            <div class="chips">{chips}</div>
          </div></div>'''

    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-projects.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">Global References</div>
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
                "Woneng overseas projects: Nigeria, Zambia, Sri Lanka, Dubai, Indonesia and Malaysia solar street lighting, storage and micro-grid deployments. Proven delivery capability.",
                "solar project Nigeria, Zambia solar, Dubai solar storage, Sri Lanka lighting, Indonesia microgrid, Woneng projects, solar deployment Africa",
                body, active="projects.html", url="projects.html",
                og_image="images/hero-projects.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Projects", "projects.html")]), org_ld()])

# ---------------- FACTORY ----------------
def build_factory():
    FACTORY_ICONS = {
        "workshop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20h20"/><path d="M5 20v-8l6-4 6 4v8"/><path d="M11 20v-6"/><path d="M15 20v-6"/></svg>',
        "battery": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="12" height="16" rx="2"/><path d="M9 2v2"/><path d="M15 2v2"/><path d="M9 10h6"/><path d="M9 14h6"/></svg>',
        "rd": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-7 7c0 2.4 1.2 4.5 3 5.7V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2.3c1.8-1.2 3-3.3 3-5.7a7 7 0 0 0-7-7z"/></svg>',
        "qc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>',
        "oem": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        "logistics": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="15" height="10" rx="2"/><path d="M17 12h3l2 3v3h-5v-6z"/><circle cx="6.5" cy="18.5" r="1.5"/><circle cx="18.5" cy="18.5" r="1.5"/></svg>',
    }
    feats = [
        ("workshop", "Standardized Workshops", "Complete production, testing and QC flows under one roof."),
        ("battery", "Self-developed Battery", "Nano-magnesium-silicon cells, 50,000 units/year, extreme-temp."),
        ("rd", "R&D Team", "In-house engineers for product and solution innovation."),
        ("qc", "QC System", "Traceable quality, certified environmental compliance."),
        ("oem", "OEM / ODM", "Private label, engineering customization, flexible MOQ."),
        ("logistics", "Global Logistics", "Factory-direct supply, worldwide delivery &amp; overseas support."),
    ]
    fcards = "".join(f'<div class="card adv"><div class="ic">{FACTORY_ICONS[k]}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for k, t, d in feats)
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-factory.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">Factory &amp; Capacity</div>
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
  <div class="stats-band"><div class="wrap">
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
                "solar factory China, energy storage manufacturer, OEM ODM solar, Woneng factory, battery production, Zhaoqing solar manufacturer",
                body, active="factory.html", url="factory.html",
                og_image="images/hero-factory.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Factory & Capacity", "factory.html")]), org_ld()])

# ---------------- CERTIFICATIONS ----------------
def build_certs():
    cards = ""
    for name, std, desc, img in CERTS:
        cards += f'''<div class="card cert"><a class="cert-thumb" href="{esc(img)}" target="_blank" rel="noopener" aria-label="View {esc(name)} certificate"><img src="{esc(img)}" alt="{esc(name)} {esc(std)} certificate" loading="lazy"></a><h3>{esc(name)}</h3><div class="muted small">{esc(std)}</div><p class="small" style="margin-top:8px">{esc(desc)}</p></div>'''
    body = f'''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-products.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">Quality &amp; Compliance</div>
    <h1>Certified &amp; Compliant</h1>
    <p>Certifications that back your procurement and import confidence.</p>
  </div></div>
</section>
<section><div class="wrap">
  <div class="section-head"><div class="eyebrow">Quality &amp; Compliance</div><h2>International Certifications</h2>
    <p>Woneng products carry certifications required for global B2B trade and import.</p></div>
  <div class="grid grid-4">{cards}</div>
  <div class="cta" style="margin-top:24px">
    <h2>Need Certificate Copies for Tender?</h2>
    <p>We provide full documentation packs for distributors and project bidding.</p>
    <div class="hero-actions"><a class="btn btn-lg btn-light" href="#" data-inquiry="Certification Documents" data-inquiry-title="Certification Documents Request">Request Documents</a></div>
  </div>
</div></section>
'''
    # Only mention certs we actually have: ISO 9001, ISO 14001, CE
    return page("Certifications — Woneng ISO & CE Certified Manufacturer",
                "Woneng holds ISO 9001, ISO 14001 and CE certifications for solar street lights and energy storage products. We provide full documentation packs for tender/bidding.",
                "solar certification, CE certified, ISO9001 solar, Woneng certified, solar product compliance",
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
    <div class="eyebrow">Get in Touch</div>
    <h1>Let's Build Your Project</h1>
    <p>Reach our international team for quotes, OEM/ODM and project support.</p>
  </div></div>
</section>

<section><div class="wrap">
  <div class="split">
    <div>
      <h2>Contact Information</h2>
      <ul class="flist">
        <li><strong>Email:</strong> <a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a></li>
        <li><strong>WhatsApp:</strong> <a href="https://wa.me/{wa}" target="_blank" rel="noopener">{esc(SITE['whatsapp'])}</a></li>
        <li><strong>Factory:</strong> {esc(SITE['address'])}</li>
        <li><strong>Business:</strong> R&amp;D, production &amp; global export of PV systems, storage and LED street lights</li>
        <li><strong>Hours:</strong> Mon–Sat 9:00–18:00 (GMT+8, China Standard Time)</li>
      </ul>
      <div style="margin-top:18px;display:flex;gap:12px;flex-wrap:wrap">
        <a class="btn btn-lg" href="https://wa.me/{wa}" target="_blank" rel="noopener">Chat on WhatsApp</a>
        <a class="btn btn-lg btn-ghost" href="mailto:{esc(SITE['email'])}">Email Us</a>
      </div>
    </div>
    <div class="card">
      <h3>Send an Inquiry</h3>
      {inquiry_form(bp="", title="Website Contact", suffix="contact")}
    </div>
  </div>
</div></section>

<section class="section-alt"><div class="wrap"><div class="cta">
  <h2>Quick Response Promise</h2>
  <p>Our international sales team replies within 24 hours on business days. Urgent inquiries get priority handling.</p>
</div></div></section>
'''
    return page("Contact Woneng — Solar & Storage Manufacturer | Get a Quote",
                "Contact Woneng for solar street lights, flood lights and energy storage. Email, WhatsApp, factory address and B2B inquiry form for quotes and OEM/ODM.",
                "contact Woneng, solar manufacturer contact, request solar quote, Nigeria solar supplier, Woneng email, WhatsApp solar supplier",
                body, active="contact.html", url="contact.html",
                og_image="images/hero-projects.webp",
                json_ld=[breadcrumb_ld([("Home", "index.html"), ("Contact", "contact.html")]), org_ld()])

# ---------------- 404 PAGE ----------------
def build_404():
    body = '''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-home.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist or has been moved.</p>
  </div></div>
</section>

<section><div class="wrap">
  <div class="cta">
    <h2>Let's Get You Back on Track</h2>
    <p>Try one of these links, or search our product catalog.</p>
    <div class="hero-actions">
      <a class="btn btn-lg btn-light" href="index.html">Go to Homepage</a>
      <a class="btn btn-lg btn-light" href="products.html">Browse Products</a>
      <a class="btn btn-lg btn-light" href="contact.html">Contact Us</a>
    </div>
  </div>
</div></section>
'''
    return page("404 — Page Not Found | Woneng",
                "The page you're looking for doesn't exist. Return to Woneng's homepage or browse our solar street light and energy storage product catalog.",
                "Woneng 404, page not found",
                body, url="404.html")

# ---------------- PRIVACY PAGE ----------------
def build_privacy():
    body = '''
<section class="pagebanner">
  <div class="hero-bg" style="background-image:url('images/hero-factory.webp')"></div>
  <div class="pagebanner-inner"><div class="wrap">
    <div class="eyebrow">Legal</div>
    <h1>Privacy Policy</h1>
    <p>How we collect, use and protect your personal information.</p>
  </div></div>
</section>

<section><div class="wrap">
  <h2>Data We Collect</h2>
  <p>When you submit an inquiry form, we collect: your name, company name, email address, phone/WhatsApp number, target market, and project details. This information is used solely to respond to your inquiry and provide relevant product quotations.</p>

  <h2>How We Use Your Data</h2>
  <p>Your data is used to:</p>
  <ul class="flist">
    <li>Respond to your product or project inquiry</li>
    <li>Send relevant quotation documents and technical specifications</li>
    <li>Follow up on project discussions (with your consent)</li>
    <li>Improve our website content and user experience</li>
  </ul>

  <h2>Data Protection</h2>
  <p>We do not sell, share or distribute your personal information to third parties for marketing purposes. Your data is stored securely and accessible only by our authorized sales team.</p>

  <h2>Cookies</h2>
  <p>We use essential cookies to ensure website functionality and analytics cookies to understand how visitors use our site. You can disable cookies in your browser settings, though some features may not work properly.</p>

  <h2>Your Rights</h2>
  <p>You may request access to, correction of, or deletion of your personal data at any time by contacting us at the email address below. We comply with applicable data protection regulations.</p>

  <h2>Contact</h2>
  <p>For privacy-related inquiries, contact us at: <a href="mailto:sales@woneng-energy.com">sales@woneng-energy.com</a></p>
  <p class="muted small">Last updated: July 2026</p>
</div></section>
'''
    return page("Privacy Policy | Woneng",
                "Woneng privacy policy: how we collect, use and protect your personal data when you submit inquiries on our B2B solar and energy storage website.",
                "privacy policy, Woneng, data protection, solar website privacy",
                body, url="privacy.html",
                json_ld=[org_ld()])

# ---------------- SEO FILES ----------------
def build_seo():
    pages = [
        ("index.html", 1.0, "daily"),
        ("products.html", 0.9, "weekly"),
        ("solutions.html", 0.9, "weekly"),
        ("about.html", 0.8, "monthly"),
        ("projects.html", 0.8, "monthly"),
        ("factory.html", 0.8, "monthly"),
        ("certifications.html", 0.7, "monthly"),
        ("news.html", 0.7, "weekly"),
        ("privacy.html", 0.3, "yearly"),
        ("404.html", 0.1, "yearly"),
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
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{urls}
</urlset>'''
    w("sitemap.xml", sitemap)
    # robots.txt — block admin, build_src, and internal pages
    w("robots.txt", f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /build_src/
Disallow: /*.py$
Disallow: /后台系统上线指南.md

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
    w("404.html", build_404())
    w("privacy.html", build_privacy())
    build_seo()
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
    for f in ["style.css", "main.js"]:
        src = os.path.join(os.path.dirname(__file__), "assets", f)
        dst = os.path.join(OUT, "css" if f.endswith(".css") else "js", f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
    # Copy favicon files
    for f in ["favicon.svg", "favicon-32.png"]:
        src = os.path.join(os.path.dirname(__file__), "assets", f)
        dst = os.path.join(OUT, f)
        if os.path.exists(src):
            shutil.copy(src, dst)
    print("Built", len(PRODUCTS) + len(SOLUTIONS) + 12, "pages + sitemap/robots")

if __name__ == "__main__":
    main()
