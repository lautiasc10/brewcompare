#!/usr/bin/env python3
"""
BrewCompare — static site generator.

Reads  datos/productos.json  +  datos/schema.json
Writes every page of the site, plus lib/db.js for the client-side layer.

No product page is ever hand-written. Adding a machine = adding a record to
productos.json and re-running this script.

    python3 tools/build_site.py

Core facts (name, price, buy button, spec table, editorial, disclosure, JSON-LD
and a fully drawn radar chart) are baked into the HTML, so every page renders
correctly with JavaScript disabled. JS only enriches: gallery switching, the
comparator, filtering, reveals.
"""

import json
import math
import pathlib
import datetime
import html as htmllib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "datos"

# Cache-buster. Bumped on EVERY build, not just deploys (gotcha E.5).
VER = datetime.datetime.now().strftime("%Y%m%d%H%M")
BUILD_DATE = datetime.date.today().isoformat()

db = json.loads((DATA / "productos.json").read_text(encoding="utf-8"))
schema = json.loads((DATA / "schema.json").read_text(encoding="utf-8"))

SITE = db["site"]
PRODUCTS = db["products"]
GUIDES = db["guides"]
CATEGORIES = schema["categories"]
SPECS = schema["specs"]
SPEC_GROUPS = schema["spec_groups"]
SCORES = schema["scores"]

BY_ID = {p["id"]: p for p in PRODUCTS}
CAT_BY_ID = {c["id"]: c for c in CATEGORIES}
SPEC_BY_KEY = {s["key"]: s for s in SPECS}

SITE_URL = (SITE.get("url") or "").rstrip("/")


# ---------------------------------------------------------------- helpers ---
def e(s):
    """Escape for HTML text/attribute context."""
    return htmllib.escape("" if s is None else str(s), quote=True)


def money(v):
    if v is None:
        return None
    return f"${v:,.2f}".replace(".00", "")


def product_url(p):
    return f"machine-{p['id']}.html"


def category_url(c):
    return f"category-{c['id']}.html"


def guide_url(g):
    return f"guide-{g['id']}.html"


def affiliate_url(p):
    """Invariant 1: the user's link is sacred. If a record carries an explicit
    affiliate_url we use it verbatim; otherwise we build the canonical Amazon
    URL and append the site-wide associate tag."""
    if p.get("affiliate_url"):
        return p["affiliate_url"]
    tag = SITE.get("affiliate_tag", "")
    return f"https://www.amazon.com/dp/{p['asin']}?tag={tag}"


def is_deal(p):
    return p.get("sale_price") is not None and p.get("retail_price") is not None \
        and p["sale_price"] < p["retail_price"]


def discount_pct(p):
    if not is_deal(p):
        return 0
    return round(100 * (p["retail_price"] - p["sale_price"]) / p["retail_price"])


def current_price(p):
    return p.get("sale_price") if p.get("sale_price") is not None else p.get("retail_price")


def in_category(cat_id):
    return [p for p in PRODUCTS if cat_id in p.get("categories", [])]


def avg_score(p):
    vals = [p["scores"].get(s["key"]) for s in SCORES]
    vals = [v for v in vals if isinstance(v, (int, float))]
    return sum(vals) / len(vals) if vals else 0


# ------------------------------------------------------------------ icons ---
# Every icon carries class="ic" and the stylesheet sizes .ic in every context
# it can appear in (gotcha E.1 — an unsized inline SVG expands to 300x150).
def _ic(path, extra=""):
    return (f'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" {extra}>{path}</svg>')


IC = {
    "check":   _ic('<polyline points="20 6 9 17 4 12"/>'),
    "x":       _ic('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'),
    "arrow":   _ic('<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'),
    "ext":     _ic('<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
                   '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>'),
    "scale":   _ic('<path d="M12 3v18"/><path d="M5 7h14"/><path d="M5 7 2 14h6z"/><path d="M19 7l-3 7h6z"/>'),
    "search":  _ic('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'),
    "menu":    _ic('<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/>'
                   '<line x1="3" y1="18" x2="21" y2="18"/>'),
    "info":    _ic('<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/>'
                   '<line x1="12" y1="8" x2="12.01" y2="8"/>'),
    "tag":     _ic('<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>'
                   '<line x1="7" y1="7" x2="7.01" y2="7"/>'),
    "coffee":  _ic('<path d="M18 8h1a4 4 0 0 1 0 8h-1"/>'
                   '<path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>'
                   '<line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/>'
                   '<line x1="14" y1="1" x2="14" y2="4"/>'),
}


def stars(rating):
    if rating is None:
        return ""
    full = int(math.floor(rating))
    half = (rating - full) >= 0.5
    glyph = "★" * full + ("⯨" if half else "") + "☆" * (5 - full - (1 if half else 0))
    return glyph[:5] if len(glyph) > 5 else glyph


# ------------------------------------------------------- value formatting ---
def format_spec(key, value):
    """Return (html, is_text). null → an em dash. Never invent a value."""
    spec = SPEC_BY_KEY[key]
    if value is None:
        return '<span class="spec-null" title="Not published for this model">—</span>', False
    if spec["type"] == "bool":
        return (f'<span class="yes">{IC["check"]} Yes</span>' if value
                else f'<span class="no">{IC["x"]} No</span>'), False
    if spec["type"] == "number":
        num = f"{value:g}"
        unit = f' <span class="muted">{e(spec["unit"])}</span>' if spec.get("unit") else ""
        return num + unit, False
    return e(value), True


def spec_value_raw(p, key):
    return p["specs"].get(key)


def best_indices(key, products):
    """Which columns hold the best value for this spec row (comparator)."""
    spec = SPEC_BY_KEY[key]
    better = spec.get("better", "none")
    if better == "none":
        return set()
    vals = [spec_value_raw(p, key) for p in products]
    if spec["type"] == "bool":
        if not any(v is True for v in vals) or all(v is True for v in vals):
            return set()
        return {i for i, v in enumerate(vals) if v is True}
    nums = [(i, v) for i, v in enumerate(vals) if isinstance(v, (int, float))]
    if len(nums) < 2:
        return set()
    target = max(v for _, v in nums) if better == "higher" else min(v for _, v in nums)
    if len({v for _, v in nums}) == 1:
        return set()
    return {i for i, v in nums if v == target}


# ------------------------------------------------------------ radar chart ---
SERIES = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)"]


def radar_svg(products, size=340, show_values=True, uid="r"):
    """Server-rendered radar. Works with JS off; JS re-renders it in the
    comparator when the selection changes."""
    n = len(SCORES)
    cx = cy = size / 2
    R = size / 2 - 52
    parts = [f'<svg class="radar-svg" viewBox="0 0 {size} {size}" role="img" '
             f'aria-label="Editor scores from 0 to 10 across {n} axes">']

    def point(i, val):
        a = -math.pi / 2 + (2 * math.pi * i / n)
        r = R * (val / 10.0)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    # rings
    for ring in (2, 4, 6, 8, 10):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, ring) for i in range(n)))
        cls = "radar-ring radar-ring--outer" if ring == 10 else "radar-ring"
        parts.append(f'<polygon class="{cls}" points="{pts}"/>')
    # axes
    for i in range(n):
        x, y = point(i, 10)
        parts.append(f'<line class="radar-axis" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>')
    # polygons
    for si, p in enumerate(products):
        colour = SERIES[si % len(SERIES)]
        pts, dots = [], []
        for i, s in enumerate(SCORES):
            v = p["scores"].get(s["key"])
            v = 0 if not isinstance(v, (int, float)) else v
            x, y = point(i, v)
            pts.append(f"{x:.1f},{y:.1f}")
            dots.append(f'<circle class="radar-dot" cx="{x:.1f}" cy="{y:.1f}" fill="{colour}"/>')
        parts.append(f'<polygon class="radar-poly" points="{" ".join(pts)}" fill="{colour}" '
                     f'fill-opacity="{0.2 if len(products) > 1 else 0.16}" stroke="{colour}"/>')
        parts.extend(dots)
    # labels
    for i, s in enumerate(SCORES):
        lx, ly = point(i, 10)
        ox, oy = lx - cx, ly - cy
        d = math.hypot(ox, oy) or 1
        tx, ty = cx + ox / d * (R + 22), cy + oy / d * (R + 22)
        anchor = "middle" if abs(ox) < R * 0.25 else ("start" if ox > 0 else "end")
        dy = ".9em" if oy > R * 0.4 else ("-.25em" if oy < -R * 0.4 else ".35em")
        parts.append(f'<text class="radar-label" x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" '
                     f'dy="{dy}">{e(s["label"])}</text>')
        if show_values and len(products) == 1:
            v = products[0]["scores"].get(s["key"])
            if isinstance(v, (int, float)):
                vx, vy = point(i, min(v + 1.35, 11.4))
                parts.append(f'<text class="radar-value" x="{vx:.1f}" y="{vy:.1f}" '
                             f'text-anchor="middle" dy=".35em">{v:g}</text>')
    parts.append("</svg>")
    return "".join(parts)


