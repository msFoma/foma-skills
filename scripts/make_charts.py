#!/usr/bin/env python3
"""Build the README infographics (SVG, English and Russian) from real data. Free: no model calls.

Usage: python3 scripts/make_charts.py [--refresh PROJECT_DIR]
Writes docs/assets/charts/{token-cost,skill-map,propose-first}.{en,ru}.svg and docs/assets/hero.svg
(the hero is rebuilt only where its background plate, which is not committed, exists).
Token numbers come from docs/assets/charts/tokens.json, captured from Claude Code's own
`claude plugin details foma-skills` (run in a project where the plugin is installed):
--refresh PROJECT_DIR re-captures them. The skill map mirrors docs/graph.html.

Style follows the brand art (docs/assets/banner.jpg): black space, a glowing Mars limb along the
bottom edge, a four-point star flare. Everything is pure vector and
self-contained (GitHub serves README SVGs through <img>: no fonts, scripts or external refs).
Motion is CSS @keyframes in an inline <style> (works inside <img>): it only animates transform, opacity
and stroke-dashoffset, every animation rests on the static design, and prefers-reduced-motion turns it off.
"""
import argparse
import base64
import json
import math
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/assets/charts"
DATA = OUT / "tokens.json"
HERO = ROOT / "docs/assets/hero.svg"
PLATE = ROOT / "photo github/чистая подложка.png"  # the clean Mars plate (not committed)

# Group colours double as the legend, so they stay far apart in hue; tuned to sit on the warm palette.
COL = {"setup": "#f2b44f", "proc": "#86b2f2", "meth": "#5fceb4", "atom": "#bcb2a8", "meta": "#f08fb4", "agent": "#f08fb4", "hook": "#bcb2a8"}
BRAND, HOT, EMBER = "#e8714a", "#ff8a4c", "#7a2e14"
INK, MUTED, SPACE = "#f4ece6", "#b3a9a1", "#0b0a10"
INVOKE = "#f4ece6"  # "when it fires" series: a warm-white comet trail
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
GROUP = {"groundwork": "setup", "tidying": "setup", "learning": "setup", "skill-finder": "setup", "handoff": "setup",
         "shaping": "proc", "design-interview": "proc", "planning": "proc", "executing": "proc",
         "debugging": "meth", "reviewing": "meth", "refactoring": "meth",
         "tdd": "atom", "committing": "atom", "documenting": "atom", "writing-skills": "meta", "tuning": "meta"}

T = {  # all visible text, per language
    "en": {
        "cost_title": "What each skill costs, in tokens", "cost_sub": "A little is always loaded; the full text is read only when a skill fires.",
        "always": "always on (every session)", "invoke": "when it fires (per use)",
        "cost_foot": "Claude Code's own estimate: claude plugin details foma-skills. Estimates, real usage may differ.",
        "chip1": "17 skills", "chip2": "≈1.4k tokens always on", "chip3": "0.7–1.4k when one fires",
        "map_title": "Skill map", "map_sub": "who calls whom. Solid arrows = calls, dashed = signals.",
        "bands": {"setup": "setup & upkeep", "proc": "processes", "meth": "methods", "atom": "atomic", "agent": "agents"},
        "contract": "CLAUDE.md contract  ·  Commands  ·  Where things live  ·  Workflow",
        "hub": "executing calls these (refactoring runs on its own)",
        "flow_title": "Propose first, write after your ok", "flow_sub": "The rule every skill that changes files follows.",
        "steps": [("You ask", "“Clean up the repo”"), ("Skill reads", "only what it needs"), ("Shows the change", "file, diff, what goes"),
                  ("You say “ok”", "per item, nothing before"), ("Then it writes", "reversible: .trash/, git rm"), ("Report", "ends with “Not checked: …”")],
        "noop": "no ok  →  nothing is written",
        "sub": {"hook": "router · note · plan", "tuning": "manual · fire log", "groundwork": "set up · audit", "tidying": "junk → .trash/",
                "handoff": "note + /clear", "learning": "lesson → rule", "skill-finder": "find · vet · install", "writing-skills": "write a skill",
                "shaping": "idea → spec", "design-interview": "variants · gallery", "planning": "plan + model/task", "executing": "tasks → done",
                "debugging": "loop → root cause", "reviewing": "standards + spec", "refactoring": "after green tests",
                "tdd": "red → green", "committing": "small · confirmed", "documenting": "docs home",
                "implementer": "model from the plan", "explorer": "Haiku · read-only", "reviewer": "Opus · per feature"},
        "hooklabel": "SessionStart hook", "fire": "fire log",
    },
    "ru": {
        "cost_title": "Сколько токенов стоит каждый скилл", "cost_sub": "Понемногу загружено всегда; полный текст читается, только когда скилл срабатывает.",
        "always": "всегда в контексте (каждая сессия)", "invoke": "при срабатывании (за раз)",
        "cost_foot": "Оценка самого Claude Code: claude plugin details foma-skills. Это оценки, фактический расход может отличаться.",
        "chip1": "17 скиллов", "chip2": "≈1,4k токенов всегда", "chip3": "0,7–1,4k при срабатывании",
        "map_title": "Карта скиллов", "map_sub": "кто кого вызывает. Сплошные стрелки — вызов, пунктир — сигнал.",
        "bands": {"setup": "подготовка", "proc": "процессы", "meth": "методы", "atom": "атомарные", "agent": "агенты"},
        "contract": "Договор в CLAUDE.md  ·  Команды  ·  Где что лежит  ·  Порядок работы",
        "hub": "executing вызывает эти (refactoring запускается отдельно)",
        "flow_title": "Сначала предлагает, пишет после вашего «ок»", "flow_sub": "Правило каждого скилла, который меняет файлы.",
        "steps": [("Вы просите", "«Убери лишнее»"), ("Скилл читает", "только нужное"), ("Показывает изменение", "файл, diff, что уйдёт"),
                  ("Вы говорите «ок»", "по каждому пункту"), ("Только потом пишет", "обратимо: .trash/, git rm"), ("Отчёт", "в конце «Не проверено: …»")],
        "noop": "нет «ок»  →  ничего не записано",
        "sub": {"hook": "роутер · заметка · план", "tuning": "вручную · журнал", "groundwork": "настройка · аудит", "tidying": "мусор → .trash/",
                "handoff": "заметка + /clear", "learning": "урок → правило", "skill-finder": "поиск · проверка", "writing-skills": "написать скилл",
                "shaping": "идея → спека", "design-interview": "варианты · галерея", "planning": "план + модель", "executing": "задачи → готово",
                "debugging": "причина бага", "reviewing": "стандарты + спека", "refactoring": "при зелёных тестах",
                "tdd": "красный → зелёный", "committing": "маленькие · с ок", "documenting": "куда писать docs",
                "implementer": "модель из плана", "explorer": "Haiku · чтение", "reviewer": "Opus · на фичу"},
        "hooklabel": "Хук SessionStart", "fire": "журнал",
    },
}

