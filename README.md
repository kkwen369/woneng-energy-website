# Woneng Technology — Corporate Website

Static, responsive B2B corporate website for **肇庆市沃能高科技有限公司 (Woneng Technology / Entelechy Energy)**.

- Solar energy products: AIO lights, floodlights, garden / pole / portable lights, generators, inverters, power walls, racks, BESS, PV panels.
- Solutions, Projects (Nigeria, Zambia, Sri Lanka, Dubai, Indonesia, Malaysia), Factory & Capacity, Certifications.
- Built for Africa / Nigeria markets. Pure-English B2B copy, SEO-optimized (per-page meta, sitemap.xml, robots.txt).

## Structure
- `index.html`, `about.html`, `products.html`, `solutions.html`, `projects.html`, `factory.html`, `certifications.html`, `contact.html` + 12 product pages + 7 solution pages — static HTML
- `css/style.css`, `js/main.js` — front-end assets
- `images/` — WebP visual assets
- `sitemap.xml`, `robots.txt` — SEO

## Local preview
```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Deploy (GitHub Pages)
1. Push this repo to GitHub.
2. Repo **Settings → Pages → Source: Deploy from a branch → main / root**.
3. `.nojekyll` is already included so Jekyll won't rewrite the static files.
