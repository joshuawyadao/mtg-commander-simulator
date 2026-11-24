"""Observable Forge log contracts for the first Phase 3 metrics."""

import unittest

from scripts.game_telemetry import EARLY_TURN_LIMIT, parse_telemetry


DECKS = [
    {"seat": 1, "name": "Green Ramp", "commander": "Ezuri, Renegade Leader"},
    {"seat": 2, "name": "Red Aggro", "commander": "Pashalik Mons"},
    {"seat": 3, "name": "Golgari Graveyard Recursion", "commander": "Meren of Clan Nel Toth"},
    {"seat": 4, "name": "Azorius Control", "commander": "Isperia, Supreme Judge"},
]
GOAL = "Ai(3)-Golgari Graveyard Recursion"
CONTROL = "Ai(4)-Azorius Control"


def game_log(*events):
    return "\n".join([*events, "Game Result: Game 1 ended in 1000 ms. Ai(3)-Golgari Graveyard Recursion has won!"])


class GameTelemetryTests(unittest.TestCase):
    def test_first_cast_early_lands_and_combat_damage_follow_exact_seats(self):
        lines = [
            f"Turn: Turn 1 ({GOAL})",
            f"Land: {GOAL} played Forest (12)",
            f"Land: {GOAL} played Swamp (13)",
            f"Add To Stack: {GOAL} triggered Meren of Clan Nel Toth",
            "Damage: Angel (20) deals 2 combat damage to Ai(1)-Green Ramp.",
            f"Turn: Turn 2 ({CONTROL})",
            f"Land: {GOAL} played Forest (14)",
            f"Damage: Spirit (21) deals 4 combat damage to {GOAL}.",
            f"Damage: Spirit (21) deals 2 combat damage to {GOAL}(as poison counters).",
            f"Damage: Spirit (21) deals 5 non-combat damage to {GOAL}.",
            "Damage: Spirit (21) deals 3 combat damage to Meren of Clan Nel Toth (22).",
            f"Turn: Turn 3 ({GOAL})",
            f"Add To Stack: {GOAL} cast Meren of Clan Nel Toth",
            f"Turn: Turn 4 ({GOAL})",
            f"Land: {GOAL} played Forest (25)",
            f"Turn: Turn 5 ({GOAL})",
            f"Land: {GOAL} played Forest (26)",
            f"Turn: Turn 6 ({GOAL})",
            f"Land: {GOAL} played Forest (27)",
            f"Add To Stack: {GOAL} cast Meren of Clan Nel Toth",
            f"Turn: Turn 7 ({GOAL})",
            f"Land: {GOAL} played Forest (28)",
        ]

        telemetry = parse_telemetry(game_log(*lines), DECKS)

        self.assertIsNotNone(telemetry)
        self.assertEqual(len(telemetry), len(DECKS))
        self.assertEqual(telemetry[0], {
            "seat": 1, "first_commander_cast_turn": None, "early_land_plays": 0,
            "early_turns_observed": 0, "combat_damage_taken": 2,
        })
        self.assertEqual(telemetry[2], {
            "seat": 3, "first_commander_cast_turn": 3, "early_land_plays": 4,
            "early_turns_observed": EARLY_TURN_LIMIT, "combat_damage_taken": 6,
        })

    def test_complete_log_with_no_cast_or_damage_reports_zero_and_none(self):
        telemetry = parse_telemetry(game_log(f"Turn: Turn 1 ({GOAL})"), DECKS)

        self.assertEqual(telemetry[2]["first_commander_cast_turn"], None)
        self.assertEqual(telemetry[2]["early_land_plays"], 0)
        self.assertEqual(telemetry[2]["early_turns_observed"], 1)
        self.assertEqual(telemetry[2]["combat_damage_taken"], 0)

    def test_unrecognized_or_incomplete_turn_stream_is_unavailable(self):
        for stdout in (
            "",
            f"Turn: Turn 1 ({GOAL})",
            game_log("Game Outcome: Turn 20"),
            game_log(f"Turn: Turn 2 ({GOAL})"),
            game_log(f"Turn: Turn 1 ({GOAL})", f"Turn: Turn 3 ({CONTROL})"),
            game_log("Turn: new format"),
            game_log("Turn: Turn 1 (Ai(9)-Other Deck)"),
        ):
            with self.subTest(stdout=stdout):
                self.assertIsNone(parse_telemetry(stdout, DECKS))

    def test_cast_name_must_match_exactly_and_may_have_a_target(self):
        lines = [
            f"Turn: Turn 1 ({GOAL})",
            f"Add To Stack: {GOAL} cast Meren of Clan Nel Toth's Familiar",
            f"Add To Stack: {GOAL} cast Meren of Clan Nel Toth targeting Ai(4)-Azorius Control",
        ]

        telemetry = parse_telemetry(game_log(*lines), DECKS)

        self.assertEqual(telemetry[2]["first_commander_cast_turn"], 1)


if __name__ == "__main__":
    unittest.main()