def score_legend(p):
    rows = []
    for s in SCORES:
        v = p["scores"].get(s["key"])
        val = f"{v:g}" if isinstance(v, (int, float)) else "—"
        pct = (v / 10 * 100) if isinstance(v, (int, float)) else 0
        rows.append(
            f'<div class="score-row"><span class="lbl" title="{e(s["how"])}">{e(s["label"])}</span>'
            f'<span class="val">{val}<span class="muted">/10</span></span>'
            f'<span class="score-bar"><i style="width:{pct:.0f}%"></i></span></div>')
    return f'<div class="score-legend">{"".join(rows)}</div>'


# --------------------------------------------------------------- partials ---
NAV = [
    ("machines.html", "Machines"),
    ("guide-best-superautomatic-espresso-machine-home-2026.html", "Buying guide"),
    ("deals.html", "Deals"),
    ("how-we-rate.html", "How we rate"),
]

DISCLOSURE_SHORT = (
    f'{SITE["name"]} earns a commission from qualifying purchases made through Amazon links on '
    'this site, at no extra cost to you. <a href="affiliate-disclosure.html">Full disclosure</a>.')


def sample_banner():
    # Controlled independently of the tag flag: the tag really is a placeholder,
    # but the banner is a presentation choice (off while the Associates
    # application is under review).
    if not SITE.get("show_sample_banner"):
        return ""
    return ('<div class="sample-bar" role="status">'
            '<strong>Sample catalogue.</strong> Three real machines with researched specifications, '
            'shown to demonstrate the site. Product illustrations are our own drawings, not photographs, '
            'and the buy links carry a placeholder associate tag until the real one is added.'
            '</div>')


