"""Write human-readable and structured reports for a Commander simulation batch."""

from collections import Counter
import csv
from html import escape
import json
from pathlib import Path
import re
from statistics import median
from urllib.parse import quote

from .game_telemetry import EARLY_TURN_LIMIT
from .meren_recursion import MEREN


CSV_FIELDS = (
    "game", "seed", "seats", "status", "winner", "duration_ms", "wall_seconds",
    "reason", "forge_version", "returncode", "peak_rss_kib", "logs",
)
CSV_TEXT_FIELDS = {"status", "winner", "reason", "forge_version"}
GOAL_OUTCOMES = {
    "win": ("🟩", "W", "win"),
    "loss": ("🟥", "L", "loss"),
    "draw": ("🟨", "D", "draw"),
    "timeout": ("⏱️", "T", "timeout"),
    "failed": ("⚠️", "F", "failed"),
    "absent": ("⬜", "—", "deck absent"),
}


def _csv_text(value):
    """Keep spreadsheet software from evaluating imported deck names and diagnostics."""
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _markdown(value):
    if value is None:
        return "—"
    text = escape(str(value).replace("\r", " ").replace("\n", " "))
    return re.sub(r"[\[\]*_`\\~!|]", lambda match: f"&#{ord(match[0])};", text)


def _log_links(logs):
    links = []
    for label, path in logs.items():
        if not path:
            continue
        # Logs are paths inside the downloadable artifact, relative to summary.md.
        target = quote(str(path), safe="/")
        links.append(f"[{_markdown(label)}]({target})")
    return ", ".join(links) if links else "—"


def _goal_outcome(game, goal_name):
    if goal_name not in game["seats"]:
        return "absent"
    if game["status"] == "won":
        return "win" if game["winner"] == goal_name else "loss"
    return game["status"]


def _goal_takeaways(goal, games):
    heading = ["### Pros and cons", ""]
    completed = goal["completed_games"]
    if not completed:
        return [*heading, "No completed games for the goal deck yet.", ""]

    opponent_wins = Counter(game["winner"] for game in games if _goal_outcome(game, goal["name"]) == "loss")
    most = max(opponent_wins.values(), default=0)
    wins = goal["wins"]
    win_label = f"**{wins}** {'win' if wins == 1 else 'wins'}"
    if not wins:
        pro = f"No wins in **{completed}** completed {'game' if completed == 1 else 'games'}."
    elif wins > most:
        pro = f"Led the lineup with {win_label}."
    elif wins == most:
        pro = f"Tied for the lead with {win_label}."
    else:
        pro = f"Recorded {win_label} in this batch."

    leaders = sorted(name for name, count in opponent_wins.items() if count == most)
    if not leaders:
        con = "No losses in completed games."
    elif len(leaders) == 1:
        con = f"**{_markdown(leaders[0])}** won **{most} of {goal['losses']}** games the goal deck lost."
    else:
        names = ", ".join(_markdown(name) for name in leaders)
        con = f"**{names}** tied for the most wins in goal-deck losses (**{most} each**)."

    return [*heading, "| Pros | Cons |", "| --- | --- |", f"| {pro} | {con} |", ""]


def _goal_telemetry(game, goal):
    if game["status"] not in ("won", "draw") or goal["name"] not in game["seats"]:
        return None
    return next((entry for entry in game.get("telemetry") or [] if entry["seat"] == goal["seat"]), None)


def _telemetry_lines(goal, games):
    eligible = [game for game in games if game["status"] in ("won", "draw") and goal["name"] in game["seats"]]
    records = [entry for game in eligible if (entry := _goal_telemetry(game, goal)) is not None]
    heading = ["### How the deck played", ""]
    if not records:
        return [*heading, "Telemetry unavailable for this batch.", ""]

    casts = [entry["first_commander_cast_turn"] for entry in records
             if entry["first_commander_cast_turn"] is not None]
    full_windows = [
        entry["early_land_plays"] for entry in records if entry["early_turns_observed"] == EARLY_TURN_LIMIT
    ]
    cast_median = f"Turn {median(casts):g} (median)" if casts else "No casts observed"
    lands_median = f"{median(full_windows):g} plays (median)" if full_windows else "Unavailable"
    damage_median = f"{median(entry['combat_damage_taken'] for entry in records):g} damage"

    return [
        *heading,
        f"Telemetry from **{len(records)} of {len(eligible)}** completed games with the goal deck.", "",
        "| Metric | Result | Games measured |",
        "| --- | ---: | ---: |",
        f"| Commander cast | **{len(casts)} of {len(records)}** games | {len(records)} |",
        f"| First commander cast | **{cast_median}** | {len(casts)} casts |",
        f"| Land plays in first {EARLY_TURN_LIMIT} own turns | **{lands_median}** | {len(full_windows)} with "
        f"{EARLY_TURN_LIMIT} turns |",
        f"| Combat damage taken | **{damage_median}** (median) | {len(records)} |",
        "",
    ]


