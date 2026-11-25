from collections import Counter
import contextlib
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
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
        self.common_args = ["--forge-dir", str(self.forge), "--output-dir", str(self.output)]
        self.args = [*self.common_args, "--decks", *self.decks]

    def test_lineups_use_the_same_opponents_and_replace_only_seat_three(self):
        candidates = {
            "baseline": ("decks/stage-a/midrange.dck", None),
            "graveyard-recursion": ("decks/phase-2/graveyard-recursion.dck", 3),
            "spellslinger": ("decks/phase-2/spellslinger.dck", 3),
            "meren-extra-swamp": ("decks/phase-4/meren-extra-swamp.dck", 3),
        }
        for lineup, (candidate, goal_seat) in candidates.items():
            with self.subTest(lineup=lineup), patch("scripts.stage_b.run_batch", return_value=0) as run:
                output = self.output / lineup
                args = ["--forge-dir", str(self.forge), "--output-dir", str(output), "--lineup", lineup]
                self.assertEqual(stage_b.main(args), 0)
                parsed, actual_output = run.call_args.args
                self.assertEqual(actual_output, output)
                self.assertEqual(parsed.lineup, lineup)
                self.assertEqual(parsed.goal_seat, goal_seat)
                self.assertEqual(tuple(map(str, parsed.decks)), (
                    "decks/stage-a/ramp.dck", "decks/stage-a/aggro.dck", candidate, "decks/stage-a/control.dck",
                ))

    def test_meren_variant_exchanges_rise_from_the_grave_for_a_swamp(self):
        def read_deck(path):
            head, main = (stage_b.forge.ROOT / path).read_text(encoding="utf-8").split("[Main]\n")
            cards = Counter()
            for line in main.splitlines():
                quantity, name = line.split(" ", 1)
                cards[name] += int(quantity)
            return head.split("[Commander]\n")[1], cards

        original_commander, original = read_deck(stage_b.RECURSION_DECK)
        variant_commander, variant = read_deck(stage_b.RECURSION_EXTRA_SWAMP_DECK)
        self.assertEqual(variant_commander, original_commander)
        self.assertEqual(sum(original.values()), 99)
        self.assertEqual(sum(variant.values()), 99)
        self.assertEqual(original - variant, Counter({"Rise from the Grave": 1}))
        self.assertEqual(variant - original, Counter({"Swamp": 1}))

    def test_explicit_goal_seat_overrides_preset_and_supports_custom_decks(self):
        for selection_number, deck_selection in enumerate((
            ["--lineup", "spellslinger"], ["--lineup", "baseline"], ["--decks", *self.decks],
        )):
            for seat in range(1, 5):
                with self.subTest(decks=deck_selection, seat=seat), patch("scripts.stage_b.run_batch", return_value=0) as run:
                    output = self.root / f"reports-{selection_number}-{seat}"
                    args = ["--forge-dir", str(self.forge), "--output-dir", str(output),
                            *deck_selection, "--goal-seat", str(seat)]
                    self.assertEqual(stage_b.main(args), 0)
                    self.assertEqual(run.call_args.args[0].goal_seat, seat)

    def test_custom_decks_have_no_implicit_goal_seat(self):
        with patch("scripts.stage_b.run_batch", return_value=0) as run:
            self.assertEqual(stage_b.main(self.args), 0)
        self.assertIsNone(run.call_args.args[0].goal_seat)

    def test_preset_from_another_directory_reports_selected_lineup_when_setup_fails(self):
        result = subprocess.run(
            [
                sys.executable, "-B", "-m", "scripts.stage_b", "--lineup", "spellslinger",
                "--forge-dir", str(self.root / "missing"), "--output-dir", str(self.output),
            ],
            cwd=self.root, env={**os.environ, "PYTHONPATH": str(stage_b.forge.ROOT)},
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads((self.output / "results.json").read_text())
        self.assertEqual(report["run"]["lineup"], "spellslinger")
        self.assertEqual(report["run"]["goal_seat"], 3)
        self.assertIn("Expected one Forge desktop JAR", report["run"]["batch_error"])
        self.assertIn("- Lineup: spellslinger", (self.output / "summary.md").read_text())

    def test_rejects_unknown_lineup_or_both_deck_selections(self):
        for args in (
            [*self.common_args, "--lineup", "unknown"],
            [*self.args, "--lineup", "baseline"],
        ):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                stage_b.main(args)
            self.assertEqual(error.exception.code, 2)
            self.assertFalse(self.output.exists())

    def test_batch_continues_after_timeout_and_launch_error(self):
        names = [f"Deck {seat}" for seat in range(1, 5)]
        commanders = ["Meren of Clan Nel Toth", "Commander 2", "Commander 3", "Commander 4"]
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
                    f"STAGE_A_DECK\t{path.name}\t{name}\t{commander}"
                    for path, name, commander in zip(paths, names, commanders, strict=True)
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
                if seed in {42, 43}:
                    stdout += (
                        f"Turn: Turn 1 ({seats[0]})\n"
                        f"Land: {seats[0]} played Forest (1)\n"
                        f"Add To Stack: {seats[0]} cast {commanders[0]}\n"
                        f"Phase: {seats[0]}'s End step\n"
                        f"Add To Stack: {seats[0]} triggered {commanders[0]} targeting [Sakura-Tribe Elder (3)]\n"
                        "Resolve Stack: At the beginning of your end step, choose target creature card in your "
                        f"graveyard. (Targeting: [[Sakura-Tribe Elder (3)]]) [Phase: {seats[0]}]\n"
                        "Zone Change: Sakura-Tribe Elder (3) was put into Graveyard from Battlefield.\n"
                        f"Turn: Turn 2 ({seats[1]})\n"
                        f"Damage: Attacker (2) deals 3 combat damage to {seats[0]}.\n"
                        "Game Outcome: Turn 1\n"
                    )
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
        self.assertIsNone(report["run"]["lineup"])
        self.assertIsNone(report["run"]["goal_seat"])
        self.assertIn("17.0.21+9", report["run"]["java_version"])
        self.assertEqual(report["decks"][0]["sha256"], hashlib.sha256(b"deck 1").hexdigest())
        self.assertEqual(report["decks"][0]["file"], self.decks[0])
        self.assertEqual([game["seed"] for game in report["games"]], list(range(42, 47)))
        self.assertEqual([game["status"] for game in report["games"]], ["won", "timeout", "failed", "draw", "won"])
        self.assertEqual(report["games"][1]["reason"], "Forge game clock expired")
        self.assertEqual(report["games"][2]["reason"], "cannot start the game")
        telemetry = report["games"][0]["telemetry"]
        self.assertEqual([entry["seat"] for entry in telemetry], [1, 2, 3, 4])
        self.assertEqual(telemetry[0], {
            "seat": 1, "first_commander_cast_turn": 1, "early_land_plays": 1,
            "early_turns_observed": 1, "combat_damage_taken": 3,
        })
        self.assertEqual([game["telemetry"] for game in report["games"][1:]], [None] * 4)
        self.assertEqual(report["games"][0]["meren_recursion"], [{"seat": 1, "events": [{
            "turn": 1, "target": "Sakura-Tribe Elder", "trigger_line": 6, "resolution_line": 7,
            "destination": "battlefield", "destination_line": 8,
        }]}])
        self.assertEqual([game["meren_recursion"] for game in report["games"][1:]], [None] * 4)
        with (self.output / "results.csv").open(newline="", encoding="utf-8") as stream:
            fields = csv.DictReader(stream).fieldnames
            self.assertNotIn("telemetry", fields)
            self.assertNotIn("meren_recursion", fields)
        failure_log = self.output / report["games"][2]["logs"]["stderr"]
        self.assertEqual(failure_log.read_text(), "launch diagnostics")
        self.assertEqual(report["games"][4]["winner"], "Deck 4")

    def test_setup_failure_emits_reports_without_game_attempts(self):
        args = [*self.args, "--goal-seat", "4", "--forge-dir", str(self.root / "missing")]
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(stage_b.main(args), 1)
        report = json.loads((self.output / "results.json").read_text())
        self.assertIn("Expected one Forge desktop JAR", report["run"]["batch_error"])
        self.assertEqual(report["run"]["goal_seat"], 4)
        self.assertEqual(report["counts"]["attempted"], 0)
        self.assertEqual(report["counts"]["requested"], 10)
        self.assertEqual(report["games"], [])
        with (self.output / "results.csv").open(newline="", encoding="utf-8") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [])
        self.assertIn("Expected one Forge desktop JAR", (self.output / "summary.md").read_text())

    def test_rejects_invalid_configuration_without_creating_output(self):
        for flags in (["--games", "0"], ["--seed", str(stage_b.MAX_SEED)], ["--process-deadline-seconds", "10"],
                      ["--goal-seat", "0"], ["--goal-seat", "5"], ["--goal-seat", "auto"]):
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