def header(active=""):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<li><a href="{href}"{cur}>{e(label)}</a></li>')
    links.append(
        '<li><a class="nav-cta" href="compare.html" data-count="0" data-compare-nav>'
        f'{IC["scale"]} Compare <span class="pill" data-compare-count>0</span></a></li>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
{sample_banner()}
<div class="disclosure-bar">{DISCLOSURE_SHORT}</div>
<header class="site-header">
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="index.html">
      <img src="assets/favicon.svg" alt="" width="30" height="30">
      <span>{e(SITE['name'])}</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links"
            aria-label="Open menu" data-nav-toggle>{IC['menu']}</button>
    <ul class="nav-links" id="nav-links">{''.join(links)}</ul>
  </nav>
</header>"""


def footer():
    cats = "".join(f'<li><a href="{category_url(c)}">{e(c["name"])}</a></li>' for c in CATEGORIES)
    guides = "".join(f'<li><a href="{guide_url(g)}">{e(g["title"])}</a></li>' for g in GUIDES)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="brand"><img src="assets/favicon.svg" alt="" width="30" height="30"><span>{e(SITE['name'])}</span></div>
        <p>{e(SITE['description'])}</p>
      </div>
      <div>
        <h4>Categories</h4>
        <ul>{cats}</ul>
      </div>
      <div>
        <h4>Guides</h4>
        <ul>{guides}<li><a href="machines.html">All machines</a></li><li><a href="compare.html">Comparator</a></li><li><a href="deals.html">Deals</a></li></ul>
      </div>
      <div>
        <h4>About</h4>
        <ul>
          <li><a href="how-we-rate.html">How we rate</a></li>
          <li><a href="about.html">About us</a></li>
          <li><a href="affiliate-disclosure.html">Affiliate disclosure</a></li>
          <li><a href="privacy.html">Privacy &amp; cookies</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-legal">
      <p>As an Amazon Associate we earn from qualifying purchases. Amazon and the Amazon logo
         are trademarks of Amazon.com, Inc. or its affiliates. Prices and availability shown are
         a snapshot taken on the date listed and may have changed &mdash; always check the price
         on Amazon before buying.</p>
      <p>&copy; {SITE['year']} {e(SITE['name'])}. Last built {BUILD_DATE}.</p>
    </div>
  </div>
</footer>"""


def page(*, title, description, body, active="", canonical="", extra_head="", jsonld=None,
         body_class=""):
    ld = ""
    if jsonld:
        blocks = jsonld if isinstance(jsonld, list) else [jsonld]
        ld = "".join(
            f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
            for b in blocks)
    can = f'<link rel="canonical" href="{SITE_URL}/{canonical}">' if SITE_URL and canonical else ""
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:image" content="assets/img/og-card.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#17120f">
{can}
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap">
<link rel="stylesheet" href="styles.css?v={VER}">
{extra_head}
{ld}
<script>document.documentElement.classList.remove('no-js');</script>
</head>
<body class="{body_class}">
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script defer src="lib/db.js?v={VER}"></script>
<script defer src="main.js?v={VER}"></script>
</body>
</html>"""


# ---------------------------------------------------------- product parts ---
def price_block(p, big=True):
    now, was = current_price(p), p.get("retail_price")
    if now is None:
        return '<p class="muted small">Check the current price on Amazon.</p>'
    was_html = (f'<span class="price-was">{money(was)}</span>'
                f'<span class="badge badge-deal">&minus;{discount_pct(p)}%</span>') if is_deal(p) else ""
    cls = "price-now" if big else "price-now"
    return (f'<div class="price"><span class="{cls}">{money(now)}</span>{was_html}</div>'
            f'<p class="price-note">Indicative price captured {p.get("price_date", BUILD_DATE)} '
            f'&middot; check Amazon for today\'s price</p>')


def rating_block(p):
    if p.get("rating") is None:
        return '<span class="muted small">No rating yet</span>'
    src = p.get("rating_source", "customer reviews")
    return (f'<span class="stars" title="{e(src)}"><span class="stars-glyph" aria-hidden="true">{stars(p["rating"])}</span>'
            f'<span class="num">{p["rating"]:g}</span>'
            f'<span class="muted small">({p["rating_count"]:,} reviews)</span></span>')


def buy_button(p, cls="btn btn-primary", label=None):
    label = label or "View on Amazon"
    return (f'<a class="{cls}" href="{e(affiliate_url(p))}" target="_blank" '
            f'rel="sponsored nofollow noopener" data-buy="{e(p["id"])}">'
            f'{label} {IC["ext"]}</a>')


def key_chips(p):
    s = p["specs"]
    bits = []
    if s.get("drinks_one_touch"):
        bits.append(f'<span class="chip"><span class="num">{s["drinks_one_touch"]}</span> drinks</span>')
    if s.get("grind_settings"):
        bits.append(f'<span class="chip"><span class="num">{s["grind_settings"]}</span> grind steps</span>')
    if s.get("water_tank_l"):
        bits.append(f'<span class="chip"><span class="num">{s["water_tank_l"]:g}L</span> tank</span>')
    bits.append(f'<span class="chip">{"One-touch milk" if s.get("milk_one_touch") else "Manual steam wand"}</span>')
    return f'<div class="pcard-specs">{"".join(bits)}</div>'


def product_card(p, reveal=True):
    rv = ' data-reveal' if reveal else ''
    flags = []
    if p.get("editor_badge"):
        flags.append(f'<span class="badge badge-award">{e(p["editor_badge"])}</span>')
    if is_deal(p):
        flags.append(f'<span class="badge badge-deal">&minus;{discount_pct(p)}%</span>')
    return f"""<article class="pcard"{rv}>
  <a class="pcard-media" href="{product_url(p)}" aria-label="{e(p['name'])}">
    <div class="pcard-flags">{''.join(flags)}</div>
    <img src="{e(p['images'][0])}" alt="{e(p['name'])}" loading="lazy" decoding="async" width="640" height="640">
  </a>
  <div class="pcard-body">
    <span class="pcard-brand">{e(p['brand'])}</span>
    <h3 class="pcard-title"><a href="{product_url(p)}">{e(p['short_name'])}</a></h3>
    <div class="ficha-meta small">{rating_block(p)}</div>
    <p class="pcard-summary">{e(p['summary'])}</p>
    {key_chips(p)}
    <div class="pcard-foot">
      <div>{price_block(p)}</div>
      <span class="badge badge-flat" title="Average of our six editor scores">{avg_score(p):.1f}/10</span>
    </div>
  </div>
  <div class="pcard-actions">
    {buy_button(p, 'btn btn-primary btn-sm')}
    <button class="btn btn-ghost btn-sm" type="button" data-compare-toggle="{e(p['id'])}">
      {IC['scale']} Compare</button>
  </div>
</article>"""


def spec_tables(p):
    out = []
    for g in SPEC_GROUPS:
        rows = []
        for spec in SPECS:
            if spec["group"] != g["id"]:
                continue
            val, is_text = format_spec(spec["key"], p["specs"].get(spec["key"]))
            rows.append(f'<tr><th scope="row">{e(spec["label"])}</th>'
                        f'<td class="{"is-text" if is_text else ""}">{val}</td></tr>')
        if rows:
            out.append(f'<div class="spec-group"><h3>{e(g["name"])}</h3>'
                       f'<table class="spec-table"><tbody>{"".join(rows)}</tbody></table></div>')
    extra = p.get("specs_extra") or {}
    if extra:
        rows = "".join(f'<tr><th scope="row">{e(k)}</th><td class="is-text">{e(v)}</td></tr>'
                       for k, v in extra.items())
        out.append(f'<div class="spec-group"><h3>Other details</h3>'
                   f'<table class="spec-table"><tbody>{rows}</tbody></table></div>')
    return f'<div class="spec-grid">{"".join(out)}</div>'


def buy_strip(p, headline="Ready to buy?"):
    return f"""<div class="buy-strip" data-reveal>
  <div>
    <p class="t">{e(headline)}</p>
    <p class="s">{e(p['name'])} &middot; {money(current_price(p)) or 'price on Amazon'} &middot; we earn a commission at no cost to you</p>
  </div>
  {buy_button(p, 'btn btn-onDark btn-lg')}
</div>"""


def breadcrumb(items):
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span>/</span>')
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span>{e(label)}</span>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{"".join(parts)}</nav>'


# ============================================================== PAGES =======
def build_index():
    featured = [p for p in PRODUCTS if p.get("featured")] or PRODUCTS
    hero_pick = max(PRODUCTS, key=avg_score)
    cards = "".join(product_card(p) for p in featured)
    cat_tiles = "".join(f"""<a class="cat-tile" href="{category_url(c)}" data-reveal>
      <h3>{e(c['name'])}</h3>
      <p>{e(c['tagline'])}</p>
      <span class="go">{len(in_category(c['id']))} machine{'s' if len(in_category(c['id'])) != 1 else ''} {IC['arrow']}</span>
    </a>""" for c in CATEGORIES)

    method = "".join(f"""<div class="method-item">
        <span class="n">0{i+1}</span><h3>{e(s['label'])}</h3><p>{e(s['how'])}</p>
      </div>""" for i, s in enumerate(SCORES))

    guide_cards = "".join(f"""<a class="cat-tile" href="{guide_url(g)}" data-reveal>
        <span class="kicker">Guide</span>
        <h3>{e(g['title'])}</h3>
        <p>{e(g['subtitle'])}</p>
        <span class="go">Read the guide {IC['arrow']}</span>
      </a>""" for g in GUIDES)

    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="kicker">{len(PRODUCTS)} machines &middot; {len(SPECS)} specs each &middot; updated {BUILD_DATE}</span>
        <h1>Superautomatic espresso machines, <em>compared properly</em>.</h1>
        <p class="lede">Not a list of links. Every machine is broken down into the same {len(SPECS)} measured
          specifications and scored on six axes, so you can put any two side by side and see exactly
          where the extra money goes.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="compare.html">{IC['scale']} Open the comparator</a>
          <a class="btn btn-onDark btn-lg" href="{guide_url(GUIDES[0])}">Read the buying guide</a>
        </div>
        <div class="hero-stats">
          <div class="hero-stat"><span class="n">{len(SPECS)}</span><span class="l">specs tracked per machine</span></div>
          <div class="hero-stat"><span class="n">6</span><span class="l">scored comparison axes</span></div>
          <div class="hero-stat"><span class="n">{len(CATEGORIES)}</span><span class="l">use-case categories</span></div>
        </div>
      </div>
      <div class="hero-visual" data-reveal>
        <img src="{e(hero_pick['images'][1])}" alt="{e(hero_pick['name'])}" width="640" height="640" fetchpriority="high">
        <div class="hero-tag">
          <span class="n">{avg_score(hero_pick):.1f}</span>
          <span class="t"><strong>{e(hero_pick['editor_badge'] or 'Top rated')}</strong><br>{e(hero_pick['short_name'])}</span>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head head-row">
      <div>
        <span class="kicker">Editor's picks</span>
        <h2>The machines we would actually buy</h2>
        <p>Each one wins on something specific. Open any two in the comparator to see the trade-off in numbers.</p>
      </div>
      <a class="btn btn-ghost" href="machines.html">All machines {IC['arrow']}</a>
    </div>
    <div class="grid grid-3">{cards}</div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section-head">
      <span class="kicker">By use case</span>
      <h2>Start from how you will use it</h2>
      <p>The right machine for a two-person kitchen is the wrong machine for an office of ten. Pick the situation first.</p>
    </div>
    <div class="grid grid-4">{cat_tiles}</div>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    <div class="section-head">
      <span class="kicker">Methodology</span>
      <h2>How we score, in the open</h2>
      <p>Every machine gets the same six scores from 0 to 10. Scores are our editorial judgement, derived from
         published specifications and hands-on reviews &mdash; never a manufacturer's marketing claim.
         Here is exactly what goes into each one.</p>
    </div>
    <div class="method-grid">{method}</div>
    <p style="margin-top:2rem"><a class="btn btn-onDark" href="how-we-rate.html">Read the full methodology {IC['arrow']}</a></p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="kicker">Guides</span>
      <h2>Work out what you need first</h2>
    </div>
    <div class="grid grid-2">{guide_cards}</div>
  </div>
</section>

<section class="section-tight">
  <div class="wrap"><div class="disclosure">{DISCLOSURE_SHORT}</div></div>
</section>
"""
    jsonld = {
        "@context": "https://schema.org", "@type": "WebSite",
        "name": SITE["name"], "description": SITE["description"],
    }
    return page(title=f"{SITE['name']} — {SITE['tagline']}",
                description=SITE["description"], body=body, canonical="index.html",
                jsonld=jsonld)


def build_machines():
    cards = "".join(product_card(p) for p in sorted(PRODUCTS, key=avg_score, reverse=True))
    filters = "".join(
        f'<button class="btn btn-ghost btn-sm" type="button" data-filter="{e(c["id"])}" '
        f'aria-pressed="false">{e(c["name"])}</button>' for c in CATEGORIES)
    body = f"""
<section class="page-head">
  <div class="wrap">
    {breadcrumb([("Home", "index.html"), ("Machines", None)])}
    <h1>Every machine we have measured</h1>
    <p class="lede">{len(PRODUCTS)} superautomatic espresso machines, each broken down into the same
       {len(SPECS)} specifications. Sorted by overall editor score.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="chip-row" style="margin-bottom:1.5rem" data-filter-bar>
      <button class="btn btn-ghost btn-sm" type="button" data-filter="all" aria-pressed="true">All</button>
      {filters}
    </div>
    <div class="grid grid-3" data-machine-grid>{cards}</div>
    <p class="muted small center" style="margin-top:2rem" data-empty-msg hidden>No machines in this category yet.</p>
  </div>
</section>
<section class="section-tight"><div class="wrap"><div class="disclosure">{DISCLOSURE_SHORT}</div></div></section>
"""
    return page(title=f"All Superautomatic Espresso Machines — {SITE['name']}",
                description="Every superautomatic espresso machine in our database, with full "
                            "specifications and editor scores. Filter by home, office, professional or premium.",
                body=body, active="machines.html", canonical="machines.html")


def build_category(c):
    items = sorted(in_category(c["id"]), key=avg_score, reverse=True)
    cards = "".join(product_card(p) for p in items) or \
        '<p class="muted">No machines in this category yet — we are testing more.</p>'
    related = [g for g in GUIDES if any(pick["product"] in {p["id"] for p in items}
                                        for pick in g["picks"])]
    rel_html = "".join(
        f'<li><a href="{guide_url(g)}" style="color:var(--accent);text-decoration:underline;'
        f'text-underline-offset:3px">{e(g["title"])}</a></li>' for g in related)
    body = f"""
<section class="page-head">
  <div class="wrap">
    {breadcrumb([("Home", "index.html"), ("Machines", "machines.html"), (c["name"], None)])}
    <span class="kicker">Category</span>
    <h1>Best superautomatic espresso machines for {e(c['name'].lower())}</h1>
    <p class="lede">{e(c['blurb'])}</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head head-row">
      <div><h2>{len(items)} machine{'s' if len(items) != 1 else ''} in {e(c['name'])}</h2>
      <p>{e(c['tagline'])}</p></div>
      <a class="btn btn-ghost" href="compare.html">{IC['scale']} Compare these</a>
    </div>
    <div class="grid grid-3">{cards}</div>
    {f'<div class="callout" style="margin-top:2.5rem"><h3>Related reading</h3><ul style="margin:0;padding-left:1.2rem">{rel_html}</ul></div>' if rel_html else ''}
  </div>
</section>
<section class="section-tight"><div class="wrap"><div class="disclosure">{DISCLOSURE_SHORT}</div></div></section>
"""
    return page(title=f"Best Superautomatic Espresso Machines for {c['name']} ({SITE['year']}) — {SITE['name']}",
                description=f"{c['blurb']} Compared spec by spec with editor scores.",
                body=body, canonical=category_url(c),
                jsonld={"@context": "https://schema.org", "@type": "ItemList",
                        "name": f"Best superautomatic espresso machines for {c['name'].lower()}",
                        "itemListElement": [
                            {"@type": "ListItem", "position": i + 1, "name": p["name"]}
                            for i, p in enumerate(items)]})


def build_ficha(p):
    thumbs = "".join(
        f'<button class="gallery-thumb" type="button" data-gallery-thumb="{i}" '
        f'aria-current="{"true" if i == 0 else "false"}" aria-label="View image {i+1}">'
        f'<img src="{e(img)}" alt="" loading="lazy" width="160" height="160"></button>'
        for i, img in enumerate(p["images"]))

    pros = "".join(f'<li>{IC["check"]}<span>{e(x)}</span></li>' for x in p["pros"])
    cons = "".join(f'<li>{IC["x"]}<span>{e(x)}</span></li>' for x in p["cons"])

    s = p["specs"]
    quick = []
    for key in ("pressure_bar", "grind_settings", "water_tank_l", "bean_hopper_g", "drinks_one_touch"):
        spec = SPEC_BY_KEY[key]
        v = s.get(key)
        txt = "—" if v is None else (f"{v:g}{spec['unit'] if spec['unit'] in ('L', 'g') else ''}")
        quick.append(f'<div class="qspec"><span class="l">{e(spec["label"])}</span>'
                     f'<span class="v">{txt}</span></div>')

    cats = " ".join(f'<a class="badge badge-flat" href="{category_url(CAT_BY_ID[c])}">{e(CAT_BY_ID[c]["name"])}</a>'
                    for c in p.get("categories", []) if c in CAT_BY_ID)

    sources = "".join(
        f'<li><a href="{e(src["url"])}" target="_blank" rel="noopener nofollow">{e(src["label"])}</a></li>'
        for src in p.get("sources", []))

    others = [q for q in PRODUCTS if q["id"] != p["id"]]
    related = "".join(product_card(q, reveal=False) for q in others[:3])

    ld_product = {
        "@context": "https://schema.org", "@type": "Product",
        "name": p["name"], "brand": {"@type": "Brand", "name": p["brand"]},
        "sku": p["asin"], "description": p["summary"],
    }
    if current_price(p) is not None:
        ld_product["offers"] = {
            "@type": "Offer", "price": current_price(p), "priceCurrency": SITE["currency"],
            "availability": "https://schema.org/InStock", "url": affiliate_url(p),
        }
    if p.get("rating") is not None:
        ld_product["aggregateRating"] = {
            "@type": "AggregateRating", "ratingValue": p["rating"],
            "reviewCount": p["rating_count"],
        }

    body = f"""
<section class="section" style="padding-top:clamp(1.5rem,3vw,2.5rem)">
  <div class="wrap">
    {breadcrumb([("Home", "index.html"), ("Machines", "machines.html"), (p["short_name"], None)])}
    <div class="ficha-top" style="margin-top:1.4rem">
      <div class="gallery">
        <div class="gallery-main"><img src="{e(p['images'][0])}" alt="{e(p['name'])}"
             data-gallery-main width="640" height="640" fetchpriority="high"></div>
        <div class="gallery-thumbs">{thumbs}</div>
        <p class="gallery-note">Illustrations drawn by us in the site's own style. They represent
           the machine's layout, not its exact appearance &mdash; see Amazon for product photography.</p>
      </div>

      <div class="ficha-head">
        <span class="kicker">{e(p['brand'])} &middot; {e(p['model'])}</span>
        <h1>{e(p['name'])}</h1>
        <div class="ficha-meta">
          {rating_block(p)}
          <span class="badge badge-flat" title="Average of our six editor scores">Editor score {avg_score(p):.1f}/10</span>
          {f'<span class="badge badge-award">{e(p["editor_badge"])}</span>' if p.get('editor_badge') else ''}
        </div>
        <div class="chip-row" style="margin-bottom:1rem">{cats}</div>
        <p class="lede">{e(p['summary'])}</p>

        <div class="ficha-buy">
          {price_block(p)}
          {buy_button(p, 'btn btn-primary btn-lg btn-block')}
          <div class="row">
            <button class="btn btn-ghost btn-sm" type="button" data-compare-toggle="{e(p['id'])}">
              {IC['scale']} Add to comparison</button>
          </div>
          <p class="tiny muted" style="margin-top:.7rem">{IC['info']} Affiliate link &mdash; we earn a commission
             if you buy, at no extra cost to you.</p>
        </div>

        <div class="ficha-quick">{''.join(quick)}</div>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section-head">
      <span class="kicker">Editor scores</span>
      <h2>Where this machine is strong</h2>
      <p>Our judgement on six axes, 0 to 10, applied identically to every machine in the database.
         These are editorial ratings, not manufacturer specifications.</p>
    </div>
    <div class="card card-pad">
      <div class="radar-wrap">
        {radar_svg([p], uid=p['id'])}
        <div>
          {score_legend(p)}
          <p class="score-note">Hover a label to see what feeds that score.
             <a href="how-we-rate.html" style="color:var(--accent);text-decoration:underline">Full methodology</a>.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="grid" style="grid-template-columns:1fr;gap:clamp(2rem,4vw,3rem)">
      <div>
        <div class="section-head"><span class="kicker">Full specifications</span>
          <h2>Every number we could verify</h2>
          <p>A dash means the manufacturer does not publish that figure and we could not verify it
             from a reliable source. We do not estimate specifications.</p></div>
        <div class="card card-pad">{spec_tables(p)}</div>
      </div>

      <div>
        <div class="section-head"><span class="kicker">Our take</span><h2>What it is actually like</h2></div>
        <div class="rich prose">{p['body']}</div>
      </div>

      <div class="proscons">
        <div class="pc pc--pro"><h3>{IC['check']} What works</h3><ul>{pros}</ul></div>
        <div class="pc pc--con"><h3>{IC['x']} What does not</h3><ul>{cons}</ul></div>
      </div>

      <div class="callout">
        <h3>Ideal for</h3>
        <p>{e(p['ideal_for'])}</p>
      </div>
      <div class="callout callout--flat">
        <h3>Probably not for</h3>
        <p>{e(p.get('not_for', '—'))}</p>
      </div>

      {buy_strip(p, f"Buy the {p['short_name']}")}

      <div>
        <div class="section-head"><span class="kicker">Owner reviews</span><h2>What buyers report</h2></div>
        <div class="card card-pad">
          <p class="review-quote">{e(p['reviews_summary'])}</p>
          <p class="tiny muted" style="margin-top:1rem">Summarised from {e(p.get('rating_source', 'published customer reviews'))}
             {f"&mdash; {p['rating']:g}/5 across {p['rating_count']:,} reviews" if p.get('rating') else ''}.
             Ratings move; check the live rating on Amazon.</p>
        </div>
      </div>

      <div>
        <div class="section-head"><span class="kicker">Sources</span><h2>Where these numbers come from</h2>
          <p>Specifications on this page were taken from the manufacturer and from published hands-on reviews.</p></div>
        <ul class="sources-list">{sources}</ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="wrap">
    <div class="section-head head-row">
      <div><span class="kicker">Alternatives</span><h2>Compare it against</h2></div>
      <a class="btn btn-ghost" href="compare.html">{IC['scale']} Open comparator</a>
    </div>
    <div class="related-strip">{related}</div>
  </div>
</section>

<section class="section-tight"><div class="wrap"><div class="disclosure">{DISCLOSURE_SHORT}</div></div></section>
"""
    return page(title=f"{p['name']} Review & Full Specs — {SITE['name']}",
                description=p["summary"][:180],
                body=body, canonical=product_url(p), jsonld=ld_product)


def build_compare():
    opts = "".join(f"""<button class="cmp-option" type="button" data-compare-toggle="{e(p['id'])}"
        aria-pressed="false" data-search="{e((p['name'] + ' ' + p['brand'] + ' ' + p['model']).lower())}">
      <img src="{e(p['images'][0])}" alt="" loading="lazy" width="84" height="84">
      <span><span class="t">{e(p['short_name'])}</span><br><span class="s">{e(p['brand'])} &middot; {money(current_price(p)) or '—'}</span></span>
      <span class="mark">{IC['check']}</span>
    </button>""" for p in PRODUCTS)

    # A server-rendered default comparison so the page is useful with JS off.
    default = sorted(PRODUCTS, key=avg_score, reverse=True)[:3]
    static_table = comparison_table_html(default)

    body = f"""
<section class="page-head">
  <div class="wrap">
    {breadcrumb([("Home", "index.html"), ("Compare", None)])}
    <span class="kicker">The comparator</span>
    <h1>Put them side by side</h1>
    <p class="lede">Pick two or more machines. Every specification lines up in one table, the best
       value in each row is highlighted, and all the score profiles overlay on a single chart.
       The URL updates as you choose, so you can share a comparison.</p>
  </div>
</section>

<section class="section" style="padding-top:clamp(1.5rem,3vw,2.5rem)">
  <div class="wrap">
    <div class="cmp-picker" data-reveal>
      <label class="cmp-search">
        <span class="sr-only">Search machines</span>
        {IC['search']}
        <input type="search" placeholder="Search by name, brand or model…" data-compare-search autocomplete="off">
      </label>
      <div class="cmp-options" data-compare-options>{opts}</div>
      <div class="cmp-slots" data-compare-slots></div>
      <p class="tiny muted" style="margin-top:.6rem">Compare up to 4 machines at once.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0" data-compare-results>
  <div class="wrap">
    <noscript><p class="callout" style="margin-bottom:1.5rem">Interactive selection needs JavaScript.
      Below is the full comparison of all {len(default)} machines in the database.</p></noscript>
    {static_table}
  </div>
</section>

<section class="section-tight"><div class="wrap"><div class="disclosure">{DISCLOSURE_SHORT}</div></div></section>
"""
    return page(title=f"Compare Superautomatic Espresso Machines Side by Side — {SITE['name']}",
                description="Compare superautomatic espresso machines specification by specification, "
                            "with overlaid score charts and the best value in each row highlighted.",
                body=body, active="compare.html", canonical="compare.html")


def comparison_table_html(products):
    """Server-rendered comparison — the JS layer rebuilds this markup exactly."""
    if len(products) < 1:
        return ""
    heads = []
    for i, p in enumerate(products):
        heads.append(f"""<th scope="col"><div class="cmp-col-head">
        <span class="cmp-swatch" style="background:{SERIES[i % len(SERIES)]}"></span>
        <img src="{e(p['images'][0])}" alt="" loading="lazy" width="124" height="124">
        <a class="t" href="{product_url(p)}">{e(p['short_name'])}</a>
        <span class="p">{money(current_price(p)) or '—'}</span>
        {buy_button(p, 'btn btn-primary btn-sm')}
      </div></th>""")

    rows = []
    # scores first
    rows.append(f'<tr class="group-row"><th scope="row">Editor scores</th>'
                + "".join('<td></td>' for _ in products) + '</tr>')
    for sc in SCORES:
        vals = [p["scores"].get(sc["key"]) for p in products]
        nums = [v for v in vals if isinstance(v, (int, float))]
        best = max(nums) if nums and len(set(nums)) > 1 else None
        cells = "".join(
            f'<td class="{"cmp-best" if best is not None and v == best else ""}">'
            f'{f"{v:g}" if isinstance(v, (int, float)) else "<span class=spec-null>—</span>"}</td>'
            for v in vals)
        rows.append(f'<tr><th scope="row">{e(sc["label"])}</th>{cells}</tr>')

    for g in SPEC_GROUPS:
        group_specs = [s for s in SPECS if s["group"] == g["id"] and s.get("compare")]
        if not group_specs:
            continue
        rows.append(f'<tr class="group-row"><th scope="row">{e(g["name"])}</th>'
                    + "".join('<td></td>' for _ in products) + '</tr>')
        for spec in group_specs:
            best = best_indices(spec["key"], products)
            cells = []
            for i, p in enumerate(products):
                val, is_text = format_spec(spec["key"], p["specs"].get(spec["key"]))
                cls = " ".join(filter(None, ["is-text" if is_text else "",
                                             "cmp-best" if i in best else ""]))
                cells.append(f'<td class="{cls}">{val}</td>')
            rows.append(f'<tr><th scope="row">{e(spec["label"])}</th>{"".join(cells)}</tr>')

    # price row
    price_cells = []
    prices = [current_price(p) for p in products]
    valid = [v for v in prices if v is not None]
    cheapest = min(valid) if len(valid) > 1 and len(set(valid)) > 1 else None
    for v in prices:
        cls = "cmp-best" if cheapest is not None and v == cheapest else ""
        price_cells.append(f'<td class="{cls}">{money(v) or "—"}</td>')
    rows.insert(0, f'<tr class="group-row"><th scope="row">Price</th>'
                   + "".join('<td></td>' for _ in products) + '</tr>')
    rows.insert(1, f'<tr><th scope="row">Current price</th>{"".join(price_cells)}</tr>')

    legend = "".join(
        f'<span class="cmp-legend-item"><i style="background:{SERIES[i % len(SERIES)]}"></i>'
        f'{e(p["short_name"])}</span>' for i, p in enumerate(products))

    verdicts = build_verdicts(products)

    return f"""<div data-compare-render>
  <div class="card card-pad" style="margin-bottom:1.6rem">
    <div class="section-head" style="margin-bottom:1rem">
      <span class="kicker">Score profiles overlaid</span>
      <h2 style="font-size:1.4rem">The shape of each machine</h2>
    </div>
    {radar_svg(products, size=400, show_values=False, uid="cmp")}
    <div class="cmp-legend">{legend}</div>
  </div>

  {verdicts}

  <div class="card card-pad" style="margin-top:1.6rem">
    <div class="section-head" style="margin-bottom:1rem">
      <span class="kicker">Specification by specification</span>
      <h2 style="font-size:1.4rem">The full table</h2>
      <p class="small">Green marks the best value in the row. A dash means the figure is not published.</p>
    </div>
    <div class="table-scroll">
      <table class="cmp-table">
        <thead><tr><th scope="col"><span class="sr-only">Specification</span></th>{"".join(heads)}</tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>
  </div>
</div>"""


def build_verdicts(products):
    """Small 'who wins what' cards, computed from the data."""
    if len(products) < 2:
        return ""
    cards = []

    cheapest = min((p for p in products if current_price(p) is not None),
                   key=current_price, default=None)
    if cheapest:
        cards.append(("Cheapest", cheapest["short_name"],
                      f"{money(current_price(cheapest))} — the lowest entry price of this selection."))

    best_overall = max(products, key=avg_score)
    cards.append(("Highest overall score", best_overall["short_name"],
                  f"{avg_score(best_overall):.1f}/10 averaged across our six axes."))

    best_coffee = max(products, key=lambda p: p["scores"].get("coffee", 0))
    cards.append(("Best in the cup", best_coffee["short_name"],
                  f"Scores {best_coffee['scores'].get('coffee')}/10 on coffee quality."))

    best_value = max(products, key=lambda p: p["scores"].get("value", 0))
    cards.append(("Best value", best_value["short_name"],
                  f"Scores {best_value['scores'].get('value')}/10 for what you get per dollar."))

    inner = "".join(f'<div class="verdict-card"><span class="h">{e(h)}</span>'
                    f'<p class="n">{e(n)}</p><p class="w">{e(w)}</p></div>'
                    for h, n, w in cards)
    return f'<div class="cmp-verdict">{inner}</div>'


def build_guide(g):
    toc = "".join(f'<li><a href="#s{i+1}">{e(s["heading"])}</a></li>'
                  for i, s in enumerate(g["sections"]))
    toc += '<li><a href="#picks">Our picks</a></li><li><a href="#faq">Questions</a></li>'

    sections = "".join(f"""<section id="s{i+1}" style="margin-top:2.6rem">
        <h2 style="font-family:var(--serif);font-size:clamp(1.35rem,2.6vw,1.85rem)">{e(s['heading'])}</h2>
        <div class="rich" style="margin-top:.9rem">{s['body']}</div>
      </section>""" for i, s in enumerate(g["sections"]))

    picks = "".join(f"""<div class="pick-card" data-reveal>
        <img src="{e(BY_ID[pk['product']]['images'][0])}" alt="{e(BY_ID[pk['product']]['name'])}"
             loading="lazy" width="340" height="340">
        <div>
          <span class="award">{e(pk['award'])}</span>
          <h3><a href="{product_url(BY_ID[pk['product']])}">{e(BY_ID[pk['product']]['name'])}</a></h3>
          <div class="ficha-meta small">{rating_block(BY_ID[pk['product']])}
            <span class="badge badge-flat">{avg_score(BY_ID[pk['product']]):.1f}/10</span></div>
          <p>{e(pk['why'])}</p>
          <div class="acts">
            {buy_button(BY_ID[pk['product']], 'btn btn-primary btn-sm')}
            <a class="btn btn-ghost btn-sm" href="{product_url(BY_ID[pk['product']])}">Full review</a>
          </div>
        </div>
      </div>""" for pk in g["picks"])

    faqs = "".join(f'<details class="faq-item"><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>'
                   for f in g["faqs"])

    body = f"""
<section class="page-head">
  <div class="wrap wrap-narrow" style="margin-inline:auto">
    {breadcrumb([("Home", "index.html"), ("Guides", None), (g["title"][:34] + "…", None)])}
    <span class="kicker">Buying guide &middot; updated {e(g['updated'])}</span>
    <h1>{e(g['title'])}</h1>
    <p class="lede">{e(g['subtitle'])}</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="guide-layout">
      <aside class="toc">
        <h3>On this page</h3>
        <ol>{toc}</ol>
      </aside>
      <div>
        <div class="rich prose">{g['intro']}</div>
        {sections}

        <section id="picks" style="margin-top:3.2rem">
          <span class="kicker">The shortlist</span>
          <h2 style="font-family:var(--serif);font-size:clamp(1.45rem,3vw,2.1rem);margin-top:.4rem">Our picks</h2>
          <p class="muted" style="margin-top:.6rem;max-width:60ch">Chosen from the machines currently in our
             database. Each links to the full specification breakdown.</p>
          <div class="grid" style="margin-top:1.6rem;grid-template-columns:1fr">{picks}</div>
          <p style="margin-top:1.5rem"><a class="btn btn-ghost" href="compare.html">{IC['scale']} Compare these side by side</a></p>
        </section>

        <section id="faq" style="margin-top:3.2rem">
          <span class="kicker">FAQ</span>
          <h2 style="font-family:var(--serif);font-size:clamp(1.45rem,3vw,2.1rem);margin-top:.4rem">Common questions</h2>
          <div style="margin-top:1.2rem">{faqs}</div>
        </section>

        <div class="disclosure" style="margin-top:2.5rem">{DISCLOSURE_SHORT}</div>
      </div>
    </div>
  </div>
</section>
"""
    ld = [
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": f["q"],
                         "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                        for f in g["faqs"]]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": g["title"],
         "itemListElement": [{"@type": "ListItem", "position": i + 1,
                              "name": BY_ID[pk["product"]]["name"]}
                             for i, pk in enumerate(g["picks"])]},
    ]
    return page(title=f"{g['title']} — {SITE['name']}", description=g["meta_description"],
                body=body, active=guide_url(g), canonical=guide_url(g), jsonld=ld)


