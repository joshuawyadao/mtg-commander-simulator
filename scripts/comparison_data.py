"""Validate two Commander batches and build matched-seed A/B dashboard data."""

from statistics import median
import re

from .game_telemetry import EARLY_TURN_LIMIT


SEATS = {1, 2, 3, 4}
COMPLETED = {"win", "loss", "draw"}
RUN_SETTINGS = (
    "requested_games", "base_seed", "game_clock_seconds",
    "process_deadline_seconds", "forge_version", "java_version", "source_commit",
)


def _integer(value):
    return type(value) is int


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _telemetry(game, seat, label):
    entries = game.get("telemetry")
    if entries is None:
        return None
    _require(isinstance(entries, list), f"{label}: telemetry must be a list or null")
    selected = [entry for entry in entries if isinstance(entry, dict) and entry.get("seat") == seat]
    _require(len(selected) <= 1, f"{label}: duplicate goal-seat telemetry")
    if not selected:
        return None
    entry = selected[0]
    _require("first_commander_cast_turn" in entry, f"{label}: missing first commander cast field")
    cast = entry.get("first_commander_cast_turn")
    lands = entry.get("early_land_plays")
    turns = entry.get("early_turns_observed")
    damage = entry.get("combat_damage_taken")
    _require(cast is None or (_integer(cast) and cast > 0), f"{label}: invalid first commander cast turn")
    _require(_integer(turns) and 0 <= turns <= EARLY_TURN_LIMIT,
             f"{label}: invalid early turns observed")
    _require(_integer(lands) and lands >= 0 and (turns > 0 or lands == 0),
             f"{label}: invalid early land plays")
    _require(_integer(damage) and damage >= 0, f"{label}: invalid combat damage taken")
    return entry


def _validate(payload, version):
    _require(isinstance(payload, dict), f"Version {version}: results must be an object")
    run = payload.get("run")
    _require(isinstance(run, dict), f"Version {version}: missing run object")
    for field in (*RUN_SETTINGS, "goal_seat"):
        _require(field in run, f"Version {version}: run is missing {field}")
    _require(_integer(run["requested_games"]) and run["requested_games"] > 0,
             f"Version {version}: requested_games must be a positive integer")
    _require(_integer(run["base_seed"]) and run["base_seed"] >= 0,
             f"Version {version}: base_seed must be a nonnegative integer")
    _require(_integer(run["goal_seat"]) and run["goal_seat"] in SEATS,
             f"Version {version}: goal_seat must be 1 through 4")
    for field in ("game_clock_seconds", "process_deadline_seconds"):
        _require(_integer(run[field]) and run[field] > 0,
                 f"Version {version}: {field} must be a positive integer")
    for field in ("forge_version", "java_version"):
        _require(isinstance(run[field], str) and bool(run[field]),
                 f"Version {version}: {field} must be present")
    _require(run["source_commit"] is None or
             (isinstance(run["source_commit"], str) and bool(run["source_commit"])),
             f"Version {version}: source_commit must be a commit or null")

    deck_rows = payload.get("decks")
    _require(isinstance(deck_rows, list), f"Version {version}: decks must be a list")
    decks = {}
    for deck in deck_rows:
        _require(isinstance(deck, dict) and _integer(deck.get("seat")) and deck["seat"] in SEATS,
                 f"Version {version}: every deck must have a seat from 1 through 4")
        seat = deck["seat"]
        _require(seat not in decks, f"Version {version}: duplicate deck seat {seat}")
        for field in ("name", "commander", "ai_profile", "sha256"):
            _require(isinstance(deck.get(field), str) and bool(deck[field]),
                     f"Version {version}: seat {seat} is missing {field}")
        _require(re.fullmatch(r"[0-9a-fA-F]{64}", deck["sha256"]) is not None,
                 f"Version {version}: seat {seat} sha256 must be 64 hex digits")
        decks[seat] = deck
    _require(set(decks) == SEATS, f"Version {version}: decks must contain exactly seats 1 through 4")
    names = [decks[seat]["name"] for seat in sorted(SEATS)]
    _require(len(set(names)) == 4, f"Version {version}: deck names must be unique")

    game_rows = payload.get("games")
    _require(isinstance(game_rows, list), f"Version {version}: games must be a list")
    games = {}
    for game in game_rows:
        _require(isinstance(game, dict), f"Version {version}: each game must be an object")
        seed = game.get("seed")
        _require(_integer(seed) and run["base_seed"] <= seed < run["base_seed"] + run["requested_games"],
                 f"Version {version}: unexpected game seed {seed!r}")
        _require(seed not in games, f"Version {version}: duplicate game seed {seed}")
        number = seed - run["base_seed"] + 1
        _require(game.get("game") == number and _integer(game.get("game")),
                 f"Version {version}: seed {seed} must be game {number}")
        _require(game.get("seats") == names,
                 f"Version {version}: seed {seed} seat names do not match the lineup")
        status = game.get("status")
        _require(isinstance(status, str) and status in {"won", "draw", "failed", "timeout"},
                 f"Version {version}: seed {seed} has invalid status {status!r}")
        winner = game.get("winner")
        if status == "won":
            _require(winner in names, f"Version {version}: seed {seed} winner is not in the lineup")
        else:
            _require(winner is None, f"Version {version}: seed {seed} {status} must have no winner")
        _require(game.get("reason") is None or isinstance(game["reason"], str),
                 f"Version {version}: seed {seed} reason must be text or null")
        games[seed] = game
    return run, decks, games


