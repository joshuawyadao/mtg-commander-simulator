# MTG Commander Simulation Framework

A framework for running four-player Magic: The Gathering Commander games with Forge AI. Stage B verified a ten-game batch on GitHub-hosted Ubuntu and produced downloadable reports and logs. [Stage B hosted verification](docs/Stage-B-Verification.md)

Stage A passed on GitHub-hosted Ubuntu with Forge 2.0.16 and Temurin 17. Azorius Control won the four-player game with seed 42. [Hosted verification and evidence](docs/Stage-A-Feasibility.md#hosted-verification)

- [Project specification v0.1](PROJECT_SPEC.md)
- [Stage A feasibility review and smoke test plan](docs/Stage-A-Feasibility.md)
- [Stage C hosted verification](docs/Stage-C-Verification.md)
- [Phase 2 lineup verification](docs/Phase-2-Verification.md)
- [Simulation run reports](reports/runs/README.md)

## Run a hosted Commander batch

1. Open **Actions → Commander batch simulation → Run workflow** in GitHub. Select **main**, choose a lineup, and enter a whole number from **1 to 10**. The defaults are `baseline` and 10 games.
2. Open the run and download its `commander-batch-<run-id>-attempt-<attempt>` artifact. Start with `batch/summary.md`. The artifact also contains the CSV, JSON, and raw logs.
3. Find the Git-tracked copy at `reports/runs/<run-id>/attempt-<attempt>/summary.md` on `main`. Use **Re-run all jobs** to repeat a batch. Download any artifact you want to keep before rerunning. The rerun uploads a new artifact and adds a summary folder.

The three lineups use Green Ramp, Red Aggro, and Azorius Control in seats one, two, and four. Games start with seed 42.

| Lineup | Seat three |
| --- | --- |
| `baseline` | Orzhov Midrange |
| `graveyard-recursion` | Golgari Graveyard Recursion, led by Meren of Clan Nel Toth |
| `spellslinger` | Mono-Blue Spellslinger, led by Talrand, Sky Summoner |

For a failure, check the artifact's `run.txt` for rejected inputs, `forge-setup.log` for installation errors, or the batch summary and its log links for deck validation and gameplay failures. Generated summaries are archived even when gameplay fails.

## Run the Stage A smoke test

1. On GitHub, open **Actions**, select **Stage A Commander smoke test**, then choose **Run workflow**. GitHub makes manual dispatch available after the workflow reaches the default branch.
2. Open the run and download its `stage-a-evidence-<run-id>-attempt-<attempt>` artifact. Start with `evidence.json` for the four decks, seed, winner or failure reason, timing, and peak memory. The artifact also includes the Java version, setup diagnostics, and separate stdout and stderr logs for fixture validation and gameplay.

On failure, check `forge-setup.log` for download, checksum, or extraction errors. Check `fixture-validation.stderr.log` for unresolved cards or deck legality issues, and `simulation.stderr.log` and `simulation.stdout.log` for engine errors and timeouts. A draw is recorded and the smoke check requires a winner to pass.

Pull requests that touch simulation scripts, tests, deck fixtures, or the workflow run the fast checks on Linux. Use `bash -n scripts/setup_forge.sh` and `python3 -B -m unittest discover -s tests -v` for the same checks locally.

## Run the batch CLI locally

On Ubuntu with Python 3.10+, Java 17, and GNU `/usr/bin/time`, run these commands from the repository root. The setup script verifies the pinned Forge archive.

```bash
work_dir=$(mktemp -d)
bash scripts/setup_forge.sh "$work_dir/forge"
python3 -B -m scripts.stage_b \
  --forge-dir "$work_dir/forge" --output-dir "$work_dir/batch" \
  --games 10 --seed 42 --lineup baseline
```

Use `--decks` with four paths for a custom lineup. Each deck needs a distinct name, one commander, and 99 main-deck cards in Forge-native format. The CLI validates a snapshot of the decks and records their SHA-256 hashes. Seating follows input order, and each game increments the seed by one. The default Forge clock is 600 seconds, with a separate 720-second process deadline. Set them with `--game-clock-seconds` and `--process-deadline-seconds`.

- **`summary.md`** shows batch settings, counts, deck results, and links to the raw logs.
- **`results.json`** contains the complete structured results. **`results.csv`** has one row per attempt, with JSON-encoded seats and log paths.
- **`game-0001/`**, **`game-0002/`**, and later folders hold each game's stdout, stderr, and available peak memory measurements. Batch-level Java and deck-validation logs sit beside the reports.

Wins and genuine draws count as completed games. Timeouts and failures stay out of deck win rates. The CLI writes reports and exits with status 1 for a setup error, timeout, or failed game. Check the batch error and setup logs for preflight failures, and the per-game reason and logs for gameplay failures. Use a fresh output directory for each run.