# --- text metrics: a rough Helvetica-like width table, used to keep >=10% slack in every text box ---
_W = {**dict.fromkeys("ijl|'", 222), **dict.fromkeys("ftI!.,:;/ ·[]\u00a0", 278), **dict.fromkeys("r-()“”\"", 333),
      **dict.fromkeys("cksvxyzJ", 500), **dict.fromkeys("mM", 833), "w": 722, "W": 944, "…": 1000, "→": 1000,
      "—": 1000, "–": 556, "≈": 584, "+": 584, "~": 584, "=": 584, "«": 556, "»": 556, "&": 667}
SLACK = 1.1


def tw(s, size, bold=False):
    """Estimated rendered width of s (px). Errs wide: the system font stack varies by OS."""
    total = 0
    for ch in s:
        if ch in _W:
            w = _W[ch]
        elif "а" <= ch.lower() <= "я" or ch in "ёЁ":
            w = 720 if ch.isupper() else (800 if ch in "жмшщыюф" else 570)
        else:
            w = 700 if ch.isupper() else 556
        total += w
    return total / 1000 * size * (1.1 if bold else 1.0) * 1.05


def fit(s, size, maxw, bold=False):
    if tw(s, size, bold) * SLACK > maxw:
        sys.exit(f"text too wide for its box ({tw(s, size, bold):.0f}px*{SLACK} > {maxw:.0f}px): {s!r}")
    return s


def wrap(s, size, maxw, bold=False):
    """Greedy word wrap; never breaks inside a quotation."""
    s = re.sub(r"[«“][^»”]*[»”]", lambda m: m.group(0).replace(" ", "\u00a0"), s)
    lines, cur = [], ""
    for word in s.split(" "):
        cand = f"{cur} {word}" if cur else word
        if cur and tw(cand, size, bold) * SLACK > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    lines.append(cur)
    for ln in lines:
        fit(ln, size, maxw, bold)
    return [ln.replace("\u00a0", " ") for ln in lines]


def n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


# --- shared frame: space background, nebula, stars, comet arc, star flare, Mars limb, header ---
MARKER_COLOURS = sorted(set(COL.values()) | {BRAND, "#8d847d"})


def marker_id(c):
    return "ar" + c.lstrip("#")


# --- motion: CSS keyframes; each one starts and ends on the static look (or grows into it once) ---
NO_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def motion(css):
    return f"<style>{css}{NO_MOTION}</style>"


def flare_css(fx, fy, delay=2):
    return (f".fr,.fc{{transform-origin:{fx}px {fy}px;animation:fr 5.5s ease-in-out {delay}s infinite}}.fc{{animation-name:fc}}"
            "@keyframes fr{0%,55%,100%{transform:scale(1)}68%{transform:scale(1.16,1.3)}80%{transform:scale(.97)}}"
            "@keyframes fc{0%,55%,100%{transform:scale(1)}68%{transform:scale(1.4)}}")


SHIMMER = ".sh{animation:sh 9s ease-in-out 3s infinite}@keyframes sh{0%{stroke-dashoffset:16}45%,100%{stroke-dashoffset:-104}}"


def shimmer(d, grad, width=1.4):
    """A short bright dash parked before the start of d; .sh runs it along the path."""
    return (f'<path class="sh" d="{d}" pathLength="100" fill="none" stroke="url(#{grad})" stroke-width="{width}" '
            'stroke-linecap="round" stroke-dasharray="12 300" stroke-dashoffset="16"/>')


def plen(d):
    """Length of a path built from absolute M/L/Q/C commands (curves sampled)."""
    toks = re.findall(r"[MLQC]|-?\d+(?:\.\d+)?", d)
    total, i, cur = 0.0, 0, (0.0, 0.0)
    while i < len(toks):
        cmd = toks[i]
        k = {"M": 1, "L": 1, "Q": 2, "C": 3}[cmd]
        pts = [(float(toks[i + 1 + 2 * j]), float(toks[i + 2 + 2 * j])) for j in range(k)]
        i += 1 + 2 * k
        if cmd == "L":
            total += math.dist(cur, pts[0])
        elif cmd in "QC":
            ctrl = [cur] + pts
            prev = cur
            for step in range(1, 41):
                t = step / 40
                q = ctrl
                while len(q) > 1:
                    q = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(q, q[1:])]
                total += math.dist(prev, q[0])
                prev = q[0]
        cur = pts[-1]
    return total


