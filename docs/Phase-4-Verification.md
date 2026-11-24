# Phase 4 Meren comparison verification

Version A is the existing Meren preset, `graveyard-recursion`. Version B, `meren-extra-swamp`, replaces one **Rise from the Grave** with one **Swamp**. Both use Meren of Clan Nel Toth in seat 3, with Green Ramp, Red Aggro, and Azorius Control in seats 1, 2, and 4.

| Version | Smoke on seed 42 | Ten-game run on seeds 42–51 | Source artifact |
| --- | --- | --- | --- |
| A · Existing Meren | [Passed](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463301405) | [10 of 10](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463937991) | [Results and logs](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463937991/artifacts/14953828103) |
| B · Extra Swamp | [Passed](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463305321) | [10 of 10](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463934391) | [Results and logs](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463934391/artifacts/14955425981) |

Both versions ran with Forge 2.0.16 and Temurin 17.0.21+9 on GitHub-hosted Ubuntu 24.04. The ten-game pair used the same simulator revision, opponent deck hashes, seats, AI profiles, seeds, and deadlines. All games completed, and the CSV and JSON outcomes agreed with the raw Forge logs. The checked-in decklists and archived hashes verified the one-card swap.

The comparison workflow passed with the one-game and ten-game artifacts. Independently calculated scorecard values and seed outcomes matched the final Markdown. The locally regenerated report, the uploaded comparison, and the Git archive matched byte for byte. GitHub's Markdown renderer displayed the smoke scorecard and expandable details. [Smoke comparison](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45464212040) · [Ten-game comparison](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45465940103) · [Comparison artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45465940103/artifacts/14953703453) · [Archived dashboard](../reports/runs/45465940103/attempt-1/summary.md)

The hosted trials used isolated workflow refs. The simulation ran at `4ccd935`, and the final comparison ran at `b5489c1` through an existing dispatch path so it could run before the new workflow reached the default branch. The archive job published a one-report branch, and its ten-game report was copied into the feature branch for review.
