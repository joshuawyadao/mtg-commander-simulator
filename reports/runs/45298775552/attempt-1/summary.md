# Commander simulation dashboard

## Goal deck · Orzhov Midrange

Daxos the Returned · Seat 3 · Midrange

| Win rate | Wins | Losses | Draws | Completed games |
| ---: | ---: | ---: | ---: | ---: |
| **10.0%** | **1** | 9 | 0 | 10 |

### Pros and cons

| Pros | Cons |
| --- | --- |
| Recorded **1** win in this batch. | **Azorius Control** won **6 of 9** games the goal deck lost. |

### How the deck played

Telemetry from **10 of 10** completed games with the goal deck.

| Metric | Result | Games measured |
| --- | ---: | ---: |
| Commander cast | **10 of 10** games | 10 |
| First commander cast | **Turn 11.5 (median)** | 10 casts |
| Land plays in first 4 own turns | **4 plays (median)** | 10 with 4 turns |
| Combat damage taken | **49 damage** (median) | 10 |

### Game-by-game

🟥 `01 L` · 🟥 `02 L` · 🟥 `03 L` · 🟥 `04 L` · 🟥 `05 L` · 🟥 `06 L` · 🟥 `07 L` · 🟩 `08 W` · 🟥 `09 L` · 🟥 `10 L`

W win · L loss

## Batch health

| Completed / requested | Attempted | Draws | Timeouts | Failures | Wall time |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **10 / 10** | 10 | 0 | 0 | 0 | 392.7 s |

## Deck standings

| Deck | Win rate | Wins | Losses | Draws | Completed |
| --- | --- | ---: | ---: | ---: | ---: |
| Azorius Control | `██████░░░░` 60.0% | 6 | 4 | 0 | 10 |
| Green Ramp | `███░░░░░░░` 30.0% | 3 | 7 | 0 | 10 |
| **Orzhov Midrange** | `█░░░░░░░░░` 10.0% | 1 | 9 | 0 | 10 |
| Red Aggro | `░░░░░░░░░░` 0.0% | 0 | 10 | 0 | 10 |

Win rate is wins divided by completed games.

<details>
<summary>Run settings and deck versions</summary>