def build_deals():
    deals = sorted([p for p in PRODUCTS if is_deal(p)], key=discount_pct, reverse=True)
    top = deals[0] if deals else None
    hero = ""
    if top:
        hero = f"""<div class="deal-hero" data-reveal>
      <img src="{e(top['images'][0])}" alt="{e(top['name'])}" loading="lazy" width="440" height="440">
      <div>
        <span class="kicker">Biggest saving right now</span>
        <h2 style="font-family:var(--serif);font-size:clamp(1.4rem,3vw,2rem);margin-top:.4rem">{e(top['name'])}</h2>
        <p style="color:var(--dark-ink-2);margin-top:.6rem;max-width:52ch">{e(top['summary'])}</p>
        <p style="margin-top:1rem"><span class="price-was" style="color:var(--dark-ink-2)">{money(top['retail_price'])}</span>
           <strong style="font-size:1.5rem;margin-left:.5rem">{money(top['sale_price'])}</strong></p>
      </div>
      <div style="text-align:center">
        <span class="deal-save">&minus;{discount_pct(top)}%</span>
        <p class="tiny" style="color:var(--dark-ink-2);margin-block:.4rem .9rem">
          Save {money(top['retail_price'] - top['sale_price'])}</p>
        {buy_button(top, 'btn btn-onDark')}
      </div>
    </div>"""

    cards = "".join(product_card(p) for p in deals)
    body = f"""
<section class="page-head">
  <div class="wrap">
    {breadcrumb([("Home", "index.html"), ("Deals", None)])}
    <span class="kicker">Deals</span>
    <h1>Machines currently below list price</h1>
    <p class="lede">Everything here is selling under its manufacturer list price at the time we last
       checked. Prices on Amazon change constantly &mdash; treat these as a starting point, not a promise.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    {hero}
    <div class="section-head" style="margin-top:2.8rem"><h2>All current deals</h2>
      <p>{len(deals)} of {len(PRODUCTS)} machines are discounted. Prices captured {BUILD_DATE}.</p></div>
    <div class="grid grid-3">{cards or '<p class="muted">Nothing discounted right now.</p>'}</div>
    <div class="callout callout--flat" style="margin-top:2.5rem">
      <h3>{IC['info']} About these prices</h3>
      <p>Prices are a snapshot taken when we last updated each machine, shown with the capture date on
         every card. Amazon prices move daily and can differ by seller and by variant. Always confirm
         the price on Amazon before you buy.</p>
    </div>
  </div>
</section>
<section class="section-tight"><div class="wrap"><div class="disclosure">{DISCLOSURE_SHORT}</div></div></section>
"""
    return page(title=f"Espresso Machine Deals — {SITE['name']}",
                description="Superautomatic espresso machines currently selling below list price, "
                            "with the saving and the capture date on every listing.",
                body=body, active="deals.html", canonical="deals.html")


