import csv
import json
from pathlib import Path
import tempfile
import unittest

from scripts.batch_report import write_reports


RUN = {
    "started_at": "2026-11-19T12:00:00+00:00",
    "requested_games": 4,
    "base_seed": 42,
    "game_clock_seconds": 600,
    "process_deadline_seconds": 720,
    "wall_seconds": 31.5,
    "forge_version": "2.0.16",
    "java_version": "17.0.21+9",
    "source_commit": "abcdef0",
    "run_id": "1234",
    "run_attempt": "1",
    "workflow_url": "https://example.test/actions/runs/1234",
    "batch_error": None,
    "logs": {"setup": "logs/setup.log"},
}
DECKS = [
    {"seat": seat, "file": f"{name}.dck", "name": name, "commander": "Commander",
     "sha256": str(seat) * 64, "archetype": "test", "ai_profile": "Forge default"}
    for seat, name in enumerate(("Ramp", "Aggro", "Midrange", "Control"), 1)
]


def game(number, status, winner=None, reason=None):
    return {
        "game": number, "seed": 42 + number - 1,
        "seats": [deck["name"] for deck in DECKS],
        "status": status, "winner": winner,
        "duration_ms": 1000 if status in ("won", "draw") else None,
        "wall_seconds": 1.5, "reason": reason,
        "logs": {"stdout": f"games/{number:02d}/simulation.stdout.log"},
        "returncode": 0 if status in ("won", "draw") else 1,
        "peak_rss_kib": 4096,
    }


class BatchReportTests(unittest.TestCase):
    def render(self, run=RUN, decks=DECKS, games=None):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            write_reports(output, run, decks, games or [])
            payload = json.loads((output / "results.json").read_text(encoding="utf-8"))
            with (output / "results.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            markdown = (output / "summary.md").read_text(encoding="utf-8")
            return payload, rows, markdown

    def test_mixed_outcomes_have_consistent_counts_and_deck_totals(self):
        games = [
            game(1, "won", "Ramp"),
            game(2, "draw", reason="No winner"),
            game(3, "timeout", reason="Forge game clock expired"),
            game(4, "failed", reason="Engine error"),
        ]
        payload, rows, markdown = self.render(games=games)

        self.assertEqual(payload["counts"], {
            "requested": 4, "attempted": 4, "completed": 2,
            "won": 1, "draw": 1, "timeout": 1, "failed": 1,
        })
        self.assertEqual([row["status"] for row in rows], [game["status"] for game in games])
        self.assertEqual([json.loads(row["seats"]) for row in rows], [game["seats"] for game in games])
        self.assertEqual(len(rows), len(payload["games"]))
        self.assertEqual(rows[2]["reason"], games[2]["reason"])
        self.assertEqual(rows[3]["returncode"], "1")
        self.assertEqual(payload["decks"][0]["wins"], 1)
        self.assertEqual(payload["decks"][0]["win_rate"], 0.5)
        self.assertEqual(payload["decks"][1]["losses"], 1)
        self.assertEqual(payload["decks"][1]["draws"], 1)
        self.assertEqual(payload["decks"][1]["win_rate"], 0)
        self.assertIn("| 3 | Ramp, Aggro, Midrange, Control | 44 | timeout |", markdown)
        self.assertIn("[stdout](games/03/simulation.stdout.log)", markdown)
        self.assertIn("- Completed: 2", markdown)

    def test_setup_failure_still_writes_three_reports_with_zero_attempts(self):
        run = {**RUN, "batch_error": "Deck validation failed"}
        payload, rows, markdown = self.render(run=run, decks=[], games=[])

        self.assertEqual(payload["counts"]["requested"], 4)
        self.assertEqual(payload["counts"]["attempted"], 0)
        self.assertEqual(payload["counts"]["completed"], 0)
        self.assertEqual(payload["decks"], [])
        self.assertEqual(rows, [])
        self.assertIn("- Batch error: Deck validation failed", markdown)
        self.assertIn("[setup](logs/setup.log)", markdown)

    def test_zero_completed_games_has_unavailable_win_rate(self):
        payload, _, markdown = self.render(games=[game(1, "failed", reason="Invalid deck")])

        self.assertTrue(all(deck["win_rate"] is None for deck in payload["decks"]))
        self.assertIn("| 0 | 0 | 0 | 0 | unavailable |", markdown)

    def test_csv_escapes_formula_text_and_markdown_escapes_deck_markup(self):
        decks = [{**DECKS[0], "name": "=SUM(1,2)|<unsafe>[deck]"}, *DECKS[1:]]
        sample = {**game(1, "won", winner=decks[0]["name"], reason="=1+1"), "seats": [deck["name"] for deck in decks]}
        payload, rows, markdown = self.render(decks=decks, games=[sample])

        self.assertEqual(payload["decks"][0]["name"], decks[0]["name"])
        self.assertEqual(json.loads(rows[0]["seats"]), sample["seats"])
        self.assertEqual(rows[0]["winner"], "'" + decks[0]["name"])
        self.assertEqual(rows[0]["reason"], "'=1+1")
        self.assertIn("=SUM(1,2)&#124;&lt;unsafe&gt;&#91;deck&#93;", markdown)

    def test_negative_exit_code_remains_numeric_in_csv(self):
        interrupted = {**game(1, "timeout", reason="Deadline"), "returncode": -9}
        _, rows, _ = self.render(games=[interrupted])
        self.assertEqual(rows[0]["returncode"], "-9")


if __name__ == "__main__":
    unittest.main()
