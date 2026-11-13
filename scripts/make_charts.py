#!/usr/bin/env python3
"""Build the README infographics (SVG, English and Russian) from real data. Free: no model calls.

Usage: python3 scripts/make_charts.py [--refresh PROJECT_DIR]
Writes docs/assets/charts/{token-cost,skill-map,propose-first}.{en,ru}.svg.
Token numbers come from docs/assets/charts/tokens.json, captured from Claude Code's own
`claude plugin details foma-skills` (run in a project where the plugin is installed):
--refresh PROJECT_DIR re-captures them. The skill map mirrors docs/graph.html.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/assets/charts"
DATA = OUT / "tokens.json"

COL = {"setup": "#e0a54a", "proc": "#7fa9d6", "meth": "#6cc0ad", "atom": "#a3adba", "meta": "#d98a9c", "agent": "#d98a9c", "hook": "#a3adba"}
BRAND = "#e8714a"
INK, MUTED = "#ece8e1", "#a29c92"
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


def head(w, h, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">\n'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#15141c"/><stop offset="0.6" stop-color="#1b1a28"/><stop offset="1" stop-color="#14202a"/></linearGradient>'
            f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#8a8579"/></marker></defs>\n'
            f'<rect width="{w}" height="{h}" rx="20" fill="url(#bg)"/><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="19" fill="none" stroke="#fff" stroke-opacity="0.08"/>\n'
            f'<g font-family="{FONT}">\n')


def title_block(t, sub, w):
    return (f'<text x="48" y="58" font-size="30" font-weight="800" fill="{INK}">{esc(t)}</text>'
            f'<text x="48" y="88" font-size="16" fill="{MUTED}">{esc(sub)}</text>'
            f'<rect x="48" y="104" width="64" height="4" rx="2" fill="{BRAND}"/>\n')


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


def kfmt(n, lang):
    s = f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)
    return s.replace(".", ",") if lang == "ru" else s


def token_cost(lang):
    d, t = json.loads(DATA.read_text()), T[lang]
    rows = sorted(d["skills"].items(), key=lambda kv: -kv[1]["invoke"])
    row_h, y0, bx, scale = 34, 190, 330, 780 / 1500
    h = y0 + row_h * len(rows) + 90
    s = head(1280, h, t["cost_title"]) + title_block(t["cost_title"], t["cost_sub"], 1280)
    # legend
    s += (f'<rect x="760" y="46" width="14" height="14" rx="3" fill="{BRAND}"/><text x="782" y="58" font-size="14" fill="{INK}">{esc(t["always"])}</text>'
          f'<rect x="760" y="70" width="14" height="14" rx="3" fill="#8fb8e6"/><text x="782" y="82" font-size="14" fill="{INK}">{esc(t["invoke"])}</text>')
    # chips
    chips = [(t["chip1"], "#e0a54a", 130), (t["chip2"], BRAND, 238), (t["chip3"], "#8fb8e6", 262)]
    x = 48
    for label, c, w in chips:
        s += (f'<rect x="{x}" y="128" width="{w}" height="34" rx="17" fill="{c}" fill-opacity="0.15" stroke="{c}" stroke-opacity="0.7"/>'
              f'<text x="{x+w/2}" y="150" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">{esc(label)}</text>')
        x += w + 12
    for i, (name, v) in enumerate(rows):
        y = y0 + i * row_h
        c = COL[GROUP[name]]
        s += (f'<circle cx="62" cy="{y+14}" r="6" fill="{c}"/><text x="78" y="{y+19}" font-size="16" font-weight="600" fill="{INK}">{esc(name)}</text>'
              f'<rect x="{bx}" y="{y+4}" width="{max(v["always"]*scale, 2):.0f}" height="10" rx="5" fill="{BRAND}"/>'
              f'<text x="{bx+v["always"]*scale+10:.0f}" y="{y+13}" font-size="12" fill="{MUTED}">~{v["always"]}</text>'
              f'<rect x="{bx}" y="{y+17}" width="{v["invoke"]*scale:.0f}" height="10" rx="5" fill="#8fb8e6"/>'
              f'<text x="{bx+v["invoke"]*scale+10:.0f}" y="{y+26}" font-size="12" fill="{INK}">~{kfmt(v["invoke"], lang)}</text>')
    for tick in (0, 500, 1000, 1500):
        x = bx + tick * scale
        s += (f'<line x1="{x:.0f}" y1="{y0-8}" x2="{x:.0f}" y2="{y0+row_h*len(rows)}" stroke="#fff" stroke-opacity="0.07"/>'
              f'<text x="{x:.0f}" y="{y0+row_h*len(rows)+22}" text-anchor="middle" font-size="12" fill="{MUTED}">{kfmt(tick, lang) if tick else "0"}</text>')
    s += f'<text x="48" y="{h-26}" font-size="13" fill="{MUTED}">{esc(t["cost_foot"])}</text>\n</g></svg>\n'
    return s


NODES = [  # id, name key, column x, row, group, width
    ("hook", "hook", 310, "hook", "hook", 190), ("tune", "tuning", 1150, "hook", "meta", 150),
    ("gw", "groundwork", 295, "setup", "setup", 150), ("tidy", "tidying", 465, "setup", "setup", 150), ("hand", "handoff", 635, "setup", "setup", 150),
    ("learn", "learning", 805, "setup", "setup", 150), ("find", "skill-finder", 975, "setup", "setup", 150), ("ws", "writing-skills", 1145, "setup", "meta", 150),
    ("shape", "shaping", 310, "proc", "proc", 190), ("design", "design-interview", 555, "proc", "proc", 190), ("plan", "planning", 800, "proc", "proc", 190), ("exec", "executing", 1045, "proc", "proc", 190),
    ("dbg", "debugging", 430, "meth", "meth", 190), ("rev", "reviewing", 730, "meth", "meth", 190), ("ref", "refactoring", 1030, "meth", "meth", 190),
    ("tdd", "tdd", 430, "atom", "atom", 190), ("com", "committing", 730, "atom", "atom", 190), ("doc", "documenting", 1030, "atom", "atom", 190),
    ("impl", "implementer", 430, "agent", "agent", 190), ("expl", "explorer", 730, "agent", "agent", 190), ("rvw", "reviewer", 1030, "agent", "agent", 190),
]
ROWS = {"hook": 150, "setup": 222, "contract": 322, "proc": 432, "meth": 542, "atom": 662, "agent": 790}
EDGES = [("hook", "hand"), ("hook", "tune", "dash"), ("hand", "tidy", "dash"), ("hand", "learn", "dash"), ("shape", "plan", "dash"), ("design", "plan", "dash"),
         ("shape", "doc"), ("plan", "doc"), ("exec", "dbg"), ("exec", "rev"), ("exec", "ref"), ("exec", "tdd"), ("exec", "com"), ("exec", "doc"),
         ("exec", "impl"), ("exec", "rvw"), ("exec", "expl"), ("dbg", "tdd"), ("dbg", "expl"), ("ref", "tdd"), ("impl", "tdd"), ("rvw", "rev")]


def skill_map(lang):
    t = T[lang]
    n = {i: dict(name=nm, x=x, y=ROWS[r], g=g, w=w, h=52) for i, nm, x, r, g, w in NODES}
    s = head(1280, 850, t["map_title"]) + title_block(t["map_title"], t["map_sub"], 1280)
    # band labels
    for key, row in (("setup", "setup"), ("proc", "proc"), ("meth", "meth"), ("atom", "atom"), ("agent", "agent")):
        y = ROWS[row]
        s += (f'<circle cx="62" cy="{y}" r="6" fill="{COL[key]}"/><text x="76" y="{y+5}" font-size="14" font-weight="600" fill="{COL[key]}">{esc(t["bands"][key])}</text>')
    # contract bar
    cy = ROWS["contract"]
    s += (f'<rect x="220" y="{cy-24}" width="1020" height="48" rx="10" fill="#4d7c3a" fill-opacity="0.14" stroke="#92c27a" stroke-opacity="0.7"/>'
          f'<text x="730" y="{cy+5}" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">{esc(t["contract"])}</text>')
    # edges first
    for e in EDGES + [("gw", "CONTRACT"), ("learn", "CONTRACT", "dash")]:
        a, b, style = e[0], e[1], (e[2] if len(e) > 2 else "solid")
        sa = n[a]
        c = COL[sa["g"]]
        dash = ' stroke-dasharray="6 5"' if style == "dash" else ""
        if b == "CONTRACT":
            x1, y1, x2, y2 = sa["x"], sa["y"] + 26, sa["x"], cy - 24
            d = f"M{x1},{y1} L{x2},{y2}"
        else:
            tb = n[b]
            if sa["y"] == tb["y"]:
                d = (f"M{sa['x']+sa['w']/2},{sa['y']} L{tb['x']-tb['w']/2},{tb['y']}" if tb["x"] > sa["x"]
                     else f"M{sa['x']-sa['w']/2},{sa['y']} L{tb['x']+tb['w']/2},{tb['y']}")
            else:
                y1, y2 = sa["y"] + 26, tb["y"] - 26
                m = (y1 + y2) / 2
                d = f"M{sa['x']},{y1} C{sa['x']},{m} {tb['x']},{m} {tb['x']},{y2}"
        s += f'<path d="{d}" fill="none" stroke="{c}" stroke-opacity="0.55" stroke-width="1.8"{dash} marker-end="url(#ar)"/>'
    # nodes
    for i, nd in n.items():
        c = COL[nd["g"]]
        key = nd["name"]
        label = t["hooklabel"] if key == "hook" else key
        dash = ' stroke-dasharray="5 4"' if key in ("hook", "tuning", "writing-skills") else ""
        s += (f'<rect x="{nd["x"]-nd["w"]/2}" y="{nd["y"]-26}" width="{nd["w"]}" height="52" rx="12" fill="#1a1927"/>'
              f'<rect x="{nd["x"]-nd["w"]/2}" y="{nd["y"]-26}" width="{nd["w"]}" height="52" rx="12" fill="{c}" fill-opacity="0.14" stroke="{c}" stroke-width="1.6"{dash}/>'
              f'<text x="{nd["x"]}" y="{nd["y"]-2}" text-anchor="middle" font-size="16" font-weight="700" fill="{INK}">{esc(label)}</text>'
              f'<text x="{nd["x"]}" y="{nd["y"]+16}" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(t["sub"][key])}</text>')
    s += f'<text x="740" y="{ROWS["hook"]-8}" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(t["fire"])}</text>'
    return s + "</g></svg>\n"


def propose_first(lang):
    t = T[lang]
    steps = t["steps"]
    w, h, n = 1280, 430, len(steps)
    gap = (w - 96) / n
    s = head(w, h, t["flow_title"]) + title_block(t["flow_title"], t["flow_sub"], w)
    cy = 215
    xs = [48 + gap * (i + 0.5) for i in range(n)]
    cols = ["#a3adba", "#7fa9d6", "#e0a54a", BRAND, "#6cc0ad", "#d98a9c"]
    for i in range(n - 1):
        s += f'<path d="M{xs[i]+46},{cy} L{xs[i+1]-46},{cy}" stroke="#8a8579" stroke-width="2.5" fill="none" marker-end="url(#ar)"/>'
    for i, ((title, sub), x) in enumerate(zip(steps, xs)):
        gate = i == 3
        r = 44 if gate else 38
        if gate:
            s += f'<circle cx="{x}" cy="{cy}" r="58" fill="{BRAND}" fill-opacity="0.16"/>'
        s += (f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{cols[i]}"/>'
              f'<text x="{x}" y="{cy+9}" text-anchor="middle" font-size="{30 if gate else 26}" font-weight="800" fill="#15141c">{i+1}</text>'
              f'<text x="{x}" y="{cy+84}" text-anchor="middle" font-size="18" font-weight="700" fill="{INK}">{esc(title)}</text>'
              f'<text x="{x}" y="{cy+108}" text-anchor="middle" font-size="14" fill="{MUTED}">{esc(sub)}</text>')
    gx = xs[3]
    s += (f'<path d="M{gx},{cy-60} C{gx},{cy-120} {xs[1]},{cy-120} {xs[1]},{cy-44}" fill="none" stroke="{BRAND}" stroke-opacity="0.8" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#ar)"/>'
          f'<text x="{(gx+xs[1])/2:.0f}" y="{cy-112}" text-anchor="middle" font-size="14" font-weight="600" fill="{BRAND}">{esc(t["noop"])}</text>')
    return s + "</g></svg>\n"


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


if __name__ == "__main__":
    main()
