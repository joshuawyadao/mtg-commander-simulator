"""Read per-seat telemetry from the pinned Forge 2.0.16 English game log."""

import re


EARLY_TURN_LIMIT = 4
TURN = re.compile(r"^Turn: Turn ([1-9][0-9]*) \((Ai\([1-9][0-9]*\)-.+)\)$")
DAMAGE = re.compile(r"^Damage: .+ deals ([0-9]+) combat damage to (Ai\([1-9][0-9]*\)-.+)\.$")


def parse_telemetry(stdout: str, decks: list[dict]) -> list[dict] | None:
    """Return input-seat-order metrics when the complete turn stream is recognizable."""
    records = [
        {
            "seat": deck["seat"],
            "first_commander_cast_turn": None,
            "early_land_plays": 0,
            "early_turns_observed": 0,
            "combat_damage_taken": 0,
        }
        for deck in decks
    ]
    identities = {
        f"Ai({deck['seat']})-{deck['name']}": (deck, record)
        for deck, record in zip(decks, records, strict=True)
    }
    turn_number = 0
    turn_owner = None
    early_turn = False

    for line in stdout.splitlines():
        if line.startswith("Turn:"):
            match = TURN.fullmatch(line)
            if match is None or int(match[1]) != turn_number + 1 or match[2] not in identities:
                return None
            turn_number += 1
            turn_owner = match[2]
            record = identities[turn_owner][1]
            early_turn = record["early_turns_observed"] < EARLY_TURN_LIMIT
            if early_turn:
                record["early_turns_observed"] += 1
            continue

        if line.startswith("Game Result:"):
            return records if turn_number else None

        if turn_number == 0:
            continue

        if line.startswith("Land:"):
            for identity, (_, record) in identities.items():
                if line.startswith(f"Land: {identity} played "):
                    if turn_owner == identity and early_turn:
                        record["early_land_plays"] += 1
                    break
            continue

        if line.startswith("Add To Stack:"):
            for identity, (deck, record) in identities.items():
                cast = f"Add To Stack: {identity} cast {deck['commander']}"
                if record["first_commander_cast_turn"] is None and (
                    line == cast or line.startswith(f"{cast} targeting ")
                ):
                    record["first_commander_cast_turn"] = turn_number
                    break
            continue

        if line.startswith("Damage:"):
            match = DAMAGE.fullmatch(line)
            if match is not None:
                target = match[2]
                if target not in identities:
                    target = target.removesuffix("(as poison counters)")
                if target in identities:
                    identities[target][1]["combat_damage_taken"] += int(match[1])

    return None