def frame(w, h, title, sub, seed, keep_out=()):
    rnd = random.Random(seed)
    pcx, R = w * 0.56, w * 1.4
    crest = h - 46
    pcy = crest + R
    fx, fy = w - 118, 60
    l1, l2, up, down = 330, 118, 60, 58
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">\n'
         f'<title>{esc(title)}</title>\n<defs>'
         f'<clipPath id="card"><rect width="{w}" height="{h}" rx="22"/></clipPath>'
         f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c0a12"/><stop offset="1" stop-color="#050508"/></linearGradient>'
         f'<radialGradient id="neb"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.2"/><stop offset="0.5" stop-color="{BRAND}" stop-opacity="0.06"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="neb2"><stop offset="0" stop-color="#6f74b8" stop-opacity="0.13"/><stop offset="1" stop-color="#6f74b8" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="planet" gradientUnits="userSpaceOnUse" cx="{n(w*0.74)}" cy="{crest}" r="{n(w*0.5)}"><stop offset="0" stop-color="#5a2410"/><stop offset="0.45" stop-color="#2a120a"/><stop offset="1" stop-color="#0d0807"/></radialGradient>'
         f'<linearGradient id="limb" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0"><stop offset="0.2" stop-color="{BRAND}" stop-opacity="0"/><stop offset="0.42" stop-color="{BRAND}" stop-opacity="0.7"/><stop offset="0.74" stop-color="#ffd2ad"/><stop offset="0.9" stop-color="{HOT}" stop-opacity="0.6"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></linearGradient>'
         f'<radialGradient id="glint"><stop offset="0" stop-color="#ffe2c8" stop-opacity="0.95"/><stop offset="0.3" stop-color="{HOT}" stop-opacity="0.45"/><stop offset="1" stop-color="{HOT}" stop-opacity="0"/></radialGradient>'
         f'<linearGradient id="rayh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd2b0" stop-opacity="0"/><stop offset="{n(l1/(l1+l2))}" stop-color="#fff1e4"/><stop offset="1" stop-color="#ffd2b0" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="rayv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd2b0" stop-opacity="0"/><stop offset="{n(up/(up+down))}" stop-color="#fff1e4"/><stop offset="1" stop-color="#ffd2b0" stop-opacity="0"/></linearGradient>'
         f'<radialGradient id="core"><stop offset="0" stop-color="#fff8f0"/><stop offset="0.18" stop-color="#ffc08f" stop-opacity="0.85"/><stop offset="0.5" stop-color="{BRAND}" stop-opacity="0.25"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></radialGradient>'
         f'<linearGradient id="arc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BRAND}" stop-opacity="0"/><stop offset="0.6" stop-color="#f3a27c" stop-opacity="0.5"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="arc2" x1="0" y1="0" x2="1" y2="0"><stop offset="0.1" stop-color="#ffe6d6" stop-opacity="0"/><stop offset="0.6" stop-color="#ffe6d6" stop-opacity="0.9"/><stop offset="0.95" stop-color="#ffe6d6" stop-opacity="0"/></linearGradient>'
         f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><feGaussianBlur stdDeviation="3"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
         f'<filter id="soft" filterUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><feGaussianBlur stdDeviation="6"/></filter>')
    for c in MARKER_COLOURS:
        s += (f'<marker id="{marker_id(c)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">'
              f'<path d="M0,0.5 L10,5 L0,9.5 z" fill="{c}"/></marker>')
    s += '</defs>' + motion(
        ".t1,.t2,.t3{animation:tw 6s ease-in-out 1s infinite}.t2{animation-duration:8s;animation-delay:2.6s}"
        ".t3{animation-duration:11s;animation-delay:4.2s}@keyframes tw{50%{opacity:.2}}"
        + flare_css(fx, fy) + SHIMMER +
        ".gl{transform-box:fill-box;transform-origin:center;animation:gl 8s ease-in-out 1s infinite}"
        "@keyframes gl{50%{opacity:.6;transform:scaleX(1.15)}}")
    s += '\n<g clip-path="url(#card)">'
    s += (f'<rect width="{w}" height="{h}" fill="url(#bg)"/>'
          f'<ellipse cx="{n(w*0.05)}" cy="0" rx="{n(w*0.42)}" ry="{n(h*0.32)}" fill="url(#neb)"/>'
          f'<ellipse cx="{n(w*0.86)}" cy="{n(h*0.08)}" rx="{n(w*0.34)}" ry="{n(h*0.3)}" fill="url(#neb2)"/>'
          f'<ellipse cx="{n(w*0.66)}" cy="{h}" rx="{n(w*0.62)}" ry="{n(min(h*0.3, 220))}" fill="url(#neb)"/>')
    # star field (deterministic), thinned out behind the data
    stars = []
    for i in range(int(w * h / 6500)):
        x, y = rnd.uniform(8, w - 8), rnd.uniform(8, h - 8)
        r = rnd.choice((0.45, 0.6, 0.6, 0.8, 0.8, 1.0, 1.3))
        op = rnd.uniform(0.25, 0.75)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in keep_out):
            op *= 0.35
        cls = f' class="t{i % 5 + 1}"' if i % 5 < 3 else ""  # three in five twinkle, three rhythms
        stars.append(f'<circle{cls} cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{rnd.choice((INK, INK, "#ffd6bf", "#c9d3ff"))}" fill-opacity="{op:.2f}"/>')
    s += "".join(stars)
    # comet arc through the top-right corner
    arc = f"M{n(w*0.4)},-10 Q{n(w*0.8)},10 {w+10},{n(min(h*0.26, 132))}"
    s += f'<path d="{arc}" fill="none" stroke="url(#arc)" stroke-width="1"/>' + shimmer(arc, "arc2")
    # four-point star flare
    s += (f'<circle cx="{fx}" cy="{fy}" r="40" fill="url(#core)" fill-opacity="0.55"/>'
          f'<g class="fr"><polygon points="{fx-l1},{fy} {fx},{fy-1.4} {fx+l2},{fy} {fx},{fy+1.4}" fill="url(#rayh)"/>'
          f'<polygon points="{fx},{fy-up} {fx+1.4},{fy} {fx},{fy+down} {fx-1.4},{fy}" fill="url(#rayv)"/></g>'
          f'<g class="fc"><circle cx="{fx}" cy="{fy}" r="9" fill="url(#core)"/><circle cx="{fx}" cy="{fy}" r="2.2" fill="#fffaf4"/></g>')
    # Mars limb along the bottom edge
    gx = w * 0.74
    gy = pcy - math.sqrt(R * R - (gx - pcx) ** 2)
    s += (f'<circle cx="{n(pcx)}" cy="{n(pcy)}" r="{n(R)}" fill="url(#planet)"/>'
          f'<circle cx="{n(pcx)}" cy="{n(pcy)}" r="{n(R)}" fill="none" stroke="{HOT}" stroke-width="16" stroke-opacity="0.42" filter="url(#soft)"/>'
          f'<circle cx="{n(pcx)}" cy="{n(pcy)}" r="{n(R)}" fill="none" stroke="url(#limb)" stroke-width="2"/>'
          f'<ellipse class="gl" cx="{n(gx)}" cy="{n(gy)}" rx="230" ry="22" fill="url(#glint)"/>')
    s += (f'</g><rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="21.5" fill="none" stroke="{INK}" stroke-opacity="0.1"/>\n'
          f'<g font-family="{FONT}">\n')
    # header: eyebrow, title, subtitle
    s += (f'<text x="48" y="56" font-size="12" font-weight="700" letter-spacing="3" fill="{BRAND}">FOMA SKILLS</text>'
          f'<text x="48" y="90" font-size="30" font-weight="800" fill="{INK}">{esc(fit(title, 30, w - 48 - 150, True))}</text>'
          f'<text x="48" y="117" font-size="16" fill="{MUTED}">{esc(fit(sub, 16, w - 48 - 48))}</text>\n')
    return s


def parse_k(s):
    s = s.strip().lstrip("~").replace(",", "")
    return int(float(s[:-1]) * 1000) if s.endswith("k") else int(float(s))


def refresh(project):
    out = subprocess.run(["claude", "plugin", "details", "foma-skills"], cwd=project, capture_output=True, text=True).stdout
    rows = {}
    for m in re.finditer(r"^\s{2}([a-z-]+)\s+~?([\d.,k]+)\s+~?([\d.,k]+)\s*$", out, re.M):
        if m.group(1) in GROUP:
            rows[m.group(1)] = {"always": parse_k(m.group(2)), "invoke": parse_k(m.group(3))}
    total = re.search(r"Always-on:\s+~([\d,]+)", out)
    if len(rows) != len(GROUP) or not total:
        sys.exit(f"could not parse `claude plugin details` ({len(rows)} skills): is the plugin installed in {project}?")
    DATA.write_text(json.dumps({"always_total": int(total.group(1).replace(",", "")), "skills": rows}, indent=2) + "\n")


def kfmt(n_, lang):
    s = f"{n_/1000:.1f}k".replace(".0k", "k") if n_ >= 1000 else str(n_)
    return s.replace(".", ",") if lang == "ru" else s


