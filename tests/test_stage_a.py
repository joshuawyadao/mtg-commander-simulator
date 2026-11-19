from pathlib import Path
import sys
import tempfile
import time
import unittest

from scripts.stage_a import GameResult, ProcessResult, fixture_metadata, parse_game, run_logged


DECKS = ["Green Ramp", "Red Aggro", "Orzhov Midrange", "Azorius Control"]
HEADER = (
    "Ai(1)-Green Ramp vs Ai(2)-Red Aggro vs Ai(3)-Orzhov Midrange vs "
    "Ai(4)-Azorius Control - one game of Commander seed 42"
)
OUTCOMES = "\n".join([
    "Game Outcome: Match Duration 0m : 01s",
    "Game Outcome: Turn 8",
    "Game Outcome: Ai(1)-Green Ramp has lost",
    "Game Outcome: Ai(2)-Red Aggro has won",
    "Game Outcome: Ai(3)-Orzhov Midrange has lost",
    "Game Outcome: Ai(4)-Azorius Control has lost",
])
WIN = "Game Result: Game 1 ended in 1234 ms. Ai(2)-Red Aggro has won!"
DRAW = "Game Result: Game 1 ended in a Draw! Took 1234 ms."
OK = ProcessResult(0, 2.0, 4096, False)


class GameResultTests(unittest.TestCase):
    def parse(self, log=WIN, stderr="", process=OK, header=HEADER, outcomes=OUTCOMES):
        return parse_game(f"{header}\n{outcomes}\n{log}\n", stderr, process, DECKS, 42)

    def test_identifies_winner_and_duration_in_expected_pod(self):
        self.assertEqual(self.parse(), GameResult("won", "Red Aggro", 1234))

    def test_records_genuine_draw_without_declaring_success(self):
        result = self.parse(DRAW)
        self.assertEqual((result.status, result.winner, result.duration_ms), ("draw", None, 1234))

    def test_engine_timeout_takes_precedence_over_draw_line(self):
        result = self.parse(f"Stopping slow match as draw\n{DRAW}")
        self.assertEqual((result.status, result.winner), ("timeout", None))
        self.assertIn("game clock", result.reason)

    def test_process_deadline_is_recorded_even_with_winner_line(self):
        result = self.parse(process=ProcessResult(-9, 12, None, True))
        self.assertEqual((result.status, result.winner), ("timeout", None))
        self.assertIn("process deadline", result.reason)

    def test_fails_on_explicit_error_even_when_forge_exits_zero(self):
        for diagnostic in (
            "Could not load deck - missing.dck, match cannot start",
            'An unsupported card was requested: "Unresolved" from "???".',
            "java.lang.IllegalStateException: broken\n\tat forge.Test.call(Test.java:42)",
        ):
            with self.subTest(diagnostic=diagnostic):
                self.assertEqual(self.parse(DRAW, stderr=diagnostic).status, "failed")

    def test_fails_on_nonzero_exit(self):
        self.assertEqual(self.parse(process=ProcessResult(1, 2, 4096, False)).status, "failed")

    def test_requires_four_matching_outcomes_and_commander_start(self):
        self.assertEqual(self.parse(outcomes="\n".join(OUTCOMES.splitlines()[:-1])).status, "failed")
        self.assertEqual(self.parse(header=HEADER.replace("Commander", "Constructed")).status, "failed")

    def test_requires_one_terminal_result_with_known_seat_and_deck(self):
        for log in ("", f"{WIN}\n{WIN}", WIN.replace("Ai(2)", "Ai(5)"), WIN.replace("Red Aggro", "Wrong Deck")):
            with self.subTest(log=log):
                self.assertEqual(self.parse(log).status, "failed")


class FixtureMetadataTests(unittest.TestCase):
    def test_requires_one_record_per_fixture_in_input_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / f"{index}.dck" for index in range(4)]
            records = []
            for path, name in zip(paths, DECKS, strict=True):
                path.write_text("fixture\n", encoding="utf-8")
                records.append(f"STAGE_A_DECK\t{path.name}\t{name}\tCommander")

            fixtures = fixture_metadata("\n".join(records), paths)
            self.assertEqual([fixture["name"] for fixture in fixtures], DECKS)
            self.assertEqual(len(fixtures[0]["sha256"]), 64)
            with self.assertRaises(ValueError):
                fixture_metadata("\n".join(records[:-1]), paths)
            with self.assertRaises(ValueError):
                fixture_metadata("\n".join(reversed(records)), paths)


@unittest.skipUnless(sys.platform == "linux", "Stage A uses GNU time on hosted Ubuntu")
class LoggedProcessTests(unittest.TestCase):
    def test_captures_separate_streams_status_and_peak_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            result = run_logged(
                [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)"],
                output, output, "child", 5,
            )
            self.assertEqual(result.returncode, 3)
            self.assertFalse(result.timed_out)
            self.assertGreater(result.peak_rss_kib, 0)
            self.assertEqual((output / "child.stdout.log").read_text(), "out\n")
            self.assertEqual((output / "child.stderr.log").read_text(), "err\n")

    def test_kills_child_on_deadline_and_keeps_flushed_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            result = run_logged(
                [sys.executable, "-c", "import os, time; print(os.getpid(), flush=True); time.sleep(10)"],
                output, output, "child", 1,
            )
            self.assertTrue(result.timed_out)
            pid = int((output / "child.stdout.log").read_text())
            status_file = Path(f"/proc/{pid}/stat")
            deadline = time.monotonic() + 2
            while True:
                try:
                    state = status_file.read_text().rsplit(")", 1)[1].split()[0]
                except FileNotFoundError:
                    break
                if state == "Z":
                    break
                if time.monotonic() >= deadline:
                    self.fail("The wrapped process was still running after its deadline")
                time.sleep(0.02)
