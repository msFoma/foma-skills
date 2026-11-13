#!/usr/bin/env python3
"""GitHub profile banner and three button panels, drawn as pixel art (docs/assets/profile/).

Usage: python3 scripts/assets/make_profile_banner.py [--out DIR]   (stdlib only, deterministic)

Writes four self-contained SVGs into docs/assets/profile/:
  banner.svg       840x380 (grid 210x95, 1 cell = 4 units): a giant rust planet on the right, the huge title
                   "Foma" / "Skills" with bevel, outline and stepped shadow, an orbit ring behind the letters, a tiny
                   cat on the planet rim, a star flare, a moon, a starfield and the tagline "Skills that ask first."
  btn-install.svg  280x84 (grid 70x21): primary orange key, rocket icon, label INSTALL
  btn-map.svg      280x84: secondary dark key, constellation icon, label LIVE MAP, blinking green status dot
  btn-star.svg     280x84: secondary dark key, star icon, label STAR
Use in the profile README: the banner as one <img> (full width), directly under it the three buttons in ONE line
with no whitespace between the tags (3 x 280 = 840), each wrapped in a link:
  <img src="banner.svg"><br><a href=".."><img src="btn-install.svg" width="280"></a><a ..>...</a>
Preview: docs/design/profile-banner/d.html.

How it is built. Every image is a grid of square cells; each cell is one <rect> on a 4-unit grid. Static art is painted
into a pixel buffer and turned into few rects by a layered "painter" decomposition (a colour may be painted under
pixels that a later colour overwrites). Only 16 palette colours are used (plus one green status dot in btn-map.svg).
No <text>, <image>, filters or gradients. Motion is CSS only (steps(), transform and opacity); prefers-reduced-motion
turns it off.
Type: the big title glyphs are drawn from stroke skeletons (rect tables), cut at the corners (chamfers) and spaced by
an optical kerning pass (equal visual gaps per pair). The small font (tagline, button labels) is a hand-drawn 5x7
table of the same design.
"""
import argparse
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs/assets/profile"
CELL = 4

# ---------------------------------------------------------------- palette (16 colours + one status dot)
BG, S1, S2, S3 = "#07060b", "#0e0b14", "#171226", "#241c3a"                # space
R0, R1, R2, R3 = "#3b1710", "#6e2f1c", "#a8512f", "#e8714a"                # rust, R3 is the one accent
L1, L2, L3 = "#ffb27a", "#ffe3cc", "#fff4ea"                               # light
CREAM, GREY, CLOAK = "#f1e2cf", "#9b95a8", "#4a4560"                       # cat
BLUE, PALE = "#86b2f2", "#c9d3ff"                                          # cold: stars, ring, secondary keys
GREEN = "#5fd38d"                                                          # the status dot, nothing else
RAMP = [R0, R1, R2, R3, L1]                                                # planet tones, dark to light


