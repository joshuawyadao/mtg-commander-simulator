"""Dashboard and command-line checks for matched-seed comparison reports."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.compare_reports import main, render_comparison
from scripts.comparison_data import build_comparison


def artifact(name, sha, outcomes):
    names = [name, "Gruul Ramp", "Azorius Control", "Rakdos Aggro"]
    run = {
        "requested_games": 3, "base_seed": 100, "goal_seat": 1,
        "game_clock_seconds": 600, "process_deadline_seconds": 720,
        "forge_version": "2.0.16", "java_version": "17", "source_commit": "abc123",
        "run_id": "1234", "run_attempt": "2",
        "workflow_url": "https://github.com/example/mtg/actions/runs/1234",
    }
    decks = [
        {"seat": seat, "name": deck_name, "commander": "Meren" if seat == 1 else "Other",
         "ai_profile": "Forge default", "sha256": sha if seat == 1 else str(seat) * 64}
        for seat, deck_name in enumerate(names, 1)
    ]
    games = []
    for number, (status, winner, telemetry) in enumerate(outcomes, 1):
        if status is None:
            continue
        games.append({
            "game": number, "seed": 99 + number, "seats": names, "status": status,
            "winner": winner, "reason": "Forge | stopped" if status == "failed" else None,
            "telemetry": ([{"seat": 1, **telemetry}] if telemetry is not None else None),
        })
    return {"run": run, "decks": decks, "games": games}


CAST = {"first_commander_cast_turn": 5, "early_land_plays": 0,
        "early_turns_observed": 4, "combat_damage_taken": 0}
NO_CAST = {"first_commander_cast_turn": None, "early_land_plays": 2,
           "early_turns_observed": 4, "combat_damage_taken": 7}


class ComparisonReportTests(unittest.TestCase):
    def setUp(self):
        self.a = artifact("Golgari Graveyard Recursion", "a" * 64, [
            ("won", "Golgari Graveyard Recursion", CAST),
            ("draw", None, NO_CAST),
            ("failed", None, None),
        ])
        self.b = artifact("Golgari Graveyard Recursion (extra Swamp)", "b" * 64, [
            ("won", "Gruul Ramp", NO_CAST),
            ("won", "Golgari Graveyard Recursion (extra Swamp)", CAST),
            (None, None, None),
        ])

    def test_dashboard_shows_scorecard_pairs_sources_and_no_data_states(self):
        report = render_comparison(build_comparison(self.a, self.b))

        self.assertIn("**2 / 3 matched seeds completed", report)
        self.assertIn("| Win rate | **50%** | **50%** | +0 pp | 2 pairs |", report)
        self.assertIn("| Commander cast rate | **50%** | **50%** | +0 pp | 2 pairs |", report)
        self.assertIn("| 100 | 🟩 Win | 🟥 Loss |", report)
        self.assertIn("| 102 | ⚠️ Failed | ⬜ Missing |", report)
        self.assertIn("[Run 1234](https://github.com/example/mtg/actions/runs/1234)", report)
        self.assertIn("goal deck SHA-256 `" + "a" * 64 + "`", report)
        self.assertIn("goal deck SHA-256 `" + "b" * 64 + "`", report)
        self.assertIn("No cast", report)
        self.assertIn("Unavailable", report)
        self.assertIn("0 / 4 own turns", report)
        self.assertIn("**0** is a measured zero", report)
        self.assertIn("Forge &#124; stopped", report)
        self.assertEqual(report, render_comparison(build_comparison(self.a, self.b)))

    def test_untrusted_text_and_workflow_url_are_not_active_markdown(self):
        changed = copy.deepcopy(self.b)
        changed["decks"][0]["name"] = "Meren | <script>"
        changed["games"][1]["winner"] = changed["decks"][0]["name"]
        for game in changed["games"]:
            game["seats"][0] = changed["decks"][0]["name"]
        changed["run"]["workflow_url"] = "https://github.com/owner/repo)/actions/runs/1234"

        report = render_comparison(build_comparison(self.a, changed))

        self.assertIn("Meren &#124; &lt;script&gt;", report)
        self.assertNotIn("<script>", report)
        self.assertNotIn("](https://github.com/owner/repo)", report)

    def test_empty_samples_and_percentage_point_change(self):
        changed = copy.deepcopy(self.b)
        changed["games"][0]["winner"] = changed["decks"][0]["name"]
        changed["games"][1]["winner"] = "Gruul Ramp"
        report = render_comparison(build_comparison(self.a, changed))
        self.assertIn("| Win rate | **50%** | **50%** | +0 pp | 2 pairs |", report)

        changed["games"][1]["winner"] = changed["decks"][0]["name"]
        report = render_comparison(build_comparison(self.a, changed))
        self.assertIn("| Win rate | **50%** | **100%** | +50 pp | 2 pairs |", report)

        for game in changed["games"]:
            game["status"] = "failed"
            game["winner"] = None
        report = render_comparison(build_comparison(self.a, changed))
        self.assertIn("**0 / 3 matched seeds completed", report)
        self.assertIn("| Win rate | **—** | **—** | — | 0 pairs |", report)

    def test_cli_writes_report_and_rejects_invalid_inputs_without_output(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            a, b = directory / "a.json", directory / "b.json"
            output = directory / "nested" / "comparison.md"
            a.write_text(json.dumps(self.a), encoding="utf-8")
            b.write_text(json.dumps(self.b), encoding="utf-8")
            args = ["--version-a", str(a), "--version-b", str(b), "--output", str(output)]
            self.assertEqual(main(args), 0)
            self.assertIn("# Commander A/B simulation dashboard", output.read_text(encoding="utf-8"))
            self.assertEqual(main([*args[:-1], str(a)]), 1)
            self.assertEqual(json.loads(a.read_text(encoding="utf-8")), self.a)

            output.unlink()
            invalid = copy.deepcopy(self.b)
            invalid["run"]["base_seed"] = 101
            b.write_text(json.dumps(invalid), encoding="utf-8")
            self.assertEqual(main(args), 1)
            self.assertFalse(output.exists())

            b.write_text("{ invalid json", encoding="utf-8")
            self.assertEqual(main(args), 1)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
