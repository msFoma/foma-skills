"""Tests for the usage-limit detection and retry voting of the test harness, and for the fire log.

Run: python3 -m unittest scripts/test_harness.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claude_run as cr  # noqa: E402
import fires  # noqa: E402
import task_test  # noqa: E402

LIMIT = "You've hit your 5-hour limit · resets 1:20am (Europe/Kiev)"


def assistant(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


class LimitTest(unittest.TestCase):
    def test_notice_is_detected_in_assistant_and_result(self):
        self.assertEqual(cr.limit_message([assistant(LIMIT)]), LIMIT)
        self.assertEqual(cr.limit_message([{"type": "result", "result": LIMIT}]), LIMIT)
        self.assertIsNotNone(cr.limit_text("Claude usage limit reached. Resets at 4pm."))
        self.assertIsNotNone(cr.limit_text("You’ve hit your weekly limit"))  # curly apostrophe

    def test_normal_text_and_quotes_are_not_a_limit(self):
        self.assertIsNone(cr.limit_message([assistant("Done. The rate limit test passes.")]))
        self.assertIsNone(cr.limit_message([assistant("The user wrote: You've hit your limit")]))
        self.assertIsNone(cr.limit_text(""))
        self.assertIsNone(cr.limit_text(None))

    def test_judge_raises_on_a_limit_reply(self):
        task = {"prompt": "p", "checklist": ["a"]}
        out = '{"type":"result","result":"%s"}' % LIMIT
        res = mock.Mock(stdout=out)
        with mock.patch.object(task_test.subprocess, "run", return_value=res):
            with self.assertRaises(cr.LimitHit):
                task_test.judge_once(task, "log", "")


class VoteTest(unittest.TestCase):
    def test_majority(self):
        self.assertTrue(task_test.majority([False, True, True]))
        self.assertFalse(task_test.majority([False, False, True]))
        self.assertFalse(task_test.majority([False, True]))  # a tie is not a pass
        self.assertIsNone(task_test.majority([None, None]))
        self.assertTrue(task_test.majority([False, None, True, True]))

    def run_voted(self, verdicts, retries=2):
        """Drive run_voted with scripted per-try verdicts; return (result, tries made)."""
        queue = list(verdicts)
        with mock.patch.object(task_test, "run_variant", side_effect=lambda *a: queue.pop(0)), \
                mock.patch.object(task_test, "show", side_effect=lambda rec: rec), \
                mock.patch("builtins.print"):
            result = task_test.run_voted("t", {}, "skill", "sonnet", retries)
        return result, len(verdicts) - len(queue)

    def test_pass_first_time_makes_one_try(self):
        self.assertEqual(self.run_voted([True]), (True, 1))

    def test_fail_then_two_passes_is_a_pass(self):
        self.assertEqual(self.run_voted([False, True, True]), (True, 3))

    def test_fail_then_fail_stops_early(self):
        self.assertEqual(self.run_voted([False, False, True]), (False, 2))

    def test_no_retries_means_single_run(self):
        self.assertEqual(self.run_voted([False], retries=0), (False, 1))

    def test_limit_in_a_retry_propagates(self):
        with mock.patch.object(task_test, "run_variant", side_effect=[{"x": 1}, cr.LimitHit(LIMIT)]), \
                mock.patch.object(task_test, "show", side_effect=[False]), \
                mock.patch("builtins.print"):
            with self.assertRaises(cr.LimitHit):
                task_test.run_voted("t", {}, "skill", "sonnet", 2)


HOOK = Path(__file__).resolve().parent.parent / "plugins/foma-skills/hooks/fire-log.sh"


class FireLogTest(unittest.TestCase):
    def fire(self, cwd, payload, *args):
        subprocess.run(["sh", str(HOOK), *args], input=payload + "\n", text=True, cwd=cwd, check=True)

    def test_hook_logs_skill_name_time_and_session_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.fire(tmp, '{"session_id":"abc-1","prompt":"secret","tool_name":"Skill",'
                           '"tool_input":{"skill":"foma-skills:planning"}}')
            row = json.loads((Path(tmp) / ".scratch/fires.jsonl").read_text())
        self.assertEqual(row["skill"], "foma-skills:planning")
        self.assertEqual(row["session"], "abc-1")
        self.assertEqual(set(row), {"t", "skill", "session"})

    def test_hook_ignores_other_tools_and_odd_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.fire(tmp, '{"tool_name":"Bash","tool_input":{"command":"ls"}}')
            self.fire(tmp, '{"tool_input":{"skill":"x\\"; rm -rf /"}}')
            self.assertFalse((Path(tmp) / ".scratch/fires.jsonl").exists())

    def test_summary_counts_and_lists_unfired_skills(self):
        t = fires.datetime(2026, 11, 13, tzinfo=fires.timezone.utc)
        rows = [(t, "planning", "s1"), (t, "planning", "s2"), (t, "tdd", "s1"), (t, "other-plugin", "s1")]
        lines = fires.summary(rows, {"planning", "tdd", "debugging"}, total=24)
        self.assertTrue(lines[0].startswith("planning") and "2 fires" in lines[0] and "of 24 sessions" in lines[0])
        self.assertTrue(lines[1].startswith("tdd"))
        self.assertTrue(lines[2].startswith("debugging") and "0 fires" in lines[2])
        self.assertEqual(len(lines), 3)  # the other plugin's skill is not listed

    def test_read_fires_skips_bad_lines_and_old_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "f.jsonl"
            log.write_text('not json\n{"t":"2020-01-01T00:00:00Z","skill":"foma-skills:tdd","session":"a"}\n'
                           '{"t":"2099-01-01T00:00:00Z","skill":"foma-skills:tdd","session":"b"}\n')
            self.assertEqual(len(fires.read_log([log])[0]), 2)
            self.assertEqual([r[2] for r in fires.read_log([log], days=30)[0]], ["b"])
            self.assertEqual(fires.read_log([Path(tmp) / "missing"]), ([], set()))

    def test_start_rows_are_the_denominator_and_dedupe_by_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.fire(tmp, '{"session_id":"s1","hook_event_name":"SessionStart"}', "start")
            self.fire(tmp, '{"session_id":"s1","hook_event_name":"SessionStart","source":"compact"}', "start")
            self.fire(tmp, '{"session_id":"s2"}', "start")
            self.fire(tmp, '{"session_id":"s2","tool_input":{"skill":"foma-skills:tdd"}}')
            rows, started = fires.read_log([Path(tmp) / ".scratch/fires.jsonl"])
        self.assertEqual(started, {"s1", "s2"})
        self.assertEqual([r[1] for r in rows], ["tdd"])

    def test_off_switch_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["sh", str(HOOK), "start"], input='{"session_id":"s1"}\n', text=True, cwd=tmp,
                           check=True, env={"FOMA_FIRE_LOG": "off", "PATH": "/usr/bin:/bin"})
            self.assertFalse((Path(tmp) / ".scratch").exists())

    def test_cost_receipt_counts_reported_calls(self):
        cr.TALLY.update(usd=0.0, tokens=0, reported=0, runs=0)
        self.assertEqual(cr.receipt("x"), "")  # nothing reported: no line
        cr.TALLY["runs"] = 3
        cr.add_cost({"total_cost_usd": 0.5, "usage": {"input_tokens": 10, "cache_creation_input_tokens": 1000,
                                                      "cache_read_input_tokens": 99999, "output_tokens": 90}})
        with mock.patch.object(cr, "ROOT", Path(tempfile.mkdtemp())):
            line = cr.receipt("x")
        self.assertIn("$0.50", line)
        self.assertIn("1k tokens", line)
        self.assertIn("1 calls reported of 3", line)


if __name__ == "__main__":
    unittest.main()
