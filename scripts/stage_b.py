"""Run a batch of four-player Forge Commander games and write reports."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

from . import stage_a as forge
from .batch_report import write_reports


MAX_SEED = 2**63 - 1
MAX_CLOCK = 2**31 - 1
BASELINE_DECKS = tuple(Path("decks/stage-a", name) for name in forge.FIXTURES)
RECURSION_DECK = Path("decks/phase-2/graveyard-recursion.dck")
SPELLSLINGER_DECK = Path("decks/phase-2/spellslinger.dck")
LINEUPS = {
    "baseline": BASELINE_DECKS,
    # Each alternate replaces midrange in seat three.
    "graveyard-recursion": (*BASELINE_DECKS[:2], RECURSION_DECK, BASELINE_DECKS[3]),
    "spellslinger": (*BASELINE_DECKS[:2], SPELLSLINGER_DECK, BASELINE_DECKS[3]),
}
GOAL_SEAT_BY_LINEUP = {
    "graveyard-recursion": 3,
    "spellslinger": 3,
}
FIXTURE_ARCHETYPES = {
    forge.ROOT / "decks/stage-a/ramp.dck": "Ramp",
    forge.ROOT / "decks/stage-a/aggro.dck": "Aggro",
    forge.ROOT / "decks/stage-a/midrange.dck": "Midrange",
    forge.ROOT / "decks/stage-a/control.dck": "Control",
    forge.ROOT / RECURSION_DECK: "Graveyard recursion",
    forge.ROOT / SPELLSLINGER_DECK: "Spellslinger",
}
LOG_SUFFIXES = {
    "stdout": "stdout.log",
    "stderr": "stderr.log",
    "peak_rss": "peak-rss-kib.txt",
}


def log_paths(output_dir, log_dir, name):
    paths = {}
    for key, suffix in LOG_SUFFIXES.items():
        path = log_dir / f"{name}.{suffix}"
        if path.is_file():
            paths[key] = path.relative_to(output_dir).as_posix()
    return paths


def read_java_version(forge_dir, output_dir):
    process = forge.run_logged(["java", "-version"], forge_dir, output_dir, "java-version", 30)
    if process.timed_out:
        raise ValueError("Java version check exceeded its deadline")
    if process.returncode:
        raise ValueError(f"Java version check exited with status {process.returncode}")
    lines = []
    for stream in ("stderr", "stdout"):
        lines.extend(forge.read_log(output_dir / f"java-version.{stream}.log").splitlines())
    version = next((line for line in lines if line.startswith(('openjdk version "', 'java version "'))), None)
    if version is None:
        raise ValueError("Java did not report its version")
    return next((line for line in lines if "Runtime Environment" in line), version)


def prepare_decks(original_paths, work_dir, jar, output_dir, *, deck_root):
    deck_dir = work_dir / "decks"
    deck_dir.mkdir()
    staged_paths = []
    for seat, path in enumerate(original_paths, start=1):
        # Forge resolves basenames within one directory. Give each staged copy its own name.
        staged = deck_dir / f"seat-{seat}.dck"
        shutil.copyfile(deck_root / path, staged)
        staged_paths.append(staged)

    preflight_home = work_dir / "preflight-home"
    preflight_home.mkdir()
    validation = forge.validate_fixtures(forge.headless_java(preflight_home), jar, staged_paths, output_dir)
    fixtures = forge.verified_fixtures(validation, output_dir, staged_paths)
    decks = []
    for seat, (fixture, original) in enumerate(zip(fixtures, original_paths, strict=True), start=1):
        decks.append({
            **fixture,
            "file": str(original),
            "seat": seat,
            "archetype": FIXTURE_ARCHETYPES.get((deck_root / original).resolve()),
            "ai_profile": "Forge default",
        })
    return staged_paths, decks


def play_game(game, seed, deck_names, jar, paths, work_dir, output_dir, game_clock, process_deadline):
    name = f"game-{game:04d}"
    game_dir = output_dir / name
    home = work_dir / name
    start = time.monotonic()
    process = None
    try:
        game_dir.mkdir()
        home.mkdir()
        command = forge.commander_command(forge.headless_java(home), jar, paths, seed, game_clock)
        process = forge.run_logged(command, jar.parent, game_dir, "simulation", process_deadline)
        result = forge.parse_game(
            forge.read_log(game_dir / "simulation.stdout.log"),
            forge.read_log(game_dir / "simulation.stderr.log"),
            process, deck_names, seed,
        )
    except OSError as exc:
        result = forge.GameResult("failed", reason=str(exc))
    return {
        "game": game,
        "seed": seed,
        "seats": deck_names,
        **asdict(result),
        "wall_seconds": process.wall_seconds if process else round(time.monotonic() - start, 3),
        "returncode": process.returncode if process else None,
        "peak_rss_kib": process.peak_rss_kib if process else None,
        "logs": log_paths(output_dir, game_dir, "simulation"),
    }


def run_batch(args, output_dir):
    start = time.monotonic()
    server = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    run = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "lineup": args.lineup,
        "goal_seat": args.goal_seat,
        "requested_games": args.games,
        "base_seed": args.seed,
        "game_clock_seconds": args.game_clock_seconds,
        "process_deadline_seconds": args.process_deadline_seconds,
        "forge_version": None,
        "java_version": None,
        "source_commit": os.environ.get("GITHUB_SHA"),
        "run_id": run_id,
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "workflow_url": f"{server}/{repository}/actions/runs/{run_id}" if server and repository and run_id else None,
        "batch_error": None,
    }
    decks = []
    games = []
    try:
        jar = forge.find_forge_jar(args.forge_dir.resolve())
        run["forge_version"] = forge.forge_version(jar)
        run["java_version"] = read_java_version(jar.parent, output_dir)
        with tempfile.TemporaryDirectory(prefix="forge-stage-b-") as temp:
            work_dir = Path(temp)
            paths, decks = prepare_decks(args.decks, work_dir, jar, output_dir, deck_root=args.deck_root)
            deck_names = [deck["name"] for deck in decks]
            for game in range(1, args.games + 1):
                result = play_game(
                    game, args.seed + game - 1, deck_names, jar, paths, work_dir, output_dir,
                    args.game_clock_seconds, args.process_deadline_seconds,
                )
                games.append(result)
                print(f"Game {game}/{args.games}: {result['status']}", flush=True)
    except (OSError, ValueError) as exc:
        run["batch_error"] = str(exc)
        print(f"Batch failed: {exc}", file=sys.stderr)

    run["wall_seconds"] = round(time.monotonic() - start, 3)
    run["logs"] = {
        f"{name} {key}": path
        for name in ("java-version", "fixture-validation")
        for key, path in log_paths(output_dir, output_dir, name).items()
    }
    write_reports(output_dir, run, decks, games)
    return 1 if run["batch_error"] or any(game["status"] in {"failed", "timeout"} for game in games) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forge-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path, help="new directory for reports and logs")
    deck_selection = parser.add_mutually_exclusive_group(required=True)
    deck_selection.add_argument("--decks", nargs=4, type=Path, metavar="DECK")
    deck_selection.add_argument("--lineup", choices=LINEUPS, help="checked-in lineup preset")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--goal-seat", type=int, choices=range(1, 5), metavar="SEAT",
                        help="seat (1 to 4) to highlight as the goal deck")
    parser.add_argument("--seed", type=int, default=42, help="seed for the first game")
    parser.add_argument("--game-clock-seconds", type=int, default=forge.GAME_CLOCK_SECONDS)
    parser.add_argument("--process-deadline-seconds", type=int, default=forge.PROCESS_DEADLINE_SECONDS)
    args = parser.parse_args(argv)
    if args.games < 1:
        parser.error("--games must be positive")
    if args.seed < 0 or args.seed + args.games - 1 > MAX_SEED:
        parser.error("all game seeds must be nonnegative signed 64-bit integers")
    if not 0 < args.game_clock_seconds < args.process_deadline_seconds <= MAX_CLOCK:
        parser.error("deadlines must be positive, with the process deadline above the game clock")
    if args.lineup is not None:
        args.decks = LINEUPS[args.lineup]
    if args.goal_seat is None:
        args.goal_seat = GOAL_SEAT_BY_LINEUP.get(args.lineup)
    args.deck_root = forge.ROOT if args.lineup is not None else Path.cwd()
    try:
        for path in args.decks:
            if path.suffix.lower() != ".dck" or not (args.deck_root / path).is_file():
                parser.error(f"expected an existing Forge .dck file: {path}")
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True)
    except OSError as exc:
        parser.error(str(exc))
    try:
        return run_batch(args, output_dir)
    except OSError as exc:
        print(f"Could not write batch reports: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
