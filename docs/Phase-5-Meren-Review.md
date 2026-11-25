# Phase 5 Meren strategy review

The review covers both Phase 4 Meren versions on seeds 42 and 47. A is the original list. B replaces Rise from the Grave with one Swamp. The outcomes flip in opposite directions across the two seeds. Turn numbers are Forge's game turns. The file and line references point into the downloaded artifacts. [Version A logs](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463937991/artifacts/14953828103) · [Version B logs](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463934391/artifacts/14955425981)

| Seed and version | First logged target | End-step targets | Confirmed battlefield | Resolved with destination unknown | Winner |
| --- | --- | ---: | ---: | ---: | --- |
| 42 · A | Turn 48 · Noxious Gearhulk | 5 | 5 | 0 | Red Aggro |
| 42 · B | Turn 21 · Izoni, Thousand-Eyed | 9 | 6 | 3 | Meren |
| 47 · A | Turn 17 · Shriekmaw | 7 | 2 | 5 | Meren |
| 47 · B | Turn 21 · Shriekmaw | 6 | 2 | 4 | Red Aggro |

All 27 logged targets have a matching resolution. The logs confirm 15 battlefield returns and leave 12 destinations uncertain.

## Decisions and tradeoffs

- **42 · A, turn 48.** Tyrant's Familiar had just killed Noxious Gearhulk. Sakura-Tribe Elder was also visible in the graveyard after its activation. Returning Gearhulk removed the Familiar and increased Meren's life from 28 to 35. The Elder offered another land and death trigger on later returns. Gearhulk addressed the visible threat immediately. See `batch/game-0001/simulation.stdout.log` in A, lines 1313–1319 and 1352–1365.
- **42 · B, turns 21 and 45.** Glowspore Shaman milled both Izoni and Stitcher's Supplier. The first Izoni target shows a resolution followed by cleanup, so its destination is unknown. The visible tradeoff was Izoni's token payoff versus the Supplier's self-mill. On turn 45, the same Izoni instance produced its entry trigger and the log confirms the battlefield return. See `batch/game-0001/simulation.stdout.log` in B, lines 447–455 and 1499–1503.
- **47 · A, turns 17 and 43.** Meren chose Shriekmaw on the turn Meren was cast. The log confirms resolution and leaves the destination unknown. Later, Fleshbag Marauder went to the graveyard in the same turn before Meren targeted Shriekmaw. Shriekmaw's entry effect removed Warmonger Hellkite directly. Fleshbag's sacrifice effect would have let the opponent choose what to lose. See `batch/game-0006/simulation.stdout.log` in A, lines 365–375 and 1294–1313.
- **47 · B, turns 21 and 37.** B also opened with Shriekmaw and an unknown destination. On turn 37, Gray Merchant of Asphodel, Skull Prophet, and Fyndhorn Elves had just died. Gray Merchant's entry reduced each opponent's life by five and raised Meren's life from 42 to 57. The other visible creatures mainly offered future mana. That immediate payoff was meaningful even though Red Aggro eventually won. See `batch/game-0006/simulation.stdout.log` in B, lines 474–486, 939–949, 963–971, and 1538–1545.

The visible candidates support those tradeoffs. Overall decision quality is unreviewable from these logs because they lack a complete board snapshot and list of legal alternatives. The dashboard reports observed behavior. Forge logs certain battlefield exits, so a resolved trigger may leave the destination unknown. [Forge 2.0.16 log formatter](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-game/src/main/java/forge/game/GameLogFormatter.java#L272)

## Hosted verification

The original Meren lineup completed its smoke game and all ten games on GitHub-hosted Ubuntu 24.04 with Forge 2.0.16 and Temurin 17.0.21+9. The ten-game run used seeds 42–51 and kept Meren in seat 3 against the three Phase 4 opponents.

| Evidence | Games completed | Logged targets | Matched resolutions | Confirmed battlefield | Unknown destination |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Smoke run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45556191145) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45556191145/artifacts/14995243880) | 1 of 1 | 5 | 5 | 5 | 0 |
| [Ten-game run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45556465077) · [Artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45556465077/artifacts/14996098361) · [Archived dashboard](../reports/runs/45556465077/attempt-1/summary.md) | 10 of 10 | 49 | 49 | 23 | 26 |

Every game logged a Meren target. The ten-game median first target was turn 29.5. The target lines, resolutions, same-card evidence, and dashboard counts matched the raw stdout and JSON. Both uploaded Markdown files matched their Git archives byte for byte. GitHub's Markdown renderer displayed the strategy section and source references.

The runs used an isolated ref at `eac4ebc`. Its workflow directed the archive job to the feature branch, with simulation and reporting code from `6b5cbcf`. The ten-game report was copied from its generated archive branch into the feature PR.