- Started at: 2026-11-24T00:38:50.957514+00:00
- Run ID: 45298775552
- Attempt: 1
- Workflow URL: https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45298775552
- Source commit: 266ad3d300ae282bf3f466428123b61e10de71e7
- Lineup: baseline
- Goal seat: 3
- Forge version: 2.0.16
- Java version: OpenJDK Runtime Environment Temurin-17.0.21+9 (build 17.0.21+9)
- Base seed: 42
- Forge game clock: 600 seconds
- Process deadline: 720 seconds
- Setup logs: [java-version stdout](java-version.stdout.log), [java-version stderr](java-version.stderr.log), [java-version peak&#95;rss](java-version.peak-rss-kib.txt), [fixture-validation stdout](fixture-validation.stdout.log), [fixture-validation stderr](fixture-validation.stderr.log), [fixture-validation peak&#95;rss](fixture-validation.peak-rss-kib.txt)

| Seat | Deck | Commander | Archetype | AI profile | Version (SHA-256) |
| --- | --- | --- | --- | --- | --- |
| 1 | Green Ramp | Ezuri, Renegade Leader | Ramp | Forge default | `cb545ee7c5cae13ecce3a10ffaab16d9f3d01cbc52ec698f83fa34ae18f22f8a` |
| 2 | Red Aggro | Krenko, Mob Boss | Aggro | Forge default | `e061729e12052512f5db503efd5455780aa5572ccf062149939d2fb1a79a1fda` |
| 3 | Orzhov Midrange | Daxos the Returned | Midrange | Forge default | `e236cb9ad3b109c7eea8a0d08437519c040b34fa4695339ff506cc4172e3ef91` |
| 4 | Azorius Control | Isperia, Supreme Judge | Control | Forge default | `5dbc7cafb6ea042ff94448d6c4ada903b9d0c7854f6b9a716055657a3f1cc73c` |

</details>

<details>
<summary>Goal deck telemetry by game</summary>

| Game | Result | First commander cast | Land plays / own turns | Combat damage taken |
| ---: | --- | --- | ---: | ---: |
| 1 | loss | Turn 13 | 4 / 4 (of first 4) | 48 |
| 2 | loss | Turn 36 | 3 / 4 (of first 4) | 70 |
| 3 | loss | Turn 9 | 4 / 4 (of first 4) | 63 |
| 4 | loss | Turn 12 | 4 / 4 (of first 4) | 76 |
| 5 | loss | Turn 22 | 4 / 4 (of first 4) | 41 |
| 6 | loss | Turn 5 | 4 / 4 (of first 4) | 42 |
| 7 | loss | Turn 10 | 4 / 4 (of first 4) | 68 |
| 8 | win | Turn 9 | 4 / 4 (of first 4) | 25 |
| 9 | loss | Turn 11 | 4 / 4 (of first 4) | 50 |
| 10 | loss | Turn 14 | 4 / 4 (of first 4) | 45 |

</details>

<details>
<summary>Game results and logs</summary>

| Game | Seats | Seed | Status | Winner | Runtime (s) | Reason | Logs |
| ---: | --- | ---: | --- | --- | ---: | --- | --- |
| 1 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 42 | won | Azorius Control | 29.839 | — | [stdout](game-0001/simulation.stdout.log), [stderr](game-0001/simulation.stderr.log), [peak&#95;rss](game-0001/simulation.peak-rss-kib.txt) |
| 2 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 43 | won | Green Ramp | 39.025 | — | [stdout](game-0002/simulation.stdout.log), [stderr](game-0002/simulation.stderr.log), [peak&#95;rss](game-0002/simulation.peak-rss-kib.txt) |
| 3 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 44 | won | Green Ramp | 22.688 | — | [stdout](game-0003/simulation.stdout.log), [stderr](game-0003/simulation.stderr.log), [peak&#95;rss](game-0003/simulation.peak-rss-kib.txt) |
| 4 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 45 | won | Azorius Control | 32.752 | — | [stdout](game-0004/simulation.stdout.log), [stderr](game-0004/simulation.stderr.log), [peak&#95;rss](game-0004/simulation.peak-rss-kib.txt) |
| 5 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 46 | won | Azorius Control | 38.008 | — | [stdout](game-0005/simulation.stdout.log), [stderr](game-0005/simulation.stderr.log), [peak&#95;rss](game-0005/simulation.peak-rss-kib.txt) |
| 6 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 47 | won | Azorius Control | 27.331 | — | [stdout](game-0006/simulation.stdout.log), [stderr](game-0006/simulation.stderr.log), [peak&#95;rss](game-0006/simulation.peak-rss-kib.txt) |
| 7 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 48 | won | Azorius Control | 40.631 | — | [stdout](game-0007/simulation.stdout.log), [stderr](game-0007/simulation.stderr.log), [peak&#95;rss](game-0007/simulation.peak-rss-kib.txt) |
| 8 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 49 | won | Orzhov Midrange | 70.157 | — | [stdout](game-0008/simulation.stdout.log), [stderr](game-0008/simulation.stderr.log), [peak&#95;rss](game-0008/simulation.peak-rss-kib.txt) |
| 9 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 50 | won | Azorius Control | 22.729 | — | [stdout](game-0009/simulation.stdout.log), [stderr](game-0009/simulation.stderr.log), [peak&#95;rss](game-0009/simulation.peak-rss-kib.txt) |
| 10 | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control | 51 | won | Green Ramp | 61.899 | — | [stdout](game-0010/simulation.stdout.log), [stderr](game-0010/simulation.stderr.log), [peak&#95;rss](game-0010/simulation.peak-rss-kib.txt) |

</details>
