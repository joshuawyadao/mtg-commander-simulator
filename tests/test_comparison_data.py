"""Matched-seed validation and metric coverage for Phase 4 comparisons."""

from copy import deepcopy
import unittest

from scripts.comparison_data import build_comparison


def telemetry(cast, lands=0, turns=4, damage=0):
    return [{"seat": 3, "first_commander_cast_turn": cast,
             "early_land_plays": lands, "early_turns_observed": turns,
             "combat_damage_taken": damage}]


def result():
    decks = [
        {"seat": seat, "name": name, "commander": commander,
         "ai_profile": "Forge default", "sha256": str(seat) * 64}
        for seat, name, commander in (
            (1, "Ramp", "Ezuri"), (2, "Aggro", "Krenko"),
            (3, "Meren A", "Meren of Clan Nel Toth"), (4, "Control", "Brago"))
    ]
    return {"run": {"goal_seat": 3, "requested_games": 5, "base_seed": 42,
                    "game_clock_seconds": 600, "process_deadline_seconds": 720,
                    "forge_version": "2.0.16", "java_version": "OpenJDK 17",
                    "source_commit": "abc123"},
            "decks": decks, "games": []}


def game(payload, number, status="won", winner="Meren A", seen=None, reason=None):
    return {"game": number, "seed": 41 + number,
            "seats": [deck["name"] for deck in payload["decks"]],
            "status": status, "winner": winner if status == "won" else None,
            "reason": reason, "telemetry": seen}