def build_how_we_rate():
    axes = "".join(f"""<div class="spec-group">
      <h3>{e(s['label'])}</h3>
      <p class="muted" style="padding-block:.7rem">{e(s['how'])}</p>
    </div>""" for s in SCORES)
    body = f"""
<section class="page-head">
  <div class="wrap wrap-narrow" style="margin-inline:auto">
    {breadcrumb([("Home", "index.html"), ("How we rate", None)])}
    <span class="kicker">Methodology</span>
    <h1>How we rate espresso machines</h1>
    <p class="lede">The whole point of this site is that two machines can be compared on the same terms.
       That only works if the terms are written down.</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow" style="margin-inline:auto">
    <div class="rich prose">
      <h3>Specifications are facts. Scores are opinions. We keep them apart.</h3>
      <p>Every machine in the database has two kinds of information attached to it. The
         <strong>specification table</strong> contains only figures published by the manufacturer or measured
         by a named review we link to. If we cannot verify a figure, the table shows a dash. We never
         estimate a specification to fill a gap, because a made-up number in a comparison table is worse
         than no number at all.</p>
      <p>The <strong>six scores</strong> are our editorial judgement, from 0 to 10, derived from those
         specifications plus what hands-on reviews and owner reviews consistently report. They are
         labelled as editor scores everywhere they appear. They are not manufacturer ratings and no brand
         has any input into them.</p>

      <h3>The six axes</h3>
    </div>
    <div class="card card-pad" style="margin-top:1.4rem">{axes}</div>

    <div class="rich prose" style="margin-top:2.5rem">
      <h3>Scores are relative to this catalogue</h3>
      <p>A 9 for coffee quality means "among the best of the machines we have measured", not "the best
         espresso physically possible". When we add machines that shift the range, we recompute the
         affected scores across the whole database rather than letting old ratings drift. That is why a
         score can change after a new machine is added.</p>

      <h3>How the comparator picks a winner per row</h3>
      <p>Each specification is tagged in our schema with whether a higher or a lower number is better.
         More grind settings is better; more decibels is worse; a wider machine is worse if counter space
         matters. Some fields — wattage, housing material — have no better or worse, so no row winner is
         highlighted. Where every machine has the same value, nothing is highlighted either.</p>

      <h3>What we do not do</h3>
      <ul>
        <li>We do not accept payment from manufacturers for a review, a score or a placement.</li>
        <li>We do not present a scraped price as a live price. Every price carries its capture date.</li>
        <li>We do not invent specifications, review quotes or ratings.</li>
        <li>We do not hide the affiliate relationship. It is disclosed on every page.</li>
      </ul>

      <h3>How we make money</h3>
      <p>Through Amazon's affiliate programme. If you buy after clicking one of our links, Amazon pays us
         a small commission and you pay exactly the same price. That funds the site. It does not change
         which machine scores highest &mdash; the cheapest machine in our database currently holds the top
         value score, and the most expensive one has the lowest.</p>
    </div>
    <div class="disclosure" style="margin-top:2.5rem">{DISCLOSURE_SHORT}</div>
  </div>
</section>
"""
    return page(title=f"How We Rate Espresso Machines — {SITE['name']}",
                description="Our scoring methodology: what goes into each of the six editor scores, "
                            "how the comparator decides a row winner, and what we refuse to do.",
                body=body, active="how-we-rate.html", canonical="how-we-rate.html")


