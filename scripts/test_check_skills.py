"""Tests for check_skills.py. Run: python3 -m unittest scripts/test_check_skills.py"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_skills  # noqa: E402

BODY = "Checks things.\n\n## Steps\n1. Do it.\n"


def skill_md(name="alpha", desc="Does alpha. Use when the user asks for alpha.",
             level="atomic", uses="", agents="", tokens=None, extra="", body=BODY):
    if tokens is None:
        tokens = str(check_skills.tokens(body))
    return (f"---\nname: {name}\ndescription: >-\n  {desc}\nlicense: Apache-2.0\n{extra}"
            f"metadata:\n  level: \"{level}\"\n  uses: \"{uses}\"\n  agents: \"{agents}\"\n"
            f"  tokens: \"{tokens}\"\n---\n{body}")


class CheckSkillsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, folder, text, files=None):
        path = self.dir / folder
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(text)
        for rel, content in (files or {}).items():
            f = path / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content)

    def errors(self):
        return check_skills.check_pack(self.dir)[0]

    def test_valid_skill_passes(self):
        self.add("alpha", skill_md())
        self.assertEqual(self.errors(), [])

    def test_name_must_match_folder(self):
        self.add("alpha", skill_md(name="beta"))
        self.assertTrue(any("folder name" in e for e in self.errors()))

    def test_unknown_key_fails(self):
        self.add("alpha", skill_md(extra="model: opus\n"))
        self.assertTrue(any("key not allowed: model" in e for e in self.errors()))

    def test_long_description_fails(self):
        self.add("alpha", skill_md(desc="x" * 251))
        self.assertTrue(any("251 chars" in e for e in self.errors()))

    def test_unquoted_metadata_fails(self):
        self.add("alpha", skill_md().replace('level: "atomic"', "level: atomic"))
        self.assertTrue(any("metadata.level must be a quoted" in e for e in self.errors()))

    def test_token_drift_fails(self):
        self.add("alpha", skill_md(tokens="1"))
        self.assertTrue(any("drifts" in e for e in self.errors()))

    def test_core_cap_fails(self):
        body = "x" * 6100
        self.add("alpha", skill_md(body=body))
        self.assertTrue(any("cap 1500" in e for e in self.errors()))

    def test_core_under_cap_passes(self):
        body = "x" * 5900
        self.add("alpha", skill_md(body=body, extra="disable-model-invocation: true\n"))
        self.assertEqual(self.errors(), [])

    def test_write_tool_not_allowed(self):
        self.add("alpha", skill_md(extra="allowed-tools: Read Write\n"))
        self.assertTrue(any("not read-only: Write" in e for e in self.errors()))

    def test_unlinked_reference_fails(self):
        self.add("alpha", skill_md(), {"references/extra.md": "More."})
        self.assertTrue(any("not linked" in e for e in self.errors()))

    def test_linked_reference_passes(self):
        body = BODY + "\nIf it is big, read `references/extra.md`.\n"
        self.add("alpha", skill_md(body=body), {"references/extra.md": "More."})
        self.assertEqual(self.errors(), [])

    def test_reference_linking_reference_fails(self):
        body = BODY + "\nIf a, read `references/a.md`.\nIf b, read `references/b.md`.\n"
        self.add("alpha", skill_md(body=body),
                 {"references/a.md": "See b.md.", "references/b.md": "B."})
        self.assertTrue(any("links another reference" in e for e in self.errors()))

    def test_uses_must_point_down(self):
        self.add("alpha", skill_md(uses="beta"))
        self.add("beta", skill_md(name="beta", level="process"))
        self.assertTrue(any("atomic may not use process" in e for e in self.errors()))

    def test_process_may_use_atomic(self):
        self.add("alpha", skill_md(level="process", uses="beta"))
        self.add("beta", skill_md(name="beta"))
        self.assertEqual(self.errors(), [])

    def test_unknown_agent_fails(self):
        self.add("alpha", skill_md(level="process", agents="implementer"))
        self.assertTrue(any("agent 'implementer'" in e for e in self.errors()))

    def test_pack_cap_counts_model_skills_only(self):
        long_desc = "y" * 240
        for i in range(21):
            n = f"s{i:02d}"
            self.add(n, skill_md(name=n, desc=long_desc))
        self.assertTrue(any("pack always-on" in e for e in self.errors()))

    def test_broken_frontmatter_fails(self):
        self.add("alpha", "no frontmatter here")
        self.assertTrue(any("frontmatter" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
