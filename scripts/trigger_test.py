#!/usr/bin/env python3
"""Trigger test for one skill (docs/lite-standard.md §8.1–8.2, DEC-024). Costs model usage.

Usage: python3 scripts/trigger_test.py <skill> [--models haiku] [--recheck sonnet] [--runs N] [--only +|-]
Default (DEC-029): every prompt on Haiku; failed prompts are re-run once on the
--recheck model to tell a Haiku weakness from a description problem.

Cases: tests/triggers/<skill>.txt, one prompt per line:
  + prompt that must fire the skill
  - prompt that must not fire it
  @fixture <name>   (optional directive; default: calc)
Each prompt runs N times on every model. A run stops at the first Skill call
or after MAX_TOOL_CALLS other tool calls.
"""
import argparse
import sys

import claude_run as cr

MAX_TOOL_CALLS = 4


def load_cases(skill, subdir=""):
    fixture, cases = "calc", []
    for line in (cr.ROOT / "tests/triggers" / subdir / f"{skill}.txt").read_text().splitlines():
        line = line.strip()
        if line.startswith("@fixture "):
            fixture = line.split(None, 1)[1]
        elif line[:2] in ("+ ", "- "):
            cases.append((line[0] == "+", line[2:]))
    return fixture, cases


def run_once(prompt, model, fixture):
    """Return (skills_called, other_tool_calls, seconds)."""
    def stop(events):
        uses = list(cr.tool_uses(events))
        return any(u.get("name") == "Skill" for u in uses) or len(uses) >= MAX_TOOL_CALLS

    with cr.new_tmp() as tmp:
        project = cr.fixture_copy(fixture, tmp)
        events, secs, _ = cr.run(cr.base_cmd(prompt, model), project, stop=stop)
    uses = list(cr.tool_uses(events))
    skills = [u.get("input", {}).get("skill", "?") for u in uses if u.get("name") == "Skill"]
    return skills, len(uses) - len(skills), secs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill")
    ap.add_argument("--models", default="haiku")
    ap.add_argument("--recheck", default="sonnet", help="model for failed prompts; '' to skip")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--only", choices=["+", "-"])
    ap.add_argument("--set", default="", help="subfolder of tests/triggers, e.g. heldout (frozen unseen prompts)")
    args = ap.parse_args()

    skill_md = cr.PLUGIN / f"skills/{args.skill}/SKILL.md"
    if "disable-model-invocation: true" in skill_md.read_text().split("---", 2)[1]:
        print(f"{args.skill}: manual skill, no trigger test (DEC-026)")
        return 0
    target = f"foma-skills:{args.skill}"
    fixture, cases = load_cases(args.skill, args.set)
    if args.only:
        cases = [c for c in cases if c[0] == (args.only == "+")]
    totals, results = {}, []
    for must_fire, prompt in cases:
        for model in args.models.split(","):
            for _ in range(args.runs):
                skills, tools, secs = run_once(prompt, model, fixture)
                ok = (target in skills or args.skill in skills) == must_fire
                p, t = totals.get(model, (0, 0))
                totals[model] = (p + ok, t + 1)
                results.append((must_fire, prompt, ok))
                print(f"{'PASS' if ok else 'FAIL'} {model:6} {'+' if must_fire else '-'} "
                      f"{prompt[:64]!r} skills={skills or '-'} tools={tools} {secs:.0f}s", flush=True)
    failed = [(f, pr) for f, pr, ok in results if not ok]
    if args.recheck and failed:
        p = 0
        for must_fire, prompt in failed:
            skills, tools, secs = run_once(prompt, args.recheck, fixture)
            ok = (target in skills or args.skill in skills) == must_fire
            p += ok
            print(f"{'PASS' if ok else 'FAIL'} {args.recheck:6} {'+' if must_fire else '-'} "
                  f"{prompt[:64]!r} skills={skills or '-'} (recheck)", flush=True)
        totals[f"{args.recheck} recheck"] = (p, len(failed))
    print(f"{args.skill}: " + ", ".join(f"{m} {p}/{t}" for m, (p, t) in totals.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