def simple_page(title, kicker, heading, lede, rich, slug, description):
    body = f"""
<section class="page-head">
  <div class="wrap wrap-narrow" style="margin-inline:auto">
    {breadcrumb([("Home", "index.html"), (heading, None)])}
    <span class="kicker">{e(kicker)}</span>
    <h1>{e(heading)}</h1>
    <p class="lede">{e(lede)}</p>
  </div>
</section>
<section class="section">
  <div class="wrap wrap-narrow" style="margin-inline:auto">
    <div class="rich prose">{rich}</div>
  </div>
</section>
"""
    return page(title=f"{title} — {SITE['name']}", description=description,
                body=body, canonical=slug, active=slug)


def build_disclosure():
    rich = f"""
<h3>The short version</h3>
<p>{SITE['name']} earns money through the Amazon Services LLC Associates Program. When you click a
   &ldquo;View on Amazon&rdquo; link on this site and buy something, Amazon pays us a commission. You pay the
   same price you would have paid anyway.</p>

<h3>The required statement</h3>
<p><strong>{SITE['name']} is a participant in the Amazon Services LLC Associates Program, an affiliate
   advertising program designed to provide a means for sites to earn advertising fees by advertising
   and linking to Amazon.com.</strong></p>
<p>As an Amazon Associate we earn from qualifying purchases. Amazon, the Amazon logo, AmazonSupply and
   the AmazonSupply logo are trademarks of Amazon.com, Inc. or its affiliates.</p>

<h3>What that does and does not affect</h3>
<ul>
  <li>It does not change the price you pay. Not by a cent.</li>
  <li>It does not determine our scores. Our scoring rules are published in full on the
      <a href="how-we-rate.html">methodology page</a> and applied identically to every machine.</li>
  <li>It does not buy placement. No manufacturer can pay to appear, to rank higher, or to have a
      criticism removed.</li>
  <li>It does mean we have a commercial interest in you buying something. You should read our
      recommendations knowing that, and we would rather say so plainly than bury it.</li>
</ul>

<h3>About the prices on this site</h3>
<p>Prices shown are a snapshot from the date printed next to them. Amazon prices change daily, vary by
   seller and by product variant, and can differ from what you see when you click through. The price on
   Amazon at the moment of purchase is the only one that counts. We label every price with its capture
   date rather than pretending it is live.</p>

<h3>About the product information</h3>
<p>Specifications come from manufacturers and from published reviews, and the sources are linked at the
   bottom of every machine page. Where a figure is not published we show a dash instead of guessing.
   Product illustrations on this site are our own drawings and represent layout, not exact appearance.</p>

<h3>Contact</h3>
<p>Questions about this disclosure, or a correction to a specification, are welcome &mdash; see the
   <a href="about.html">about page</a>.</p>
"""
    return simple_page("Affiliate Disclosure", "Legal", "Affiliate disclosure",
                       "Required by Amazon's operating agreement, and by basic honesty. Here is exactly "
                       "how this site makes money.",
                       rich, "affiliate-disclosure.html",
                       "How BrewCompare makes money through the Amazon Associates Program, and what that "
                       "does and does not affect.")


