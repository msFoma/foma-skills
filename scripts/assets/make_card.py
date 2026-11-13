#!/usr/bin/env python3
"""Project banner cards for the GitHub profile (docs/assets/cards/<id>.{en,ru}.svg), one per entry of cards.json.

Usage: python3 scripts/assets/make_card.py   (stdlib only; reuses the palette and helpers of make_charts.py and make_header.py)

Adding a card for another skill or project = add one object to docs/assets/cards/cards.json:
  id        file name stem
  mascot    image file in docs/assets/cards/ (JPEG or PNG), cropped to a circle; optional
  title     [plain word, accent word]
  eyebrow   {"en": ..., "ru": ...} small caps line above the title
  tagline   {"en": ..., "ru": ...} one sentence under the title
  stats     up to 3 of {"value", "label": {"en","ru"}, "icon", "color"}; icon is a file in docs/assets/icons,
            colour a hex or a palette key (setup, proc, meth, atom, meta); value "@skills", "@tokens", "@version"
            are filled from this repo (skill count, always-on tokens from tokens.json, plugin version)
Each SVG is self-contained (the mascot is a data URI) and dark, so it reads on light and dark themes.
Motion: twinkling stars, a breathing star flare, a pulsing ring around the mascot; only transform and opacity animate;
prefers-reduced-motion turns it off.
"""
import base64
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_charts as mc  # noqa: E402
import make_header as mh  # noqa: E402

ROOT = mc.ROOT
DIR = ROOT / "docs/assets/cards"
BRAND, HOT, INK, MUTED, COL, FONT, esc, n = mc.BRAND, mc.HOT, mc.INK, mc.MUTED, mc.COL, mc.FONT, mc.esc, mc.n
W, H = 860, 300
MASCOT_D, MASCOT_X = 176, 46


def resolve(value, lang="en"):
    skills, tokens, _, version = mh.facts()
    if value == "@skills":
        return str(skills)
    if value == "@tokens":
        return f"≈{tokens / 1000:.1f}k".replace(".", "," if lang == "ru" else ".")
    if value == "@version":
        return f"v{version}"
    return value


def colour(c):
    return COL.get(c, c)


def stars(seed):
    rnd = random.Random(seed)
    out, tw = [], []
    for i in range(70):
        x, y = rnd.uniform(8, W - 8), rnd.uniform(8, H - 8)
        if 20 < x < 280 and 40 < y < 260:  # keep the mascot clear
            continue
        r = rnd.choice((0.5, 0.7, 0.9, 1.2))
        fill = rnd.choice((INK, "#ffd6bf", "#c9d3ff"))
        op = rnd.uniform(0.25, 0.65)
        if i % 6 == 0:
            tw.append(f'<circle class="tw" style="animation-delay:{rnd.uniform(0, 4):.1f}s" cx="{x:.0f}" cy="{y:.0f}" r="{r + 0.4}" fill="{fill}"/>')
        else:
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{fill}" fill-opacity="{op:.2f}"/>')
    return "".join(out) + "".join(tw)


def flare(cx, cy):
    """A four-point star: two thin crossed diamonds and a soft glow."""
    return (f'<g class="fr"><ellipse cx="{cx}" cy="{cy}" rx="46" ry="46" fill="url(#glow)"/>'
            f'<path d="M{cx},{cy - 58} L{cx + 3.2},{cy} L{cx},{cy + 58} L{cx - 3.2},{cy} Z" fill="#ffe3cc" fill-opacity="0.95"/>'
            f'<path d="M{cx - 86},{cy} L{cx},{cy - 3} L{cx + 86},{cy} L{cx},{cy + 3} Z" fill="#ffd2ad" fill-opacity="0.85"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="#fff4ea"/></g>')


