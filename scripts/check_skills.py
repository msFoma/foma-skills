#!/usr/bin/env python3
"""Static checks for foma-skills (docs/lite-standard.md §9). Stdlib only.

Usage: python3 scripts/check_skills.py [skills_dir]
Exit 1 on any failure.
"""
import re
import sys
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parent.parent / "plugins/foma-skills/skills"

ALLOWED_KEYS = {"name", "description", "license", "metadata", "allowed-tools",
                "disable-model-invocation", "effort"}
REQUIRED_KEYS = {"name", "description", "license", "metadata"}
METADATA_KEYS = {"level", "uses", "agents", "tokens"}
LEVELS = {"setup", "process", "method", "atomic", "meta"}
USES_ALLOWED = {"process": {"method", "atomic"}, "method": {"atomic"},
                "setup": set(), "atomic": set(), "meta": set()}
AGENT_LEVELS = {"process", "method"}
READ_ONLY_TOOLS = {"Read", "Grep", "Glob"}
FORBIDDEN_FILES = {"README.md", "CHANGELOG.md", "examples"}

DESC_MAX_CHARS = 250
CORE_CAP = {"model": 800, "manual": 1200}
REFERENCE_CAP = 1000
PACK_CAP = 1200
DRIFT = 0.10


def tokens(text):
    return round(len(text) / 4)


def parse_scalar(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1], True
    return raw, False


def parse_frontmatter(text):
    """Parse the restricted YAML subset the standard allows.

    Returns (fields, body, quoted) where quoted maps metadata keys to
    whether their value was a quoted string. Raises ValueError.
    """
    if not text.startswith("---\n"):
        raise ValueError("no frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    lines = text[4:end].split("\n")
    body = text[end + 5:]
    fields, quoted = {}, {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z][\w-]*):(.*)$", line)
        if not m:
            raise ValueError(f"cannot parse line: {line!r}")
        key, rest = m.group(1), m.group(2).strip()
        if key in fields:
            raise ValueError(f"duplicate key: {key}")
        i += 1
        block = []
        while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
            block.append(lines[i])
            i += 1
        if rest in (">-", ">", "|", "|-"):
            sep = " " if rest.startswith(">") else "\n"
            fields[key] = sep.join(b.strip() for b in block if b.strip())
        elif rest == "":
            items = [b.strip() for b in block if b.strip()]
            if items and all(b.startswith("- ") for b in items):
                fields[key] = [parse_scalar(b[2:])[0] for b in items]
            else:
                mapping = {}
                for b in items:
                    mm = re.match(r"^([A-Za-z][\w-]*):(.*)$", b)
                    if not mm:
                        raise ValueError(f"cannot parse {key} entry: {b!r}")
                    val, q = parse_scalar(mm.group(2))
                    mapping[mm.group(1)] = val
                    quoted[mm.group(1)] = q
                fields[key] = mapping
        else:
            if block and any(b.strip() for b in block):
                raise ValueError(f"unexpected indented lines after {key}")
            fields[key] = parse_scalar(rest)[0]
    return fields, body, quoted