def build_privacy():
    rich = """
<h3>The short version</h3>
<p>This site is a set of static pages. It has no accounts, no login, no comment system and no server-side
   database. We do not ask you for personal information and we have nowhere to store it if you gave it to us.</p>

<h3>Cookies</h3>
<p>We do not set any tracking cookies ourselves. Your machine selections in the comparator are held in the
   page URL, not in a cookie, which is why you can copy a comparison link and send it to someone.</p>

<h3>Third parties</h3>
<ul>
  <li><strong>Amazon.</strong> When you click a &ldquo;View on Amazon&rdquo; link you leave this site and
      Amazon's own privacy policy and cookies apply. Amazon uses a cookie to attribute any purchase to us
      so it can pay the commission described in our <a href="affiliate-disclosure.html">affiliate disclosure</a>.</li>
  <li><strong>Google Fonts.</strong> The site loads two typefaces from Google's font service, which means
      your browser makes a request to Google when the page loads.</li>
  <li><strong>GitHub Pages.</strong> The site is hosted on GitHub Pages, which keeps standard server logs.</li>
</ul>

<h3>Analytics</h3>
<p>No analytics scripts are installed at present. If that changes, this page will say so before it happens
   rather than after.</p>

<h3>Your rights</h3>
<p>Since we hold no personal data about you, there is nothing for us to export, correct or delete. For data
   Amazon or Google hold, contact them directly under their own policies.</p>
"""
    return simple_page("Privacy & Cookies", "Legal", "Privacy and cookies",
                       "A static site with no accounts and no tracking. Here is what that means in practice.",
                       rich, "privacy.html",
                       "BrewCompare's privacy policy: no accounts, no tracking cookies, and what "
                       "third parties are involved.")


