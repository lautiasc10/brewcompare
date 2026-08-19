#!/usr/bin/env python3
"""
Generates the placeholder product illustrations used by the sample catalogue.

These are original vector drawings in the site's palette, NOT photographs of the
real machines. When real affiliate links are added, the populate step downloads
the actual Amazon product images and these files are replaced.

Run:  python3 tools/make_images.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
IMG.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- palettes ---
MACHINES = {
    "delonghi-magnifica-evo": {
        "body": "#b6b9be", "body_dark": "#8e9196", "trim": "#3b3e43",
        "screen": "#20232a", "glow": "#c47b3a", "wand": True, "carafe": False,
        "label": "MAGNIFICA EVO",
    },
    "philips-5400-lattego": {
        "body": "#2f3236", "body_dark": "#212427", "trim": "#c7cbd1",
        "screen": "#0f2f3d", "glow": "#3fa9d6", "wand": False, "carafe": True,
        "label": "5400 LATTEGO",
    },
    "jura-e8": {
        "body": "#1a1b1e", "body_dark": "#101113", "trim": "#b9bec6",
        "screen": "#141b24", "glow": "#c9963f", "wand": False, "carafe": False,
        "label": "JURA E8",
    },
    "philips-3200-lattego": {
        "body": "#3a3d42", "body_dark": "#26282c", "trim": "#b6bac0",
        "screen": "#10262f", "glow": "#4bb3d8", "wand": False, "carafe": True,
        "label": "3200 LATTEGO",
    },
    "gaggia-anima-prestige": {
        "body": "#c2c5c9", "body_dark": "#8d9196", "trim": "#33363b",
        "screen": "#0e1a33", "glow": "#4a72c4", "wand": False, "carafe": True,
        "label": "ANIMA PRESTIGE",
    },
    "delonghi-dinamica-plus": {
        "body": "#a9adb3", "body_dark": "#7d8288", "trim": "#2f3237",
        "screen": "#151a22", "glow": "#c47b3a", "wand": False, "carafe": True,
        "label": "DINAMICA PLUS",
    },
    "philips-5500-lattego": {
        "body": "#26282b", "body_dark": "#17191b", "trim": "#cfd3d8",
        "screen": "#0d2b3a", "glow": "#3fa9d6", "wand": False, "carafe": True,
        "label": "5500 LATTEGO",
    },
    "jura-ena-8": {
        "body": "#202226", "body_dark": "#141619", "trim": "#c0c5cc",
        "screen": "#141b24", "glow": "#c9963f", "wand": False, "carafe": False,
        "label": "JURA ENA 8",
    },
    "miele-cm5310-silence": {
        "body": "#232427", "body_dark": "#141517", "trim": "#9aa0a8",
        "screen": "#1a1410", "glow": "#b8383c", "wand": False, "carafe": False,
        "label": "MIELE CM 5310",
    },
    "jura-we8": {
        "body": "#2b2d31", "body_dark": "#1a1c1f", "trim": "#c3c8ce",
        "screen": "#141b24", "glow": "#c9963f", "wand": False, "carafe": False,
        "label": "JURA WE8",
    },
}

W = H = 640


def head(uid: str, p: dict) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
<defs>
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f8f2e8"/><stop offset="1" stop-color="#eadfcd"/>
  </linearGradient>
  <radialGradient id="glow{uid}" cx="50%" cy="38%" r="52%">
    <stop offset="0" stop-color="{p['glow']}" stop-opacity=".22"/>
    <stop offset="1" stop-color="{p['glow']}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="body{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{p['body_dark']}"/>
    <stop offset=".42" stop-color="{p['body']}"/>
    <stop offset="1" stop-color="{p['body_dark']}"/>
  </linearGradient>
  <linearGradient id="chrome{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{p['trim']}" stop-opacity=".55"/>
    <stop offset=".5" stop-color="{p['trim']}"/>
    <stop offset="1" stop-color="{p['trim']}" stop-opacity=".55"/>
  </linearGradient>
  <linearGradient id="scr{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['screen']}"/><stop offset="1" stop-color="#05070a"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg{uid})"/>
<rect width="{W}" height="{H}" fill="url(#glow{uid})"/>
<ellipse cx="320" cy="556" rx="196" ry="24" fill="#2a201a" opacity=".14"/>"""


