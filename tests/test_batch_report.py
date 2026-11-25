import csv
import json
from pathlib import Path
import tempfile
import unittest

from scripts.batch_report import write_reports
from scripts.meren_recursion import MEREN


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
        self.assertIn("| **2 / 4** | 4 | 1 | 1 | 1 | 31.5 s |", markdown)
        self.assertNotIn("## Goal deck", markdown)
        self.assertNotIn("### Pros and cons", markdown)

    def test_goal_dashboard_distinguishes_game_outcomes_and_compares_decks(self):
        absent = {**game(6, "won", "Aggro"), "seats": ["Aggro", "Midrange", "Control"]}
        games = [
            game(1, "won", "Ramp"),
            game(2, "won", "Aggro"),
            game(3, "draw", reason="No winner"),
            game(4, "timeout", reason="Forge game clock expired"),
            game(5, "failed", reason="Engine error"),
            absent,
        ]
        payload, rows, markdown = self.render(run={**RUN, "requested_games": 6, "goal_seat": 1}, games=games)

        self.assertEqual(payload["run"]["goal_seat"], 1)
        self.assertEqual(len(rows), 6)
        self.assertIn("## Goal deck · Ramp\n\nCommander · Seat 1 · test", markdown)
        self.assertIn("| **33.3%** | **1** | 1 | 1 | 3 |", markdown)
        self.assertLess(markdown.index("### Pros and cons"), markdown.index("### Game-by-game"))
        self.assertIn(
            "| Tied for the lead with **1** win. | **Aggro** won **1 of 1** games the goal deck lost. |",
            markdown,
        )
        self.assertIn("🟩 `01 W` · 🟥 `02 L` · 🟨 `03 D` · ⏱️ `04 T` · ⚠️ `05 F` · ⬜ `06 —`", markdown)
        self.assertIn("W win · L loss · D draw · T timeout · F failed · — deck absent", markdown)
        self.assertIn("| **Ramp** | `███░░░░░░░` 33.3% | 1 | 1 | 1 | 3 |", markdown)
        self.assertLess(markdown.index("| Aggro |"), markdown.index("| **Ramp** |"))
        self.assertIn("### How the deck played\n\nTelemetry unavailable for this batch.", markdown)
        self.assertIn("<summary>Game results and logs</summary>", markdown)
        self.assertIn("[stdout](games/05/simulation.stdout.log)", markdown)

    def test_goal_telemetry_uses_only_completed_games_and_full_early_windows(self):
        def telemetry(cast, lands, own_turns, damage):
            return [
                {"seat": seat, "first_commander_cast_turn": cast if seat == 1 else None,
                 "early_land_plays": lands if seat == 1 else 0,
                 "early_turns_observed": own_turns if seat == 1 else 4,
                 "combat_damage_taken": damage if seat == 1 else 0}
                for seat in range(1, 5)
            ]

        absent = {**game(6, "won", "Aggro"), "seats": ["Aggro", "Midrange", "Control"],
                  "telemetry": telemetry(3, 4, 4, 9)}
        games = [
            {**game(1, "won", "Ramp"), "telemetry": telemetry(4, 3, 4, 0)},
            {**game(2, "won", "Aggro"), "telemetry": telemetry(None, 0, 4, 6)},
            {**game(3, "draw"), "telemetry": telemetry(8, 1, 2, 4)},
            game(4, "won", "Control"),
            {**game(5, "timeout"), "telemetry": telemetry(3, 4, 4, 99)},
            absent,
        ]
        payload, rows, markdown = self.render(run={**RUN, "requested_games": 6, "goal_seat": 1}, games=games)

        self.assertEqual(len(payload["games"][0]["telemetry"]), 4)
        self.assertEqual(payload["games"][0]["telemetry"][0]["combat_damage_taken"], 0)
        self.assertNotIn("telemetry", rows[0])
        self.assertIn("Telemetry from **3 of 4** completed games with the goal deck.", markdown)
        self.assertIn("| Commander cast | **2 of 3** games | 3 |", markdown)
        self.assertIn("| First commander cast | **Turn 6 (median)** | 2 casts |", markdown)
        self.assertIn("| Land plays in first 4 own turns | **1.5 plays (median)** | 2 with 4 turns |", markdown)
        self.assertIn("| Combat damage taken | **4 damage** (median) | 3 |", markdown)
        self.assertLess(markdown.index("### Pros and cons"), markdown.index("### How the deck played"))
        self.assertLess(markdown.index("### How the deck played"), markdown.index("### Game-by-game"))
        self.assertIn("<summary>Goal deck telemetry by game</summary>", markdown)
        self.assertIn("| 1 | win | Turn 4 | 3 / 4 (of first 4) | 0 |", markdown)
        self.assertIn("| 2 | loss | No cast | 0 / 4 (of first 4) | 6 |", markdown)
        self.assertIn("| 3 | draw | Turn 8 | 1 / 2 (of first 4) | 4 |", markdown)
        self.assertIn("| 4 | loss | Unavailable | Unavailable | Unavailable |", markdown)
        self.assertIn("| 5 | timeout | Unavailable | Unavailable | Unavailable |", markdown)
        self.assertIn("| 6 | absent | Unavailable | Unavailable | Unavailable |", markdown)

    def test_telemetry_distinguishes_no_cast_and_short_games_from_missing_data(self):
        available = [
            {"seat": 1, "first_commander_cast_turn": None,
             "early_land_plays": 0, "early_turns_observed": 2, "combat_damage_taken": 0},
        ]
        _, _, markdown = self.render(
            run={**RUN, "requested_games": 2, "goal_seat": 1},
            games=[{**game(1, "won", "Aggro"), "telemetry": available}, game(2, "failed")],
        )

        self.assertIn("Telemetry from **1 of 1** completed games with the goal deck.", markdown)
        self.assertIn("| Commander cast | **0 of 1** games | 1 |", markdown)
        self.assertIn("| First commander cast | **No casts observed** | 0 casts |", markdown)
        self.assertIn("| Land plays in first 4 own turns | **Unavailable** | 0 with 4 turns |", markdown)
        self.assertIn("| Combat damage taken | **0 damage** (median) | 1 |", markdown)
        self.assertIn("| 1 | loss | No cast | 0 / 2 (of first 4) | 0 |", markdown)
        self.assertIn("| 2 | failed | Unavailable | Unavailable | Unavailable |", markdown)

    def test_merens_recursion_scorecard_separates_observed_zero_unknown_and_unavailable(self):
        decks = [{**DECKS[0], "commander": MEREN}, *DECKS[1:]]
        def event(turn, target, trigger, resolution=None, destination=None, destination_line=None):
            return {"turn": turn, "target": target, "trigger_line": trigger, "resolution_line": resolution,
                    "destination": destination, "destination_line": destination_line}
        games = [
            {**game(1, "won", "Ramp"), "meren_recursion": [{"seat": 1, "events": [
                event(4, "Sakura-Tribe Elder", 100, 101, "battlefield", 103),
                event(8, "Shriekmaw", 200, 201),
            ]}]},
            {**game(2, "draw"), "meren_recursion": [{"seat": 1, "events": []}]},
            {**game(3, "won", "Aggro"), "meren_recursion": [{"seat": 1, "events": [
                event(6, "Plaguecrafter", 300), event(9, "Sakura-Tribe Elder", 400, 401),
            ]}]},
            game(4, "won", "Control"),
            {**game(5, "timeout"), "meren_recursion": [{"seat": 1, "events": [
                event(1, "Excluded", 1, 2, "battlefield", 3),
            ]}]},
        ]
        payload, _, markdown = self.render(
            run={**RUN, "requested_games": 5, "goal_seat": 1}, decks=decks, games=games,
        )

        self.assertEqual(payload["games"][1]["meren_recursion"][0]["events"], [])
        self.assertIn("Observed in **3 of 4** completed games with Meren.", markdown)
        self.assertIn("| Games with targeted triggers | **2 of 3** observed |", markdown)
        self.assertIn("| First targeted trigger (Forge game turn) | **Turn 5 (median)** across 2 games |", markdown)
        self.assertIn("| Targets | **4** |", markdown)
        self.assertIn("| Matched resolutions | **3** |", markdown)
        self.assertIn("| Confirmed battlefield returns | **1** |", markdown)
        self.assertIn("| Resolved, destination unknown | **2** |", markdown)
        self.assertIn("| Resolution unconfirmed | **1** |", markdown)
        self.assertIn("including returns to hand", markdown)
        self.assertNotIn("Confirmed hand", markdown)
        self.assertLess(markdown.index("### How the deck played"), markdown.index("### Meren recursion"))
        self.assertLess(markdown.index("### Meren recursion"), markdown.index("### Game-by-game"))
        self.assertIn("| 1 · 42 | 4 | Sakura-Tribe Elder | Returned to battlefield | "
                      "[stdout](games/01/simulation.stdout.log) · L100, L101, L103 |", markdown)
        self.assertIn("| 3 · 44 | 9 | Sakura-Tribe Elder | Resolved, destination unknown | "
                      "[stdout](games/03/simulation.stdout.log) · L400, L401 |", markdown)
        self.assertIn("| 3 · 44 | 6 | Plaguecrafter | Resolution unconfirmed | "
                      "[stdout](games/03/simulation.stdout.log) · L300 |", markdown)
        self.assertNotIn("Excluded", markdown)

    def test_merens_recursion_reports_zero_targets_and_missing_coverage(self):
        decks = [{**DECKS[0], "commander": MEREN}, *DECKS[1:]]
        _, _, zero = self.render(
            run={**RUN, "goal_seat": 1}, decks=decks,
            games=[{**game(1, "draw"), "meren_recursion": [{"seat": 1, "events": []}]}],
        )
        self.assertIn("Observed in **1 of 1** completed games with Meren.", zero)
        self.assertIn("| Targets | **0** |", zero)
        self.assertIn("No targeted triggers were logged in the observed games.", zero)
        _, _, missing = self.render(
            run={**RUN, "goal_seat": 1}, decks=decks, games=[game(1, "won", "Ramp")],
        )
        self.assertIn("Observed in **0 of 1** completed games with Meren.", missing)
        self.assertIn("Recursion data unavailable for these games.", missing)
        self.assertNotIn("| Targets | **0** |", missing)

    def test_recursion_section_only_appears_for_designated_merens_deck(self):
        decks = [{**DECKS[0], "commander": MEREN}, *DECKS[1:]]
        sample = {**game(1, "won", "Ramp"), "meren_recursion": [{"seat": 1, "events": []}]}
        _, _, other_goal = self.render(run={**RUN, "goal_seat": 2}, decks=decks, games=[sample])
        _, _, no_goal = self.render(decks=decks, games=[sample])
        self.assertNotIn("### Meren recursion", other_goal)
        self.assertNotIn("### Meren recursion", no_goal)

    def test_winless_takeaways_show_all_most_frequent_opposing_winners(self):
        renamed = "Aggro | <attack>"
        decks = [DECKS[0], {**DECKS[1], "name": renamed}, *DECKS[2:]]
        games = [
            {**game(number, "won", winner), "seats": [deck["name"] for deck in decks]}
            for number, winner in enumerate((renamed, "Control", "Midrange", renamed, "Control"), 1)
        ]
        _, _, markdown = self.render(run={**RUN, "requested_games": 5, "goal_seat": 1}, decks=decks, games=games)

        self.assertIn(
            "| No wins in **5** completed games. | **Aggro &#124; &lt;attack&gt;, Control** tied for the most "
            "wins in goal-deck losses (**2 each**). |",
            markdown,
        )

    def test_takeaways_report_a_table_lead_and_distinguish_lossless_from_draw_only(self):
        for outcomes, expected in (
            (["Ramp", "Ramp"], "Led the lineup with **2** wins."),
            ([None, None], "No wins in **2** completed games."),
        ):
            with self.subTest(outcomes=outcomes):
                games = [game(number, "won" if winner else "draw", winner) for number, winner in enumerate(outcomes, 1)]
                _, _, markdown = self.render(run={**RUN, "requested_games": 2, "goal_seat": 1}, games=games)

                self.assertIn(f"| {expected} | No losses in completed games. |", markdown)

    def test_takeaways_credit_wins_without_claiming_a_lead(self):
        games = [game(number, "won", winner) for number, winner in enumerate(("Ramp", "Aggro", "Aggro"), 1)]
        _, _, markdown = self.render(run={**RUN, "requested_games": 3, "goal_seat": 1}, games=games)

        self.assertIn(
            "| Recorded **1** win in this batch. | **Aggro** won **2 of 2** games the goal deck lost. |",
            markdown,
        )

    def test_setup_failure_still_writes_three_reports_with_zero_attempts(self):
        run = {**RUN, "batch_error": "Deck validation failed", "goal_seat": 3}
        payload, rows, markdown = self.render(run=run, decks=[], games=[])

        self.assertEqual(payload["counts"]["requested"], 4)
        self.assertEqual(payload["counts"]["attempted"], 0)
        self.assertEqual(payload["counts"]["completed"], 0)
        self.assertEqual(payload["decks"], [])
        self.assertEqual(rows, [])
        self.assertIn("## Goal deck · Seat 3\n\nDeck details unavailable.", markdown)
        self.assertIn("> Deck validation failed", markdown)
        self.assertIn("| **0 / 4** | 0 | 0 | 0 | 0 | 31.5 s |", markdown)
        self.assertIn("[setup](logs/setup.log)", markdown)

    def test_zero_completed_games_has_unavailable_win_rate(self):
        payload, _, markdown = self.render(
            run={**RUN, "goal_seat": 1}, games=[game(1, "failed", reason="Invalid deck")],
        )

        self.assertTrue(all(deck["win_rate"] is None for deck in payload["decks"]))
        self.assertIn("| **Unavailable** | **0** | 0 | 0 | 0 |", markdown)
        self.assertIn("### Pros and cons\n\nNo completed games for the goal deck yet.", markdown)
        self.assertNotIn("| Pros | Cons |", markdown)
        self.assertIn("| **Ramp** | Unavailable | 0 | 0 | 0 | 0 |", markdown)

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
