#!/usr/bin/env python3
"""README header assets: a stats strip, navigation pills and language pills (docs/assets/header/*.svg).

Usage: python3 scripts/assets/make_header.py   (stdlib only; reuses the palette and helpers of make_charts.py)
The numbers come from the repo: skill count (skills dir), always-on tokens (docs/assets/charts/tokens.json),
helper agents (docs/agents), version (plugin.json). Icons are the recoloured Lucide files in docs/assets/icons.
Each file is self-contained (no fonts, scripts or external refs) and is a dark card, so it reads on light and dark themes.
"""
import json
import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_charts as mc  # noqa: E402

ROOT = mc.ROOT
OUT = ROOT / "docs/assets/header"
BRAND, HOT, INK, MUTED, COL, FONT, esc, n = mc.BRAND, mc.HOT, mc.INK, mc.MUTED, mc.COL, mc.FONT, mc.esc, mc.n


def facts():
    skills = len([p for p in (ROOT / "plugins/foma-skills/skills").iterdir() if (p / "SKILL.md").is_file()])
    tokens = json.loads((ROOT / "docs/assets/charts/tokens.json").read_text())["always_total"]
    agents = len(list((ROOT / "docs/agents").glob("*.md")))
    version = json.loads((ROOT / "plugins/foma-skills/.claude-plugin/plugin.json").read_text())["version"]
    return skills, tokens, agents, version


def icon(name, colour, x, y, size):
    src = (ROOT / f"docs/assets/icons/{name}.svg").read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
    return (f'<g transform="translate({n(x)},{n(y)}) scale({n(size / 24)})" fill="none" stroke="{colour}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{inner}</g>')


def svg(w, h, label, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
            f'<title>{esc(label)}</title>{css}\n{body}</svg>\n')


def pill(label, icon_name, style=None):
    """style: "cta" (filled, the main action), "live" (accent outline and a pulsing dot, for the live map) or None."""
    cta, live = style == "cta", style == "live"
    h, fs, isz = (44, 16, 20) if (cta or live) else (38, 14, 18)  # the two main actions are larger
    tw = mc.tw(label, fs, True) * 1.04
    w = math.ceil(16 + isz + 9 + tw + 18 + (14 if live else 0))
    fg = "#1c0b05" if cta else INK
    ic = "#1c0b05" if cta else (HOT if live else BRAND)
    fill = "url(#cta)" if cta else ("url(#lv)" if live else "url(#gh)")
    stroke = (f'stroke="{HOT}" stroke-opacity="0.9"' if cta else
              ('stroke="url(#lvs)" stroke-opacity="1"' if live else f'stroke="{BRAND}" stroke-opacity="0.55"'))
    body = (f'<defs><linearGradient id="cta" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f08a5c"/><stop offset="1" stop-color="{BRAND}"/></linearGradient>'
            f'<linearGradient id="gh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a151c"/><stop offset="1" stop-color="#0d0b12"/></linearGradient>'
            f'<linearGradient id="lv" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.3"/><stop offset="1" stop-color="#0d0b12"/></linearGradient>'
            f'<linearGradient id="lvs" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{HOT}"/><stop offset="1" stop-color="#86b2f2"/></linearGradient></defs>'
            f'<rect x="0.9" y="0.9" width="{w - 1.8}" height="{h - 1.8}" rx="{h / 2 - 0.9}" fill="{fill}" {stroke} stroke-width="{1.8 if live else 1.5}"/>'
            f'{icon(icon_name, ic, 16, (h - isz) / 2, isz)}'
            f'<text x="{n(16 + isz + 9)}" y="{n(h / 2 + fs * 0.36)}" font-family="{FONT}" font-size="{fs}" font-weight="{700 if (cta or live) else 600}" fill="{fg}">{esc(label)}</text>')
    css = ""
    if live:
        cx, cy = w - 17, h / 2
        body += (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="3.4" fill="#5fceb4"/>'
                 f'<circle class="pl" cx="{n(cx)}" cy="{n(cy)}" r="3.4" fill="none" stroke="#5fceb4" stroke-width="1.4"/>')
        css = mc.motion(".pl{transform-box:fill-box;transform-origin:center;animation:pl 2.4s ease-out infinite}"
                        "@keyframes pl{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(2.9);opacity:0}}")
    return svg(w, h, label, body, css)


def lang_pill(label, on):
    h, fs = 34, 14
    w = math.ceil(mc.tw(label, fs, True) * 1.04 + 34)
    if on:
        look = f'fill="{BRAND}" fill-opacity="0.2" stroke="{BRAND}" stroke-width="1.5"'
        txt = f'fill="{INK}" font-weight="700"'
    else:
        look = f'fill="#0d0b12" stroke="{INK}" stroke-opacity="0.22" stroke-width="1.2"'
        txt = f'fill="{MUTED}" font-weight="600"'
    body = (f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="{h / 2 - 0.75}" fill="#0d0b12"/>'
            f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="{h / 2 - 0.75}" {look}/>'
            f'<text x="{n(w / 2)}" y="22" text-anchor="middle" font-family="{FONT}" font-size="{fs}" {txt}>{esc(label)}</text>')
    return svg(w, h, label, body)