class ComparisonDataTests(unittest.TestCase):
    def test_metrics_share_matched_denominators_and_keep_zero_values(self):
        a = result()
        b = deepcopy(a)
        b["decks"][2]["name"] = "Meren B"
        b["decks"][2]["sha256"] = "f" * 64
        a["games"] = [
            game(a, 1, seen=telemetry(3, 3, 4, 0)),
            game(a, 2, winner="Aggro", seen=telemetry(None, 0, 4, 4)),
            game(a, 3, status="draw", seen=telemetry(5, 1, 2, 8)),
            game(a, 4, status="timeout", seen=telemetry(2, 4, 4, 99)),
        ]
        b["games"] = [
            game(b, 1, winner="Aggro", seen=telemetry(4, 2, 4, 2)),
            game(b, 2, winner="Meren B", seen=telemetry(None, 0, 4, 0)),
            game(b, 3, status="draw", seen=telemetry(None, 4, 4, 0)),
            game(b, 5, status="failed", reason="Forge error"),
        ]
        a["games"][3].pop("winner")

        comparison = build_comparison(a, b)
        self.assertEqual(set(comparison), {"runs", "decks", "goal_seat", "pairs",
                                           "paired_completed", "metrics"})
        self.assertIs(comparison["runs"]["a"], a["run"])
        self.assertIs(comparison["decks"]["b"][3], b["decks"][2])
        self.assertEqual(comparison["goal_seat"], 3)
        self.assertEqual(comparison["paired_completed"], 3)
        self.assertEqual([row["seed"] for row in comparison["pairs"]], [42, 43, 44, 45, 46])
        self.assertEqual([row["a"]["outcome"] for row in comparison["pairs"]],
                         ["win", "loss", "draw", "timeout", "missing"])
        self.assertEqual([row["b"]["outcome"] for row in comparison["pairs"]],
                         ["loss", "win", "draw", "missing", "failed"])
        self.assertIsNone(comparison["pairs"][3]["a"]["telemetry"])
        self.assertEqual(comparison["pairs"][4]["b"]["reason"], "Forge error")
        self.assertEqual(comparison["metrics"], [
            {"label": "Win rate", "unit": "%", "a": 100 / 3, "b": 100 / 3, "n": 3},
            {"label": "Commander cast rate", "unit": "%", "a": 200 / 3,
             "b": 100 / 3, "n": 3},
            {"label": "Median first cast", "unit": "game turn", "a": 3,
             "b": 4, "n": 1},
            {"label": "Median early land plays", "unit": "plays", "a": 1.5,
             "b": 1, "n": 2},
            {"label": "Median combat damage taken", "unit": "damage", "a": 4,
             "b": 0, "n": 3},
        ])

    def test_no_completed_pairs_have_nullable_metrics(self):
        a = result()
        b = deepcopy(a)
        a["run"]["source_commit"] = b["run"]["source_commit"] = None
        a["games"] = [game(a, 1, status="failed")]
        b["games"] = [game(b, 1, status="timeout")]
        comparison = build_comparison(a, b)
        self.assertEqual(comparison["paired_completed"], 0)
        self.assertTrue(all(metric["a"] is None and metric["b"] is None and metric["n"] == 0
                            for metric in comparison["metrics"]))

    def test_no_cast_is_zero_rate_and_null_cast_median(self):
        a = result()
        b = deepcopy(a)
        a["games"] = [game(a, 1, seen=telemetry(None, 0, 4, 0))]
        b["games"] = [game(b, 1, seen=telemetry(None, 0, 4, 0))]
        comparison = build_comparison(a, b)
        self.assertEqual(comparison["metrics"][1],
                         {"label": "Commander cast rate", "unit": "%", "a": 0.0, "b": 0.0, "n": 1})
        self.assertEqual(comparison["metrics"][2]["n"], 0)
        self.assertIsNone(comparison["metrics"][2]["a"])
        self.assertEqual(comparison["metrics"][4]["a"], 0)

    def test_rejects_incompatible_run_goal_and_opponents(self):
        changes = [
            (lambda b: b["run"].update(base_seed=43), "base_seed"),
            (lambda b: b["run"].update(source_commit="different"), "source_commit"),
            (lambda b: b["run"].update(goal_seat=2), "Goal seat"),
            (lambda b: b["decks"][2].update(commander="Other"), "Goal deck commander"),
            (lambda b: b["decks"][0].update(sha256="a" * 64), "Opponent seat 1 sha256"),
            (lambda b: b["decks"][1].update(ai_profile="Other"), "Opponent seat 2 ai_profile"),
        ]
        for change, message in changes:
            with self.subTest(message=message):
                a, b = result(), result()
                change(b)
                with self.assertRaisesRegex(ValueError, message):
                    build_comparison(a, b)

    def test_rejects_bad_scheduled_rows_and_seat_metadata(self):
        changes = [
            (lambda a: a["games"].append(deepcopy(a["games"][0])), "duplicate game seed"),
            (lambda a: a["games"][0].update(seed=99), "unexpected game seed"),
            (lambda a: a["games"][0].update(game=2), "must be game 1"),
            (lambda a: a["games"][0].update(seats=["wrong"] * 4), "seat names"),
            (lambda a: a["games"][0].update(winner="unknown"), "winner"),
            (lambda a: a["games"][0].update(status=[]), "invalid status"),
            (lambda a: a["games"][0].update(telemetry=[{"seat": 3}]), "missing first commander cast"),
            (lambda a: a["decks"].append(deepcopy(a["decks"][0])), "duplicate deck seat"),
        ]
        for change, message in changes:
            with self.subTest(message=message):
                a, b = result(), result()
                a["games"] = [game(a, 1)]
                change(a)
                with self.assertRaisesRegex(ValueError, message):
                    build_comparison(a, b)

    def test_multiple_land_plays_in_one_turn_are_valid(self):
        a, b = result(), result()
        a["games"] = [game(a, 1, seen=telemetry(2, 2, 1, 0))]
        b["games"] = [game(b, 1, seen=telemetry(3, 2, 1, 0))]
        comparison = build_comparison(a, b)
        self.assertEqual(comparison["paired_completed"], 1)
        self.assertEqual(comparison["metrics"][3]["n"], 0)


if __name__ == "__main__":
    unittest.main()