def card(spec, lang):
    title_a, title_b = spec["title"]
    eyebrow, tagline = spec["eyebrow"][lang], spec["tagline"][lang]
    tx = MASCOT_X + MASCOT_D + 46
    maxw = W - tx - 48
    t_size = 58
    mc.fit(f"{title_a} {title_b}", t_size, maxw, True)
    lines = mc.wrap(tagline, 17, maxw)
    ty = 128
    body = ""
    if spec.get("mascot"):
        p = DIR / spec["mascot"]
        mime = "image/png" if p.suffix == ".png" else "image/jpeg"
        b64 = base64.b64encode(p.read_bytes()).decode()
        cy = H / 2
        body += (f'<circle class="ring" cx="{MASCOT_X + MASCOT_D / 2}" cy="{cy}" r="{MASCOT_D / 2 + 5}" fill="none" stroke="url(#rg)" stroke-width="2.5"/>'
                 f'<circle cx="{MASCOT_X + MASCOT_D / 2}" cy="{cy}" r="{MASCOT_D / 2 + 5}" fill="#0b0a10"/>'
                 f'<image href="data:{mime};base64,{b64}" x="{MASCOT_X}" y="{cy - MASCOT_D / 2}" width="{MASCOT_D}" height="{MASCOT_D}" '
                 'clip-path="url(#mc)" preserveAspectRatio="xMidYMid slice"/>'
                 f'<circle cx="{MASCOT_X + MASCOT_D / 2}" cy="{cy}" r="{MASCOT_D / 2}" fill="none" stroke="url(#rg)" stroke-width="2.5"/>')
    body += (f'<text x="{tx}" y="64" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="2.2" fill="{BRAND}">{esc(eyebrow)}</text>'
             f'<text x="{tx}" y="{ty}" font-family="{FONT}" font-size="{t_size}" font-weight="800" fill="{INK}" letter-spacing="-1">{esc(title_a)}'
             f'<tspan fill="url(#tg)"> {esc(title_b)}</tspan></text>')
    y = ty + 34
    for ln in lines:
        body += f'<text x="{tx}" y="{y}" font-family="{FONT}" font-size="17" fill="{MUTED}">{esc(ln)}</text>'
        y += 24
    # stat chips
    cx, cy2 = tx, H - 62
    for st in spec["stats"][:3]:
        val, lab = resolve(st["value"], lang), st["label"][lang]
        c = colour(st["color"])
        vw, lw = mc.tw(val, 15, True), mc.tw(lab, 12.5)
        w = int(14 + 16 + 8 + vw + 8 + lw + 14)
        body += (f'<rect x="{cx + 0.5}" y="{cy2 + 0.5}" width="{w - 1}" height="38" rx="19" fill="#12101a" stroke="{INK}" stroke-opacity="0.14"/>'
                 f'{mh.icon(st["icon"], c, cx + 14, cy2 + 11, 16)}'
                 f'<text x="{n(cx + 14 + 16 + 8)}" y="{cy2 + 24.2}" font-family="{FONT}" font-size="15" font-weight="800" fill="{INK}">{esc(val)}</text>'
                 f'<text x="{n(cx + 14 + 16 + 8 + vw + 8)}" y="{cy2 + 24}" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{esc(lab)}</text>')
        cx += w + 10
    if cx - 10 > W - 36:
        sys.exit(f"stat chips too wide for the card: {spec['id']} ({lang})")
    defs = (f'<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>'
            f'<clipPath id="mc"><circle cx="{MASCOT_X + MASCOT_D / 2}" cy="{H / 2}" r="{MASCOT_D / 2}"/></clipPath>'
            '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0e0b14"/><stop offset="1" stop-color="#060509"/></linearGradient>'
            f'<radialGradient id="n1"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.26"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="n2"><stop offset="0" stop-color="#6f74b8" stop-opacity="0.2"/><stop offset="1" stop-color="#6f74b8" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="glow"><stop offset="0" stop-color="#ffb27a" stop-opacity="0.75"/><stop offset="1" stop-color="#ffb27a" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{HOT}"/><stop offset="1" stop-color="#86b2f2"/></linearGradient>'
            f'<linearGradient id="tg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f58f5f"/><stop offset="1" stop-color="{BRAND}"/></linearGradient></defs>')
    arc = (f'<path d="M-20,{H - 40} C {W * 0.35},{H - 150} {W * 0.7},{H - 190} {W + 20},{H - 120}" fill="none" stroke="{BRAND}" stroke-opacity="0.22" stroke-width="1.4"/>'
           f'<path d="M-20,{H - 10} C {W * 0.4},{H - 130} {W * 0.75},{H - 175} {W + 20},{H - 80}" fill="none" stroke="{INK}" stroke-opacity="0.08" stroke-width="1"/>')
    inner = (f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/>'
             f'<ellipse cx="90" cy="20" rx="330" ry="130" fill="url(#n1)"/><ellipse cx="{W - 60}" cy="{H}" rx="360" ry="120" fill="url(#n2)"/>'
             f'{arc}{stars(len(spec["id"]) * 7)}{flare(W - 96, 70)}{body}</g>'
             f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="21.5" fill="none" stroke="{INK}" stroke-opacity="0.14"/>')
    css = mc.motion(".tw{animation:tw 4s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}"
                    ".fr{transform-box:fill-box;transform-origin:center;animation:fr 6s ease-in-out infinite}"
                    "@keyframes fr{0%,55%,100%{transform:scale(1)}70%{transform:scale(1.12,1.22)}85%{transform:scale(.98)}}"
                    ".ring{transform-box:fill-box;transform-origin:center;animation:ring 4s ease-out infinite}"
                    "@keyframes ring{0%{transform:scale(1);opacity:.7}70%,100%{transform:scale(1.14);opacity:0}}")
    label = f"{title_a} {title_b}: {tagline}"
    return mh.svg(W, H, label, defs + inner, css)


def main():
    specs = json.loads((DIR / "cards.json").read_text())
    for spec in specs:
        for lang in ("en", "ru"):
            svg = card(spec, lang)
            (DIR / f"{spec['id']}.{lang}.svg").write_text(svg)
            print(f"{spec['id']}.{lang}.svg  {len(svg) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