def check_skill(folder, errors):
    """Check one skill folder. Returns (name, info) for pack-level checks."""
    def err(msg):
        errors.append(f"{folder.name}: {msg}")

    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        err("missing SKILL.md")
        return None
    try:
        fm, body, quoted = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    except ValueError as e:
        err(f"frontmatter: {e}")
        return None

    for key in sorted(set(fm) - ALLOWED_KEYS):
        err(f"key not allowed: {key}")
    for key in sorted(REQUIRED_KEYS - set(fm)):
        err(f"missing key: {key}")

    if fm.get("name") != folder.name:
        err(f"name {fm.get('name')!r} != folder name")
    if fm.get("license") != "Apache-2.0":
        err("license must be Apache-2.0")

    manual = "disable-model-invocation" in fm
    if manual and fm["disable-model-invocation"] != "true":
        err("disable-model-invocation must be true when present")

    desc = fm.get("description", "")
    if not isinstance(desc, str) or not desc:
        err("description must be a non-empty string")
        desc = ""
    if len(desc) > DESC_MAX_CHARS:
        err(f"description {len(desc)} chars > {DESC_MAX_CHARS}")
    if re.search(r"<[A-Za-z/]", desc):
        err("description contains XML-like tags")

    tools = fm.get("allowed-tools")
    if tools is not None:
        names = tools if isinstance(tools, list) else re.split(r"[,\s]+", tools.strip())
        bad = [t for t in names if t and t not in READ_ONLY_TOOLS]
        if bad:
            err(f"allowed-tools not read-only: {' '.join(bad)}")

    meta = fm.get("metadata", {})
    if not isinstance(meta, dict):
        err("metadata must be a mapping")
        meta = {}
    for key in sorted(set(meta) - METADATA_KEYS):
        err(f"metadata key not allowed: {key}")
    for key in sorted(METADATA_KEYS - set(meta)):
        err(f"missing metadata key: {key}")
    for key in sorted(METADATA_KEYS & set(meta)):
        if not quoted.get(key):
            err(f"metadata.{key} must be a quoted string")
    level = meta.get("level", "")
    if level not in LEVELS:
        err(f"metadata.level {level!r} not in {sorted(LEVELS)}")

    core = tokens(body)
    cap = CORE_CAP["manual" if manual else "model"]
    if core > cap:
        err(f"core {core} tokens > cap {cap}")
    declared = meta.get("tokens", "")
    if not declared.isdigit():
        err(f"metadata.tokens {declared!r} is not a number")
    elif core and abs(int(declared) - core) / core > DRIFT:
        err(f"metadata.tokens {declared} drifts >10% from measured {core}")

    for item in folder.iterdir():
        if item.name in FORBIDDEN_FILES:
            err(f"not allowed in a skill: {item.name}")

    refs_dir = folder / "references"
    if refs_dir.exists():
        refs = sorted(refs_dir.iterdir())
        ref_names = {r.name for r in refs}
        branch_lines = [l for l in body.splitlines() if l.strip().startswith("If ")]
        for ref in refs:
            if ref.is_dir():
                err(f"references/{ref.name}: nested folders not allowed")
                continue
            if ref.suffix != ".md":
                err(f"references/{ref.name}: only .md files")
                continue
            if not any(f"references/{ref.name}" in l for l in branch_lines):
                err(f"references/{ref.name} not linked by an 'If …' line")
            text = ref.read_text(encoding="utf-8")
            if tokens(text) > REFERENCE_CAP:
                err(f"references/{ref.name}: {tokens(text)} tokens > cap {REFERENCE_CAP}")
            for other in ref_names - {ref.name}:
                if other in text:
                    err(f"references/{ref.name} links another reference ({other})")

    return fm.get("name", folder.name), {
        "level": level,
        "uses": meta.get("uses", "").split(),
        "agents": meta.get("agents", "").split(),
        "manual": manual,
        "desc_tokens": tokens(desc),
    }


def check_pack(skills_dir):
    errors = []
    skills = {}
    folders = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    for folder in folders:
        result = check_skill(folder, errors)
        if result:
            skills[result[0]] = result[1]

    agents = {p.stem for p in skills_dir.glob("*/assets/agents/*.md")}
    # Agent drafts until groundwork ships them as assets (DEC-025).
    agents |= {p.stem for p in (skills_dir.parent.parent.parent / "docs/agents").glob("*.md")}
    for name, info in skills.items():
        allowed = USES_ALLOWED.get(info["level"], set())
        for target in info["uses"]:
            if target not in skills:
                errors.append(f"{name}: uses unknown skill {target!r}")
            elif skills[target]["level"] not in allowed:
                errors.append(f"{name}: {info['level']} may not use "
                              f"{skills[target]['level']} skill {target!r}")
        if info["agents"] and info["level"] not in AGENT_LEVELS:
            errors.append(f"{name}: {info['level']} skills may not use agents")
        for agent in info["agents"]:
            if agent not in agents:
                errors.append(f"{name}: agent {agent!r} has no assets/agents/{agent}.md")

    total = sum(i["desc_tokens"] for i in skills.values() if not i["manual"])
    if total > PACK_CAP:
        errors.append(f"pack always-on {total} tokens > cap {PACK_CAP}")
    return errors, len(skills), total


def main():
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    errors, count, total = check_pack(skills_dir)
    for e in errors:
        print(f"FAIL {e}")
    print(f"{count} skills, always-on {total} tokens, {len(errors)} failures")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
