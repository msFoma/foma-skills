#!/usr/bin/env python3
"""README teaser for the live skill map: a browser-window card with a real screenshot of docs/graph.html
(docs/assets/graph-teaser.{en,ru}.svg).

Usage: python3 scripts/make_graph_preview.py
Needs Chrome (set CHROME to its binary if it is not the macOS default) and `sips` (macOS) to turn the screenshot into
a JPEG; stdlib only otherwise. Rerun it after the graph page or the skills change (make_graph.py first).
Each SVG embeds the JPEG as a data URI (an <img> SVG cannot load files), so it is self-contained. Motion: a shimmer
and a soft ring on the call-to-action button; only transform and opacity animate; prefers-reduced-motion turns it off.
"""
import base64
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_charts as mc  # noqa: E402

ROOT = mc.ROOT
OUT = ROOT / "docs/assets"
GRAPH = ROOT / "docs/graph.html"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
BRAND, HOT, INK, MUTED, COL, FONT, esc, n = mc.BRAND, mc.HOT, mc.INK, mc.MUTED, mc.COL, mc.FONT, mc.esc, mc.n
SHOT_W, SHOT_H = 1280, 760
W, PAD, BAR = 860, 32, 38
IMG_H = round(W * SHOT_H / SHOT_W)
H = BAR + IMG_H
BODY = "#0a0910"
URL = "t8jwscc7qy-sketch.github.io/foma-skills/graph.html"

T = {
    "en": {"title": "Explore the live skill map",
           "sub": "Hover a skill, filter by group, press “Play a task” and watch a request travel through the pack.",
           "cta": "Open the live map", "alt": "The live skill map in a browser window: 17 skills in five groups, who calls whom. Click to open it."},
    "ru": {"title": "Откройте живую карту скиллов",
           "sub": "Наведите на скилл, фильтруйте по группам, нажмите «Проиграть задачу» и смотрите, как идёт запрос.",
           "cta": "Открыть живую карту", "alt": "Живая карта скиллов в окне браузера: 17 скиллов в пяти группах, кто кого вызывает. Нажмите, чтобы открыть."},
}


def screenshot(lang, tmp):
    png, jpg = Path(tmp) / f"{lang}.png", Path(tmp) / f"{lang}.jpg"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={SHOT_W},{SHOT_H}",
                    "--virtual-time-budget=6000", f"--screenshot={png}", f"{GRAPH.as_uri()}#lang={lang}"],
                   check=True, capture_output=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", str(png), "--out", str(jpg)],
                   check=True, capture_output=True)
    return base64.b64encode(jpg.read_bytes()).decode()


def teaser(lang, b64):
    t = T[lang]
    lines = mc.wrap(t["sub"], 14.5, 520)
    cta_w, cta_h = math.ceil(mc.tw(t["cta"], 16, True) * 1.05 + 76), 48
    cx, cy = W - PAD - cta_w, H - 30 - cta_h
    # a two-line subtitle puts the title above the button, so it may use the full width
    mc.fit(t["title"], 26, W - 2 * PAD - (0 if len(lines) > 1 else cta_w + 24), True)
    base = H - 44 - 21 * (len(lines) - 1)
    sub = "".join(f'<text x="{PAD}" y="{n(base + 21 * i)}" font-family="{FONT}" font-size="14.5" fill="{MUTED}">{esc(ln)}</text>'
                  for i, ln in enumerate(lines))
    dots = "".join(f'<circle cx="{PAD - 6 + i * 19}" cy="{BAR / 2}" r="5.5" fill="{c}"/>' for i, c in enumerate((BRAND, COL["setup"], COL["meth"])))
    arrow = (f'<path d="M{n(cx + cta_w - 40)},{n(cy + cta_h / 2)} h15 m-6,-6 l6,6 l-6,6" fill="none" stroke="#1c0b05" stroke-width="2.4" '
             'stroke-linecap="round" stroke-linejoin="round"/>')
    body = (f'<defs><clipPath id="win"><rect width="{W}" height="{H}" rx="16"/></clipPath>'
            f'<clipPath id="cta"><rect x="{n(cx)}" y="{n(cy)}" width="{cta_w}" height="{cta_h}" rx="{cta_h / 2}"/></clipPath>'
            f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BODY}" stop-opacity="0"/>'
            f'<stop offset="0.55" stop-color="{BODY}" stop-opacity="0.86"/><stop offset="1" stop-color="{BODY}" stop-opacity="0.97"/></linearGradient>'
            f'<linearGradient id="btn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f79a68"/><stop offset="1" stop-color="{BRAND}"/></linearGradient>'
            '<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset="0.5" stop-color="#fff" stop-opacity="0.5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
            f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{BODY}"/>'
            f'<rect width="{W}" height="{BAR}" fill="#15111b"/><line x1="0" y1="{BAR - 0.5}" x2="{W}" y2="{BAR - 0.5}" stroke="{INK}" stroke-opacity="0.08"/>{dots}'
            f'<rect x="{W / 2 - 210}" y="7" width="420" height="24" rx="12" fill="#0a0910" stroke="{INK}" stroke-opacity="0.12"/>'
            f'<circle cx="{W / 2 - 192}" cy="{BAR / 2}" r="3.4" fill="#5fceb4"/>'
            f'<text x="{W / 2 - 180}" y="{BAR / 2 + 4}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11.5" fill="{MUTED}">{URL}</text>'
            f'<image href="data:image/jpeg;base64,{b64}" x="0" y="{BAR}" width="{W}" height="{IMG_H}" preserveAspectRatio="xMidYMid slice"/>'
            f'<rect x="0" y="{H - 230}" width="{W}" height="230" fill="url(#fade)"/>'
            f'<text x="{PAD}" y="{n(base - 31)}" font-family="{FONT}" font-size="26" font-weight="800" fill="{INK}">{esc(t["title"])}</text>'
            f'{sub}'
            f'<rect class="ring" x="{n(cx)}" y="{n(cy)}" width="{cta_w}" height="{cta_h}" rx="{cta_h / 2}" fill="none" stroke="{HOT}" stroke-width="2"/>'
            f'<rect x="{n(cx)}" y="{n(cy)}" width="{cta_w}" height="{cta_h}" rx="{cta_h / 2}" fill="url(#btn)"/>'
            f'<g clip-path="url(#cta)"><rect class="sh" x="{n(cx - 90)}" y="{n(cy - 4)}" width="70" height="{cta_h + 8}" fill="url(#sh)"/></g>'
            f'<text x="{n(cx + 26)}" y="{n(cy + cta_h / 2 + 5.8)}" font-family="{FONT}" font-size="16" font-weight="800" fill="#1c0b05">{esc(t["cta"])}</text>{arrow}</g>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{INK}" stroke-opacity="0.16"/>')
    css = mc.motion(f".ring{{transform-box:fill-box;transform-origin:center;animation:ring 3s ease-out infinite}}"
                    "@keyframes ring{0%{transform:scale(1);opacity:.8}70%,100%{transform:scale(1.12,1.35);opacity:0}}"
                    f".sh{{animation:sh 4.5s ease-in-out 1s infinite}}@keyframes sh{{0%{{transform:translateX(0)}}55%,100%{{transform:translateX({cta_w + 160}px)}}}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["alt"])}">\n'
            f'<title>{esc(t["alt"])}</title>{css}\n{body}</svg>\n')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        for lang in ("en", "ru"):
            svg = teaser(lang, screenshot(lang, tmp))
            (OUT / f"graph-teaser.{lang}.svg").write_text(svg)
            print(f"graph-teaser.{lang}.svg  {len(svg) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
