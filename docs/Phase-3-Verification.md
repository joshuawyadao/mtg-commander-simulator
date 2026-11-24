# Phase 3 telemetry verification

GitHub-hosted Ubuntu 24.04 ran one smoke game and one ten-game batch for each lineup with Forge 2.0.16 and Temurin 17.0.21+9. All 33 games completed. The ten-game batches used seeds 42–51 and showed telemetry for all ten goal-deck games. Baseline selected seat 3 explicitly. The alternate presets selected it automatically.

| Lineup | Goal commander | Batch completed | Evidence |
| --- | --- | ---: | --- |
| `baseline` | Daxos the Returned | 10 of 10 | [Smoke run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298423793) · [Batch run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298775552) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298775552/artifacts/14877782619) · [Archived dashboard](../reports/runs/45298775552/attempt-1/summary.md) |
| `graveyard-recursion` | Meren of Clan Nel Toth | 10 of 10 | [Smoke run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298421074) · [Batch run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298772952) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298772952/artifacts/14877453690) · [Archived dashboard](../reports/runs/45298772952/attempt-1/summary.md) |
| `spellslinger` | Talrand, Sky Summoner | 10 of 10 | [Smoke run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298423012) · [Batch run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298779202) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298779202/artifacts/14878750642) · [Archived dashboard](../reports/runs/45298779202/attempt-1/summary.md) |

## Dashboard results

| Lineup | Games with a cast | Median first cast, game turn | Median early land plays | Median combat damage taken |
| --- | ---: | ---: | ---: | ---: |
| `baseline` | 10 of 10 | 11.5 | 4 | 49 |
| `graveyard-recursion` | 10 of 10 | 17.5 | 4 | 44 |
| `spellslinger` | 9 of 10 | 16 | 4 | 41.5 |

For every logged game, a second pass over the raw logs checked the three metrics for all four seats against `results.json`. The selected seat's median values and per-game entries matched the rendered Markdown. The spellslinger smoke game also showed a valid no-cast result. GitHub's Markdown renderer displayed the telemetry table and the collapsible game details.

The workflow ran on an isolated verification ref at `266ad3d` using the feature's simulation code at `6f65c40`. The overlay directed the archive step to the feature branch. The workflow's report branches each added one Markdown file. The three ten-game report commits were copied to the feature branch and the copies matched the uploaded Markdown byte for byte.
