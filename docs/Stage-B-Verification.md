# Stage B hosted verification

All ten games completed with verified winners on GitHub-hosted Ubuntu 24.04. The run used Forge 2.0.16, Temurin 17.0.21+9, the four Stage A decks, and seeds 42–51. The runner used one Forge process per game, a 600-second game clock, and a 720-second process deadline. [Successful run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44591940927) · [Reports and raw logs](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44591940927/artifacts/14565765165)

| Measurement | Observed value |
| --- | --- |
| Attempted / completed | 10 / 10 |
| Draws / timeouts / failures | 0 / 0 / 0 |
| Batch wall time | 668.298 seconds |
| Per-game process wall time | 35.575–125.429 seconds |
| Highest game process peak RSS | 1,559,968 KiB |
| Wins by deck | Azorius Control 6, Green Ramp 3, Orzhov Midrange 1, Red Aggro 0 |

The artifact was generated on revision `10f0154`. The downloaded deck hashes matched the checked-in decks. All ten raw logs confirmed the expected four seats, seed, and winner. The CSV, JSON, and Markdown agreed on the outcomes and rollups. The branch-only verification used the existing manual smoke workflow to exercise the batch. Stage C will add the permanent manual workflow and Markdown archive.

## Parser correction

The first hosted batch produced reports and logs for all ten attempts. Its report showed nine wins and one failure. For game 8, seed `49`, Forge caught a timeout while choosing an AI action and continued to a terminal Orzhov Midrange win. The parser had treated the recovered exception's stack trace as fatal. [First run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44589965578) · [Original artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44589965578/artifacts/14562982552) · [Forge AI timeout recovery](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-ai/src/main/java/forge/ai/AiController.java#L2928-L2965)

The corrected parser recognizes the matching exception and profiling sample. The parser still checks deadlines, other errors, all four seat outcomes, and the terminal result. Replaying the ten original logs recovered the game 8 win and confirmed the other nine winners. Regression tests cover the recovered timeout, an unpaired exception, an unrelated exception, a missing terminal result, and a genuine game-clock timeout.
