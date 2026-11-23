# Phase 2 lineup verification

Both alternate lineups completed ten games on GitHub-hosted Ubuntu 24.04 with Forge 2.0.16 and Temurin 17.0.21+9. Green Ramp, Red Aggro, and Azorius Control occupied seats one, two, and four. Each lineup used seeds 42–51.

| Lineup | Seat three | Completed | Timeouts or failures | Evidence |
| --- | --- | ---: | ---: | --- |
| `graveyard-recursion` | Meren of Clan Nel Toth | 10 of 10 | 0 | [Git summary](../reports/runs/45249196122/attempt-1/summary.md) · [Run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45249196122) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45249196122/artifacts/14855027774) |
| `spellslinger` | Talrand, Sky Summoner | 10 of 10 | 0 | [Git summary](../reports/runs/45249189729/attempt-1/summary.md) · [Run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45249189729) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45249189729/artifacts/14856106900) |

- Graveyard recursion game 1 (seed 42) shows Meren's end-step trigger returning Noxious Gearhulk. Its entry ability destroyed Tyrant's Familiar. See `batch/game-0001/simulation.stdout.log` near lines 1360–1364.
- Spellslinger game 8 (seed 49) shows Talrand's Drake trigger resolving after Brainstorm. The Drake later attacked and dealt two combat damage. See `batch/game-0008/simulation.stdout.log` near lines 342–343 and 427–432.

The registered workflow ran from an isolated rehearsal branch at `00fee30`, with its archive destination set to that branch. Forge validated both decks. The deck hashes matched the checked-in fixtures, the CSV and JSON matched the raw game outcomes, and the Git summaries matched the artifacts byte-for-byte. The two archive commits were copied to the feature branch. A separate one-game dispatch confirmed the baseline default. [Baseline smoke run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45249258046)

## Goal deck dashboard

GitHub's Markdown renderer displayed the dashboard correctly for both archived ten-game result sets. Meren won 4 of 10 games and Talrand won 0 of 10. The original run summaries are retained above.

Two one-game dispatches on an isolated rehearsal branch verified the dashboard from simulation through archive. The graveyard recursion lineup automatically highlighted Meren in seat 3, and a baseline dispatch with seat 4 explicitly selected highlighted Azorius Control. Both games completed and both Git summaries matched the uploaded Markdown byte-for-byte. [Automatic goal run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45253174984) · [Explicit goal run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45253177732)
