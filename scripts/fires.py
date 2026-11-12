#!/usr/bin/env python3
"""Count how often each pack skill fired (IDEA-128). Free: reads a local log only.

Usage: python3 scripts/fires.py [log ...] [--days N]
Default log: .scratch/fires.jsonl in the current project; pass several logs to merge projects.
Log lines are written by plugins/foma-skills/hooks/fire-log.sh: {"t": ISO UTC, "skill": ..., "session": ...}.
Pack skills with zero fires are listed last: candidates for pruning once the log spans enough sessions.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "plugins/foma-skills/skills"


def read_fires(paths, days=None):
    """Return [(time, skill, session)] from the logs, newest window only if days is set; bad lines skipped."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days else None
    rows = []
    for path in paths:
        if not Path(path).is_file():
            continue
        for line in Path(path).read_text().splitlines():
            try:
                row = json.loads(line)
                when = datetime.strptime(row["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                skill = row["skill"].removeprefix("foma-skills:")
            except (ValueError, KeyError, AttributeError):
                continue
            if cutoff is None or when >= cutoff:
                rows.append((when, skill, row.get("session", "")))
    return rows


def summary(rows, pack):
    """Lines: skill, fires, sessions, last fire; pack skills never fired at the end."""
    counts = Counter(s for _, s, _ in rows)
    sessions = {s: {sess for _, sk, sess in rows if sk == s} for s in counts}
    last = {s: max(t for t, sk, _ in rows if sk == s) for s in counts}
    lines = [f"{s:18} {n:4} fires {len(sessions[s]):3} sessions  last {last[s]:%Y-%m-%d}"
             for s, n in counts.most_common() if s in pack]
    lines += [f"{s:18}    0 fires" for s in sorted(pack - set(counts))]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="*", default=[".scratch/fires.jsonl"])
    ap.add_argument("--days", type=int)
    args = ap.parse_args()
    rows = read_fires(args.logs, args.days)
    print(f"{len(rows)} fires, {len({r[2] for r in rows})} sessions")
    print("\n".join(summary(rows, {p.name for p in SKILLS.iterdir() if p.is_dir()})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
