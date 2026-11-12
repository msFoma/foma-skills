"""Run one headless Claude Code session in a fresh copy of a fixture project.

Shared by trigger_test.py and task_test.py. Isolation (FACT-109, FACT-113):
--setting-sources project, the user's ~/.claude/CLAUDE.md excluded, stdin
closed, the whole process group killed on stop or timeout.
"""
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins/foma-skills"
FIXTURES = ROOT / "tests/fixtures"
_SNAPSHOT = None


def plugin_snapshot():
    """Copy the plugin once per test process so edits during a run don't leak in."""
    global _SNAPSHOT
    if _SNAPSHOT is None:
        _SNAPSHOT = tempfile.TemporaryDirectory()
        shutil.copytree(PLUGIN, Path(_SNAPSHOT.name) / "foma-skills")
    return Path(_SNAPSHOT.name) / "foma-skills"


TALLY = {"usd": 0.0, "tokens": 0, "reported": 0, "runs": 0}


def add_cost(obj):
    """Add one result object (stream event or judge JSON) to the batch total."""
    usage = obj.get("usage") or {}
    TALLY["usd"] += obj.get("total_cost_usd") or 0
    TALLY["tokens"] += sum(usage.get(k) or 0 for k in
                           ("input_tokens", "cache_creation_input_tokens", "output_tokens"))
    TALLY["reported"] += 1


def receipt(label):
    """One line for the end of a batch; also appended to tests/.runs/cost.jsonl (ignored by git).

    A run that was stopped early (trigger tests) reports no cost, so the line says how many reported.
    """
    if not TALLY["reported"]:
        return ""
    row = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "what": label, "usd": round(TALLY["usd"], 2),
           "tokens": TALLY["tokens"], "reported": TALLY["reported"], "runs": TALLY["runs"]}
    log = ROOT / "tests/.runs/cost.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write(json.dumps(row) + "\n")
    return (f"cost: ${row['usd']:.2f} at list price, {row['tokens'] / 1000:.0f}k tokens "
            f"(cache reads excluded), {row['reported']} calls reported of {row['runs']} agent runs + judge")


class LimitHit(Exception):
    """The account's usage limit stopped the session; the run says nothing about the skill."""


LIMIT_RE = re.compile(r"(?:you.ve (?:hit|reached) your .{0,40}limit|claude (?:ai )?usage limit reached)", re.I)


def limit_text(text):
    """The limit notice if text is one (the notice is the whole reply, so match at the start), else None."""
    text = str(text or "").strip()
    return text.splitlines()[0] if LIMIT_RE.match(text) else None


def limit_message(events):
    """The limit notice found in a session's events, else None."""
    for e in events:
        if e.get("type") == "result":
            found = limit_text(e.get("result"))
        elif e.get("type") == "assistant":
            blocks = e.get("message", {}).get("content", [])
            found = next((m for b in blocks if b.get("type") == "text" for m in [limit_text(b.get("text"))] if m), None)
        else:
            continue
        if found:
            return found
    return None


def base_cmd(prompt, model, plugin=True, allowed_tools=None, extra=None):
    """model may carry an effort level: "haiku@low"."""
    model, _, effort = model.partition("@")
    cmd = ["claude", "-p", prompt, "--model", model,
           "--setting-sources", "project",
           "--settings", json.dumps({"claudeMdExcludes": [str(Path.home() / ".claude/CLAUDE.md")]}),
           "--output-format", "stream-json", "--verbose", "--no-session-persistence"]
    if effort:
        cmd += ["--effort", effort]
    if plugin:
        cmd += ["--plugin-dir", str(plugin_snapshot())]
    if allowed_tools:
        cmd += ["--allowedTools", *allowed_tools]
    return cmd + (extra or [])


def run(cmd, project, stop=None, timeout=180, env=None):
    """Run cmd in project; return (events, seconds, timed_out).

    stop(events) -> bool ends the run early.
    """
    start = time.time()
    TALLY["runs"] += 1
    env = {**os.environ, "FOMA_FIRE_LOG": "off", **(env or {})}  # tests must not write the user-facing fire log
    proc = subprocess.Popen(cmd, cwd=project, env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, start_new_session=True)
    timed_out = threading.Event()

    def kill_group():
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:  # group already gone (macOS may report EPERM)
            proc.kill()

    def on_timeout():
        timed_out.set()
        kill_group()

    watchdog = threading.Timer(timeout, on_timeout)
    watchdog.start()
    events = []
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if stop and stop(events):
                break
    finally:
        watchdog.cancel()
        kill_group()
        proc.wait()
    for e in events:
        if e.get("type") == "result":
            add_cost(e)
    return events, time.time() - start, timed_out.is_set()


AGENT_DRAFTS = ROOT / "docs/agents"


def fixture_copy(name, tmp, claude_md_extra=None, git=False, agents=False):
    """Copy tests/fixtures/<name> into tmp/project.

    Optionally append to CLAUDE.md, add the pack agents to .claude/agents/
    (the state after groundwork) and git-init.
    """
    project = Path(tmp) / "project"
    shutil.copytree(FIXTURES / name, project)
    if agents:
        shutil.copytree(AGENT_DRAFTS, project / ".claude/agents")
    if claude_md_extra:
        with open(project / "CLAUDE.md", "a") as f:
            f.write("\n" + claude_md_extra.strip() + "\n")
    if git:
        (project / ".gitignore").write_text("__pycache__/\n*.pyc\n")
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.name=test", "-c", "user.email=test@example.invalid",
                      "commit", "-q", "-m", "fixture"]):
            subprocess.run(["git", *args], cwd=project, check=True)
    return project


def tool_uses(events):
    for e in events:
        if e.get("type") == "assistant":
            for block in e.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    yield block


def new_tmp():
    return tempfile.TemporaryDirectory()
