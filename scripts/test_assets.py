"""Invariants of the pixel-art profile banner (scripts/assets/make_profile_banner.py, DEC-045). Free, stdlib only.

Run: python3 -m unittest scripts/test_assets.py
"""
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "assets"))
import make_profile_banner as mpb  # noqa: E402

CELL = 4
PALETTE = {  # the 16 approved colours plus the single green status dot
    "#07060b", "#0e0b14", "#171226", "#241c3a", "#3b1710", "#6e2f1c", "#a8512f", "#e8714a",
    "#ffb27a", "#ffe3cc", "#fff4ea", "#f1e2cf", "#9b95a8", "#4a4560", "#86b2f2", "#c9d3ff",
    "#5fd38d",
}
FORBIDDEN_TAGS = {"image", "filter", "text", "foreignObject", "linearGradient", "radialGradient", "script", "a"}
SIZES = {"banner": (840, 380, 120_000), "install": (280, 84, 40_000), "map": (280, 84, 40_000), "star": (280, 84, 40_000)}


def tag(el):
    return el.tag.rsplit("}", 1)[-1]


class ProfileBannerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.svgs = {"banner": mpb.build_banner(), **{k: mpb.build_button(k) for k in ("install", "map", "star")}}
        cls.roots = {k: ET.fromstring(v) for k, v in cls.svgs.items()}

    def test_deterministic(self):
        self.assertEqual(self.svgs["banner"], mpb.build_banner())
        self.assertEqual(self.svgs["map"], mpb.build_button("map"))

    def test_size_and_viewbox(self):
        for name, (w, h, cap) in SIZES.items():
            with self.subTest(name):
                self.assertEqual(self.roots[name].get("viewBox"), f"0 0 {w} {h}")
                self.assertLessEqual(len(self.svgs[name].encode()), cap)

    def test_every_rect_sits_on_the_grid(self):
        for name, root in self.roots.items():
            for r in root.iter():
                if tag(r) != "rect":
                    continue
                for attr in ("x", "y", "width", "height"):
                    v = float(r.get(attr, 0))
                    self.assertEqual(v % CELL, 0, f"{name}: rect {attr}={v}")

    def test_palette_only(self):
        for name, svg in self.svgs.items():
            used = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", svg)}
            self.assertGreater(len(used), 5, name)  # guards against a vacuous pass
            self.assertLessEqual(used - PALETTE, set(), name)

    def test_no_forbidden_elements_or_links(self):
        for name, root in self.roots.items():
            tags = {tag(e) for e in root.iter()}
            self.assertEqual(tags & FORBIDDEN_TAGS, set(), name)
            for e in root.iter():
                for attr in e.attrib:
                    self.assertFalse(attr.endswith("href"), f"{name}: {attr}")

    def test_only_transform_and_opacity_animate_and_reduced_motion_is_honoured(self):
        for name, svg in self.svgs.items():
            props = set()
            for m in re.finditer(r"@keyframes\s+[\w-]+\s*\{((?:[^{}]|\{[^{}]*\})*)\}", svg):
                props |= set(re.findall(r"([\w-]+)\s*:", m.group(1)))
            self.assertLessEqual(props, {"transform", "opacity"}, name)
            if props:
                self.assertIn("prefers-reduced-motion", svg, name)


if __name__ == "__main__":
    unittest.main()