def _telemetry_details(goal, games):
    lines = [
        "<details>", "<summary>Goal deck telemetry by game</summary>", "",
        "| Game | Result | First commander cast | Land plays / own turns | Combat damage taken |",
        "| ---: | --- | --- | ---: | ---: |",
    ]
    for game in games:
        entry = _goal_telemetry(game, goal)
        if entry is None:
            first_cast = lands = damage = "Unavailable"
        else:
            turn = entry["first_commander_cast_turn"]
            first_cast = f"Turn {turn}" if turn is not None else "No cast"
            lands = f"{entry['early_land_plays']} / {entry['early_turns_observed']} (of first {EARLY_TURN_LIMIT})"
            damage = str(entry["combat_damage_taken"])
        lines.append(
            f"| {game['game']} | {_goal_outcome(game, goal['name'])} | {first_cast} | {lands} | {damage} |"
        )
    return [*lines, "", "</details>", ""]


def _meren_record(game, goal):
    if game["status"] not in ("won", "draw") or goal["name"] not in game["seats"]:
        return None
    return next((entry for entry in game.get("meren_recursion") or [] if entry["seat"] == goal["seat"]), None)


def _recursion_status(event):
    if event["resolution_line"] is None:
        return "Resolution unconfirmed"
    if event["destination"] == "battlefield":
        return "Returned to battlefield"
    return "Resolved, destination unknown"


def _recursion_examples(records):
    """Favor distinct games and show both a confirmed and an unknown result when available."""
    candidates = [
        (game, event) for game, record in records for event in record["events"]
    ]
    chosen = []
    used_games = set()
    for predicate in (
        lambda event: event["destination"] == "battlefield",
        lambda event: event["resolution_line"] is not None and event["destination"] is None,
        lambda event: event["resolution_line"] is None,
    ):
        match = next((item for item in candidates if predicate(item[1]) and item[0]["game"] not in used_games), None)
        if match is None:
            match = next((item for item in candidates if predicate(item[1]) and item not in chosen), None)
        if match is not None and match not in chosen:
            chosen.append(match)
            used_games.add(match[0]["game"])
    for item in candidates:
        if len(chosen) == 3:
            break
        if item not in chosen and item[0]["game"] not in used_games:
            chosen.append(item)
            used_games.add(item[0]["game"])
    for item in candidates:
        if len(chosen) == 3:
            break
        if item not in chosen:
            chosen.append(item)
    return chosen


def _meren_lines(goal, games):
    if goal.get("commander") != MEREN:
        return []
    eligible = [game for game in games if game["status"] in ("won", "draw") and goal["name"] in game["seats"]]
    records = [(game, record) for game in eligible if (record := _meren_record(game, goal)) is not None]
    lines = ["### Meren recursion", "", f"Observed in **{len(records)} of {len(eligible)}** completed games with Meren.", ""]
    if not records:
        return [*lines, "Recursion data unavailable for these games.", ""]

    events = [event for _, record in records for event in record["events"]]
    games_with_targets = sum(bool(record["events"]) for _, record in records)
    first_turns = [min(event["turn"] for event in record["events"]) for _, record in records if record["events"]]
    first_label = f"Turn {median(first_turns):g} (median)" if first_turns else "No targeted triggers observed"
    matched = sum(event["resolution_line"] is not None for event in events)
    battlefield = sum(event["destination"] == "battlefield" for event in events)
    unknown = sum(event["resolution_line"] is not None and event["destination"] is None for event in events)
    lines.extend([
        "| Logged target evidence | Result |", "| --- | ---: |",
        f"| Games with targeted triggers | **{games_with_targets} of {len(records)}** observed |",
        f"| First targeted trigger (Forge game turn) | **{first_label}** across {games_with_targets} games |",
        f"| Targets | **{len(events)}** |",
        f"| Matched resolutions | **{matched}** |",
        f"| Confirmed battlefield returns | **{battlefield}** |",
        f"| Resolved, destination unknown | **{unknown}** |",
        f"| Resolution unconfirmed | **{len(events) - matched}** |",
        "", "Forge's logs can leave the return destination unknown, including returns to hand.", "",
    ])
    examples = _recursion_examples(records)
    if not examples:
        return [*lines, "No targeted triggers were logged in the observed games.", ""]
    lines.extend([
        "#### Log examples", "",
        "| Game · seed | Turn | Target | Observed result | Raw stdout lines |",
        "| --- | ---: | --- | --- | --- |",
    ])
    for game, event in examples:
        line_numbers = [event["trigger_line"], event["resolution_line"], event["destination_line"]]
        refs = ", ".join(f"L{line}" for line in dict.fromkeys(line for line in line_numbers if line is not None))
        stdout = _log_links({"stdout": game.get("logs", {}).get("stdout")})
        lines.append(
            f"| {game['game']} · {_markdown(game['seed'])} | {event['turn']} | {_markdown(event['target'])} | "
            f"{_recursion_status(event)} | {stdout} · {refs} |"
        )
    return [*lines, "", "The workflow run under **Run settings and deck versions** provides the downloadable stdout.", ""]


