# BrewCompare

An Amazon affiliate comparison site for superautomatic espresso machines, targeting
amazon.com (United States).

It is not a list of product cards. Every machine is a **record** in one data file, and
every page on the site — reviews, category pages, the comparator, the charts, the buying
guides — is **generated from that record**. Adding a machine means adding data and
re-running one command. No page is ever edited by hand.

---

## The two things you'll actually touch

### 1. `datos/productos.json` — the database

Everything visible on the site lives here: the machines, their specifications, their
scores, the editorial text, the buying guides, and the site-wide affiliate tag.

### 2. `python3 tools/build_site.py` — rebuild

Run this after any change to the data. It rewrites every HTML page, regenerates
`lib/db.js`, refreshes `sitemap.xml`, and bumps the cache-buster so browsers pick up the
new files immediately.

```bash
python3 tools/build_site.py
```

---

## Adding your real affiliate tag

Open `datos/productos.json` and change these two lines near the top:

```json
"affiliate_tag": "YOURTAG-20",
"affiliate_tag_placeholder": true,
```

to

```json
"affiliate_tag": "your-real-tag-20",
"affiliate_tag_placeholder": false,
```

Then rebuild. Every "View on Amazon" button on every page — there are 36 of them — is
rebuilt with your tag. Setting `affiliate_tag_placeholder` to `false` also removes the
yellow "sample catalogue" banner from the top of the site.

If a machine has its own short link (an `amzn.to/...` URL from the Amazon SiteStripe
bar), put it in that machine's `affiliate_url` field and it will be used verbatim,
exactly as Amazon gave it to you, instead of the built URL.

---

## Adding a machine

Copy an existing block inside `"products": [ ... ]` and fill it in. The fields that
matter:

| Field | What it is |
|---|---|
| `id` | URL slug — becomes `machine-<id>.html`. Lowercase, hyphens, no spaces. |
| `asin` | The 10-character code in the Amazon URL after `/dp/`. |
| `affiliate_url` | Your own link, used verbatim. Leave `null` to build one from the ASIN + your tag. |
| `categories` | Any of `home`, `office`, `professional`, `premium`. A machine can be in several. |
| `featured` | `true` puts it on the homepage. |
| `specs` | The numbers. Use `null` for anything you cannot verify — never guess. |
| `scores` | Your 0–10 editorial ratings on the six axes. These drive the radar charts. |
| `sources` | Where the specs came from. Shown at the bottom of the machine's page. |

Then run the build. The machine appears in the catalogue, its category pages, the
comparator, the deals page (if discounted) and the homepage — automatically.

**Never invent a specification.** A `null` renders as an em dash and the site says so
plainly. A made-up number in a comparison table is the one thing that destroys a
comparison site's credibility.

---

## Adding or changing a specification field

Edit `datos/schema.json`. Each entry declares the field's label, type, unit, spec group,
and — importantly — whether a higher or a lower number is better:

```json
{ "key": "noise_db", "label": "Grinder noise", "group": "physical",
  "type": "number", "unit": "dB", "better": "lower", "compare": true }
```

`better` is what tells the comparator which cell to highlight green in that row. Use
`"none"` for fields where neither direction is better (wattage, housing material).

Add the field here, add its value to each machine's `specs`, rebuild, and it appears in
every machine page and in the comparator.

---

## Project layout

```
datos/
  productos.json      ← the database: machines, guides, site settings
  schema.json         ← field definitions: types, units, better-higher-or-lower
tools/
  build_site.py       ← the generator. Run after every data change.
  make_images.py      ← draws the placeholder machine illustrations
styles.css            ← the whole design system, one sectioned file
main.js               ← the client layer: comparator, gallery, filters, reveals
lib/db.js             ← generated — do not edit by hand
assets/img/           ← illustrations, favicon, share card
*.html                ← generated — do not edit by hand
sitemap.xml           ← generated
```

Anything marked generated gets overwritten on the next build. All real edits happen in
`datos/`, `styles.css`, `main.js` and `tools/`.

---

## Technical notes

- **No build tooling, no framework, no dependencies.** Plain HTML, CSS and vanilla
  JavaScript as classic scripts. No npm, no bundler, no `node_modules`.
- **No third-party JavaScript at runtime.** The radar charts are hand-drawn SVG. The site
  ships 0 KB of vendor JS.
- **Works with JavaScript disabled.** Every machine page renders its full specification
  table, price, buy button, radar chart and legal notices from static HTML. The
  comparator falls back to a complete server-rendered comparison of every machine. JS only
  adds interactivity.
- **SEO.** `Product` structured data on machine pages (real values only), `ItemList` on
  category pages, `FAQPage` on guides, generated sitemap, canonical URLs, meta
  descriptions everywhere.
- **Cache busting.** Every build stamps a new `?v=` on `styles.css`, `main.js` and
  `lib/db.js`, so a deploy is never served stale.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`. Use the server rather than double-clicking the HTML
files — a couple of features need a real HTTP origin.

## Publish

The site is a plain folder of static files. Pushing to the `main` branch of the GitHub
repository republishes it via GitHub Pages, usually within a minute.

```bash
git add -A && git commit -m "Update the site" && git push
```

---

## Legal

The affiliate disclosure required by the Amazon Services LLC Associates Program operating
agreement appears in a bar at the top of every page, in a box at the bottom of every
page, in the footer, and on its own dedicated page. Do not remove it — Amazon can and
does close accounts over a missing disclosure.

Prices are labelled with the date they were captured and are never presented as live.