def token_cost(lang):
    d, t = json.loads(DATA.read_text()), T[lang]
    rows = sorted(d["skills"].items(), key=lambda kv: -kv[1]["invoke"])
    w, row_h, y0, bx, scale = 1280, 34, 222, 300, 840 / 1500
    y1 = y0 + row_h * len(rows)
    h = y1 + 146
    s = frame(w, h, t["cost_title"], t["cost_sub"], 11, keep_out=[(40, y0 - 10, w - 40, y1 + 30)])
    s += ('<defs><linearGradient id="gal" x1="0" y1="0" x2="1" y2="0">'
          f'<stop offset="0" stop-color="{EMBER}"/><stop offset="0.5" stop-color="{BRAND}"/><stop offset="1" stop-color="{HOT}"/></linearGradient>'
          '<linearGradient id="ginv" x1="0" y1="0" x2="1" y2="0">'
          f'<stop offset="0" stop-color="{INVOKE}" stop-opacity="0.08"/><stop offset="0.7" stop-color="{INVOKE}" stop-opacity="0.5"/><stop offset="1" stop-color="{INVOKE}" stop-opacity="0.95"/></linearGradient>'
          '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff4ea" stop-opacity="0"/>'
          '<stop offset="0.5" stop-color="#fff4ea" stop-opacity="0.55"/><stop offset="1" stop-color="#fff4ea" stop-opacity="0"/></linearGradient></defs>')
    # bars grow in once, staggered; their labels and end dots arrive after; then a light sweep runs over the bars
    s += motion(".gb{transform-box:fill-box;transform-origin:0 50%;animation:grow 1.2s cubic-bezier(.2,.75,.25,1) backwards}"
               "@keyframes grow{from{transform:scaleX(0)}}.fi{animation:fi .5s ease-out backwards}@keyframes fi{from{opacity:0}}"
               ".pop{transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.3,1.6,.5,1) backwards}"
               "@keyframes pop{from{opacity:0;transform:scale(0)}}"
               ".sw{animation:sw 8s ease-in-out 3.2s infinite}@keyframes sw{0%{transform:translateX(0)}45%,100%{transform:translateX(1100px)}}")
    # chips (left) and legend (right) on one line
    cy = 148
    x = 48
    for label, c in ((t["chip1"], COL["atom"]), (t["chip2"], BRAND), (t["chip3"], INVOKE)):
        cw = tw(label, 15, True) * SLACK + 34
        s += (f'<rect x="{n(x)}" y="{cy}" width="{n(cw)}" height="34" rx="17" fill="{c}" fill-opacity="0.1" stroke="{c}" stroke-opacity="0.6"/>'
              f'<text x="{n(x+cw/2)}" y="{cy+22}" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">{esc(label)}</text>')
        x += cw + 12
    lw = max(tw(t["always"], 14), tw(t["invoke"], 14)) * SLACK
    lx = w - 48 - lw - 34
    if lx < x + 20:
        sys.exit("token chart: chips run into the legend")
    s += (f'<rect x="{n(lx)}" y="{cy+5}" width="24" height="7" rx="3.5" fill="url(#gal)" filter="url(#glow)"/>'
          f'<text x="{n(lx+34)}" y="{cy+13}" font-size="14" fill="{INK}">{esc(t["always"])}</text>'
          f'<rect x="{n(lx)}" y="{cy+22}" width="24" height="9" rx="4.5" fill="url(#ginv)"/><circle cx="{n(lx+21)}" cy="{cy+26.5}" r="3.4" fill="#fffaf4" filter="url(#glow)"/>'
          f'<text x="{n(lx+34)}" y="{cy+31}" font-size="14" fill="{INK}">{esc(t["invoke"])}</text>')
    # grid
    for tick in (0, 500, 1000, 1500):
        gx = bx + tick * scale
        s += (f'<line x1="{n(gx)}" y1="{y0-6}" x2="{n(gx)}" y2="{y1+4}" stroke="{INK}" stroke-opacity="{0.16 if tick == 0 else 0.07}"{"" if tick == 0 else " stroke-dasharray=\"2 5\""}/>'
              f'<text x="{n(gx)}" y="{y1+24}" text-anchor="middle" font-size="12" fill="{MUTED}">{kfmt(tick, lang) if tick else "0"}</text>')
    # rows
    clip = ""
    for i, (name, v) in enumerate(rows):
        y = y0 + i * row_h
        c = COL[GROUP[name]]
        if i % 2 == 0:
            s += f'<rect x="40" y="{y}" width="{w-80}" height="{row_h}" rx="8" fill="{INK}" fill-opacity="0.028"/>'
        aw, iw = max(v["always"] * scale, 3), v["invoke"] * scale
        d0, d1 = f' style="animation-delay:{0.2 + i * 0.06:.2f}s"', f' style="animation-delay:{1.1 + i * 0.06:.2f}s"'
        s += (f'<circle cx="60" cy="{y+17}" r="5" fill="{c}" filter="url(#glow)"/>'
              f'<text x="76" y="{y+22}" font-size="15" font-weight="600" fill="{INK}">{esc(fit(name, 15, bx - 76 - 16, True))}</text>'
              f'<rect class="gb"{d0} x="{bx}" y="{y+7}" width="{n(aw)}" height="7" rx="3.5" fill="url(#gal)" filter="url(#glow)"/>'
              f'<text class="fi"{d1} x="{n(bx+aw+9)}" y="{y+14}" font-size="11.5" fill="{MUTED}">~{v["always"]}</text>'
              f'<rect class="gb"{d0} x="{bx}" y="{y+18}" width="{n(iw)}" height="9" rx="4.5" fill="url(#ginv)"/>'
              f'<circle class="pop"{d1} cx="{n(bx+iw-3.5)}" cy="{y+22.5}" r="3.4" fill="#fffaf4" filter="url(#glow)"/>'
              f'<text class="fi"{d1} x="{n(bx+iw+10)}" y="{y+27}" font-size="12.5" font-weight="600" fill="{INK}">~{kfmt(v["invoke"], lang)}</text>')
        clip += (f'<rect x="{bx}" y="{y+7}" width="{n(aw)}" height="7" rx="3.5"/>'
                 f'<rect x="{bx}" y="{y+18}" width="{n(iw)}" height="9" rx="4.5"/>')
    s += (f'<clipPath id="bars">{clip}</clipPath><g clip-path="url(#bars)">'
          f'<rect class="sw" x="{bx-170}" y="{y0}" width="150" height="{y1-y0}" fill="url(#sweep)"/></g>')
    s += f'<text x="48" y="{y1+62}" font-size="13" fill="{MUTED}">{esc(fit(t["cost_foot"], 13, w - 96))}</text>\n'
    return s + "</g></svg>\n"


