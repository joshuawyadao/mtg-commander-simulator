# Commander simulation dashboard

## Goal deck · Golgari Graveyard Recursion

Meren of Clan Nel Toth · Seat 3 · Graveyard recursion

| Win rate | Wins | Losses | Draws | Completed games |
| ---: | ---: | ---: | ---: | ---: |
| **40.0%** | **4** | 6 | 0 | 10 |

### Pros and cons

| Pros | Cons |
| --- | --- |
| Led the lineup with **4** wins. | **Azorius Control** won **3 of 6** games the goal deck lost. |

### How the deck played

Telemetry from **10 of 10** completed games with the goal deck.

| Metric | Result | Games measured |
| --- | ---: | ---: |
| Commander cast | **10 of 10** games | 10 |
| First commander cast | **Turn 17.5 (median)** | 10 casts |
| Land plays in first 4 own turns | **4 plays (median)** | 10 with 4 turns |
| Combat damage taken | **44 damage** (median) | 10 |

### Meren recursion

Observed in **10 of 10** completed games with Meren.

| Logged target evidence | Result |
| --- | ---: |
| Games with targeted triggers | **10 of 10** observed |
| First targeted trigger (Forge game turn) | **Turn 29.5 (median)** across 10 games |
| Targets | **49** |
| Matched resolutions | **49** |
| Confirmed battlefield returns | **23** |
| Resolved, destination unknown | **26** |
| Resolution unconfirmed | **0** |

Forge's logs can leave the return destination unknown, including returns to hand.

#### Log examples

| Game · seed | Turn | Target | Observed result | Raw stdout lines |
| --- | ---: | --- | --- | --- |
| 1 · 42 | 48 | Noxious Gearhulk | Returned to battlefield | [stdout](game-0001/simulation.stdout.log) · L1360, L1361, L1365 |
| 2 · 43 | 24 | Plaguecrafter | Resolved, destination unknown | [stdout](game-0002/simulation.stdout.log) · L679, L680 |
| 3 · 44 | 25 | Merciless Executioner | Resolved, destination unknown | [stdout](game-0003/simulation.stdout.log) · L564, L565 |

The workflow run under **Run settings and deck versions** provides the downloadable stdout.

### Game-by-game

🟥 `01 L` · 🟩 `02 W` · 🟩 `03 W` · 🟥 `04 L` · 🟥 `05 L` · 🟩 `06 W` · 🟩 `07 W` · 🟥 `08 L` · 🟥 `09 L` · 🟥 `10 L`

W win · L loss

## Batch health

| Completed / requested | Attempted | Draws | Timeouts | Failures | Wall time |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **10 / 10** | 10 | 0 | 0 | 0 | 350.713 s |

## Deck standings

| Deck | Win rate | Wins | Losses | Draws | Completed |
| --- | --- | ---: | ---: | ---: | ---: |
| **Golgari Graveyard Recursion** | `████░░░░░░` 40.0% | 4 | 6 | 0 | 10 |
| Azorius Control | `███░░░░░░░` 30.0% | 3 | 7 | 0 | 10 |
| Green Ramp | `██░░░░░░░░` 20.0% | 2 | 8 | 0 | 10 |
| Red Aggro | `█░░░░░░░░░` 10.0% | 1 | 9 | 0 | 10 |

Win rate is wins divided by completed games.

<details>
<summary>Run settings and deck versions</summary>

- Started at: 2026-11-25T05:52:07.289816+00:00
- Run ID: 45556465077
- Attempt: 1
- Workflow URL: https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45556465077
- Source commit: eac4ebc29451464ac0bae0f7ad0e16ad74635478
- Lineup: graveyard-recursion
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
| 3 | Golgari Graveyard Recursion | Meren of Clan Nel Toth | Graveyard recursion | Forge default | `087865b6a6ae0474294818b01586400bccf5dae7c10289f4dfe0aacbf46baf2a` |
| 4 | Azorius Control | Isperia, Supreme Judge | Control | Forge default | `5dbc7cafb6ea042ff94448d6c4ada903b9d0c7854f6b9a716055657a3f1cc73c` |

