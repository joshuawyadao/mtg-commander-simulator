"""Run and verify one headless Commander game using the pinned Forge desktop release."""

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ("ramp.dck", "aggro.dck", "midrange.dck", "control.dck")
GAME_CLOCK_SECONDS = 600
PROCESS_DEADLINE_SECONDS = 720
FIXTURE_DEADLINE_SECONDS = 120
FORGE_JAR_PREFIX = "forge-gui-desktop-"
FORGE_JAR_SUFFIX = "-jar-with-dependencies.jar"
DRAW = re.compile(r"Game Result: Game 1 ended in a Draw! Took (\d+) ms\.")
WIN = re.compile(r"Game Result: Game 1 ended in (\d+) ms\. (.+) has won!")
PLAYER_OUTCOME = re.compile(r"^Game Outcome: Ai\(\d+\)-")
FORGE_ERROR = re.compile(
    r"^(?:Could not load deck - |No deck found in |Deck is NULL|An unsupported card was requested:|"
    r"Uncaught exception in thread |Exception in thread |Caused by: |"
    r"[ \t]+at [\w.$/]+\([^\n]+\))",
    re.MULTILINE,
)
STACK_FRAMES = r"(?:\n[ \t]+at [^\n]+)*"
AI_TIMEOUT_SAMPLE = re.compile(r"^AI eval thread at timeout:" + STACK_FRAMES + "$", re.MULTILINE)
AI_TIMEOUT_TRACE = re.compile(
    r"^java\.util\.concurrent\.TimeoutException\n"
    r"[ \t]+at java\.base/java\.util\.concurrent\.FutureTask\.get\([^\n]+\)\n"
    r"[ \t]+at forge\.ai\.AiController\.chooseSpellAbilitiesToPlayFromList\([^\n]+\)"
    + STACK_FRAMES + "$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    wall_seconds: float
    peak_rss_kib: int | None
    timed_out: bool


@dataclass(frozen=True)
class GameResult:
    status: str
    winner: str | None = None
    duration_ms: int | None = None
    reason: str | None = None


def read_log(path):
    return path.read_text(encoding="utf-8", errors="replace")


def forge_error(stdout, stderr):
    for log in (stderr, stdout):
        match = FORGE_ERROR.search(log)
        if match:
            return log[match.start():].split("\n", 1)[0].strip()
    return None


def simulation_error(stdout, stderr):
    # Forge catches this AI choice timeout and emits a companion profiling sample.
    gameplay_log, samples = AI_TIMEOUT_SAMPLE.subn("", stdout)
    error_log, traces = AI_TIMEOUT_TRACE.subn("", stderr)
    if samples and traces == samples:
        return forge_error(gameplay_log, error_log)
    return forge_error(stdout, stderr)


def parse_game(stdout, stderr, process, deck_names, seed):
    lines = stdout.splitlines()
    if process.timed_out or "Stopping slow match as draw" in lines:
        reason = "Java process deadline exceeded" if process.timed_out else "Forge game clock expired"
        return GameResult("timeout", reason=reason)

    diagnostic = simulation_error(stdout, stderr)
    if diagnostic or process.returncode != 0:
        return GameResult("failed", reason=diagnostic or f"Java exited with status {process.returncode}")

    seats = [f"Ai({seat})-{name}" for seat, name in enumerate(deck_names, start=1)]
    start = f"{' vs '.join(seats)} - one game of Commander seed {seed}"
    if lines.count(start) != 1:
        return GameResult("failed", reason="Missing or repeated setup for the expected Commander pod")

    # Forge uses the same label for the match duration, turn count, and player results.
    outcome_lines = [line for line in lines if PLAYER_OUTCOME.match(line)]
    if len(outcome_lines) != len(seats) or any(
        sum(line.startswith(f"Game Outcome: {seat} ") for line in outcome_lines) != 1
        for seat in seats
    ):
        return GameResult("failed", reason="Missing or unexpected player outcomes for the Commander pod")

    results = [line for line in lines if line.startswith("Game Result:")]
    if len(results) != 1:
        return GameResult("failed", reason="Expected exactly one terminal game result")
    if draw := DRAW.fullmatch(results[0]):
        return GameResult("draw", duration_ms=int(draw[1]), reason="Game ended without a winner")
    if (win := WIN.fullmatch(results[0])) and win[2] in seats:
        return GameResult("won", winner=deck_names[seats.index(win[2])], duration_ms=int(win[1]))
    return GameResult("failed", reason="Terminal game result did not identify an expected winner")


def run_logged(command, cwd, output_dir, name, deadline):
    rss_path = output_dir / f"{name}.peak-rss-kib.txt"
    stdout_path = output_dir / f"{name}.stdout.log"
    stderr_path = output_dir / f"{name}.stderr.log"
    timed_out = False
    start = time.monotonic()
    environment = os.environ.copy()
    environment.pop("DISPLAY", None)
    environment.pop("WAYLAND_DISPLAY", None)
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        with subprocess.Popen(
            ["/usr/bin/time", "-f", "%M", "-o", str(rss_path), *command],
            cwd=cwd, env=environment, stdout=stdout, stderr=stderr, start_new_session=True,
        ) as child:
            try:
                child.wait(timeout=deadline)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait()

    rss = read_log(rss_path).strip().splitlines()[-1:] if rss_path.is_file() and not timed_out else []
    return ProcessResult(
        child.returncode, round(time.monotonic() - start, 3),
        int(rss[0]) if rss and rss[0].isdecimal() else None, timed_out,
    )


def fixture_metadata(stdout, paths):
    records = [line.split("\t") for line in stdout.splitlines() if line.startswith("STAGE_A_DECK\t")]
    if len(records) != len(paths) or any(len(fields) != 4 for fields in records):
        raise ValueError("Forge fixture validation did not identify exactly four decks")
    fixtures = []
    for (_, actual_file, name, commander), path in zip(records, paths, strict=True):
        if actual_file != path.name or not name or not commander:
            raise ValueError(f"Unexpected fixture validation data for {path.name}")
        fixtures.append({"file": path.name, "name": name, "commander": commander,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if len({fixture["name"] for fixture in fixtures}) != len(fixtures):
        raise ValueError("Forge fixture names must be distinct")
    return fixtures


def find_forge_jar(forge_dir):
    jars = [path for path in forge_dir.glob(f"{FORGE_JAR_PREFIX}*{FORGE_JAR_SUFFIX}") if path.is_file()]
    if len(jars) != 1:
        raise ValueError("Expected one Forge desktop JAR in the verified release directory")
    return jars[0]


def forge_version(jar):
    return jar.name.removeprefix(FORGE_JAR_PREFIX).removesuffix(FORGE_JAR_SUFFIX)


def headless_java(home):
    return ["java", "-Djava.awt.headless=true", f"-Duser.home={home}", "-Xmx4g"]


def validate_fixtures(java, jar, paths, output_dir):
    preflight = [*java, "-cp", str(jar),
                 str(ROOT / "scripts" / "ValidateCommanderFixtures.java"), *map(str, paths)]
    return run_logged(preflight, jar.parent, output_dir, "fixture-validation", FIXTURE_DEADLINE_SECONDS)


def verified_fixtures(validation, output_dir, paths):
    stdout = read_log(output_dir / "fixture-validation.stdout.log")
    diagnostic = forge_error(stdout, read_log(output_dir / "fixture-validation.stderr.log"))
    if validation.timed_out:
        raise ValueError("Forge fixture validation exceeded its deadline")
    if diagnostic or validation.returncode != 0:
        raise ValueError(diagnostic or f"Forge fixture validation exited with status {validation.returncode}")
    return fixture_metadata(stdout, paths)


def commander_command(java, jar, paths, seed, clock):
    return [*java, "-jar", str(jar), "sim", "-f", "commander", "-n", "1",
            "-D", str(paths[0].parent), "-d", *(path.name for path in paths), "-s", str(seed), "-c", str(clock)]


def smoke_test(forge_dir, output_dir, seed):
    evidence = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "game_clock_seconds": GAME_CLOCK_SECONDS,
        "process_deadline_seconds": PROCESS_DEADLINE_SECONDS,
    }
    result = GameResult("failed", reason="Stage A did not finish")
    try:
        jar = find_forge_jar(forge_dir)
        evidence["forge_version"] = forge_version(jar)
        paths = [ROOT / "decks" / "stage-a" / name for name in FIXTURES]
        with tempfile.TemporaryDirectory(prefix="forge-stage-a-") as home:
            java = headless_java(home)
            validation = validate_fixtures(java, jar, paths, output_dir)
            evidence["fixture_validation"] = asdict(validation)
            fixtures = verified_fixtures(validation, output_dir, paths)
            evidence["fixtures"] = fixtures

            command = commander_command(java, jar, paths, seed, GAME_CLOCK_SECONDS)
            evidence["command"] = command
            process = run_logged(command, forge_dir, output_dir, "simulation", PROCESS_DEADLINE_SECONDS)
            evidence["simulation"] = asdict(process)
            result = parse_game(
                read_log(output_dir / "simulation.stdout.log"), read_log(output_dir / "simulation.stderr.log"),
                process, [fixture["name"] for fixture in fixtures], seed,
            )
    except (OSError, ValueError) as exc:
        result = GameResult("failed", reason=str(exc))
    finally:
        evidence["result"] = asdict(result)
        (output_dir / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forge-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0 <= args.seed < 2**63:
        parser.error("--seed must be a nonnegative signed 64-bit integer")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if (output / "evidence.json").exists():
        parser.error("--output-dir already contains a Stage A run")
    result = smoke_test(args.forge_dir.resolve(), output, args.seed)
    print(f"Stage A {result.status}: {result.winner or result.reason}")
    return 0 if result.status == "won" else 1


if __name__ == "__main__":
    raise SystemExit(main())