def machine_front(p: dict, uid: str) -> str:
    """Front elevation of the machine."""
    s = []
    # bean hopper lid
    s.append(f'<rect x="216" y="88" width="208" height="34" rx="16" fill="url(#chrome{uid})"/>')
    s.append(f'<rect x="248" y="80" width="144" height="16" rx="8" fill="{p["body_dark"]}" opacity=".85"/>')
    # main body
    s.append(f'<rect x="196" y="116" width="248" height="352" rx="26" fill="url(#body{uid})"/>')
    # side highlight
    s.append(f'<rect x="206" y="130" width="10" height="322" rx="5" fill="#ffffff" opacity=".14"/>')
    # display panel
    s.append(f'<rect x="226" y="150" width="188" height="78" rx="12" fill="url(#scr{uid})"/>')
    s.append(f'<rect x="240" y="166" width="70" height="8" rx="4" fill="{p["glow"]}" opacity=".85"/>')
    s.append(f'<rect x="240" y="184" width="118" height="6" rx="3" fill="#ffffff" opacity=".34"/>')
    s.append(f'<rect x="240" y="198" width="92" height="6" rx="3" fill="#ffffff" opacity=".2"/>')
    for i, cx in enumerate((356, 380, 404)):
        s.append(f'<circle cx="{cx}" cy="210" r="6" fill="{p["glow"]}" opacity="{0.9 - i*0.28:.2f}"/>')
    # brand plate
    s.append(f'<rect x="226" y="240" width="188" height="3" rx="1.5" fill="url(#chrome{uid})" opacity=".7"/>')
    # spout head
    s.append(f'<rect x="246" y="256" width="148" height="62" rx="14" fill="{p["body_dark"]}"/>')
    s.append(f'<rect x="258" y="268" width="124" height="6" rx="3" fill="url(#chrome{uid})" opacity=".8"/>')
    s.append(f'<rect x="292" y="316" width="12" height="20" rx="4" fill="url(#chrome{uid})"/>')
    s.append(f'<rect x="336" y="316" width="12" height="20" rx="4" fill="url(#chrome{uid})"/>')
    # cup
    s.append('<path d="M282 372 L358 372 L349 424 Q348 432 340 432 L300 432 Q292 432 291 424 Z" fill="#fdfaf4"/>')
    s.append('<path d="M282 372 L358 372 L356 384 L284 384 Z" fill="#e8ddcb"/>')
    s.append(f'<path d="M358 384 q22 2 20 18 q-2 16 -22 16" fill="none" stroke="#fdfaf4" stroke-width="7" stroke-linecap="round"/>')
    s.append('<ellipse cx="320" cy="374" rx="36" ry="6" fill="#6b4224"/>')
    s.append('<ellipse cx="320" cy="373" rx="26" ry="4" fill="#c08a4e" opacity=".8"/>')
    # drip tray
    s.append(f'<rect x="256" y="436" width="128" height="14" rx="4" fill="url(#chrome{uid})"/>')
    s.append(f'<rect x="196" y="452" width="248" height="26" rx="12" fill="{p["body_dark"]}"/>')
    # steam wand
    if p["wand"]:
        s.append(f'<circle cx="452" cy="262" r="15" fill="{p["body_dark"]}"/>')
        s.append(f'<rect x="446" y="262" width="12" height="96" rx="6" fill="url(#chrome{uid})"/>')
        s.append(f'<rect x="442" y="352" width="20" height="16" rx="6" fill="{p["body_dark"]}"/>')
    # milk carafe
    if p["carafe"]:
        s.append(f'<rect x="120" y="330" width="76" height="118" rx="12" fill="#f2f4f6" opacity=".92"/>')
        s.append(f'<rect x="120" y="330" width="76" height="24" rx="10" fill="{p["trim"]}"/>')
        s.append(f'<rect x="130" y="372" width="56" height="66" rx="8" fill="#ffffff" opacity=".7"/>')
        s.append(f'<rect x="188" y="352" width="34" height="9" rx="4" fill="{p["trim"]}"/>')
    return "".join(s)