# --- skill map ---
NODES = [  # id, name key, centre x, row, group, width
    ("hook", "hook", 330, "hook", "hook", 210), ("tune", "tuning", 1160, "hook", "meta", 150),
    ("gw", "groundwork", 290, "setup", "setup", 150), ("tidy", "tidying", 464, "setup", "setup", 150), ("hand", "handoff", 638, "setup", "setup", 150),
    ("learn", "learning", 812, "setup", "setup", 150), ("find", "skill-finder", 986, "setup", "setup", 150), ("ws", "writing-skills", 1160, "setup", "meta", 150),
    ("shape", "shaping", 330, "proc", "proc", 190), ("design", "design-interview", 560, "proc", "proc", 190), ("plan", "planning", 790, "proc", "proc", 190), ("exec", "executing", 1050, "proc", "proc", 190),
    ("dbg", "debugging", 480, "meth", "meth", 200), ("ref", "refactoring", 750, "meth", "meth", 200), ("rev", "reviewing", 1020, "meth", "meth", 200),
    ("doc", "documenting", 480, "atom", "atom", 200), ("tdd", "tdd", 750, "atom", "atom", 200), ("com", "committing", 1020, "atom", "atom", 200),
    ("expl", "explorer", 480, "agent", "agent", 200), ("impl", "implementer", 750, "agent", "agent", 200), ("rvw", "reviewer", 1020, "agent", "agent", 200),
]
ROWS = {"hook": 180, "setup": 290, "contract": 380, "proc": 500, "meth": 630, "atom": 740, "agent": 850}
EDGES = [("hook", "hand"), ("hook", "tune", "dash"), ("hand", "tidy", "dash"), ("hand", "learn", "dash"), ("shape", "plan", "dash"), ("design", "plan", "dash"),
         ("shape", "doc"), ("plan", "doc"), ("exec", "dbg"), ("exec", "rev"), ("exec", "tdd"), ("exec", "com"), ("exec", "doc"),
         ("exec", "impl"), ("exec", "rvw"), ("exec", "expl"), ("dbg", "tdd"), ("dbg", "expl"), ("ref", "tdd"), ("impl", "tdd"), ("rvw", "rev")]
NH = 52
CONTRACT = (215, 1235)  # x span of the contract bar
PANEL = (290, 570, 1186, 902)  # every node executing calls sits in this panel


def ortho(pts, r=12):
    """Orthogonal polyline with rounded corners."""
    d = f"M{n(pts[0][0])},{n(pts[0][1])}"
    for (x0, y0), (x1, y1), (x2, y2) in zip(pts, pts[1:], pts[2:]):
        la, lb = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr = min(r, la / 2, lb / 2)
        ax, ay = x1 + (x0 - x1) * rr / la, y1 + (y0 - y1) * rr / la
        bx, by = x1 + (x2 - x1) * rr / lb, y1 + (y2 - y1) * rr / lb
        d += f" L{n(ax)},{n(ay)} Q{n(x1)},{n(y1)} {n(bx)},{n(by)}"
    return d + f" L{n(pts[-1][0])},{n(pts[-1][1])}"


def routes(nd):
    """Hand-routed edges: through the gaps and corridors, never across a node."""
    def top(k, dx=0): return (nd[k]["x"] + dx, nd[k]["y"] - NH / 2)
    def bot(k, dx=0): return (nd[k]["x"] + dx, nd[k]["y"] + NH / 2)
    def lft(k): return (nd[k]["x"] - nd[k]["w"] / 2, nd[k]["y"])
    def rgt(k): return (nd[k]["x"] + nd[k]["w"] / 2, nd[k]["y"])
    ct = ROWS["contract"] - 22
    lane = (bot("plan")[1] + PANEL[1]) / 2  # between the process row and the panel
    gap_ma = (bot("dbg")[1] + top("tdd")[1]) / 2  # between methods and atomic
    corr = (rgt("doc")[0] + lft("tdd")[0]) / 2  # between the first two columns
    (hx, hy), (ax_, ay_) = bot("hook", 40), top("hand")
    (sx, sy), (px_, py_) = top("shape", 40), top("plan", -40)
    return {
        ("hook", "hand"): f"M{n(hx)},{n(hy)} C{n(hx)},{n(hy+30)} {n(ax_)},{n(ay_-34)} {n(ax_)},{n(ay_)}",
        ("hook", "tune"): ortho([rgt("hook"), lft("tune")]),
        ("hand", "tidy"): ortho([lft("hand"), rgt("tidy")]),
        ("hand", "learn"): ortho([rgt("hand"), lft("learn")]),
        ("gw", "CONTRACT"): ortho([bot("gw"), (nd["gw"]["x"], ct)]),
        ("learn", "CONTRACT"): ortho([bot("learn"), (nd["learn"]["x"], ct)]),
        ("shape", "plan"): f"M{n(sx)},{n(sy)} C{n(sx)},{n(sy-44)} {n(px_)},{n(py_-44)} {n(px_)},{n(py_)}",
        ("design", "plan"): ortho([rgt("design"), lft("plan")]),
        ("shape", "doc"): ortho([bot("shape"), (nd["shape"]["x"], nd["doc"]["y"]), lft("doc")], 16),
        ("plan", "doc"): ortho([bot("plan"), (nd["plan"]["x"], lane), (nd["shape"]["x"], lane), (nd["shape"]["x"], nd["doc"]["y"]), lft("doc")], 16),
        ("dbg", "tdd"): ortho([bot("dbg", 40), (nd["dbg"]["x"] + 40, gap_ma), (nd["tdd"]["x"] - 40, gap_ma), top("tdd", -40)]),
        ("dbg", "expl"): ortho([bot("dbg", 40), (nd["dbg"]["x"] + 40, gap_ma), (corr, gap_ma), (corr, nd["expl"]["y"]), rgt("expl")]),
        ("ref", "tdd"): ortho([bot("ref"), top("tdd")]),
        ("impl", "tdd"): ortho([top("impl"), bot("tdd")]),
        ("rvw", "rev"): ortho([rgt("rvw"), (PANEL[2] - 34, nd["rvw"]["y"]), (PANEL[2] - 34, nd["rev"]["y"]), rgt("rev")]),
        ("exec", "PANEL"): ortho([bot("exec"), (nd["exec"]["x"], PANEL[1])]),
    }


def node(nd, t, i=0):
    c, key = COL[nd["g"]], nd["name"]
    x, y, w = nd["x"] - nd["w"] / 2, nd["y"] - NH / 2, nd["w"]
    rx = NH / 2 if nd["g"] == "agent" else 12
    label = t["hooklabel"] if key == "hook" else key
    dash = ' stroke-dasharray="5 4"' if key in ("hook", "tuning", "writing-skills") else ""
    gid = "ng" + nd["g"]
    return (f'<rect class="nb" style="animation-delay:{0.5 + i * 0.63 % 7:.2f}s" x="{n(x)}" y="{n(y)}" width="{w}" height="{NH}" rx="{n(rx)}" fill="none" stroke="{c}" stroke-width="5" stroke-opacity="0.32" filter="url(#soft)"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{w}" height="{NH}" rx="{n(rx)}" fill="#0d0b12"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{w}" height="{NH}" rx="{n(rx)}" fill="url(#{gid})" stroke="{c}" stroke-width="1.5"{dash}/>'
            f'<text x="{n(nd["x"])}" y="{n(nd["y"]-3)}" text-anchor="middle" font-size="16" font-weight="700" fill="{INK}">{esc(fit(label, 16, w - 16, True))}</text>'
            f'<text x="{n(nd["x"])}" y="{n(nd["y"]+15)}" text-anchor="middle" font-size="12.5" fill="{MUTED}">{esc(fit(t["sub"][key], 12.5, w - 16))}</text>')