def _goal_lines(goal, games):
    rate = goal["win_rate"]
    rate_label = f"{rate:.1%}" if rate is not None else "Unavailable"
    identity = [_markdown(goal.get("commander")), f"Seat {goal['seat']}"]
    if goal.get("archetype"):
        identity.append(_markdown(goal["archetype"]))
    lines = [
        f"## Goal deck · {_markdown(goal['name'])}", "",
        " · ".join(identity), "",
        "| Win rate | Wins | Losses | Draws | Completed games |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| **{rate_label}** | **{goal['wins']}** | {goal['losses']} | {goal['draws']} | {goal['completed_games']} |",
        "",
    ]
    lines.extend(_goal_takeaways(goal, games))
    lines.extend(_telemetry_lines(goal, games))
    lines.extend(_meren_lines(goal, games))
    if games:
        markers = []
        present = set()
        for game in games:
            outcome = _goal_outcome(game, goal["name"])
            present.add(outcome)
            icon, code, _ = GOAL_OUTCOMES[outcome]
            markers.append(f"{icon} `{game['game']:02d} {code}`")
        lines.extend(["### Game-by-game", ""])
        for start in range(0, len(markers), 10):
            lines.extend([" · ".join(markers[start:start + 10]), ""])
        lines.extend([
            " · ".join(
                f"{code} {label}" for outcome, (_, code, label) in GOAL_OUTCOMES.items() if outcome in present
            ),
            "",
        ])
    return lines


