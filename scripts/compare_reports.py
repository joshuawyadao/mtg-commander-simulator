"""Render a matched-seed A/B dashboard from two batch results artifacts."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit

from .batch_report import _markdown as _md
from .comparison_data import build_comparison


OUTCOME = {
    "win": "🟩 Win", "loss": "🟥 Loss", "draw": "🟨 Draw",
    "failed": "⚠️ Failed", "timeout": "⏱️ Timeout", "missing": "⬜ Missing",
}
RUN_PATH = re.compile(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/([0-9]+)/?")


def _number(value):
    if value is None:
        return "—"
    return f"{value:g}" if isinstance(value, (int, float)) else _md(value)


def _metric(value, unit):
    if value is None:
        return "—"
    if unit == "game turn":
        return f"Turn {_number(value)}"
    display_unit = "play" if unit == "plays" and value == 1 else unit
    suffix = "%" if unit == "%" else (f" {display_unit}" if display_unit else "")
    return f"{_number(value)}{suffix}"


def _delta(a, b, unit):
    if a is None or b is None:
        return "—"
    value = b - a
    delta_unit = {"%": "pp", "game turn": "turns"}.get(unit, unit)
    if abs(value) == 1:
        delta_unit = delta_unit.removesuffix("s")
    suffix = f" {delta_unit}" if delta_unit else ""
    return f"{value:+g}{suffix}"


def _source(run):
    run_id = run.get("run_id")
    label = f"Run {_md(run_id)}" if run_id is not None else "Local run"
    url = run.get("workflow_url")
    if not isinstance(url, str):
        return label
    try:
        parsed = urlsplit(url)
        match = RUN_PATH.fullmatch(parsed.path)
        safe = (parsed.scheme == "https" and parsed.netloc == "github.com" and match is not None
                and not parsed.query and not parsed.fragment
                and run_id is not None and str(run_id) == match[1])
    except ValueError:
        safe = False
    return f"[{label}](https://github.com{parsed.path})" if safe else label


def _version(deck):
    return _md(deck["sha256"])


def _identity(label, deck, run, seat):
    return (f"**{label} · {_md(deck.get('name'))}** · {_md(deck.get('commander'))} · "
            f"seat {seat} · {_source(run)} · attempt {_md(run.get('run_attempt'))}")


def _outcome(game):
    return OUTCOME[game["outcome"]]


def _telemetry(game, field):
    data = game.get("telemetry")
    if data is None:
        return "Unavailable"
    value = data.get(field)
    if field == "first_commander_cast_turn":
        return f"Turn {_number(value)}" if value is not None else "No cast"
    if field == "early_land_plays":
        observed = data.get("early_turns_observed")
        return f"{_number(value)} / {_number(observed)} own turns" if value is not None else "Unavailable"
    return _number(value) if value is not None else "Unavailable"


def render_comparison(comparison):
    """Build a deterministic dashboard from validated comparison data."""
    runs, decks = comparison["runs"], comparison["decks"]
    seat = comparison["goal_seat"]
    goal_a, goal_b = decks["a"][seat], decks["b"][seat]
    pairs = comparison["pairs"]
    lines = [
        "# Commander A/B simulation dashboard", "",
        _identity("A", goal_a, runs["a"], seat), "",
        _identity("B", goal_b, runs["b"], seat), "",
        f"**{comparison['paired_completed']} / {len(pairs)} matched seeds completed in both versions.** "
        "Each metric uses eligible matched pairs. B − A shows the observed difference.", "",
        "## Scorecard", "",
        "| Goal deck metric | A · baseline | B · card swap | B − A | Paired sample |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for metric in comparison["metrics"]:
        pairs_label = "pair" if metric["n"] == 1 else "pairs"
        lines.append(
            f"| {_md(metric['label'])} | **{_metric(metric['a'], metric['unit'])}** | "
            f"**{_metric(metric['b'], metric['unit'])}** | {_delta(metric['a'], metric['b'], metric['unit'])} | "
            f"{metric['n']} {pairs_label} |"
        )
    lines.extend([
        "", "## Matched seed outcomes", "",
        "🟩 Win · 🟥 Loss · 🟨 Draw · ⚠️ Failed · ⏱️ Timeout · ⬜ Missing", "",
        "| Seed | A · baseline | B · card swap |",
        "| ---: | --- | --- |",
    ])
    for pair in pairs:
        lines.append(f"| {pair['seed']} | {_outcome(pair['a'])} | {_outcome(pair['b'])} |")

    lines.extend([
        "", "<details>", "<summary>How to read the scorecard</summary>", "",
        "A matched pair uses the same seed and completes in both versions (win or draw). "
        "Failed, timed out, or missing games appear above but do not enter paired metrics. "
        "Win rate counts goal deck wins among paired completed games; a draw is not a win. "
        "Commander cast rate counts games with an observed cast among pairs with telemetry in both versions. "
        "First cast medians include pairs with a cast observed in both versions. "
        "Early land play medians include pairs with all four early own turns observed in both versions. "
        "Combat damage medians include pairs with telemetry in both versions. "
        "Each row's sample is the number of pairs eligible for that specific metric. "
        "**No cast** means a completed game had telemetry but no commander cast; "
        "**Unavailable** means telemetry was missing; **0** is a measured zero. "
        "Percent deltas use percentage points (pp).", "", "</details>", "",
        "<details>", "<summary>Game details and exclusions</summary>", "",
        "| Seed | A result · winner | B result · winner | A first cast | B first cast | "
        "A early lands | B early lands | A damage | B damage | Reason / exclusion |",
        "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ])
    for pair in pairs:
        a, b = pair["a"], pair["b"]
        reason = "; ".join(
            f"{label}: {game['outcome']}" + (f" ({game['reason']})" if game.get("reason") else "")
            for label, game in (("A", a), ("B", b))
            if game["outcome"] in ("failed", "timeout", "missing") or game.get("reason")
        )
        lines.append(
            f"| {pair['seed']} | {_outcome(a)} · {_md(a.get('winner'))} | "
            f"{_outcome(b)} · {_md(b.get('winner'))} | "
            f"{_telemetry(a, 'first_commander_cast_turn')} | {_telemetry(b, 'first_commander_cast_turn')} | "
            f"{_telemetry(a, 'early_land_plays')} | {_telemetry(b, 'early_land_plays')} | "
            f"{_telemetry(a, 'combat_damage_taken')} | {_telemetry(b, 'combat_damage_taken')} | "
            f"{_md(reason) if reason else '—'} |"
        )
    lines.extend(["", "</details>", "", "<details>",
                  "<summary>Sources, deck versions, and shared settings</summary>", "",
                  f"- A: {_source(runs['a'])}, attempt {_md(runs['a'].get('run_attempt'))}; "
                  f"goal deck SHA-256 `{_version(goal_a)}`",
                  f"- B: {_source(runs['b'])}, attempt {_md(runs['b'].get('run_attempt'))}; "
                  f"goal deck SHA-256 `{_version(goal_b)}`",
                  f"- Seed range: {_md(runs['a'].get('base_seed'))} through "
                  f"{_md(pairs[-1]['seed']) if pairs else '—'}",
                  f"- Forge: {_md(runs['a'].get('forge_version'))}; Java: {_md(runs['a'].get('java_version'))}",
                  f"- Source commit: {_md(runs['a'].get('source_commit'))}",
                  f"- AI profile: {_md(goal_a.get('ai_profile'))}",
                  f"- Game clock: {_md(runs['a'].get('game_clock_seconds'))} s; "
                  f"process deadline: {_md(runs['a'].get('process_deadline_seconds'))} s",
                  "", "| Opponent seat | Deck | SHA-256 |", "| ---: | --- | --- |"])
    for opponent_seat, deck in sorted(decks["a"].items()):
        if opponent_seat != seat:
            lines.append(f"| {opponent_seat} | {_md(deck.get('name'))} | `{_version(deck)}` |")
    lines.extend(["", "</details>", ""])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version-a", required=True, type=Path, help="Baseline results.json")
    parser.add_argument("--version-b", required=True, type=Path, help="Card-swap results.json")
    parser.add_argument("--output", required=True, type=Path, help="Markdown dashboard path")
    args = parser.parse_args(argv)
    try:
        if args.output.resolve() in {args.version_a.resolve(), args.version_b.resolve()}:
            raise ValueError("The dashboard output must be distinct from both source reports.")
        a = json.loads(args.version_a.read_text(encoding="utf-8"))
        b = json.loads(args.version_b.read_text(encoding="utf-8"))
        markdown = render_comparison(build_comparison(a, b))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent,
                                             prefix=f".{args.output.name}.", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(markdown)
            os.replace(temporary, args.output)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    except (OSError, ValueError) as error:
        print(f"Comparison failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