def _pair_side(game, goal, version):
    if game is None:
        return {"outcome": "missing", "winner": None, "reason": None, "telemetry": None}
    status = game["status"]
    outcome = ("win" if game["winner"] == goal["name"] else "loss") if status == "won" else status
    telemetry = _telemetry(game, goal["seat"], f"Version {version}, seed {game['seed']}") if outcome in COMPLETED else None
    return {"outcome": outcome, "winner": game["winner"],
            "reason": game.get("reason"), "telemetry": telemetry}


def _metric(label, unit, pairs, value, aggregate):
    values_a = [value(pair["a"]["telemetry"], pair["a"]) for pair in pairs]
    values_b = [value(pair["b"]["telemetry"], pair["b"]) for pair in pairs]
    selected = [(a, b) for a, b in zip(values_a, values_b) if a is not None and b is not None]
    return {"label": label, "unit": unit,
            "a": aggregate([a for a, _ in selected]) if selected else None,
            "b": aggregate([b for _, b in selected]) if selected else None,
            "n": len(selected)}


def build_comparison(version_a: dict, version_b: dict) -> dict:
    """Compare only matched scheduled seeds under identical simulation conditions."""
    run_a, decks_a, games_a = _validate(version_a, "A")
    run_b, decks_b, games_b = _validate(version_b, "B")
    _require(run_a["goal_seat"] == run_b["goal_seat"], "Goal seat differs between versions")
    for field in RUN_SETTINGS:
        _require(run_a[field] == run_b[field], f"Run setting {field} differs between versions")
    goal_seat = run_a["goal_seat"]
    for field in ("commander", "ai_profile"):
        _require(decks_a[goal_seat][field] == decks_b[goal_seat][field],
                 f"Goal deck {field} differs between versions")
    for seat in sorted(SEATS - {goal_seat}):
        for field in ("name", "commander", "ai_profile", "sha256"):
            _require(decks_a[seat][field] == decks_b[seat][field],
                     f"Opponent seat {seat} {field} differs between versions")

    pairs = []
    for seed in range(run_a["base_seed"], run_a["base_seed"] + run_a["requested_games"]):
        pairs.append({"seed": seed,
                      "a": _pair_side(games_a.get(seed), decks_a[goal_seat], "A"),
                      "b": _pair_side(games_b.get(seed), decks_b[goal_seat], "B")})
    completed = [pair for pair in pairs if pair["a"]["outcome"] in COMPLETED
                 and pair["b"]["outcome"] in COMPLETED]
    percent = lambda values: 100 * sum(values) / len(values)
    metrics = [
        _metric("Win rate", "%", completed,
                lambda telemetry, side: int(side["outcome"] == "win"), percent),
        _metric("Commander cast rate", "%", completed,
                lambda telemetry, side: None if telemetry is None else
                int(telemetry["first_commander_cast_turn"] is not None), percent),
        _metric("Median first cast", "game turn", completed,
                lambda telemetry, side: None if telemetry is None else
                telemetry["first_commander_cast_turn"], median),
        _metric("Median early land plays", "plays", completed,
                lambda telemetry, side: None if telemetry is None or
                telemetry["early_turns_observed"] != EARLY_TURN_LIMIT else
                telemetry["early_land_plays"], median),
        _metric("Median combat damage taken", "damage", completed,
                lambda telemetry, side: None if telemetry is None else
                telemetry["combat_damage_taken"], median),
    ]
    return {"runs": {"a": run_a, "b": run_b},
            "decks": {"a": decks_a, "b": decks_b},
            "goal_seat": goal_seat, "pairs": pairs,
            "paired_completed": len(completed), "metrics": metrics}
