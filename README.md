# MTG Commander Simulation Framework

A framework for running four-player Magic: The Gathering Commander games with Forge AI and collecting results on GitHub Actions. The first milestone is a single headless game on a hosted Ubuntu runner. The proof of concept expands that to ten games with downloadable reports and logs.

Stage A passed on GitHub-hosted Ubuntu with Forge 2.0.16 and Temurin 17. Azorius Control won the four-player game with seed 42. [Hosted verification and evidence](docs/Stage-A-Feasibility.md#hosted-verification)

- [Project specification v0.1](PROJECT_SPEC.md)
- [Stage A feasibility review and smoke test plan](docs/Stage-A-Feasibility.md)
- [Simulation run reports](reports/runs/README.md)

## Run the Stage A smoke test

1. On GitHub, open **Actions**, select **Stage A Commander smoke test**, then choose **Run workflow**. GitHub makes manual dispatch available after the workflow reaches the default branch.
2. Open the run and download its `stage-a-evidence-<run-id>-attempt-<attempt>` artifact. Start with `evidence.json` for the four decks, seed, winner or failure reason, timing, and peak memory. The artifact also includes the Java version, setup diagnostics, and separate stdout and stderr logs for fixture validation and gameplay.

On failure, check `forge-setup.log` for download, checksum, or extraction errors. Check `fixture-validation.stderr.log` for unresolved cards or deck legality issues, and `simulation.stderr.log` and `simulation.stdout.log` for engine errors and timeouts. A draw is recorded and the smoke check requires a winner to pass.

Pull requests that touch Stage A code or fixtures run the fast checks on Linux. Use `bash -n scripts/setup_forge.sh` and `python3 -B -m unittest discover -s tests -v` for the same checks locally. Running the actual game uses the hosted workflow.