def skill_map(lang):
    t = T[lang]
    w, h = 1280, 990
    nd = {i: dict(name=nm, x=x, y=ROWS[r], g=g, w=wd) for i, nm, x, r, g, wd in NODES}
    s = frame(w, h, t["map_title"], t["map_sub"], 23, keep_out=[(200, 140, w - 30, PANEL[3] + 10)])
    s += "<defs>" + "".join(
        f'<linearGradient id="ng{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c}" stop-opacity="0.2"/><stop offset="1" stop-color="{c}" stop-opacity="0.05"/></linearGradient>'
        for g, c in COL.items()) + (
        f'<linearGradient id="ctr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.06"/><stop offset="0.5" stop-color="{BRAND}" stop-opacity="0.2"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0.06"/></linearGradient></defs>')
    # band labels: the colour legend
    for key in ("setup", "proc", "meth", "atom", "agent"):
        y = ROWS[key]
        s += (f'<circle cx="56" cy="{y}" r="5" fill="{COL[key]}" filter="url(#glow)"/>'
              f'<text x="70" y="{y+5}" font-size="14" font-weight="700" fill="{COL[key]}">{esc(fit(t["bands"][key], 14, 210 - 70, True))}</text>')
    # panel of everything executing calls
    px0, py0, px1, py1 = PANEL
    s += f'<rect x="{px0}" y="{py0}" width="{px1-px0}" height="{py1-py0}" rx="18" fill="{COL["proc"]}" fill-opacity="0.035" stroke="{COL["proc"]}" stroke-opacity="0.45"/>'
    hub_w = tw(t["hub"], 13, True) * SLACK
    hx1 = nd["exec"]["x"] - 18
    s += (f'<rect x="{n(hx1-hub_w-12)}" y="{py0-11}" width="{n(hub_w+24)}" height="22" rx="11" fill="{SPACE}" stroke="{COL["proc"]}" stroke-opacity="0.45"/>'
          f'<text x="{n(hx1)}" y="{py0+4.5}" text-anchor="end" font-size="13" font-weight="700" fill="{COL["proc"]}">{esc(t["hub"])}</text>')
    # contract bar
    cy = ROWS["contract"]
    cx0, cx1 = CONTRACT
    s += (f'<rect class="nb" x="{cx0}" y="{cy-22}" width="{cx1-cx0}" height="44" rx="12" fill="none" stroke="{BRAND}" stroke-width="5" stroke-opacity="0.3" filter="url(#soft)"/>'
          f'<rect x="{cx0}" y="{cy-22}" width="{cx1-cx0}" height="44" rx="12" fill="#0d0b12"/>'
          f'<rect x="{cx0}" y="{cy-22}" width="{cx1-cx0}" height="44" rx="12" fill="url(#ctr)" stroke="{BRAND}" stroke-width="1.5"/>'
          f'<text x="{(cx0+cx1)/2}" y="{cy+5}" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">{esc(fit(t["contract"], 15, cx1 - cx0 - 40, True))}</text>')
    for i, k in enumerate(nd):
        s += node(nd[k], t, i)
    # edges on top of the nodes so every arrowhead stays visible; executing's nine calls go to the panel
    rt = routes(nd)
    hub = {b for a, b, *_ in EDGES if a == "exec"}
    inside = {k for k, v in nd.items() if v["g"] in ("meth", "atom", "agent")}
    inside -= {"ref"}  # refactoring sits in the panel but is not called by executing (its frontmatter `uses` omits it)
    if hub != inside:
        sys.exit(f"skill map: executing must call exactly the panel nodes ({sorted(hub ^ inside)})")
    todo = [e for e in EDGES if e[0] != "exec"] + [("gw", "CONTRACT"), ("learn", "CONTRACT", "dash"), ("exec", "PANEL")]
    pulses = []
    for e in todo:
        a, b, style = e[0], e[1], (e[2] if len(e) > 2 else "solid")
        if (a, b) not in rt:
            sys.exit(f"skill map: no route for {a} -> {b}")
        c = COL[nd[a]["g"]]
        dash = ' class="df" stroke-dasharray="6 5"' if style == "dash" else ""
        sw = 2.2 if b == "PANEL" else 1.8
        s += f'<path d="{rt[(a, b)]}" fill="none" stroke="{c}" stroke-opacity="0.9" stroke-width="{sw}"{dash} marker-end="url(#{marker_id(c)})"/>'
        if style != "dash":
            pulses.append(rt[(a, b)])
    # signals flow along the dashes; a light pulse runs down each call in turn (7 s round)
    css = ".df{animation:df 1.8s linear infinite}@keyframes df{to{stroke-dashoffset:-11}}"
    css += ".nb{animation:nb 7s ease-in-out .5s infinite}@keyframes nb{50%{opacity:.35}}"
    for i, d in enumerate(pulses):
        ln = plen(d)
        pct = min(max(ln / 170, 0.8) / 7 * 100, 60)
        css += f"@keyframes p{i}{{0%{{stroke-dashoffset:20}}{pct:.0f}%,100%{{stroke-dashoffset:-{ln+4:.0f}}}}}"
        s += (f'<path d="{d}" fill="none" stroke="#fff4ea" stroke-opacity="0.9" stroke-width="2.4" stroke-linecap="round" '
              f'stroke-dasharray="16 {ln+60:.0f}" stroke-dashoffset="20" style="animation:p{i} 7s ease-in-out {0.6 + i * 0.6:.1f}s infinite"/>')
    s += motion(css)
    fx = (nd["hook"]["x"] + nd["hook"]["w"] / 2 + nd["tune"]["x"] - nd["tune"]["w"] / 2) / 2
    s += f'<text x="{n(fx)}" y="{ROWS["hook"]-9}" text-anchor="middle" font-size="12.5" fill="{MUTED}">{esc(t["fire"])}</text>'
    return s + "</g></svg>\n"