</details>

<details>
<summary>Goal deck telemetry by game</summary>

| Game | Result | First commander cast | Land plays / own turns | Combat damage taken |
| ---: | --- | --- | ---: | ---: |
| 1 | loss | Turn 13 | 4 / 4 (of first 4) | 56 |
| 2 | win | Turn 24 | 4 / 4 (of first 4) | 0 |
| 3 | win | Turn 13 | 4 / 4 (of first 4) | 41 |
| 4 | loss | Turn 16 | 4 / 4 (of first 4) | 47 |
| 5 | loss | Turn 18 | 4 / 4 (of first 4) | 97 |
| 6 | win | Turn 17 | 4 / 4 (of first 4) | 30 |
| 7 | win | Turn 18 | 4 / 4 (of first 4) | 25 |
| 8 | loss | Turn 33 | 3 / 4 (of first 4) | 47 |
| 9 | loss | Turn 19 | 4 / 4 (of first 4) | 66 |
| 10 | loss | Turn 10 | 3 / 4 (of first 4) | 26 |

</details>

<details>
<summary>Game results and logs</summary>

| Game | Seats | Seed | Status | Winner | Runtime (s) | Reason | Logs |
| ---: | --- | ---: | --- | --- | ---: | --- | --- |
| 1 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 42 | won | Red Aggro | 36.829 | — | [stdout](game-0001/simulation.stdout.log), [stderr](game-0001/simulation.stderr.log), [peak&#95;rss](game-0001/simulation.peak-rss-kib.txt) |
| 2 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 43 | won | Golgari Graveyard Recursion | 15.793 | — | [stdout](game-0002/simulation.stdout.log), [stderr](game-0002/simulation.stderr.log), [peak&#95;rss](game-0002/simulation.peak-rss-kib.txt) |
| 3 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 44 | won | Golgari Graveyard Recursion | 46.362 | — | [stdout](game-0003/simulation.stdout.log), [stderr](game-0003/simulation.stderr.log), [peak&#95;rss](game-0003/simulation.peak-rss-kib.txt) |
| 4 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 45 | won | Azorius Control | 32.49 | — | [stdout](game-0004/simulation.stdout.log), [stderr](game-0004/simulation.stderr.log), [peak&#95;rss](game-0004/simulation.peak-rss-kib.txt) |
| 5 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 46 | won | Green Ramp | 41.02 | — | [stdout](game-0005/simulation.stdout.log), [stderr](game-0005/simulation.stderr.log), [peak&#95;rss](game-0005/simulation.peak-rss-kib.txt) |
| 6 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 47 | won | Golgari Graveyard Recursion | 38.563 | — | [stdout](game-0006/simulation.stdout.log), [stderr](game-0006/simulation.stderr.log), [peak&#95;rss](game-0006/simulation.peak-rss-kib.txt) |
| 7 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 48 | won | Golgari Graveyard Recursion | 36.687 | — | [stdout](game-0007/simulation.stdout.log), [stderr](game-0007/simulation.stderr.log), [peak&#95;rss](game-0007/simulation.peak-rss-kib.txt) |
| 8 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 49 | won | Azorius Control | 30.103 | — | [stdout](game-0008/simulation.stdout.log), [stderr](game-0008/simulation.stderr.log), [peak&#95;rss](game-0008/simulation.peak-rss-kib.txt) |
| 9 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 50 | won | Green Ramp | 40.24 | — | [stdout](game-0009/simulation.stdout.log), [stderr](game-0009/simulation.stderr.log), [peak&#95;rss](game-0009/simulation.peak-rss-kib.txt) |
| 10 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 51 | won | Azorius Control | 25.083 | — | [stdout](game-0010/simulation.stdout.log), [stderr](game-0010/simulation.stderr.log), [peak&#95;rss](game-0010/simulation.peak-rss-kib.txt) |

</details>
