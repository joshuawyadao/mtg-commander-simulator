import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import stage_b
from scripts.stage_a import ProcessResult


class BatchTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.forge = self.root / "forge"
        self.forge.mkdir()
        (self.forge / "forge-gui-desktop-2.0.16-jar-with-dependencies.jar").touch()
        self.output = self.root / "reports"
        self.decks = []
        for seat in range(1, 5):
            folder = self.root / f"source-{seat}"
            folder.mkdir()
            path = folder / "my deck.dck"
            path.write_text(f"deck {seat}", encoding="utf-8")
            self.decks.append(str(path))
        self.args = [
            "--forge-dir", str(self.forge), "--output-dir", str(self.output), "--decks", *self.decks,
        ]

    def test_batch_continues_after_timeout_and_launch_error(self):
        names = [f"Deck {seat}" for seat in range(1, 5)]
        seats = [f"Ai({seat})-{name}" for seat, name in enumerate(names, start=1)]
        expected_homes = set()

        def fake_java(command, cwd, log_dir, log_name, deadline):
            self.assertEqual(cwd, self.forge)
            stdout = ""
            stderr = ""
            process = ProcessResult(0, 1.5, 2048, False)
            if log_name == "java-version":
                stderr = 'openjdk version "17.0.21"\nOpenJDK Runtime Environment Temurin-17.0.21+9\n'
            elif log_name == "fixture-validation":
                paths = list(map(Path, command[-4:]))
                self.assertEqual([path.name for path in paths], [f"seat-{seat}.dck" for seat in range(1, 5)])
                self.assertEqual([path.read_text() for path in paths], [f"deck {seat}" for seat in range(1, 5)])
                stdout = "\n".join(
                    f"STAGE_A_DECK\t{path.name}\t{name}\tCommander {seat}"
                    for seat, (path, name) in enumerate(zip(paths, names), start=1)
                )
                # Subsequent changes to the source files cannot affect the validated batch.
                Path(self.decks[0]).write_text("changed after validation", encoding="utf-8")
            else:
                self.assertEqual(log_name, "simulation")
                home = command[2].removeprefix("-Duser.home=")
                self.assertNotIn(home, expected_homes)
                expected_homes.add(home)
                deck_dir = Path(command[command.index("-D") + 1])
                self.assertEqual((deck_dir / "seat-1.dck").read_text(), "deck 1")
                self.assertEqual(command[command.index("-n") + 1], "1")
                self.assertEqual(command[command.index("-c") + 1], "10")
                self.assertEqual(deadline, 15)
                seed = int(command[command.index("-s") + 1])
                winner = seats[0] if seed == 42 else seats[3]
                stdout = f"{' vs '.join(seats)} - one game of Commander seed {seed}\n"
                for seat in seats:
                    outcome = "won" if seed not in {43, 45} and seat == winner else "lost"
                    stdout += f"Game Outcome: {seat} has {outcome}\n"
                if seed == 43:
                    stdout += "Stopping slow match as draw\n"
                if seed in {43, 45}:
                    stdout += "Game Result: Game 1 ended in a Draw! Took 1000 ms.\n"
                else:
                    stdout += f"Game Result: Game 1 ended in 1000 ms. {winner} has won!\n"
                if seed == 44:
                    (log_dir / "simulation.stderr.log").write_text("launch diagnostics", encoding="utf-8")
                    raise OSError("cannot start the game")

            (log_dir / f"{log_name}.stdout.log").write_text(stdout, encoding="utf-8")
            (log_dir / f"{log_name}.stderr.log").write_text(stderr, encoding="utf-8")
            return process

        with patch("scripts.stage_a.run_logged", side_effect=fake_java) as launch:
            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = stage_b.main([
                    *self.args, "--games", "5", "--game-clock-seconds", "10", "--process-deadline-seconds", "15",
                ])

        self.assertEqual(exit_code, 1)
        self.assertEqual(launch.call_count, 7)
        report = json.loads((self.output / "results.json").read_text())
        self.assertEqual(report["counts"], {
            "requested": 5, "attempted": 5, "completed": 3, "won": 2, "draw": 1, "timeout": 1, "failed": 1,
        })
        self.assertEqual(report["run"]["forge_version"], "2.0.16")
        self.assertIn("17.0.21+9", report["run"]["java_version"])
        self.assertEqual(report["decks"][0]["sha256"], hashlib.sha256(b"deck 1").hexdigest())
        self.assertEqual(report["decks"][0]["file"], self.decks[0])
        self.assertEqual([game["seed"] for game in report["games"]], list(range(42, 47)))
        self.assertEqual([game["status"] for game in report["games"]], ["won", "timeout", "failed", "draw", "won"])
        self.assertEqual(report["games"][1]["reason"], "Forge game clock expired")
        self.assertEqual(report["games"][2]["reason"], "cannot start the game")
        failure_log = self.output / report["games"][2]["logs"]["stderr"]
        self.assertEqual(failure_log.read_text(), "launch diagnostics")
        self.assertEqual(report["games"][4]["winner"], "Deck 4")

    def test_setup_failure_emits_reports_without_game_attempts(self):
        args = [*self.args, "--forge-dir", str(self.root / "missing")]
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(stage_b.main(args), 1)
        report = json.loads((self.output / "results.json").read_text())
        self.assertIn("Expected one Forge desktop JAR", report["run"]["batch_error"])
        self.assertEqual(report["counts"]["attempted"], 0)
        self.assertEqual(report["counts"]["requested"], 10)
        self.assertEqual(report["games"], [])
        with (self.output / "results.csv").open(newline="", encoding="utf-8") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [])
        self.assertIn("Expected one Forge desktop JAR", (self.output / "summary.md").read_text())

    def test_rejects_invalid_configuration_without_creating_output(self):
        for flags in (["--games", "0"], ["--seed", str(stage_b.MAX_SEED)], ["--process-deadline-seconds", "10"]):
            with self.subTest(flags=flags), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                stage_b.main([*self.args, *flags])
            self.assertEqual(error.exception.code, 2)
            self.assertFalse(self.output.exists())

    def test_refuses_to_overwrite_existing_run(self):
        self.output.mkdir()
        report = self.output / "results.json"
        report.write_text("previous run", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            stage_b.main(self.args)
        self.assertEqual(error.exception.code, 2)
        self.assertEqual(report.read_text(), "previous run")
