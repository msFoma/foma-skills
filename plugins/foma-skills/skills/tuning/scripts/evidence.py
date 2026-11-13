#!/usr/bin/env python3
"""Free evidence for the `tuning` skill: what in the pack is not working. Reads local files only.

Usage: python3 evidence.py [--days N] [--log .scratch/fires.jsonl] [--runs tests/.runs]
Prints: the mode (repo = the pack's own repository, project = anything else), fire counts
(fires.py) and, in repo mode, tasks whose recent saved runs fail or flake (tests/.runs/<task>/*.json).
A run older than the last edit of its skill's files is ignored (the skill changed since) and listed apart.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fires  # noqa: E402

MIN_SESSIONS = 20  # below this a zero says nothing
LAST = 5  # recent runs per task


def is_repo(root="."):
    root = Path(root)
    return (root / "scripts/trigger_test.py").is_file() and (root / "plugins/foma-skills").is_dir()


def fire_lines(log, days, pack):
    rows, started = fires.read_log([log], days)
    total = len(started | {r[2] for r in rows})
    if not total:
        return ["fire log: none (.scratch/fires.jsonl is missing or empty)"]
    counts = {}
    for _, skill, session in rows:
        counts.setdefault(skill, set()).add(session)
    top = ", ".join(f"{s} {len(v)}/{total}" for s, v in sorted(counts.items(), key=lambda kv: -len(kv[1])) if s in pack)
    lines = [f"fire log: {total} sessions, {len(rows)} fires. Fired in sessions: {top or 'none'}"]
    never = sorted(pack - set(counts))
    if total >= MIN_SESSIONS:
        lines.append(f"NEVER fired ({len(never)}): {', '.join(never)}" if never else "every pack skill fired at least once")
    else:
        lines.append(f"log too short ({total} < {MIN_SESSIONS} sessions): no zero is meaningful yet")
    return lines


def verdict(record):
    """True/False, or None when the run is not a verdict (no agent output, usage limit, not judged)."""
    if record.get("reason", "").startswith(("NORUN", "LIMIT")) or record.get("marks") is None:
        return None
    items = record.get("checks", []) + record["marks"]  # old records have no "checks"
    return bool(items) and all(items)


def skill_for_task(task, pack):
    """The pack skill a task file tests: the longest skill name that is the task name or its prefix."""
    names = [s for s in pack if task == s or task.startswith(s + "-")]
    return max(names, key=len) if names else None


def changed_at(skills_dir, skill):
    """Latest modification time of the skill's files (0 if the folder is missing)."""
    files = [p.stat().st_mtime for p in (Path(skills_dir) / skill).rglob("*") if p.is_file()]
    return max(files, default=0)


def run_time(path):
    """Time of a saved run from its file name YYYYMMDD-HHMMSS-..., or 0."""
    try:
        return time.mktime(time.strptime(path.name[:15], "%Y%m%d-%H%M%S"))
    except ValueError:
        return 0


def run_history(runs_dir, skills_dir=None, last=LAST, limit=8):
    """Lines for tasks whose last `last` verdicts are not all PASS (newest run decides 'failing now').

    With skills_dir: tasks that test no pack skill are skipped, and runs older than the skill's last edit
    are ignored; a task left with no newer run is listed in a final line.
    """
    out, stale = [], []
    pack = {p.name for p in Path(skills_dir).iterdir() if p.is_dir()} if skills_dir else None
    for task in sorted(Path(runs_dir).glob("*/")):
        paths = sorted(task.glob("*.json"))
        if pack is not None:
            skill = skill_for_task(task.name, pack)
            if skill is None:
                continue
            fresh = [p for p in paths if run_time(p) > changed_at(skills_dir, skill)]
            if paths and not fresh:
                stale.append(task.name)
            paths = fresh
        records = []
        for path in paths[-last * 2:]:
            try:
                records.append(json.loads(path.read_text()))
            except (OSError, ValueError):
                continue
        verdicts = [(r, verdict(r)) for r in records if verdict(r) is not None][-last:]
        if not verdicts or all(v for _, v in verdicts):
            continue
        passed = sum(v for _, v in verdicts)
        state = "FAILING now" if not verdicts[-1][1] else "flaky"
        fails = [r for r, v in verdicts if not v]
        reason = fails[-1].get("reason", "").replace("\n", " ")[:160]
        out.append((state != "FAILING now", f"{state} {task.name} {passed}/{len(verdicts)} recent; last fail: {reason}"))
    out.sort()
    lines = [line for _, line in out][:limit] or ["saved task runs: none failing in the last %d" % last]
    if stale:
        lines.append("older than the skill's last edit, ignored (rerun the smoke to judge): " + ", ".join(stale))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int)
    ap.add_argument("--log", default=".scratch/fires.jsonl")
    ap.add_argument("--runs", default="tests/.runs")
    args = ap.parse_args()
    pack = {p.name for p in fires.SKILLS.iterdir() if p.is_dir()}
    repo = is_repo()
    print("mode: " + ("repo (pack sources and test scripts found)" if repo else "project (pack files are read-only)"))
    print("\n".join(fire_lines(args.log, args.days, pack)))
    if repo and Path(args.runs).is_dir():
        print("\n".join(run_history(args.runs, fires.SKILLS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