# --- propose-first cycle ---
def propose_first(lang):
    t = T[lang]
    steps = t["steps"]
    w, k = 1280, len(steps)
    col_w = (w - 64) / k
    cy = 286
    titles = [wrap(a, 18, col_w - 14, True) for a, _ in steps]
    subs = [wrap(b, 14, col_w - 14) for _, b in steps]
    ty = cy + 88
    sy = ty + 21 * (max(map(len, titles)) - 1) + 25
    h = int(sy + 18 * (max(map(len, subs)) - 1) + 108)
    s = frame(w, h, t["flow_title"], t["flow_sub"], 37, keep_out=[(32, cy - 70, w - 32, sy + 30)])
    cols = [COL["atom"], COL["proc"], COL["setup"], BRAND, COL["meth"], COL["meta"]]
    s += "<defs>" + "".join(
        f'<radialGradient id="orb{i}" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="{c}" stop-opacity="0.42"/><stop offset="1" stop-color="{c}" stop-opacity="0.06"/></radialGradient>'
        for i, c in enumerate(cols)) + (
        f'<radialGradient id="gate" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="#ffc59a"/><stop offset="0.45" stop-color="{HOT}"/><stop offset="1" stop-color="{EMBER}"/></radialGradient></defs>')
    # a 10 s round: steps 1..6 light up in turn (the gate strongest), a pulse runs down each arrow,
    # the gate's dashed ring turns, and the "no ok" arc flows back to step 2
    s += motion(".fb{transform-box:fill-box;transform-origin:center;animation:bump 10s ease-in-out infinite}.fb3{animation-name:bumpg}"
               "@keyframes bump{0%,14%,100%{transform:scale(1)}5%{transform:scale(1.08)}}"
               "@keyframes bumpg{0%,16%,100%{transform:scale(1)}6%{transform:scale(1.13)}}"
               ".rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:rg 10s ease-out infinite}"
               "@keyframes rg{0%{opacity:0;transform:scale(1)}4%{opacity:.9}14%,100%{opacity:0;transform:scale(1.4)}}"
               ".ap{animation:ap 10s ease-in-out infinite}@keyframes ap{0%{stroke-dashoffset:26}9%,100%{stroke-dashoffset:-106}}"
               ".spin{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
               ".df{animation:df 1.8s linear infinite}@keyframes df{to{stroke-dashoffset:-11}}")
    xs = [32 + col_w * (i + 0.5) for i in range(k)]
    rad = [46 if i == 3 else 38 for i in range(k)]
    step = 1.4  # seconds between steps in the round
    for i in range(k - 1):
        d = f"M{n(xs[i]+rad[i]+10)},{cy} L{n(xs[i+1]-rad[i+1]-12)},{cy}"
        s += (f'<path d="{d}" stroke="#8d847d" stroke-width="2" fill="none" marker-end="url(#{marker_id("#8d847d")})"/>'
              f'<path class="ap" style="animation-delay:{0.8 + i * step + 0.5:.1f}s" d="{d}" pathLength="100" stroke="#fff4ea" stroke-width="2.6" '
              'stroke-linecap="round" stroke-dasharray="20 400" stroke-dashoffset="26" fill="none"/>')
    for i, x in enumerate(xs):
        c = cols[i]
        delay = f' style="animation-delay:{0.8 + i * step:.1f}s"'
        if i == 3:  # the gate: nothing is written before this
            s += (f'<g class="fb fb3"{delay}><circle cx="{n(x)}" cy="{cy}" r="64" fill="{BRAND}" fill-opacity="0.22" filter="url(#soft)"/>'
                  f'<circle class="spin" cx="{n(x)}" cy="{cy}" r="58" fill="none" stroke="{BRAND}" stroke-opacity="0.55" stroke-dasharray="2 5"/>'
                  f'<circle cx="{n(x)}" cy="{cy}" r="{rad[i]}" fill="url(#gate)" filter="url(#glow)"/>'
                  f'<text x="{n(x)}" y="{cy+11}" text-anchor="middle" font-size="31" font-weight="800" fill="#1c0b05">{i+1}</text></g>'
                  f'<circle class="rg"{delay} cx="{n(x)}" cy="{cy}" r="{rad[i]+4}" fill="none" stroke="#ffc59a" stroke-width="3"/>'
                  f'<circle class="rg" style="animation-delay:{0.8 + i * step + 0.25:.2f}s" cx="{n(x)}" cy="{cy}" r="60" fill="none" stroke="{BRAND}" stroke-width="2.5"/>')
        else:
            s += (f'<g class="fb"{delay}><circle cx="{n(x)}" cy="{cy}" r="{rad[i]}" fill="none" stroke="{c}" stroke-width="5" stroke-opacity="0.3" filter="url(#soft)"/>'
                  f'<circle cx="{n(x)}" cy="{cy}" r="{rad[i]}" fill="#0d0b12"/>'
                  f'<circle cx="{n(x)}" cy="{cy}" r="{rad[i]}" fill="url(#orb{i})" stroke="{c}" stroke-width="2"/>'
                  f'<text x="{n(x)}" y="{cy+9}" text-anchor="middle" font-size="26" font-weight="800" fill="{c}">{i+1}</text></g>'
                  f'<circle class="rg"{delay} cx="{n(x)}" cy="{cy}" r="{rad[i]+3}" fill="none" stroke="{c}" stroke-width="2"/>')
        for j, ln in enumerate(titles[i]):
            s += f'<text x="{n(x)}" y="{ty+21*j}" text-anchor="middle" font-size="18" font-weight="700" fill="{BRAND if i == 3 else INK}">{esc(ln)}</text>'
        for j, ln in enumerate(subs[i]):
            s += f'<text x="{n(x)}" y="{sy+18*j}" text-anchor="middle" font-size="14" fill="{MUTED}">{esc(ln)}</text>'
    gx, bx = xs[3], xs[1]
    s += (f'<path class="df" d="M{n(gx)},{cy-66} C{n(gx)},{cy-128} {n(bx)},{cy-128} {n(bx)},{cy-48}" fill="none" stroke="{BRAND}" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#{marker_id(BRAND)})"/>'
          f'<text x="{n((gx+bx)/2)}" y="{cy-122}" text-anchor="middle" font-size="14" font-weight="700" fill="{HOT}">{esc(fit(t["noop"], 14, gx - bx + 120, True))}</text>')
    return s + "</g></svg>\n"


# --- hero: the clean Mars plate (embedded JPEG) with the vector mark, wordmark and motion on top ---
def plate_jpeg():
    """The plate as a small JPEG, or None (plate not on this machine, or no ImageMagick)."""
    tool = shutil.which("magick")
    if not PLATE.exists() or not tool:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "plate.jpg"
        subprocess.run([tool, str(PLATE), "-resize", "1280x", "-strip", "-sampling-factor", "4:2:0",
                        "-interlace", "JPEG", "-quality", "76", str(out)], check=True)
        return out.read_bytes()


