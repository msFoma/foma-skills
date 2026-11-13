#!/usr/bin/env python3
"""Colour the README icons: Lucide (ISC) line icons plus one hand-drawn icon, in the brand palette.

Usage: python3 scripts/assets/make_icons.py LUCIDE_ICONS_DIR
LUCIDE_ICONS_DIR holds the stock Lucide SVGs (`icons/` of https://github.com/lucide-icons/lucide, or the
`icons/` folder of the npm package `lucide-static`). Output: docs/assets/icons/*.svg (one colour each, no
external refs, readable on light and dark GitHub themes) and the Lucide licence next to them.
Stdlib only. Re-run after changing the mapping below.
"""
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs/assets/icons"
BRAND = "#e8714a"
GROUP = {"setup": "#e0a54a", "proc": "#7fa9d6", "meth": "#4fbfa5", "atom": "#a3adba", "meta": "#e07fa3"}
STROKE = "1.75"

# README section headings (brand orange): file name -> Lucide icon
HEADINGS = {"install": "rocket", "what-you-get": "gift", "first-5-minutes": "compass", "task-flow": "workflow",
            "all-skills": "toolbox", "skill-map": "network", "usage-log": "activity", "cost": "gauge",
            "dropped": "archive", "docs": "book-open", "contributing": "handshake", "license": "scale",
            # small inline icons: feature table, docs table, callouts
            "f-light": "feather", "f-tested": "circle-check", "f-open": "lock-open", "lang": "languages",
            "standard": "ruler", "research": "microscope", "credits": "heart", "how-it-works": "cog",
            "faq": "circle-question-mark", "report": "target", "agents": "bot", "version": "tag"}
# skill groups
GROUPS = {"setup": ("setup", "settings"), "proc": ("proc", "route"), "meth": ("meth", "hammer"),
          "atom": ("atom", "atom"), "meta": ("meta", "puzzle")}
# the 17 skills: name -> (group, Lucide icon)
SKILLS = {"groundwork": ("setup", "blocks"), "tidying": ("setup", "brush-cleaning"), "learning": ("setup", "graduation-cap"),
          "skill-finder": ("setup", "telescope"), "handoff": ("setup", "forward"),
          "shaping": ("proc", "shapes"), "design-interview": ("proc", "messages-square"), "planning": ("proc", "list-checks"),
          "executing": ("proc", "play"),
          "debugging": ("meth", "bug"), "reviewing": ("meth", "scan-search"), "refactoring": ("meth", "recycle"),
          "tdd": ("atom", "flask-conical"), "committing": ("atom", "git-commit-horizontal"), "documenting": ("atom", "file-text"),
          "writing-skills": ("meta", "pen-line"), "tuning": ("meta", "sliders-horizontal")}

# hand-drawn in the same 24-grid, round-capped line style: a check inside a gate, a line passing through it
# (the "propose first, write after your ok" gate of the pack)
OK_GATE = ('<circle cx="12" cy="12" r="6.5" />\n  <path d="m9.2 12.3 2 2 3.8-4.2" />\n'
           '  <path d="M1.8 12h3.7" />\n  <path d="M18.5 12h3.7" />')


def paint(inner, colour):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
            f'stroke="{colour}" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round">\n  {inner}\n</svg>\n')


def body(src):
    m = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S)
    return re.sub(r"\n\s+", "\n  ", m.group(1).strip())


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = {name: (BRAND, icon) for name, icon in HEADINGS.items()}
    jobs.update({f"g-{k}": (GROUP[g], icon) for k, (g, icon) in GROUPS.items()})
    jobs.update({f"skill-{k}": (GROUP[g], icon) for k, (g, icon) in SKILLS.items()})
    for name, (colour, icon) in jobs.items():
        f = src / f"{icon}.svg"
        if not f.is_file():
            sys.exit(f"missing Lucide icon: {icon}.svg")
        (OUT / f"{name}.svg").write_text(paint(body(f.read_text()), colour))
    for name in ("safe", "f-careful"):
        (OUT / f"{name}.svg").write_text(paint(OK_GATE, BRAND))
    licence = src.parent / "LICENSE"
    if licence.is_file():
        (OUT / "LICENSE-lucide.txt").write_text(licence.read_text())
    print(f"wrote {len(jobs) + 2} icons to {OUT}")


if __name__ == "__main__":
    main()