# ---------------------------------------------------------------- pixel buffer and rect output
class Canvas:
    """A w x h grid of cells; px[y][x] is a colour or None (bare background)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]
        self.soft = [[False] * w for _ in range(h)]   # haze-only cells: stars may sit on them
        self.keepout = set()                          # cells stars must stay away from (text)

    def put(self, x, y, c, soft=False):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c
            self.soft[y][x] = soft

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def paint(self, cells, c):
        for (x, y) in cells:
            self.put(x, y, c)

    def frame(self, c):
        for x in range(self.w):
            self.px[0][x] = self.px[self.h - 1][x] = c
        for y in range(self.h):
            self.px[y][0] = self.px[y][self.w - 1] = c


def layer_rects(cv, color, later):
    """Rects that paint `color`; they may cover cells of colours painted later (those overwrite)."""
    w, h, px = cv.w, cv.h, cv.px
    rows = []
    for y in range(h):
        row, runs, x = px[y], [], 0
        while x < w:
            v = row[x]
            if v is None or not (v == color or v in later):
                x += 1
                continue
            x2, has = x, False
            while x2 < w:
                u = row[x2]
                if u is None or not (u == color or u in later):
                    break
                has = has or u == color
                x2 += 1
            runs.append((x, x2 - x, has))
            x = x2
        rows.append(runs)
    out, open_ = [], {}
    for y in range(h + 1):
        cur = {(x, wd): has for (x, wd, has) in rows[y]} if y < h else {}
        for key in [k for k in open_ if k not in cur]:
            y0, hs = open_.pop(key)
            a, b = 0, len(hs)
            while a < b and not hs[a]:
                a += 1
            while b > a and not hs[b - 1]:
                b -= 1
            if a < b:
                out.append((key[0], y0 + a, key[1], b - a))
        for key, has in cur.items():
            if key in open_:
                open_[key][1].append(has)
            else:
                open_[key] = [y, [has]]
    return out


def transposed(cv):
    t = Canvas(cv.h, cv.w)
    t.px = [list(col) for col in zip(*cv.px)]
    return t


def best_layer(cv, cvt, color, later):
    """Fewer rects of two: merged row runs, or merged column runs (drawn from the transposed canvas)."""
    a = layer_rects(cv, color, later)
    b = [(y, x, h, w) for (x, y, w, h) in layer_rects(cvt, color, later)]
    return a if len(a) <= len(b) else b


def painter_order(cv):
    """Colour order (first painted first) that needs the fewest rects; greedy local search, deterministic."""
    colors = sorted({c for row in cv.px for c in row if c})
    area = {c: sum(r.count(c) for r in cv.px) for c in colors}
    order = sorted(colors, key=lambda c: (-area[c], c))
    cache, cvt = {}, transposed(cv)

    def cost(o):
        n = 0
        for i, c in enumerate(o):
            key = (c, frozenset(o[i + 1:]))
            if key not in cache:
                cache[key] = best_layer(cv, cvt, c, set(o[i + 1:]))
            n += len(cache[key])
        return n

    best, improved = cost(order), True
    while improved:
        improved = False
        for i in range(len(order)):
            for j in range(len(order)):
                if i != j:
                    cand = order[:]
                    cand.insert(j, cand.pop(i))
                    n = cost(cand)
                    if n < best:
                        best, order, improved = n, cand, True
    return order, cache


def rect(x, y, w, h):
    return f'<rect x="{x * CELL}" y="{y * CELL}" width="{w * CELL}" height="{h * CELL}"/>'


def group(color, rects, cls=None):
    cl = f' class="{cls}"' if cls else ""
    return f'<g fill="{color}"{cl}>' + "".join(rect(*r) for r in rects) + "</g>"


def static_markup(cv):
    order, cache = painter_order(cv)
    parts = []
    for i, c in enumerate(order):
        rs = cache.get((c, frozenset(order[i + 1:])))
        if rs is None:
            rs = best_layer(cv, transposed(cv), c, set(order[i + 1:]))
        if rs:
            parts.append(group(c, rs))
    return "".join(parts)


def flat_markup(cells_by_color, cls=None, w=400, h=400):
    """Plain (non-overlapping) rects for overlay groups; cells_by_color = {colour: iterable of (x, y)}."""
    out = ""
    for color in sorted(cells_by_color):
        cv = Canvas(w, h)
        cv.paint(cells_by_color[color], color)
        out += group(color, layer_rects(cv, color, set()), cls)
    return out


def svg_doc(cv_w, cv_h, body, css, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cv_w * CELL} {cv_h * CELL}" '
        f'width="{cv_w * CELL}" height="{cv_h * CELL}" shape-rendering="crispEdges" role="img" aria-label="{label}">'
        f"<style>{css.strip()}</style>" + body + "</svg>\n"
    )


def count_rects(svg):
    return svg.count("<rect")


# ---------------------------------------------------------------- shape helpers (sets of (x, y) cells)
def box(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1) for x in range(x0, x1)}


def shift(cells, dx, dy):
    return {(x + dx, y + dy) for (x, y) in cells}


def dilate4(cells):
    out = set()
    for (x, y) in cells:
        out.update(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return out - cells


def stepped_shadow(cells, depth=2):
    out = set()
    for d in range(1, depth + 1):
        out |= shift(cells, d, d) | shift(cells, d, d - 1) | shift(cells, d - 1, d)
    return out - cells


def chamfer(cells, c):
    """Cut every convex corner of a straight-edged shape by c cells (a 45-degree bevel of c-1 steps)."""
    if c < 2:
        return set(cells)
    out = set(cells)
    for (x, y) in cells:
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):          # NW, NE, SW, SE corner cell
            if (x - sx, y) in cells or (x, y - sy) in cells:
                continue
            edge_h = all((x + sx * i, y) in cells and (x + sx * i, y - sy) not in cells for i in range(c + 1))
            edge_v = all((x, y + sy * j) in cells and (x - sx, y + sy * j) not in cells for j in range(c + 1))
            if edge_h and edge_v:
                for i in range(c):
                    for j in range(c - i):
                        out.discard((x + sx * i, y + sy * j))
    return out


def round_corners(cells, c_out, c_in):
    """Chamfer outer corners by c_out and fill inner (concave) corners by c_in."""
    shape = chamfer(cells, c_out)
    if c_in >= 2:
        xs, ys = [p[0] for p in shape], [p[1] for p in shape]
        pad = box(min(xs) - 3, min(ys) - 3, max(xs) + 4, max(ys) + 4)
        hole = pad - shape
        kept = chamfer(hole, c_in)
        inner = box(min(xs), min(ys), max(xs) + 1, max(ys) + 1)
        shape |= (hole - kept) & inner
    return shape


def bevel(cells):
    """Split a shape into (light, face, dark): light = top-left rim, dark = bottom-right rim, 1 cell wide."""
    light, dark = set(), set()
    for (x, y) in cells:
        tl = (x, y - 1) not in cells or (x - 1, y) not in cells
        br = (x, y + 1) not in cells or (x + 1, y) not in cells
        if tl and not br:
            light.add((x, y))
        elif br and not tl:
            dark.add((x, y))
    return light, cells - light - dark, dark


# ---------------------------------------------------------------- small font: hand-drawn 5x7 table
# '#' = ink. Same design as the title face: cut corners, one cell stroke, i and l are narrow.
SMALL = {
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "k": ["#....", "#....", "#...#", "#..#.", "###..", "#..#.", "#...#"],
    "i": [".#.", "...", "##.", ".#.", ".#.", ".#.", "###"],
    "l": ["##.", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "t": [".#..", ".#..", "####", ".#..", ".#..", ".#..", "..##"],
    "h": ["#....", "#....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "r": [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
    "f": [".##.", "#...", "###.", "#...", "#...", "#...", "#..."],
    ".": ["..", "..", "..", "..", "..", "##", "##"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "N": ["#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    " ": ["..", "..", "..", "..", "..", "..", ".."],
}


def small_text_cells(text, x0, y0):
    """Cells of text in the small font and its advance width (1 cell between glyphs)."""
    cells, x = set(), x0
    for ch in text:
        g = SMALL[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "#":
                    cells.add((x + c, y0 + r))
        x += len(g[0]) + (0 if ch == " " else 1)
    return cells, x - 1 - x0


def small_width(text):
    return small_text_cells(text, 0, 0)[1]


# ---------------------------------------------------------------- big font: skeletons, corner cuts, optical kerning
class Size:
    """One title size: cap height, x-height and stroke are in cells; the baseline is the last row."""

    def __init__(self, cap, xh, stroke, cut, rcut, stem, fill):
        self.H, self.XH, self.T = cap, xh, stroke
        self.y0 = cap - xh
        self.cuts = dict(cut=cut, rcut=rcut, stem=stem, fill=fill, none=0)   # corner cuts in cells


def stroke_line(xa, ya, xb, yb, ht):
    """A diagonal stroke from (xa, ya) to (xb, yb), ht cells thick horizontally, flat top and bottom."""
    cells = set()
    for y in range(ya, yb + 1):
        xc = xa + (xb - xa) * (y - ya) / (yb - ya)
        for x in range(round(xc - ht / 2), round(xc + ht / 2)):
            cells.add((x, y))
    return cells


def sk_F(s):
    w, m = round(s.H * 0.58), round(s.H * 0.42)
    return box(0, 0, s.T, s.H) | box(0, 0, w, s.T) | box(0, m, w - 1, m + s.T)


def sk_S(s):
    w, mid = round(s.H * 0.62), (s.H - s.T) // 2
    return (box(0, 0, w, s.T) | box(0, mid, w, mid + s.T) | box(0, s.H - s.T, w, s.H)
            | box(0, 0, s.T, mid + s.T) | box(w - s.T, mid, w, s.H))


def sk_o(s):
    w = round(s.XH * 0.78)
    return (box(0, s.y0, w, s.y0 + s.T) | box(0, s.H - s.T, w, s.H)
            | box(0, s.y0, s.T, s.H) | box(w - s.T, s.y0, w, s.H))


def sk_m(s):
    g = s.T
    w = 3 * s.T + 2 * g
    return (box(0, s.y0, w, s.y0 + s.T) | box(0, s.y0, s.T, s.H)
            | box(s.T + g, s.y0, 2 * s.T + g, s.H) | box(w - s.T, s.y0, w, s.H))


def sk_a(s):
    w = round(s.XH * 0.80)
    ym = s.y0 + (s.XH - s.T) // 2
    return (box(0, s.y0, w, s.y0 + s.T) | box(w - s.T, s.y0, w, s.H) | box(0, ym, w, ym + s.T)
            | box(0, ym, s.T, s.H) | box(0, s.H - s.T, w, s.H))


def sk_s(s):
    w = round(s.XH * 0.80)
    ym = s.y0 + (s.XH - s.T) // 2
    return (box(0, s.y0, w, s.y0 + s.T) | box(0, ym, w, ym + s.T) | box(0, s.H - s.T, w, s.H)
            | box(0, s.y0, s.T, ym + s.T) | box(w - s.T, ym, w, s.H))


def sk_k(s):
    w, ht = round(s.XH * 0.84), round(s.T * 1.5)
    ymid = s.y0 + round(s.XH * 0.56)
    top = stroke_line(w - ht // 2, s.y0, s.T + ht // 2 - 1, ymid, ht)
    bot = stroke_line(s.T + ht // 2 - 1, ymid, w - ht // 2, s.H - 1, ht)
    return box(0, 0, s.T, s.H) | top | bot


def sk_i(s):
    return box(0, 0, s.T, s.T) | box(0, s.y0, s.T, s.H)


def sk_l(s):
    return box(0, 0, s.T, s.H)


# glyph -> (skeleton, outer corner cut, inner corner fill); the names pick a cell count from Size.cuts
GLYPHS = {
    "F": (sk_F, "cut", "none"), "S": (sk_S, "rcut", "none"), "o": (sk_o, "rcut", "fill"), "m": (sk_m, "cut", "fill"),
    "a": (sk_a, "cut", "none"), "s": (sk_s, "cut", "none"), "k": (sk_k, "cut", "none"), "i": (sk_i, "stem", "none"),
    "l": (sk_l, "stem", "none"),
}


def build_glyph(ch, size):
    sk, outer, inner = GLYPHS[ch]
    return round_corners(sk(size), size.cuts[outer], size.cuts[inner])


def optical_offsets(word, glyphs, size, target, min_gap, kern):
    """x offset of every glyph so that the capped mean gap over the x-height band is `target` cells per pair."""
    xs, cap = [0], target * 2
    band = range(size.y0, size.H)
    for a, b in zip(word, word[1:]):
        right, left = {}, {}
        for (x, y) in glyphs[a]:
            right[y] = max(right.get(y, -1), x)
        for (x, y) in glyphs[b]:
            left[y] = min(left.get(y, 999), x)
        s = 1
        while True:
            ds = [(left[y] + s - right[y] - 1) if (y in right and y in left) else cap for y in band]
            both = [d for d in ds if d < cap]
            if (not both or min(both) >= min_gap) and sum(min(d, cap) for d in ds) / len(ds) >= target:
                break
            s += 1
        xs.append(xs[-1] + s + kern.get((a, b), 0))
    return xs


def title_cells(word, size, kern, gap_extra=0, min_gap=4):
    """Face cells of a whole word at the origin, plus the x extent."""
    glyphs = {ch: build_glyph(ch, size) for ch in set(word)}
    xs = optical_offsets(word, glyphs, size, size.T + gap_extra, min_gap, kern)
    cells = set()
    for ch, x in zip(word, xs):
        cells |= shift(glyphs[ch], x, 0)
    return cells


# ---------------------------------------------------------------- styled title words
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def paint_word(cv, cells, light, mid, dark, outline, shadow, dither_rows=3):
    """Shadow, outline, then a 3-tone bevelled face with an ordered-dither skirt on its lower rows."""
    body = cells | dilate4(cells)
    for (x, y) in stepped_shadow(body):
        cv.put(x, y, shadow(x, y))
    for (x, y) in dilate4(cells):
        cv.put(x, y, outline)
    lt, face, dk = bevel(cells)
    cv.paint(face, mid)
    cv.paint(lt, light)
    cv.paint(dk, dark)
    ybase = max(y for (_, y) in cells)
    for (x, y) in face:
        k = ybase - y - 1                      # 0 = the face row just above the dark rim
        if 0 <= k < dither_rows:
            level = (dither_rows - k) / (dither_rows + 1) * 16
            if BAYER[y % 4][x % 4] < level - 2:
                cv.put(x, y, dark)
    cv.keepout |= body | stepped_shadow(body)


def paint_small(cv, text, x, y, color, shadow):
    cells, w = small_text_cells(text, x, y)
    for (cx, cy) in shift(cells, 1, 1) - cells:
        cv.put(cx, cy, shadow)
    cv.paint(cells, color)
    cv.keepout |= cells | shift(cells, 1, 1)
    return w


# ================================================================ BANNER SCENE
BW, BH = 210, 95
PCX, PCY, PR = 158, 58, 66                      # planet centre and radius
LEDGE_Y = 30                                    # row of the rock ledge the cat stands on
CAT_X = 88
MOON_AT = (33, 5)
FLARE_AT = (85, 16)
RING = dict(cx=158, cy=59, a=152, b=13, th=0.115)
FOMA_AT, SKILLS_AT, TAG_AT = (10, 10), (10, 41), (10, 79)
FOMA_SIZE = Size(23, 17, 4, cut=2, rcut=3, stem=1, fill=2)
SKILLS_SIZE = Size(30, 22, 5, cut=3, rcut=5, stem=1, fill=2)
KERN_FOMA = {("F", "o"): -1}
KERN_SKILLS = {("S", "k"): 0, ("l", "s"): 0}

LIGHT = (0.74, -0.42, 0.52)
_n = math.sqrt(sum(a * a for a in LIGHT))
LIGHT = tuple(a / _n for a in LIGHT)
LDIR2 = (LIGHT[0] / math.hypot(LIGHT[0], LIGHT[1]), LIGHT[1] / math.hypot(LIGHT[0], LIGHT[1]))
POLE = (math.sin(0.30) * math.cos(0.42), -math.cos(0.30) * math.cos(0.42), math.sin(0.42))
BAND_OFF = [0.0, -0.45, 0.30, -0.20, 0.50, -0.50, 0.15, -0.35, 0.45, -0.10, 0.35, -0.40, 0.25, -0.25]
# craters: (x, y, radius). The second group (small, clustered) sits in the lower left of the lit side.
CRATERS = [
    (150, 22, 8), (187, 40, 11), (141, 54, 6), (205, 17, 7), (172, 70, 9), (130, 32, 5), (122, 14, 4),
    (158, 44, 3.5), (176, 12, 4), (211, 48, 5), (136, 74, 5), (160, 35, 2.5), (192, 25, 2.5), (148, 9, 2.5),
    (125, 50, 3), (180, 55, 3), (205, 33, 3), (112, 40, 4), (118, 66, 5), (196, 82, 6),
    (146, 82, 4), (154, 86, 3), (140, 88, 2.5), (160, 80, 2.5), (150, 90, 2), (133, 84, 3), (166, 90, 3),
]
STORM = (190, 66, 14, 6.5, -0.18)
STREAKS = [(0.735, (146, 204), 0.021), (0.655, (160, 196), 0.013), (0.50, (128, 176), 0.012)]


def in_planet(x, y):
    dx, dy = x + 0.5 - PCX, y + 0.5 - PCY
    return dx * dx + dy * dy <= PR * PR


def sphere(x, y):
    dx, dy = (x + 0.5 - PCX) / PR, (y + 0.5 - PCY) / PR
    d2 = dx * dx + dy * dy
    return None if d2 > 1 else (dx, dy, math.sqrt(1 - d2))


def shade(x, y):
    nx, ny, nz = sphere(x, y)
    lam = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
    v = 2.45 * (lam - 0.03)
    s = nx * POLE[0] + ny * POLE[1] + nz * POLE[2]
    warp = 0.30 * math.sin(2.7 * nx + 1.1) + 0.20 * math.sin(6.3 * ny - 1.9 * nx + 0.4) + 0.10 * math.sin(13 * nx + 4 * ny)
    k = math.floor(s * 8.4 + warp)
    v += BAND_OFF[k % len(BAND_OFF)] * (0.35 + 0.65 * max(0.0, min(1.0, lam * 2.2)))
    return v, lam


def quantise(v, x, y, w=0.075):
    f = v - math.floor(v)
    fp = max(0.0, min(1.0, (f - 0.5 + w) / (2 * w)))
    lvl = math.floor(v) + (1 if fp > (BAYER[y % 4][x % 4] + 0.5) / 16.0 else 0)
    return max(0, min(4, lvl))


def crater_delta(x, y):
    px, py = x + 0.5, y + 0.5
    best = 0
    for (cx, cy, r) in CRATERS:
        rx, ry = cx - PCX, cy - PCY
        rd = math.hypot(rx, ry) + 1e-6
        sq = max(0.42, math.sqrt(max(0.02, 1 - (rd / PR) ** 2)))
        ux, uy = rx / rd, ry / rd
        dx, dy = px - cx, py - cy
        a, b = dx * ux + dy * uy, -dx * uy + dy * ux
        e = (a / (r * sq)) ** 2 + (b / r) ** 2
        if e > 1.0:
            continue
        side = (dx * LDIR2[0] + dy * LDIR2[1]) / (math.hypot(dx, dy) + 1e-6)
        if r < 4:
            d = -1 if e < 0.45 else (1 if side < -0.2 else (-1 if side > 0.4 else 0))
        elif e <= 0.5:
            d = -1
        elif e <= 0.82:
            d = -1 if side > 0.1 else (1 if side < -0.25 else 0)
        else:
            d = 1 if side > 0.15 else 0
        if d:
            best = d
    return best


def storm_delta(x, y):
    cx, cy, rx, ry, th = STORM
    dx, dy = x + 0.5 - cx, y + 0.5 - cy
    u, v = dx * math.cos(th) + dy * math.sin(th), -dx * math.sin(th) + dy * math.cos(th)
    e = (u / rx) ** 2 + (v / ry) ** 2
    if e > 1:
        return 0
    return 1 if e < 0.10 else -1 if e < 0.34 else 1 if e < 0.62 else -1 if e < 0.82 else 0


def paint_planet(cv):
    rng = random.Random(11)
    lam_at = {}
    for y in range(BH):
        for x in range(BW):
            if sphere(x, y) is None:
                continue
            v, lam = shade(x, y)
            lam_at[(x, y)] = lam
            lvl = quantise(v, x, y)
            lvl = max(0, min(4, lvl + crater_delta(x, y) + storm_delta(x, y)))
            if lam > 0.15 and rng.random() < 0.005:
                lvl = max(0, min(4, lvl + rng.choice((-1, 1))))
            cv.put(x, y, RAMP[lvl])
    for (x, y), lam in lam_at.items():                      # thin limb light so the dark side reads against space
        if all(in_planet(a, b) for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))):
            continue
        ang = math.atan2(y + 0.5 - PCY, x + 0.5 - PCX)
        if lam > 0.30:
            cv.put(x, y, RAMP[min(3, RAMP.index(cv.get(x, y)) + 1)])
        elif x < 150:
            cv.put(x, y, RAMP[2] if (ang < -2.0 or ang > 2.95) else RAMP[1])


def rim_x(y):
    return next(x for x in range(BW) if in_planet(x, y))


def paint_ledge(cv):
    rng = random.Random(3)
    xs, xr = CAT_X, rim_x(LEDGE_Y)
    for x in range(xs, xr + 6):
        if x < xr + 1:
            t = 1 + (x - xs) // 4
        else:
            t = next((y - LEDGE_Y for y in range(LEDGE_Y, BH) if in_planet(x, y)), 3)
        t = max(t, 1)
        for k in range(t):
            col = RAMP[2] if k == 0 else RAMP[0] if (k >= t - 1 and t > 2) else (RAMP[1] if rng.random() > 0.2 else RAMP[0])
            cv.put(x, LEDGE_Y + k, col)


CAT = [
    "..KK..........KK..", ".KCAK........KACK.", ".KCAAK......KAACK.", ".KCCAAKKKKKKAACCK.",
    ".KCCCCCCCCCCCCCCK.", "KCCCCCCCCCCCCCCCCK", "KCMMMMMMMMMMMMMMCK", "KMMCCMMMMMMMMCCMMK",
    "KMCMMCMMMMMMCMMCMK", "KCCCCCCCAACCCCCCCK", ".KCCCCCCCCCCCCCCK.", "..KOOOOOOOOOOOOK..",
    "..KooooooooooooK..", "..KgDDDDDDDDDDDK..", "..KgDDDDDLLDDDDK..", ".KgDDDDDLLLLDDDDK.",
    ".KgDDDDDLLLLDDDDK.", ".KgDDDDDDLLDDDDDK.", ".KgDDDDDDDDDDDDDK.", "..KCCCK....KCCCK..",
]
CAT_LEG = dict(K=S3, A=R2, C=CREAM, M=S1, D=CLOAK, O=R3, o=R2, L=L2, g=GREY, h=L1)
FLAP = [(4, 13, "O"), (5, 13, "O"), (4, 14, "O"), (5, 14, "o"), (4, 15, "o"), (5, 15, "o")]


def scarf_tail():
    out = {}
    for t in range(12):
        top = round(10.4 + 0.16 * t + 1.35 * math.sin(0.85 * t))
        n = 3 if t < 8 else (2 if t < 10 else 1)
        for k in range(n):
            ch = "o" if (k == n - 1 and n > 1) else "O"
            if k == 0 and t % 4 == 2:
                ch = "h"
            out[(15 + t, top + k)] = ch
    return [(c, r, ch) for (c, r), ch in out.items()]


def paint_cat(cv):
    x0, y0 = CAT_X + 2, LEDGE_Y - 20
    for r, row in enumerate(CAT):
        for c, ch in enumerate(row):
            if ch in CAT_LEG:
                cv.put(x0 + c, y0 + r, CAT_LEG[ch])
    for (c, r, ch) in FLAP + scarf_tail():
        cv.put(x0 + c, y0 + r, CAT_LEG[ch])


def paint_moon(cv, x0, y0):
    rows = ["..###..", ".#####.", "#######", "#######", "#######", ".#####.", "..###.."]
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "#":
                cv.put(x0 + c, y0 + r, CLOAK if (c + r >= 9 or (c <= 1 and r >= 3)) else GREY)
    for (c, r) in ((3, 2), (4, 3), (2, 4)):
        cv.put(x0 + c, y0 + r, CLOAK)
    cv.put(x0 + 4, y0 + 1, L2)
    cv.put(x0 + 5, y0 + 2, L2)


def paint_haze(cv, cx, cy, rx, ry, outer, inner):
    for y in range(cv.h):
        for x in range(cv.w):
            e = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
            if e >= 1:
                continue
            lvl = math.floor((1 - e) * 2.3 + ((BAYER[y % 4][x % 4] + 0.5) / 16.0 - 0.5) * 0.9 + 0.5)
            if lvl >= 2:
                cv.put(x, y, inner, soft=True)
            elif lvl == 1:
                cv.put(x, y, outer, soft=True)


def ring_cells(cx, cy, a, b, th, n=12000):
    ct, st = math.cos(th), math.sin(th)
    seen = {}
    for i in range(n):
        t = 2 * math.pi * i / n
        ex, ey = a * math.cos(t), b * math.sin(t)
        key = (round(cx + ex * ct - ey * st - 0.5), round(cy + ex * st + ey * ct - 0.5))
        seen.setdefault(key, t)
    ps, changed = set(seen), True
    while changed:                                         # thin L-corners so the ring stays 1 cell wide
        changed = False
        for (x, y) in sorted(ps):
            for hx, vy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                if (x + hx, y) in ps and (x, y + vy) in ps and (x + hx, y + vy) not in ps:
                    ps.discard((x, y))
                    changed = True
                    break
    return {p: seen[p] for p in ps}


def banner_title(cv):
    for (word, size, kern, at, tones) in (
        ("Foma", FOMA_SIZE, KERN_FOMA, FOMA_AT, (L3, L2, L1)),
        ("Skills", SKILLS_SIZE, KERN_SKILLS, SKILLS_AT, (L1, R3, R2)),
    ):
        cells = shift(title_cells(word, size, kern), *at)
        paint_word(cv, cells, *tones, outline=S1, shadow=lambda x, y: S1 if in_planet(x, y) else R0)
    paint_small(cv, "Skills that ask first.", TAG_AT[0], TAG_AT[1], PALE, S1)


def make_stars(cv):
    rng = random.Random(7)
    free = [[True] * cv.w for _ in range(cv.h)]
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.px[y][x] is not None and not cv.soft[y][x]:
                for yy in range(max(0, y - 2), min(cv.h, y + 3)):
                    for xx in range(max(0, x - 2), min(cv.w, x + 3)):
                        free[yy][xx] = False
            if x < 3 or y < 3 or x > cv.w - 4 or y > cv.h - 4:
                free[y][x] = False
    for (px, py) in cv.keepout:
        for yy in range(py - 5, py + 6):
            for xx in range(px - 5, px + 6):
                if 0 <= xx < cv.w and 0 <= yy < cv.h:
                    free[yy][xx] = False
    fx, fy = FLARE_AT
    for yy in range(fy - 9, fy + 10):
        for xx in range(fx - 9, fx + 10):
            if 0 <= xx < cv.w and 0 <= yy < cv.h:
                free[yy][xx] = False
    cand = [(x, y) for y in range(cv.h) for x in range(cv.w) if free[y][x]]
    rng.shuffle(cand)
    used = []

    def take(sep, n, r):
        got = []
        for (x, y) in cand:
            if len(got) >= n:
                break
            if all(abs(x - u) > sep or abs(y - v) > sep for (u, v) in used) and all(
                    0 <= xx < cv.w and 0 <= yy < cv.h and free[yy][xx]
                    for yy in range(y - r, y + r + 1) for xx in range(x - r, x + r + 1)):
                got.append((x, y))
                used.append((x, y))
        return got

    stars = []
    for (x, y) in take(20, 3, 2):                                   # large: 5x5 plus
        stars.append([(x, y, L3)] + [(x + dx, y + dy, PALE) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                     + [(x + dx, y + dy, BLUE) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))])
    for (x, y) in take(12, 6, 1):                                    # medium: 3x3 plus
        stars.append([(x, y, PALE)] + [(x + dx, y + dy, BLUE) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))])
    for (x, y) in take(6, 46, 0):                                   # small: one cell
        stars.append([(x, y, rng.choice([BLUE, BLUE, PALE, CLOAK, L2]))])
    return stars


def flare_cells():
    fx, fy = FLARE_AT
    out = {}
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            d = abs(dx) + abs(dy)
            on = dx == 0 or dy == 0 or d <= 2 or (abs(dx) == 1 and abs(dy) <= 3) or (abs(dy) == 1 and abs(dx) <= 3)
            if on:
                out.setdefault(L3 if d <= 1 else L2 if d <= 2 else L1 if d <= 3 else R3, []).append((fx + dx, fy + dy))
    return out


def streak_cells(cv):
    out = {}
    for (s0, (xa, xb), th) in STREAKS:
        xm = (xa + xb) / 2
        for y in range(BH):
            for x in range(xa, xb + 1):
                sp = sphere(x, y)
                if sp is None:
                    continue
                s = sp[0] * POLE[0] + sp[1] * POLE[1] + sp[2] * POLE[2]
                tp = 1 - ((x - xm) / ((xb - xa) / 2)) ** 2
                if abs(s - s0) < th * max(0.0, tp) ** 0.6 + 0.003:
                    base = cv.get(x, y)
                    if base in RAMP:
                        out.setdefault(RAMP[min(4, RAMP.index(base) + 1)], []).append((x, y))
    return out


BANNER_CSS = """
.t1,.t2,.t3,.t4{animation-name:tw;animation-timing-function:steps(2,end);animation-iteration-count:infinite}
.t1{animation-duration:3s;animation-delay:-.6s}
.t2{animation-duration:3.7s;animation-delay:-2.1s}
.t3{animation-duration:4.4s;animation-delay:-1.2s}
.t4{animation-duration:5s;animation-delay:-3.4s}
@keyframes tw{0%{opacity:1}50%{opacity:.3}100%{opacity:1}}
.fl{transform-origin:%FX%px %FY%px;animation:pu 4s steps(2,end) infinite}
@keyframes pu{0%{transform:scale(1)}50%{transform:scale(1.15)}100%{transform:scale(1)}}
.cb{animation:dr 9s steps(1,end) infinite}
@keyframes dr{0%{transform:translateX(0)}50%{transform:translateX(4px)}}
@media (prefers-reduced-motion:reduce){.t1,.t2,.t3,.t4,.fl,.cb{animation:none}}
"""


def build_banner():
    cv = Canvas(BW, BH)
    for hz in ((100, 17, 36, 20, S1, S2), (30, 86, 40, 14, S1, S1)):
        paint_haze(cv, *hz)
    ring = ring_cells(RING["cx"], RING["cy"], RING["a"], RING["b"], RING["th"])
    front = []
    for (x, y), t in ring.items():
        if 0 <= x < BW and 0 <= y < BH:
            if not in_planet(x, y):
                cv.put(x, y, BLUE)
            elif math.sin(t) > 0:
                front.append((x, y))
    paint_moon(cv, *MOON_AT)
    paint_planet(cv)
    paint_ledge(cv)
    for (x, y) in front:
        cv.put(x, y, BLUE)
    banner_title(cv)
    paint_cat(cv)
    cv.frame(S3)
    streak = streak_cells(cv)
    stars = make_stars(cv)
    by = {}
    for i, st in enumerate(stars):
        for (x, y, c) in st:
            by.setdefault((f"t{i % 4 + 1}", c), []).append((x, y))
    star_markup = "".join(flat_markup({c: pts}, cls, BW, BH) for (cls, c), pts in sorted(by.items()))
    body = (f'<rect width="{BW * CELL}" height="{BH * CELL}" fill="{BG}"/>' + static_markup(cv) + star_markup
            + f'<g class="cb">{flat_markup(streak, None, BW, BH)}</g>'
            + f'<g class="fl">{flat_markup(flare_cells(), None, BW, BH)}</g>')
    css = BANNER_CSS.replace("%FX%", str(FLARE_AT[0] * CELL + 2)).replace("%FY%", str(FLARE_AT[1] * CELL + 2))
    return svg_doc(BW, BH, body, css, "Foma Skills. Skills that ask first. A tiny cat on the rim of a giant rust planet.")


# ================================================================ BUTTONS
PW, PH = 70, 21
KEY = dict(x=5, y=5, w=58, h=11)               # key body (the outline sits 1 cell outside, the shadow 1 more)

ROCKET = [
    "....K....", "...KWK...", "..KWWwK..", "..KWBwK..", "..KWWwK..", ".KKWWwKK.", "KDKWWwKDK", "KDDKKKDDK", "...fFf...",
]
ROCKET_LEG = dict(K=R0, W=L3, w=L2, B=BLUE, D=R2, f=L1, F=L2)
STAR_ICON = [
    "....#....", "...###...", "...###...", "#########", ".#######.", "..#####..", "..#####..", ".###.###.", ".##...##.",
]
GRAPH_NODES = [(1, 2), (4, 7), (7, 1)]    # a triangle of three nodes; the last one is the live node
GRAPH_EDGES = [(0, 1), (1, 2), (2, 0)]


def line_cells(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0))
    return {(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)}


def plus(x, y):
    return {(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}


def paint_key(cv, style):
    """Chamfered key with outline, 1-cell bevel and shadow, seated in a dark well with a lit lip (pressed in)."""
    x, y, w, h = KEY["x"], KEY["y"], KEY["w"], KEY["h"]
    shape = chamfer(box(x, y, x + w, y + h), 2)
    outer = shape | dilate4(shape)
    shadow = stepped_shadow(outer, 1)
    well = dilate4(outer | shadow) | dilate4(dilate4(outer | shadow))
    cv.paint(well, BG)
    cv.paint({(a, b) for (a, b) in well if a > x + w + 1 or b > y + h + 1}, S3)
    cv.paint(shadow, style["shadow"])
    cv.paint(outer - shape, style["outline"])
    lt, face, dk = bevel(shape)
    cv.paint(face, style["face"])
    cv.paint(lt, style["light"])
    cv.paint(dk, style["dark"])


def panel_base(seed):
    cv = Canvas(PW, PH)
    cv.paint(box(0, 0, PW, PH), S1)
    cv.paint(box(1, 1, PW - 1, 2) | box(1, 1, 2, PH - 1), CLOAK)           # inner highlight, top and left
    cv.paint(box(PW - 2, 2, PW - 1, PH - 1) | box(2, PH - 2, PW - 1, PH - 1), S2)
    cv.frame(S3)
    rng = random.Random(seed)
    spots = [(x, 2) for x in range(4, PW - 3)] + [(2, y) for y in range(3, PH - 3)]
    spots += [(x, y) for x in (PW - 4, PW - 3) for y in range(2, PH - 3)]
    rng.shuffle(spots)
    placed = []
    for (x, y) in spots:
        if len(placed) < 9 and all(abs(x - u) + abs(y - v) > 5 for u, v in placed):
            placed.append((x, y))
            cv.put(x, y, rng.choice([CLOAK, CLOAK, BLUE, PALE, GREY]))
    return cv


def content_x(icon_w, label, gap):
    """x of the icon and of the label so [icon, gap, label] is centred in the key face."""
    face_l, face_r = KEY["x"] + 1, KEY["x"] + KEY["w"] - 1
    x = face_l + (face_r - face_l - (icon_w + gap + small_width(label))) // 2
    return x, x + icon_w + gap


def paint_icon(cv, rows, legend, x, y):
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in legend:
                cv.put(x + c, y + r, legend[ch])


PRIMARY = dict(face=R3, light=L1, dark=R2, outline=R0, shadow=R0)
SECONDARY = dict(face=S2, light=S3, dark=S1, outline=BLUE, shadow=BG)

BTN_CSS = """
.sh{opacity:0;animation:sw 6s steps(1,end) infinite}
.sh>g{animation:sx 6s steps(24,end) infinite}
@keyframes sw{0%,76%{opacity:0}77%,99%{opacity:1}100%{opacity:0}}
@keyframes sx{0%,76%{transform:translateX(0)}100%{transform:translateX(%SW%px)}}
.dot{animation:bl 2s steps(1,end) infinite}
@keyframes bl{0%{opacity:1}60%{opacity:.15}100%{opacity:1}}
.tw{animation:tq 3.4s steps(2,end) infinite}
@keyframes tq{0%{opacity:1}50%{opacity:.35}100%{opacity:1}}
@media (prefers-reduced-motion:reduce){.sh,.sh>g,.dot,.tw{animation:none}}
"""


def build_button(kind):
    cv = panel_base({"install": 1, "map": 2, "star": 3}[kind])
    primary = kind == "install"
    paint_key(cv, PRIMARY if primary else SECONDARY)
    label = {"install": "INSTALL", "map": "LIVE MAP", "star": "STAR"}[kind]
    ix, lx = content_x(9, label, 3)
    ft = KEY["y"] + 1                                          # first face row, below the light rim
    overlay = shine = ""
    css = BTN_CSS.replace("%SW%", "0")
    if kind == "install":
        paint_icon(cv, ROCKET, ROCKET_LEG, ix, ft)
        fl, fr = KEY["x"] + 1, KEY["x"] + KEY["w"] - 1
        diag = {(fl + 8 - i, ft + i) for i in range(9)}        # one 1-cell diagonal glint over the key face
        shine = f'<g class="sh"><g>{flat_markup({L2: diag}, None, PW, PH)}</g></g>'
        css = BTN_CSS.replace("%SW%", str((fr - fl - 10) * CELL))
    elif kind == "map":
        for a, b in GRAPH_EDGES:
            cv.paint({(ix + x, ft + y) for (x, y) in line_cells(*GRAPH_NODES[a], *GRAPH_NODES[b])}, BLUE)
        for i, (nx, ny) in enumerate(GRAPH_NODES[:-1]):
            cv.paint({(ix + x, ft + y) for (x, y) in plus(nx, ny)}, PALE)
        lx_, ly_ = GRAPH_NODES[-1]
        overlay = f'<g class="dot">{flat_markup({GREEN: {(ix + x, ft + y) for (x, y) in plus(lx_, ly_)}}, None, PW, PH)}</g>'
    else:
        pts = [(ix + c, ft + r) for r, row in enumerate(STAR_ICON) for c, ch in enumerate(row) if ch == "#"]
        overlay = f'<g class="tw">{flat_markup({L2: pts}, None, PW, PH)}</g>'
    lcells, _ = small_text_cells(label, lx, ft + 1)
    cv.paint(shift(lcells, 1, 1) - lcells, R0 if primary else BG)
    cv.paint(lcells, L3 if primary else PALE)
    body = f'<rect width="{PW * CELL}" height="{PH * CELL}" fill="{BG}"/>' + static_markup(cv) + overlay + shine
    return svg_doc(PW, PH, body, css, {"install": "Install", "map": "Live map", "star": "Star"}[kind])


# ================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=OUT_DIR, help="output directory (default docs/assets/profile)")
    out = ap.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    files = {"banner.svg": build_banner(), "btn-install.svg": build_button("install"),
             "btn-map.svg": build_button("map"), "btn-star.svg": build_button("star")}
    for name, svg in files.items():
        (out / name).write_text(svg, encoding="utf-8")
        print(f"{name}: {len(svg.encode()) / 1024:.1f} KB, {count_rects(svg)} rects")


if __name__ == "__main__":
    main()