def build_about():
    rich = f"""
<h3>What this site is</h3>
<p>{SITE['name']} exists because shopping for a superautomatic espresso machine is unusually hard. The
   category is full of near-identical specification sheets, every machine advertises the same 15 bar, and
   the differences that actually matter &mdash; whether milk is a button or a skill, whether you can pull the
   brew group out, how loud the grinder is at seven in the morning &mdash; are the ones nobody puts on the box.</p>
<p>So we built a database instead of a list. Every machine is broken into the same
   {len(SPECS)} fields and scored on the same six axes, which means any two of them can be put side by side
   and compared honestly. That comparator is the point of the site; everything else exists to feed it.</p>

<h3>How it works behind the scenes</h3>
<p>Every page you see &mdash; the machine reviews, the category pages, the comparison table, the charts &mdash;
   is generated from one structured data file. Nothing is written by hand per product. That is what keeps the
   site consistent as it grows, and it is why a specification correction only has to be made in one place.</p>

<h3>Where the numbers come from</h3>
<p>Manufacturer specification sheets first, then published hands-on reviews where a manufacturer does not
   disclose something. Every machine page lists its sources at the bottom with links, so you can check us.
   Where a figure could not be verified, the table shows a dash. We would rather have a gap than a guess.</p>

<h3>Corrections</h3>
<p>If a specification here is wrong, we want to know &mdash; a comparison site is only worth reading if the
   numbers are right. Corrections with a source get made quickly.</p>

<h3>How it is funded</h3>
<p>Amazon affiliate commissions, disclosed in full on the
   <a href="affiliate-disclosure.html">affiliate disclosure page</a>. No sponsored reviews, no paid placement,
   no manufacturer input into scores.</p>
"""
    return simple_page("About", "About", "About BrewCompare",
                       "Why this site is a database rather than a list, and how the numbers on it are sourced.",
                       rich, "about.html",
                       "About BrewCompare: an independent, data-driven comparison site for superautomatic "
                       "espresso machines.")


def build_404():
    body = f"""
<section class="section" style="padding-block:clamp(4rem,12vw,8rem);text-align:center">
  <div class="wrap wrap-narrow" style="margin-inline:auto">
    <span class="kicker">404</span>
    <h1 class="display" style="margin-block:.6rem 1rem">This page has not been brewed</h1>
    <p class="lede">The link you followed does not point anywhere on this site any more.</p>
    <div class="hero-actions" style="justify-content:center">
      <a class="btn btn-primary btn-lg" href="index.html">Back to the homepage</a>
      <a class="btn btn-ghost btn-lg" href="machines.html">Browse all machines</a>
    </div>
  </div>
</section>
"""
    return page(title=f"Page not found — {SITE['name']}",
                description="Page not found.", body=body)


# ------------------------------------------------------------------ db.js ---
def build_db_js():
    """The client-side data layer. One global, IIFE, classic script — works on
    file:// and needs no build tooling in the browser."""
    payload = {
        "site": {k: SITE[k] for k in ("name", "currency", "store", "affiliate_tag")},
        "categories": CATEGORIES,
        "specGroups": SPEC_GROUPS,
        "specs": SPECS,
        "scores": SCORES,
        "series": ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)"],
        "products": [{
            "id": p["id"], "name": p["name"], "shortName": p["short_name"],
            "brand": p["brand"], "model": p["model"],
            "url": product_url(p), "image": p["images"][0], "images": p["images"],
            "affiliateUrl": affiliate_url(p),
            "retailPrice": p.get("retail_price"), "salePrice": p.get("sale_price"),
            "price": current_price(p), "priceDate": p.get("price_date"),
            "rating": p.get("rating"), "ratingCount": p.get("rating_count"),
            "categories": p.get("categories", []),
            "badge": p.get("editor_badge"),
            "summary": p["summary"],
            "specs": p["specs"], "scores": p["scores"],
            "avgScore": round(avg_score(p), 1),
        } for p in PRODUCTS],
    }
    js = ("(function () {\n  \"use strict\";\n  window.__DB__ = "
          + json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")
          + ";\n})();\n")
    (ROOT / "lib" / "db.js").write_text(js, encoding="utf-8")


def build_sitemap():
    urls = ["index.html", "machines.html", "compare.html", "deals.html", "how-we-rate.html",
            "about.html", "affiliate-disclosure.html", "privacy.html"]
    urls += [category_url(c) for c in CATEGORIES]
    urls += [product_url(p) for p in PRODUCTS]
    urls += [guide_url(g) for g in GUIDES]
    base = SITE_URL or ""
    entries = "".join(
        f"  <url><loc>{base}/{u}</loc><lastmod>{BUILD_DATE}</lastmod></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n',
        encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n"
    if base:
        robots += f"Sitemap: {base}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


# ------------------------------------------------------------------- main ---
def write(name, content):
    (ROOT / name).write_text(content, encoding="utf-8")
    return name


def main():
    written = []
    written.append(write("index.html", build_index()))
    written.append(write("machines.html", build_machines()))
    for c in CATEGORIES:
        written.append(write(category_url(c), build_category(c)))
    for p in PRODUCTS:
        written.append(write(product_url(p), build_ficha(p)))
    written.append(write("compare.html", build_compare()))
    for g in GUIDES:
        written.append(write(guide_url(g), build_guide(g)))
    written.append(write("deals.html", build_deals()))
    written.append(write("how-we-rate.html", build_how_we_rate()))
    written.append(write("affiliate-disclosure.html", build_disclosure()))
    written.append(write("privacy.html", build_privacy()))
    written.append(write("about.html", build_about()))
    written.append(write("404.html", build_404()))
    build_db_js()
    build_sitemap()

    print(f"Built {len(written)} pages at v={VER}")
    for w in written:
        print("  ", w)
    print("   lib/db.js, sitemap.xml, robots.txt")

    if SITE.get("affiliate_tag_placeholder"):
        print("\n  NOTE: affiliate tag is still the placeholder "
              f"'{SITE['affiliate_tag']}'. Replace site.affiliate_tag in "
              "datos/productos.json and re-run to monetise every button.")


if __name__ == "__main__":
    main()
