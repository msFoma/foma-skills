#!/usr/bin/env python3
"""README install steps: three numbered bars (docs/assets/install/step-{1,2,3}.{en,ru}.svg).

Usage: python3 scripts/assets/make_install.py   (stdlib only; reuses the palette and helpers of make_charts.py and make_header.py)
The commands themselves stay plain code blocks in the README (GitHub gives them a copy button); these bars only head
each step. Numbers in the hints come from the repo (skill count, always-on tokens). Each file is self-contained and
static except a slow running light on the border; prefers-reduced-motion turns it off.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_charts as mc  # noqa: E402
import make_header as mh  # noqa: E402

OUT = mc.ROOT / "docs/assets/install"
BRAND, HOT, INK, MUTED, FONT, esc, n = mc.BRAND, mc.HOT, mc.INK, mc.MUTED, mc.FONT, mc.esc, mc.n
W, H = 860, 52


def steps(lang):
    skills, tokens, _, _ = mh.facts()
    k = f"{tokens / 1000:.1f}".replace(".", "," if lang == "ru" else ".")
    if lang == "en":
        return [("Add the marketplace", "one time per machine", "Step 1: add the marketplace"),
                ("Install the plugin", f"{skills} skills, about {k}k tokens always on", "Step 2: install the plugin"),
                ("Restart Claude Code in your project", "the plugin loads when a session starts", "Step 3: restart Claude Code in your project")]
    return [("Добавьте маркетплейс", "один раз на машине", "Шаг 1: добавьте маркетплейс"),
            ("Установите плагин", f"{skills} скиллов, около {k}k токенов всегда", "Шаг 2: установите плагин"),
            ("Перезапустите Claude Code в проекте", "плагин подключается при старте сессии", "Шаг 3: перезапустите Claude Code в проекте")]


def bar(num, title, hint, alt, last):
    tw_t, tw_h = mc.tw(title, 17, True), mc.tw(hint, 13.5)
    if (tw_t + tw_h) * mc.SLACK > W - 62 - 24 - 24:
        sys.exit(f"step bar text too wide: {title!r} + {hint!r}")
    border = BRAND if last else INK
    b_op = "0.7" if last else "0.14"
    fill = "url(#tint)" if last else "url(#bg)"
    body = (f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14101a"/><stop offset="1" stop-color="#0a0910"/></linearGradient>'
            f'<linearGradient id="tint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.22"/><stop offset="1" stop-color="#0a0910"/></linearGradient>'
            f'<linearGradient id="dot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f58f5f"/><stop offset="1" stop-color="{BRAND}"/></linearGradient></defs>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{fill}" stroke="{border}" stroke-opacity="{b_op}"/>'
            f'<circle cx="34" cy="{H / 2}" r="15" fill="url(#dot)"/>'
            f'<text x="34" y="{H / 2 + 5.8}" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="800" fill="#1c0b05">{num}</text>'
            f'<text x="62" y="{H / 2 + 6}" font-family="{FONT}" font-size="17" font-weight="700" fill="{INK}">{esc(title)}</text>'
            f'<text x="{W - 24}" y="{H / 2 + 5}" text-anchor="end" font-family="{FONT}" font-size="13.5" fill="{MUTED}">{esc(hint)}</text>'
            f'<rect class="run" x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" pathLength="100" fill="none" stroke="#ffd2ad" '
            'stroke-width="1.5" stroke-linecap="round" stroke-dasharray="6 400" stroke-dashoffset="6"/>')
    css = mc.motion(".run{animation:run 9s ease-in-out 1s infinite}@keyframes run{0%{stroke-dashoffset:6}60%,100%{stroke-dashoffset:-106}}")
    return mh.svg(W, H, alt, body, css)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "ru"):
        rows = steps(lang)
        for i, (title, hint, alt) in enumerate(rows, 1):
            (OUT / f"step-{i}.{lang}.svg").write_text(bar(i, title, hint, alt, last=i == len(rows)))
    print("wrote", len(list(OUT.glob("*.svg"))), "svg files to", OUT.relative_to(mc.ROOT))


if __name__ == "__main__":
    main()