def machine_angle(p: dict, uid: str) -> str:
    """Three-quarter view, showing the bean hopper open."""
    s = []
    # depth: a darker side panel offset to the right, drawn first
    s.append(f'<path d="M400 150 L452 176 L452 448 L400 470 Z" fill="{p["body_dark"]}"/>')
    s.append(f'<path d="M400 150 L452 176 L452 200 L400 176 Z" fill="#ffffff" opacity=".08"/>')
    # main face
    s.append(f'<rect x="192" y="140" width="212" height="322" rx="22" fill="url(#body{uid})"/>')
    s.append(f'<rect x="202" y="154" width="9" height="294" rx="4.5" fill="#ffffff" opacity=".14"/>')
    # open hopper with beans, sitting on top and following the perspective
    s.append(f'<path d="M192 152 L404 152 L452 178 L240 178 Z" fill="{p["body_dark"]}"/>')
    s.append(f'<ellipse cx="298" cy="140" rx="104" ry="30" fill="{p["body_dark"]}"/>')
    s.append(f'<ellipse cx="298" cy="138" rx="90" ry="23" fill="#2b1a11"/>')
    beans = [(262, 132), (292, 126), (324, 134), (278, 145), (314, 145), (344, 137), (250, 142)]
    for bx, by in beans:
        s.append(f'<ellipse cx="{bx}" cy="{by}" rx="11" ry="8" fill="#6a3f22" transform="rotate(-18 {bx} {by})"/>')
        s.append(f'<path d="M{bx-8} {by} q8 -5 16 0 q-8 5 -16 0" fill="#3c2213" transform="rotate(-18 {bx} {by})"/>')
    # display
    s.append(f'<rect x="216" y="196" width="164" height="72" rx="12" fill="url(#scr{uid})"/>')
    s.append(f'<rect x="230" y="212" width="84" height="9" rx="4" fill="{p["glow"]}" opacity=".9"/>')
    s.append(f'<rect x="230" y="230" width="118" height="6" rx="3" fill="#fff" opacity=".3"/>')
    s.append(f'<rect x="230" y="244" width="92" height="6" rx="3" fill="#fff" opacity=".18"/>')
    # spout head + twin spouts
    s.append(f'<rect x="230" y="288" width="136" height="56" rx="14" fill="{p["body_dark"]}"/>')
    s.append(f'<rect x="244" y="300" width="108" height="6" rx="3" fill="url(#chrome{uid})" opacity=".8"/>')
    s.append(f'<rect x="272" y="342" width="12" height="20" rx="5" fill="url(#chrome{uid})"/>')
    s.append(f'<rect x="312" y="342" width="12" height="20" rx="5" fill="url(#chrome{uid})"/>')
    # two cups
    for cx in (278, 318):
        s.append(f'<path d="M{cx-30} 386 L{cx+30} 386 L{cx+23} 434 Q{cx+22} 442 {cx+14} 442 '
                 f'L{cx-14} 442 Q{cx-22} 442 {cx-23} 434 Z" fill="#fdfaf4"/>')
        s.append(f'<path d="M{cx-30} 386 L{cx+30} 386 L{cx+28} 396 L{cx-28} 396 Z" fill="#e8ddcb"/>')
        s.append(f'<ellipse cx="{cx}" cy="388" rx="28" ry="6" fill="#6b4224"/>')
        s.append(f'<ellipse cx="{cx}" cy="387" rx="20" ry="4" fill="#c08a4e" opacity=".8"/>')
    # drip tray
    s.append(f'<rect x="238" y="446" width="118" height="12" rx="4" fill="url(#chrome{uid})"/>')
    s.append(f'<path d="M192 458 L404 458 L452 434 L452 462 L404 486 L192 486 Z" fill="{p["body_dark"]}"/>')
    return "".join(s)