def hero(jpeg):
    w, h = 1280, 480
    my = 214  # wordmark baseline anchor
    fx, fy = 1172, 84  # the plate's star flare
    pcx, pcy, R = 640, 2007, 1640  # the plate's planet limb (fitted to the brightest rim pixels)
    title = "Foma Skills"
    tag = "Lightweight skills for Claude Code"
    fit(title, 84, w - 120, True)
    fit(tag, 24, w - 120)

    def limb_y(x):
        return pcy - math.sqrt(R * R - (x - pcx) ** 2)
    ax0, ax1 = 150, 1130
    arc = f"M{ax0},{n(limb_y(ax0))} A{R},{R} 0 0 1 {ax1},{n(limb_y(ax1))}"
    sparks = [(118, 128, 1.4, 1), (330, 64, 1.1, 2), (566, 104, 1.6, 3), (772, 58, 1.2, 1), (912, 150, 1.5, 2),
              (1064, 246, 1.3, 3), (1218, 196, 1.1, 1), (214, 318, 1.5, 2), (1108, 318, 1.2, 3), (640, 34, 1.0, 2),
              (992, 36, 1.3, 1), (468, 336, 1.1, 3)]
    css = (flare_css(fx, fy, 1.5) + SHIMMER.replace("9s ease-in-out 3s", "12s ease-in-out 2s") +
           ".lb{animation:lb 7s ease-in-out .5s infinite}@keyframes lb{50%{opacity:.45}}"
           ".gl{transform-box:fill-box;transform-origin:center;animation:gl 7s ease-in-out .5s infinite}"
           "@keyframes gl{50%{opacity:.55;transform:scaleX(1.18)}}"
           ".s1,.s2,.s3{animation:s1 9s ease-in-out infinite alternate}.s2{animation-name:s2;animation-duration:12s}"
           ".s3{animation-name:s3;animation-duration:15s}"
           "@keyframes s1{50%{opacity:.25}100%{transform:translate(10px,-7px)}}"
           "@keyframes s2{50%{opacity:.3}100%{transform:translate(-9px,-10px)}}"
           "@keyframes s3{50%{opacity:.2}100%{transform:translate(7px,8px)}}")
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
         f'role="img" aria-label="{title}: {tag}">\n<title>{title}: {tag}</title>\n<defs>'
         f'<clipPath id="card"><rect width="{w}" height="{h}" rx="24"/></clipPath>'
         '<filter id="hg" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
         f'<linearGradient id="lg" gradientUnits="userSpaceOnUse" x1="{ax0}" y1="0" x2="{ax1}" y2="0"><stop offset="0" stop-color="{BRAND}" stop-opacity="0"/>'
         f'<stop offset="0.45" stop-color="#ffd2ad" stop-opacity="0.85"/><stop offset="0.7" stop-color="{HOT}" stop-opacity="0.6"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="arc2" gradientUnits="userSpaceOnUse" x1="{ax0}" y1="0" x2="{ax1}" y2="0"><stop offset="0.05" stop-color="#fff0e0" stop-opacity="0"/>'
         '<stop offset="0.5" stop-color="#fff0e0" stop-opacity="0.95"/><stop offset="0.95" stop-color="#fff0e0" stop-opacity="0"/></linearGradient>'
         f'<radialGradient id="glint"><stop offset="0" stop-color="#ffe2c8" stop-opacity="0.6"/><stop offset="0.35" stop-color="{HOT}" stop-opacity="0.25"/><stop offset="1" stop-color="{HOT}" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="rayh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd2b0" stop-opacity="0"/><stop offset="0.62" stop-color="#fff1e4"/><stop offset="1" stop-color="#ffd2b0" stop-opacity="0"/></linearGradient>'
         '<linearGradient id="rayv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd2b0" stop-opacity="0"/><stop offset="0.45" stop-color="#fff1e4"/><stop offset="1" stop-color="#ffd2b0" stop-opacity="0"/></linearGradient>'
         f'<radialGradient id="core"><stop offset="0" stop-color="#fff8f0"/><stop offset="0.2" stop-color="#ffc08f" stop-opacity="0.8"/><stop offset="0.55" stop-color="{BRAND}" stop-opacity="0.2"/><stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></radialGradient>'
         '</defs>' + motion(css) + '\n<g clip-path="url(#card)">'
         f'<rect width="{w}" height="{h}" fill="{SPACE}"/>'
         f'<image width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/jpeg;base64,{base64.b64encode(jpeg).decode()}"/>\n'
         # the limb: a breathing rim light, a glint at the crest and a slow light running along it
         f'<g class="lb"><path d="{arc}" fill="none" stroke="url(#lg)" stroke-width="10" stroke-opacity="0.22"/>'
         f'<path d="{arc}" fill="none" stroke="url(#lg)" stroke-width="2"/></g>'
         f'<ellipse class="gl" cx="700" cy="{n(limb_y(700))}" rx="300" ry="20" fill="url(#glint)"/>'
         + shimmer(arc, "arc2", 2.2) +
         # star flare over the plate's own
         f'<circle cx="{fx}" cy="{fy}" r="34" fill="url(#core)" fill-opacity="0.5"/>'
         f'<g class="fr"><polygon points="{fx-190},{fy} {fx},{fy-1.5} {fx+108},{fy} {fx},{fy+1.5}" fill="url(#rayh)"/>'
         f'<polygon points="{fx},{fy-66} {fx+1.5},{fy} {fx},{fy+80} {fx-1.5},{fy}" fill="url(#rayv)"/></g>'
         f'<g class="fc"><circle cx="{fx}" cy="{fy}" r="10" fill="url(#core)"/><circle cx="{fx}" cy="{fy}" r="2.4" fill="#fffaf4"/></g>\n'
         + "".join(f'<circle class="s{c}" style="animation-delay:{i * 0.7 % 5:.1f}s" cx="{x}" cy="{y}" r="{r}" fill="#ffe9d8"/>'
                   for i, (x, y, r, c) in enumerate(sparks)) +
         f'</g><rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="23.5" fill="none" stroke="{INK}" stroke-opacity="0.1"/>\n'
         + f'<g font-family="{FONT}" text-anchor="middle"><text x="{w // 2}" y="{my+30}" font-size="84" font-weight="700" letter-spacing="-1" fill="{INK}">Foma <tspan fill="{BRAND}">Skills</tspan></text>'
         f'<text x="{w // 2}" y="{my+80}" font-size="24" letter-spacing="0.3" fill="#d9cbc0" fill-opacity="0.85">{tag}</text></g>\n</svg>\n')
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", metavar="PROJECT_DIR")
    args = ap.parse_args()
    if args.refresh:
        refresh(args.refresh)
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "ru"):
        for name, fn in (("token-cost", token_cost), ("skill-map", skill_map), ("propose-first", propose_first)):
            (OUT / f"{name}.{lang}.svg").write_text(fn(lang))
    print("wrote", len(list(OUT.glob("*.svg"))), "svg files")
    jpeg = plate_jpeg()
    if jpeg is None:
        print(f"hero: kept the committed {HERO.name} (rebuilding needs {PLATE.name} in photo github/ and ImageMagick)")
    else:
        HERO.write_text(hero(jpeg))
        kb = HERO.stat().st_size / 1024
        if kb > 200:
            sys.exit(f"hero: {kb:.0f} KB is over the 200 KB budget")
        print(f"wrote {HERO.relative_to(ROOT)} ({kb:.0f} KB)")


if __name__ == "__main__":
    main()
