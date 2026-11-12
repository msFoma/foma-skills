#!/usr/bin/env python3
"""Trigger test for one skill (docs/lite-standard.md §8.1–8.2). Costs model usage.

Usage: python3 scripts/trigger_test.py <skill> [--runs N] [--model sonnet] [--only +|-]

Cases: tests/triggers/<skill>.txt, one prompt per line:
  + prompt that must fire the skill
  - prompt that must not fire it
Each run uses a fresh copy of tests/fixture/ as the project and loads only
plugins/foma-skills. User settings and plugins are skipped (--setting-sources
project) and the user's ~/.claude/CLAUDE.md is excluded (claudeMdExcludes),
because --setting-sources alone still loads it.
A run stops at the first Skill call or after MAX_TOOL_CALLS other tool calls.
"""
import argparse
import json
import os
import signal
import shutil
import threading
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins/foma-skills"
FIXTURE = ROOT / "tests/fixture"
MAX_TOOL_CALLS = 4
TIMEOUT_S = 180


def load_cases(skill):
    cases = []
    for line in (ROOT / f"tests/triggers/{skill}.txt").read_text().splitlines():
        line = line.strip()
        if line[:2] in ("+ ", "- "):
            cases.append((line[0] == "+", line[2:]))
    return cases


def run_once(prompt, model):
    """Return (skills_called, tool_calls, seconds)."""
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(FIXTURE, project)
        cmd = ["claude", "-p", prompt, "--model", model,
               "--plugin-dir", str(PLUGIN), "--setting-sources", "project",
               "--output-format", "stream-json", "--verbose",
               "--settings", json.dumps({"claudeMdExcludes": [str(Path.home() / ".claude/CLAUDE.md")]}),
               "--no-session-persistence"]
        start = time.time()
        proc = subprocess.Popen(cmd, cwd=project, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                start_new_session=True)

        def kill_group():
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:  # group already gone (macOS may report EPERM)
                proc.kill()

        watchdog = threading.Timer(TIMEOUT_S, kill_group)
        watchdog.start()
        skills, tools = [], 0
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") != "assistant":
                    continue
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") != "tool_use":
                        continue
                    if block.get("name") == "Skill":
                        skills.append(block.get("input", {}).get("skill", "?"))
                    else:
                        tools += 1
                if skills or tools >= MAX_TOOL_CALLS:
                    break
        finally:
            watchdog.cancel()
            kill_group()
            proc.wait()
        return skills, tools, time.time() - start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--only", choices=["+", "-"])
    args = ap.parse_args()

    target = f"foma-skills:{args.skill}"
    cases = load_cases(args.skill)
    if args.only:
        cases = [c for c in cases if c[0] == (args.only == "+")]
    passed = total = 0
    for must_fire, prompt in cases:
        for _ in range(args.runs):
            skills, tools, secs = run_once(prompt, args.model)
            fired = any(s in (target, args.skill) for s in skills)
            ok = fired == must_fire
            passed += ok
            total += 1
            mark = "PASS" if ok else "FAIL"
            print(f"{mark} {'+' if must_fire else '-'} {prompt[:70]!r} "
                  f"skills={skills or '-'} tools={tools} {secs:.0f}s", flush=True)
    print(f"{passed}/{total} passed ({args.model})")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