def machine_detail(p: dict, uid: str) -> str:
    """Close-up: spout pouring into a cup, with steam."""
    s = []
    s.append(f'<rect x="156" y="72" width="330" height="150" rx="22" fill="url(#body{uid})"/>')
    s.append(f'<rect x="180" y="100" width="282" height="10" rx="5" fill="url(#chrome{uid})" opacity=".55"/>')
    s.append(f'<rect x="216" y="212" width="210" height="66" rx="16" fill="{p["body_dark"]}"/>')
    s.append(f'<rect x="234" y="228" width="174" height="8" rx="4" fill="url(#chrome{uid})" opacity=".8"/>')
    s.append(f'<rect x="286" y="276" width="16" height="30" rx="6" fill="url(#chrome{uid})"/>')
    s.append(f'<rect x="342" y="276" width="16" height="30" rx="6" fill="url(#chrome{uid})"/>')
    # streams
    for x in (294, 350):
        s.append(f'<rect x="{x}" y="306" width="4" height="72" rx="2" fill="#7a4a26" opacity=".85"/>')
    # big cup
    s.append('<path d="M242 376 L404 376 L386 486 Q384 500 370 500 L276 500 Q262 500 260 486 Z" fill="#fdfaf4"/>')
    s.append('<path d="M242 376 L404 376 L400 400 L246 400 Z" fill="#e8ddcb"/>')
    s.append('<path d="M404 402 q46 4 42 40 q-4 36 -48 36" fill="none" stroke="#fdfaf4" stroke-width="14" stroke-linecap="round"/>')
    s.append('<ellipse cx="323" cy="380" rx="78" ry="13" fill="#5d3819"/>')
    s.append('<ellipse cx="323" cy="378" rx="60" ry="9" fill="#c99659"/>')
    s.append('<ellipse cx="305" cy="377" rx="16" ry="5" fill="#e5c9a2" opacity=".8"/>')
    # saucer
    s.append('<ellipse cx="323" cy="506" rx="118" ry="17" fill="#f3ece0"/>')
    s.append('<ellipse cx="323" cy="502" rx="118" ry="17" fill="#fdfaf4"/>')
    # steam
    for i, sx in enumerate((286, 323, 360)):
        o = 0.5 - i * 0.08
        s.append(f'<path d="M{sx} 350 q-16 -26 0 -50 q16 -24 0 -48" fill="none" stroke="#ffffff" '
                 f'stroke-width="7" stroke-linecap="round" opacity="{o:.2f}"/>')
    return "".join(s)


VIEWS = {1: machine_front, 2: machine_angle, 3: machine_detail}


def build() -> None:
    written = []
    for pid, p in MACHINES.items():
        for n, fn in VIEWS.items():
            uid = f"{pid.replace('-', '')}{n}"
            svg = head(uid, p) + fn(p, uid) + "</svg>"
            path = IMG / f"{pid}-{n}.svg"
            path.write_text(svg, encoding="utf-8")
            written.append(path.name)

    # ---- site favicon / logo mark: a stylised bean split into two halves ----
    logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
<rect width="64" height="64" rx="14" fill="#17120f"/>
<ellipse cx="32" cy="32" rx="19" ry="14" fill="#b5651d" transform="rotate(-38 32 32)"/>
<path d="M18 32 q14 -11 28 0 q-14 11 -28 0" fill="#17120f" transform="rotate(-38 32 32)"/>
<circle cx="32" cy="32" r="26" fill="none" stroke="#c9963f" stroke-width="2.5" opacity=".55"/>
</svg>"""
    (ROOT / "assets" / "favicon.svg").write_text(logo, encoding="utf-8")
    written.append("favicon.svg")

    # ---- open-graph share card ----
    og = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#17120f"/><stop offset="1" stop-color="#2b1d14"/></linearGradient></defs>
<rect width="1200" height="630" fill="url(#g)"/>
<circle cx="1010" cy="150" r="220" fill="#b5651d" opacity=".18"/>
<text x="90" y="270" font-family="Georgia,serif" font-size="86" fill="#faf7f2">BrewCompare</text>
<text x="90" y="340" font-family="Helvetica,Arial,sans-serif" font-size="34" fill="#c9963f">Superautomatic espresso machines, compared properly.</text>
<text x="90" y="410" font-family="Helvetica,Arial,sans-serif" font-size="26" fill="#a89a8e">Real specs · Editor scores on six axes · Side-by-side comparator</text>
</svg>"""
    (ROOT / "assets" / "img" / "og-card.svg").write_text(og, encoding="utf-8")
    written.append("og-card.svg")

    print(f"Wrote {len(written)} images:")
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    build()
