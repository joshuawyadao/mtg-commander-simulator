"""Write human-readable and structured reports for a Commander simulation batch."""

import csv
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote


CSV_FIELDS = (
    "game", "seed", "seats", "status", "winner", "duration_ms", "wall_seconds",
    "reason", "forge_version", "returncode", "peak_rss_kib", "logs",
)
CSV_TEXT_FIELDS = {"status", "winner", "reason", "forge_version"}


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

    lines = [
        "# Commander simulation batch", "",
        "## Run summary", "",
        f"- Started at: {_markdown(run.get('started_at'))}",
        f"- Run ID: {_markdown(run.get('run_id'))}",
        f"- Attempt: {_markdown(run.get('run_attempt'))}",
        f"- Workflow URL: {_markdown(run.get('workflow_url'))}",
        f"- Source commit: {_markdown(run.get('source_commit'))}",
        f"- Lineup: {_markdown(run.get('lineup'))}",
        f"- Forge version: {_markdown(run.get('forge_version'))}",
        f"- Java version: {_markdown(run.get('java_version'))}",
        f"- Games requested: {counts['requested']}",
        f"- Base seed: {_markdown(run.get('base_seed'))}",
        f"- Forge game clock: {_markdown(run.get('game_clock_seconds'))} seconds",
        f"- Process deadline: {_markdown(run.get('process_deadline_seconds'))} seconds",
        f"- Total wall time: {_markdown(run.get('wall_seconds'))} seconds",
        f"- Attempted: {counts['attempted']}",
        f"- Completed: {counts['completed']}",
        f"- Wins: {counts['won']}",
        f"- Draws: {counts['draw']}",
        f"- Timeouts: {counts['timeout']}",
        f"- Failures: {counts['failed']}",
        f"- Batch error: {_markdown(run.get('batch_error'))}",
        f"- Setup logs: {_log_links(run.get('logs', {}))}",
        "", "## Deck results", "",
        "| Seat | Deck | Version (SHA-256) | Archetype | AI profile | Completed | Wins | Losses | Draws | Win rate |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for deck in deck_results:
        rate = f"{deck['win_rate']:.1%}" if deck["win_rate"] is not None else "unavailable"
        lines.append(
            f"| {deck['seat']} | {_markdown(deck['name'])} | {_markdown(deck['version'])} | "
            f"{_markdown(deck.get('archetype'))} | {_markdown(deck.get('ai_profile'))} | "
            f"{deck['completed_games']} | {deck['wins']} | {deck['losses']} | {deck['draws']} | {rate} |"
        )
    lines.extend([
        "", "## Game results", "",
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
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
