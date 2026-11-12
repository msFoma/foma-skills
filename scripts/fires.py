#!/usr/bin/env python3
"""Count how often each pack skill fired (IDEA-128). Free: reads a local log only.

Usage: python3 scripts/fires.py [log ...] [--days N]
Default log: .scratch/fires.jsonl in the current project; pass several logs to merge projects.
Log lines are written by plugins/foma-skills/hooks/fire-log.sh: a fire {"t", "skill", "session"} or a
session start {"t", "event": "start", "session"}; the starts are the denominator ("fired in 9 of 24 sessions").
Pack skills with zero fires are listed last: candidates for pruning once the log spans about 20 sessions.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "plugins/foma-skills/skills"


def read_log(paths, days=None):
    """Return (fires [(time, skill, session)], started session ids); only the last `days` if set; bad lines skipped."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days else None
    rows, started = [], set()
    for path in paths:
        if not Path(path).is_file():
            continue
        for line in Path(path).read_text().splitlines():
            try:
                row = json.loads(line)
                when = datetime.strptime(row["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if row.get("event") == "start":
                    skill = None
                else:
                    skill = row["skill"].removeprefix("foma-skills:")
            except (ValueError, KeyError, AttributeError):
                continue
            if cutoff is not None and when < cutoff:
                continue
            if skill is None:
                started.add(row.get("session", ""))
            else:
                rows.append((when, skill, row.get("session", "")))
    return rows, started


def summary(rows, pack, total=None):
    """Lines: skill, fires, sessions it fired in (of `total` started), last fire; unfired pack skills at the end."""
    counts = Counter(s for _, s, _ in rows)
    sessions = {s: {sess for _, sk, sess in rows if sk == s} for s in counts}
    last = {s: max(t for t, sk, _ in rows if sk == s) for s in counts}
    of = f" of {total}" if total else ""
    lines = [f"{s:18} {n:4} fires in {len(sessions[s]):3}{of} sessions  last {last[s]:%Y-%m-%d}"
             for s, n in counts.most_common() if s in pack]
    lines += [f"{s:18}    0 fires" for s in sorted(pack - set(counts))]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="*", default=[".scratch/fires.jsonl"])
    ap.add_argument("--days", type=int)
    args = ap.parse_args()
    rows, started = read_log(args.logs, args.days)
    total = len(started | {r[2] for r in rows})  # a log from before the start events still counts fired sessions
    print(f"{len(rows)} fires, {total} sessions" + ("" if total >= 20 else " (under 20: too few to judge a zero)"))
    print("\n".join(summary(rows, {p.name for p in SKILLS.iterdir() if p.is_dir()}, total)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
