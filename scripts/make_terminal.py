#!/usr/bin/env python3
"""README terminal card: the "first 5 minutes" session as an animated terminal
(docs/assets/charts/first-5-minutes.{en,ru}.svg).

Usage: python3 scripts/make_terminal.py   (stdlib only; reuses the palette and helpers of make_charts.py)
The static look (also what prefers-reduced-motion shows) is the finished session. Motion: user lines are typed
(a body-coloured curtain slides off the text in one step per character), skill replies fade in, the session holds,
fades out and loops. Only transform and opacity animate. Monospace text uses textLength, so widths do not depend on
the viewer's font. Each file is self-contained (no fonts, scripts or external refs).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_charts as mc  # noqa: E402

OUT = mc.OUT
BRAND, INK, MUTED, COL, GROUP, FONT, esc, n = mc.BRAND, mc.INK, mc.MUTED, mc.COL, mc.GROUP, mc.FONT, mc.esc, mc.n

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
FS, CW = 13.5, 8.1          # mono font size and the fixed advance per character
W, PAD, BAR, LH, GAP = 860, 28, 40, 25, 14
TAG_CH = 12                 # width of the skill-label column, in characters
MSG_X = PAD + TAG_CH * CW + 14
MAX_CH = int((W - PAD - MSG_X) / CW)
BODY, BARFILL = "#0a0910", "#15111b"

SESSIONS = {
    "en": {
        "title": "claude  ·  ~/shop", "note": "illustrative session",
        "turns": [
            ("you", "I want to build a loyalty points system for the shop.", None),
            ("ai", "shaping", "Before I write anything: how do customers earn points, and can they expire?"),
            ("you", "...answers...", "→ an approved spec in docs/specs/"),
            ("you", "Make a plan.", None),
            ("ai", "planning", "4 tasks in docs/plans/loyalty/plan.md, each with a check and a model."),
            ("you", "Execute the plan.", None),
            ("ai", "executing", "Runs the tasks, checks each one, one review at the end."),
            ("you", "Commit my changes.", None),
            ("ai", "committing", "Small commits in your style, only the files it changed. It does not push."),
            ("you", "Wrap up, I'll continue tomorrow.", None),
            ("ai", "handoff", 'Saves a short note; the next session starts with "Next: ...".'),
        ],
    },
    "ru": {
        "title": "claude  ·  ~/shop", "note": "пример сессии",
        "turns": [
            ("you", "Хочу сделать систему бонусных баллов для магазина.", None),
            ("ai", "shaping", "Прежде чем писать код: как покупатели получают баллы, и сгорают ли они?"),
            ("you", "...отвечаете...", "→ утверждённая спека в docs/specs/"),
            ("you", "Составь план.", None),
            ("ai", "planning", "4 задачи в docs/plans/loyalty/plan.md, у каждой проверка и модель."),
            ("you", "Выполняй план.", None),
            ("ai", "executing", "Делает задачи по одной, проверяет каждую, в конце одно ревью."),
            ("you", "Закоммить мои изменения.", None),
            ("ai", "committing", "Маленькие коммиты в стиле проекта, только свои файлы. Не пушит."),
            ("you", "Завершаем, продолжу завтра.", None),
            ("ai", "handoff", 'Сохраняет короткую заметку; новая сессия начнётся с "Next: ...".'),
        ],
    },
}


def card(lang):
    s = SESSIONS[lang]
    # layout and timeline in one pass
    y = BAR + 36
    t = 0.9
    rows = []
    for i, turn in enumerate(s["turns"]):
        kind = turn[0]
        text = turn[1] if kind == "you" else turn[2]
        if len(text) > MAX_CH:
            sys.exit(f"terminal line too long ({len(text)} > {MAX_CH} chars): {text!r}")
        if i:
            y += LH + (GAP if kind == "you" else 0)
        if kind == "you":
            a, b = t, t + max(0.7, len(text) * 0.045)
            note_at = b + 0.15
            t = b + 0.9
        else:
            a, b, note_at = t, t + 0.4, None
            t = b + 1.0 + len(text) * 0.012
        rows.append({"kind": kind, "y": y, "turn": turn, "text": text, "a": a, "b": b, "note_at": note_at})
    y_prompt = y + LH + GAP
    total = round(t + 3.6 + 0.8, 1)
    fade_at = total - 0.8
    h = int(y_prompt + 26)

    def pct(x):
        return f"{x / total * 100:.3f}"

    css = [".bk{animation:bk 1.1s steps(1) infinite}@keyframes bk{50%{opacity:0}}"]
    body = []
    for i, r in enumerate(rows):
        y_, a, b = r["y"], r["a"], r["b"]
        if r["kind"] == "you":
            note = r["turn"][2]
            tw_ = len(r["text"]) * CW
            chev = (f'<path d="M{n(MSG_X - 17)},{n(y_ - 10)} l6,5.2 l-6,5.2" fill="none" stroke="{BRAND}" stroke-width="2" '
                    'stroke-linecap="round" stroke-linejoin="round"/>')
            txt = (f'<text x="{n(MSG_X)}" y="{n(y_)}" textLength="{n(tw_)}" lengthAdjust="spacing" font-family="{MONO}" '
                   f'font-size="{FS}" font-weight="600" fill="{INK}" xml:space="preserve">{esc(r["text"])}</text>')
            curtain = (f'<rect class="c{i}" x="{n(MSG_X + tw_)}" y="{n(y_ - 17)}" width="{n(tw_ + 8)}" height="{LH}" fill="{BODY}"/>')
            extra = ""
            if note:
                nx = MSG_X + tw_ + 2 * CW
                extra = (f'<text class="n{i}" x="{n(nx)}" y="{n(y_)}" textLength="{n(len(note) * CW)}" lengthAdjust="spacing" '
                         f'font-family="{MONO}" font-size="{FS}" fill="{COL["proc"]}">{esc(note)}</text>')
                css.append(f".n{i}{{animation:n{i} {total}s linear infinite}}@keyframes n{i}{{0%,{pct(r['note_at'])}%{{opacity:0}}"
                           f"{pct(r['note_at'] + 0.3)}%,{pct(fade_at)}%{{opacity:1}}100%{{opacity:0}}}}")
            body.append(f'<g class="r{i}">{chev}{txt}{curtain}{extra}</g>')
            css.append(f".r{i}{{animation:r{i} {total}s linear infinite}}@keyframes r{i}{{0%,{pct(a)}%{{opacity:0}}"
                       f"{pct(a + 0.1)}%,{pct(fade_at)}%{{opacity:1}}100%{{opacity:0}}}}")
            css.append(f".c{i}{{animation:c{i} {total}s steps({len(r['text'])},end) infinite}}@keyframes c{i}{{0%,{pct(a)}%"
                       f"{{transform:translateX({n(-tw_)}px)}}{pct(b)}%,100%{{transform:translateX(0)}}}}")
        else:
            skill, text = r["turn"][1], r["text"]
            colour = COL[GROUP[skill]]
            pw = (len(skill) + 2) * CW
            pill = (f'<rect x="{n(PAD)}" y="{n(y_ - 14.5)}" width="{n(pw)}" height="21" rx="10.5" fill="{colour}" fill-opacity="0.14" '
                    f'stroke="{colour}" stroke-opacity="0.55"/>'
                    f'<text x="{n(PAD + CW)}" y="{n(y_ - 0.2)}" textLength="{n(len(skill) * CW)}" lengthAdjust="spacing" font-family="{MONO}" '
                    f'font-size="{FS - 1}" font-weight="700" fill="{colour}">{esc(skill)}</text>')
            txt = (f'<text x="{n(MSG_X)}" y="{n(y_)}" textLength="{n(len(text) * CW)}" lengthAdjust="spacing" font-family="{MONO}" '
                   f'font-size="{FS}" fill="{MUTED}">{esc(text)}</text>')
            body.append(f'<g class="r{i}">{pill}{txt}</g>')
            css.append(f".r{i}{{animation:r{i} {total}s linear infinite}}@keyframes r{i}{{0%,{pct(a)}%{{opacity:0;transform:translateY(5px)}}"
                       f"{pct(b)}%,{pct(fade_at)}%{{opacity:1;transform:none}}100%{{opacity:0;transform:none}}}}")
    prompt = (f'<path d="M{n(MSG_X - 17)},{n(y_prompt - 10)} l6,5.2 l-6,5.2" fill="none" stroke="{BRAND}" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round"/>'
              f'<rect class="bk" x="{n(MSG_X)}" y="{n(y_prompt - 13)}" width="{n(CW)}" height="17" fill="{BRAND}" fill-opacity="0.85"/>')

    dots = "".join(f'<circle cx="{PAD + 7 + i * 19}" cy="{BAR / 2}" r="5.5" fill="{c}"/>'
                   for i, c in enumerate((BRAND, COL["setup"], COL["meth"])))
    chrome = (f'<rect width="{W}" height="{BAR}" fill="{BARFILL}"/>'
              f'<line x1="0" y1="{BAR - 0.5}" x2="{W}" y2="{BAR - 0.5}" stroke="{INK}" stroke-opacity="0.08"/>{dots}'
              f'<text x="{W / 2}" y="{BAR / 2 + 4.5}" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{MUTED}">{esc(s["title"])}</text>'
              f'<text x="{W - PAD}" y="{BAR / 2 + 4.2}" text-anchor="end" font-family="{FONT}" font-size="12" fill="{MUTED}" '
              f'fill-opacity="0.75">{esc(s["note"])}</text>')
    label = " ".join((f'You: {t_[1]}' if t_[0] == "you" else f'Claude [{t_[1]}]: {t_[2]}') if lang == "en"
                     else (f'Вы: {t_[1]}' if t_[0] == "you" else f'Claude [{t_[1]}]: {t_[2]}') for t_ in s["turns"])
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{esc(label).replace(chr(34), "&quot;")}">\n'
           f'<title>{esc(label)}</title>{mc.motion("".join(css))}\n'
           f'<defs><clipPath id="c"><rect width="{W}" height="{h}" rx="16"/></clipPath>'
           f'<radialGradient id="g" cx="0" cy="0" r="1"><stop offset="0" stop-color="{BRAND}" stop-opacity="0.2"/>'
           f'<stop offset="1" stop-color="{BRAND}" stop-opacity="0"/></radialGradient></defs>\n'
           f'<g clip-path="url(#c)"><rect width="{W}" height="{h}" fill="{BODY}"/>{chrome}'
           f'<ellipse cx="0" cy="{BAR}" rx="260" ry="60" fill="url(#g)"/>{"".join(body)}{prompt}</g>\n'
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="{INK}" stroke-opacity="0.14"/>\n</svg>\n')
    return out, total


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "ru"):
        svg, total = card(lang)
        (OUT / f"first-5-minutes.{lang}.svg").write_text(svg)
        print(f"first-5-minutes.{lang}.svg  {len(svg) / 1024:.1f} KB  loop {total}s")


if __name__ == "__main__":
    main()