STATS = {
    "en": ["skills", "tokens always on", "helper agents", "license", "pre-release"],
    "ru": ["скиллов", "токенов всегда", "агента-помощника", "лицензия", "пре-релиз"],
}


def stats(lang):
    skills, tokens, agents, version = facts()
    k = f"{tokens / 1000:.1f}".replace(".", "," if lang == "ru" else ".")
    vals = [str(skills), f"≈{k}k", str(agents), "Apache-2.0", f"v{version}"]
    icons = [("all-skills", BRAND), ("cost", COL["setup"]), ("agents", COL["meta"]), ("license", COL["meth"]), ("version", COL["proc"])]
    w, h, seg = 960, 112, 960 / 5
    rnd = random.Random(7)
    s = (f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath>'
         '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0b13"/><stop offset="1" stop-color="#060509"/></linearGradient>'
         f'<radialGradient id="n1"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.22"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="n2"><stop offset="0" stop-color="#6f74b8" stop-opacity="0.16"/><stop offset="1" stop-color="#6f74b8" stop-opacity="0"/></radialGradient></defs>'
         f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#bg)"/>'
         f'<ellipse cx="60" cy="0" rx="300" ry="90" fill="url(#n1)"/><ellipse cx="{w - 80}" cy="{h}" rx="320" ry="80" fill="url(#n2)"/>')
    for i in range(34):
        s += (f'<circle cx="{rnd.uniform(6, w - 6):.0f}" cy="{rnd.uniform(5, h - 5):.0f}" r="{rnd.choice((0.5, 0.7, 0.9, 1.2))}" '
              f'fill="{rnd.choice((INK, "#ffd6bf", "#c9d3ff"))}" fill-opacity="{rnd.uniform(0.2, 0.6):.2f}"/>')
    s += "</g>"
    for i, (val, label, (ic, colour)) in enumerate(zip(vals, STATS[lang], icons)):
        cx = seg * (i + 0.5)
        size = 34 if mc.tw(val, 34, True) <= seg - 40 else 26
        s += icon(ic, colour, cx - 10, 14, 20)
        s += (f'<text x="{n(cx)}" y="68" text-anchor="middle" font-family="{FONT}" font-size="{size}" font-weight="800" fill="{INK}">{esc(val)}</text>'
              f'<text x="{n(cx)}" y="92" text-anchor="middle" font-family="{FONT}" font-size="13.5" fill="{MUTED}">{esc(label)}</text>')
        if i:
            s += f'<line x1="{n(seg * i)}" y1="24" x2="{n(seg * i)}" y2="88" stroke="{INK}" stroke-opacity="0.1"/>'
    s += (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="21.5" fill="none" stroke="{INK}" stroke-opacity="0.12"/>'
          f'<rect class="run" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="21.5" pathLength="100" fill="none" stroke="#ffd2ad" '
          'stroke-width="1.6" stroke-linecap="round" stroke-dasharray="7 400" stroke-dashoffset="7"/>')
    css = mc.motion(".run{animation:run 10s ease-in-out 1s infinite}@keyframes run{0%{stroke-dashoffset:7}65%,100%{stroke-dashoffset:-107}}")
    return svg(w, h, "  ·  ".join(f"{v} {l}" for v, l in zip(vals, STATS[lang])), s, css)


NAV = {
    "en": [("install", "Install", "install", "cta"), ("map", "Live map", "skill-map", "live"),
           ("what-you-get", "What you get", "what-you-get", None), ("first-5-minutes", "First 5 minutes", "first-5-minutes", None),
           ("skills", "All skills", "all-skills", None), ("docs", "Документация на русском", "lang", None)],
    "ru": [("install", "Установка", "install", "cta"), ("map", "Живая карта", "skill-map", "live"),
           ("what-you-get", "Что вы получаете", "what-you-get", None), ("first-5-minutes", "Первые 5 минут", "first-5-minutes", None),
           ("skills", "Все скиллы", "all-skills", None), ("docs", "Документация", "docs", None)],
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "ru"):
        (OUT / f"stats.{lang}.svg").write_text(stats(lang))
        widths = []
        for key, label, ic, style in NAV[lang]:
            text = pill(label, ic, style)
            (OUT / f"nav-{key}.{lang}.svg").write_text(text)
            widths.append(int(re.search(r'width="(\d+)"', text).group(1)))
        print(f"nav {lang}: {len(widths)} pills, {sum(widths)} px + gaps")
    for lang, label in (("en", "English"), ("ru", "Русский")):
        for on in (True, False):
            (OUT / f"lang-{lang}.{'on' if on else 'off'}.svg").write_text(lang_pill(label, on))
    print("wrote", len(list(OUT.glob("*.svg"))), "svg files to", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