def _standings_lines(decks, goal_seat):
    standings = sorted(
        decks, key=lambda deck: (deck["win_rate"] is not None, deck["win_rate"] or 0), reverse=True,
    )
    lines = [
        "## Deck standings", "",
        "| Deck | Win rate | Wins | Losses | Draws | Completed |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for deck in standings:
        rate = deck["win_rate"]
        if rate is None:
            rate_label = "Unavailable"
        else:
            filled = round(rate * 10)
            bar = "█" * filled + "░" * (10 - filled)
            rate_label = f"`{bar}` {rate:.1%}"
        name = _markdown(deck["name"])
        if deck["seat"] == goal_seat:
            name = f"**{name}**"
        lines.append(
            f"| {name} | {rate_label} | {deck['wins']} | {deck['losses']} | {deck['draws']} | "
            f"{deck['completed_games']} |"
        )
    return [*lines, "", "Win rate is wins divided by completed games.", ""]


def write_reports(output_dir: Path, run: dict, decks: list[dict], games: list[dict]) -> None:
    """Produce a CSV row per attempt plus matching JSON and Markdown summaries."""
    output_dir.mkdir(parents=True, exist_ok=True)

    counts = {
        "requested": run["requested_games"],
        "attempted": len(games),
        "completed": sum(game["status"] in ("won", "draw") for game in games),
        "won": sum(game["status"] == "won" for game in games),
        "draw": sum(game["status"] == "draw" for game in games),
        "timeout": sum(game["status"] == "timeout" for game in games),
        "failed": sum(game["status"] == "failed" for game in games),
    }
    deck_results = []
    for deck in decks:
        name = deck["name"]
        completed = [game for game in games if game["status"] in ("won", "draw") and name in game["seats"]]
        wins = sum(game["winner"] == name for game in completed)
        draws = sum(game["status"] == "draw" for game in completed)
        deck_results.append({
            **deck,
            "version": deck["sha256"],
            "completed_games": len(completed),
            "wins": wins,
            "losses": len(completed) - wins - draws,
            "draws": draws,
            "win_rate": wins / len(completed) if completed else None,
        })

    payload = {"run": run, "counts": counts, "decks": deck_results, "games": games}
    (output_dir / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with (output_dir / "results.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for game in games:
            row = {field: game.get(field) for field in CSV_FIELDS}
            row["seats"] = json.dumps(game["seats"], ensure_ascii=False)
            row["forge_version"] = run.get("forge_version")
            row["logs"] = json.dumps(game.get("logs", {}), ensure_ascii=False)
            writer.writerow({
                field: _csv_text(value) if field in CSV_TEXT_FIELDS else value
                for field, value in row.items()
            })

    (output_dir / "summary.md").write_text(render_markdown(run, counts, deck_results, games), encoding="utf-8")


def render_markdown(run, counts, decks, games):
    """Render the dashboard from the same structured results written to JSON."""
    goal_seat = run.get("goal_seat")
    goal = next((deck for deck in decks if deck["seat"] == goal_seat), None)
    lines = ["# Commander simulation dashboard", ""]
    if goal is not None:
        lines.extend(_goal_lines(goal, games))
    elif goal_seat is not None:
        lines.extend([f"## Goal deck · Seat {goal_seat}", "", "Deck details unavailable.", ""])

    lines.extend([
        "## Batch health", "",
        "| Completed / requested | Attempted | Draws | Timeouts | Failures | Wall time |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| **{counts['completed']} / {counts['requested']}** | {counts['attempted']} | {counts['draw']} | "
        f"{counts['timeout']} | {counts['failed']} | {_markdown(run.get('wall_seconds'))} s |",
        "",
    ])
    if run.get("batch_error"):
        lines.extend(["> **Batch error**", ">", f"> {_markdown(run['batch_error'])}", ""])
    if decks:
        lines.extend(_standings_lines(decks, goal_seat))

    lines.extend([
        "<details>", "<summary>Run settings and deck versions</summary>", "",
        f"- Started at: {_markdown(run.get('started_at'))}",
        f"- Run ID: {_markdown(run.get('run_id'))}",
        f"- Attempt: {_markdown(run.get('run_attempt'))}",
        f"- Workflow URL: {_markdown(run.get('workflow_url'))}",
        f"- Source commit: {_markdown(run.get('source_commit'))}",
        f"- Lineup: {_markdown(run.get('lineup'))}",
        f"- Goal seat: {_markdown(goal_seat)}",
        f"- Forge version: {_markdown(run.get('forge_version'))}",
        f"- Java version: {_markdown(run.get('java_version'))}",
        f"- Base seed: {_markdown(run.get('base_seed'))}",
        f"- Forge game clock: {_markdown(run.get('game_clock_seconds'))} seconds",
        f"- Process deadline: {_markdown(run.get('process_deadline_seconds'))} seconds",
        f"- Setup logs: {_log_links(run.get('logs', {}))}",
    ])
    if decks:
        lines.extend([
            "", "| Seat | Deck | Commander | Archetype | AI profile | Version (SHA-256) |",
            "| --- | --- | --- | --- | --- | --- |",
        ])
        for deck in decks:
            lines.append(
                f"| {deck['seat']} | {_markdown(deck['name'])} | {_markdown(deck.get('commander'))} | "
                f"{_markdown(deck.get('archetype'))} | {_markdown(deck.get('ai_profile'))} | "
                f"`{_markdown(deck['version'])}` |"
            )
    lines.extend(["", "</details>", ""])

    if goal is not None and games:
        lines.extend(_telemetry_details(goal, games))

    if games:
        lines.extend([
            "<details>", "<summary>Game results and logs</summary>", "",
            "| Game | Seats | Seed | Status | Winner | Runtime (s) | Reason | Logs |",
            "| ---: | --- | ---: | --- | --- | ---: | --- | --- |",
        ])
        for game in games:
            lines.append(
                f"| {game['game']} | {_markdown(', '.join(game['seats']))} | {game['seed']} | "
                f"{_markdown(game['status'])} | {_markdown(game.get('winner'))} | "
                f"{_markdown(game['wall_seconds'])} | {_markdown(game.get('reason'))} | "
                f"{_log_links(game.get('logs', {}))} |"
            )
        lines.extend(["", "</details>", ""])
    return "\n".join(lines)
