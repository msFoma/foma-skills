"""Run one headless Claude Code session in a fresh copy of a fixture project.

Shared by trigger_test.py and task_test.py. Isolation (FACT-109, FACT-113):
--setting-sources project, the user's ~/.claude/CLAUDE.md excluded, stdin
closed, the whole process group killed on stop or timeout.
"""
import json
import os
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


def run(cmd, project, stop=None, timeout=180):
    """Run cmd in project; return (events, seconds, timed_out).

    stop(events) -> bool ends the run early.
    """
    start = time.time()
    proc = subprocess.Popen(cmd, cwd=project, stdin=subprocess.DEVNULL,
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
    return events, time.time() - start, timed_out.is_set()


def fixture_copy(name, tmp, claude_md_extra=None, git=False):
    """Copy tests/fixtures/<name> into tmp/project; optionally append to CLAUDE.md and git-init."""
    project = Path(tmp) / "project"
    shutil.copytree(FIXTURES / name, project)
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
