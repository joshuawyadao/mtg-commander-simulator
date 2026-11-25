"""Conservative Meren end-step observations from Forge 2.0.16 English logs."""

import re

from .game_telemetry import TURN

MEREN = "Meren of Clan Nel Toth"

_TARGET = re.compile(r"^(.+) \(([0-9]+)\)$")
_BATTLEFIELD_EXIT = re.compile(
    r"^Zone Change: (.+ \([0-9]+\)) was put into (?:Graveyard|Exile) from Battlefield\."
)
_END_STEP_RESOLUTION = "Resolve Stack: At the beginning of your end step, choose target creature card in your graveyard."
_RESOLUTION_TARGET = re.compile(r"\(Targeting: \[\[(.+ \([0-9]+\))\]\]\) \[Phase: (.+)\]$")
_MAX_EVIDENCE_LINES = 12


def parse_meren_recursion(stdout: str, decks: list[dict]) -> list[dict]:
    """Report witnessed Meren targets and only corroborated destinations.

    ``resolution_line`` records the matched end-step ability, even when Forge does
    not expose the resulting zone. A missing resolution is left unknown.
    """
    identities = {f"Ai({deck['seat']})-{deck['name']}": {"seat": deck["seat"], "events": []}
                  for deck in decks if deck.get("commander") == MEREN}
    if not identities:
        return []
    end_steps = {f"Phase: {identity}{possessive} End step": identity
                 for identity in identities for possessive in ("'s", "'")}
    turn = 0
    phase_owner = None
    pending = {}
    evidence = None

    for line_number, line in enumerate(stdout.splitlines(), 1):
        turn_match = TURN.fullmatch(line)
        if turn_match:
            turn = int(turn_match[1])
            phase_owner = None
            pending.clear()
            evidence = None
            continue
        if line.startswith("Phase:"):
            phase_owner = end_steps.get(line)
            pending.clear()
            evidence = None
            continue
        if phase_owner is None or turn == 0:
            continue

        trigger_prefix = f"Add To Stack: {phase_owner} triggered {MEREN} targeting ["
        if line.startswith(trigger_prefix) and line.endswith("]"):
            target = line[len(trigger_prefix):-1]
            match = _TARGET.fullmatch(target)
            if match:
                event = {
                    "turn": turn,
                    "target": match[1],
                    "trigger_line": line_number,
                    "resolution_line": None,
                    "destination": None,
                    "destination_line": None,
                }
                identities[phase_owner]["events"].append(event)
                pending.setdefault(target, []).append(event)
                evidence = None
            continue

        if line.startswith(_END_STEP_RESOLUTION):
            match = _RESOLUTION_TARGET.search(line)
            if match and match[2] == phase_owner and pending.get(match[1]):
                target = match[1]
                event = pending[target].pop()
                event["resolution_line"] = line_number
                evidence = (target, event, False)
            else:
                evidence = None
            continue

        if evidence is None:
            continue
        target, event, enter_trigger = evidence
        if line_number - event["resolution_line"] > _MAX_EVIDENCE_LINES:
            evidence = None
            continue
        # The indirect enter evidence must belong to the same immediate stack
        # action. Later casts and reanimation may reuse the same card instance.
        if line.startswith("Add To Stack:"):
            enter_prefix = f"Add To Stack: {phase_owner} triggered {event['target']}"
            if line == enter_prefix or line.startswith(f"{enter_prefix} targeting "):
                evidence = (target, event, True)
            else:
                evidence = None
            continue

        zone = _BATTLEFIELD_EXIT.fullmatch(line)
        if zone and zone[1] == target:
            event["destination"] = "battlefield"
            event["destination_line"] = line_number
            evidence = None
            continue

        if (enter_trigger and line.startswith("Resolve Stack:")
                and f"When {event['target']} enters" in line
                and line.endswith(f"[Zone Changer: {target}]")):
            event["destination"] = "battlefield"
            event["destination_line"] = line_number
            evidence = None
            continue

        # Keep the enter stack action short; unrelated resolutions cannot
        # corroborate Meren's return even if they mention the same card ID.
        if line.startswith("Resolve Stack:"):
            evidence = None

    return list(identities.values())
