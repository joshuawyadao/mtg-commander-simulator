"""Conservative Meren recursion evidence from Forge's chronological log."""

import unittest

from scripts.meren_recursion import MEREN, parse_meren_recursion


GOAL = "Ai(3)-Golgari Graveyard Recursion"
OTHER = "Ai(4)-Other Meren Deck"
DECKS = [
    {"seat": 1, "name": "Green Ramp", "commander": "Ezuri, Renegade Leader"},
    {"seat": 3, "name": "Golgari Graveyard Recursion", "commander": MEREN},
    {"seat": 4, "name": "Other Meren Deck", "commander": MEREN},
]
RULES = ("At the beginning of your end step, choose target creature card in your graveyard. "
         "If that card's mana value is less than or equal to the number of experience counters "
         "you have, return it to the battlefield. Otherwise, put it into your hand.")


def trigger(owner, target):
    return f"Add To Stack: {owner} triggered {MEREN} targeting [{target}]"


def resolve(owner, target):
    return f"Resolve Stack: {RULES} (Targeting: [[{target}]]) [Phase: {owner}]"


def event(turn, target, trigger_line, resolution_line=None, destination=None,
          destination_line=None):
    return {"turn": turn, "target": target, "trigger_line": trigger_line,
            "resolution_line": resolution_line, "destination": destination,
            "destination_line": destination_line}


class MerenRecursionTests(unittest.TestCase):
    def test_no_meren_deck(self):
        self.assertEqual(parse_meren_recursion("", DECKS[:1]), [])

    def test_exact_target_resolution_and_enter_evidence(self):
        lines = [
            f"Turn: Turn 1 ({GOAL})",
            f"Phase: {GOAL}'s End step",
            f"Add To Stack: {GOAL} triggered {MEREN}",  # Experience trigger.
            trigger(GOAL, "Noxious Gearhulk (275)"),
            resolve(GOAL, "Noxious Gearhulk (275)"),
            f"Add To Stack: {GOAL} triggered Noxious Gearhulk targeting [Elf (6)]",
            "Zone Change: Elf (6) was put into Graveyard from Battlefield.",
            "Resolve Stack: When Noxious Gearhulk enters, destroy target. "
            "(Targeting: [[Elf (6)]]) [Zone Changer: Noxious Gearhulk (275)]",
        ]
        self.assertEqual(parse_meren_recursion("\n".join(lines), DECKS), [
            {"seat": 3, "events": [event(1, "Noxious Gearhulk", 4, 5, "battlefield", 8)]},
            {"seat": 4, "events": []},
        ])

    def test_generic_resolution_only_keeps_destination_unknown(self):
        lines = [f"Turn: Turn 1 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Shriekmaw (262)"), resolve(GOAL, "Shriekmaw (262)"),
                 f"Phase: {GOAL}'s Cleanup step",
                 f"Turn: Turn 2 ({GOAL})", f"Phase: {GOAL}'s Main phase, precombat",
                 f"Add To Stack: {GOAL} cast Shriekmaw",
                 "Resolve Stack: When Shriekmaw enters, destroy a creature. "
                 "[Zone Changer: Shriekmaw (262)]"]
        self.assertEqual(parse_meren_recursion("\n".join(lines), DECKS)[0]["events"],
                         [event(1, "Shriekmaw", 3, 4)])

    def test_immediate_battlefield_exit_and_unobserved_hand_transfer(self):
        lines = [f"Turn: Turn 1 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Sakura-Tribe Elder (286)"),
                 resolve(GOAL, "Sakura-Tribe Elder (286)"),
                 "Zone Change: Sakura-Tribe Elder (286) was put into Graveyard from Battlefield.",
                 f"Turn: Turn 2 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Shriekmaw (262)"), resolve(GOAL, "Shriekmaw (262)"),
                 "Zone Change: Shriekmaw (262) was put into Hand from Graveyard."]
        self.assertEqual(parse_meren_recursion("\n".join(lines), DECKS)[0]["events"], [
            event(1, "Sakura-Tribe Elder", 3, 4, "battlefield", 5),
            event(2, "Shriekmaw", 8, 9),
        ])

    def test_missing_resolution_and_target_or_owner_mismatch(self):
        lines = [f"Turn: Turn 1 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Shriekmaw (262)"),
                 resolve(GOAL, "Shriekmaw (263)"),
                 resolve(OTHER, "Shriekmaw (262)"),
                 f"Phase: {GOAL}'s Cleanup step",
                 f"Phase: {OTHER}'s End step",
                 trigger(OTHER, "Shriekmaw (262)"), resolve(OTHER, "Shriekmaw (262)"),
                 "Zone Change: Shriekmaw (263) was put into Hand from Graveyard."]
        self.assertEqual(parse_meren_recursion("\n".join(lines), DECKS), [
            {"seat": 3, "events": [event(1, "Shriekmaw", 3)]},
            {"seat": 4, "events": [event(1, "Shriekmaw", 8, 9)]},
        ])

    def test_repeats_are_separate_and_later_stack_actions_do_not_confirm(self):
        lines = [f"Turn: Turn 1 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Izoni, Thousand-Eyed (289)"),
                 resolve(GOAL, "Izoni, Thousand-Eyed (289)"),
                 f"Add To Stack: {GOAL} cast Reanimate",
                 f"Add To Stack: {GOAL} triggered Izoni, Thousand-Eyed",
                 "Resolve Stack: When Izoni, Thousand-Eyed enters, create tokens. "
                 "[Zone Changer: Izoni, Thousand-Eyed (289)]",
                 f"Turn: Turn 2 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Izoni, Thousand-Eyed (289)"),
                 resolve(GOAL, "Izoni, Thousand-Eyed (289)"),
                 f"Add To Stack: {GOAL} triggered Izoni, Thousand-Eyed",
                 "Resolve Stack: When Izoni, Thousand-Eyed enters, create tokens. "
                 "[Zone Changer: Izoni, Thousand-Eyed (289)]"]
        self.assertEqual(parse_meren_recursion("\n".join(lines), DECKS)[0]["events"], [
            event(1, "Izoni, Thousand-Eyed", 3, 4),
            event(2, "Izoni, Thousand-Eyed", 10, 11, "battlefield", 13),
        ])

    def test_two_pending_targets_resolve_against_their_own_card_instances(self):
        lines = [f"Turn: Turn 1 ({GOAL})", f"Phase: {GOAL}'s End step",
                 trigger(GOAL, "Shriekmaw (262)"), trigger(GOAL, "Shriekmaw (263)"),
                 resolve(GOAL, "Shriekmaw (263)"), resolve(GOAL, "Shriekmaw (262)")]
        self.assertEqual(parse_meren_recursion("\n".join(lines), DECKS)[0]["events"], [
            event(1, "Shriekmaw", 3, 6), event(1, "Shriekmaw", 4, 5),
        ])


if __name__ == "__main__":
    unittest.main()
