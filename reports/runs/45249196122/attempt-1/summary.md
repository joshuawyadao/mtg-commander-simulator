# Commander simulation batch

## Run summary

- Started at: 2026-11-23T19:28:19.419299+00:00
- Run ID: 45249196122
- Attempt: 1
- Workflow URL: https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45249196122
- Source commit: 00fee308196771a158279fa6ecff01b54d373668
- Lineup: graveyard-recursion
- Forge version: 2.0.16
- Java version: OpenJDK Runtime Environment Temurin-17.0.21+9 (build 17.0.21+9)
- Games requested: 10
- Base seed: 42
- Forge game clock: 600 seconds
- Process deadline: 720 seconds
- Total wall time: 468.76 seconds
- Attempted: 10
- Completed: 10
- Wins: 10
- Draws: 0
- Timeouts: 0
- Failures: 0
- Batch error: —
- Setup logs: [java-version stdout](java-version.stdout.log), [java-version stderr](java-version.stderr.log), [java-version peak&#95;rss](java-version.peak-rss-kib.txt), [fixture-validation stdout](fixture-validation.stdout.log), [fixture-validation stderr](fixture-validation.stderr.log), [fixture-validation peak&#95;rss](fixture-validation.peak-rss-kib.txt)

## Deck results

| Seat | Deck | Version (SHA-256) | Archetype | AI profile | Completed | Wins | Losses | Draws | Win rate |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Green Ramp | cb545ee7c5cae13ecce3a10ffaab16d9f3d01cbc52ec698f83fa34ae18f22f8a | Ramp | Forge default | 10 | 2 | 8 | 0 | 20.0% |
| 2 | Red Aggro | e061729e12052512f5db503efd5455780aa5572ccf062149939d2fb1a79a1fda | Aggro | Forge default | 10 | 1 | 9 | 0 | 10.0% |
| 3 | Golgari Graveyard Recursion | 087865b6a6ae0474294818b01586400bccf5dae7c10289f4dfe0aacbf46baf2a | Graveyard recursion | Forge default | 10 | 4 | 6 | 0 | 40.0% |
| 4 | Azorius Control | 5dbc7cafb6ea042ff94448d6c4ada903b9d0c7854f6b9a716055657a3f1cc73c | Control | Forge default | 10 | 3 | 7 | 0 | 30.0% |

## Game results

| Game | Seats | Seed | Status | Winner | Runtime (s) | Reason | Logs |
| ---: | --- | ---: | --- | --- | ---: | --- | --- |
| 1 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 42 | won | Red Aggro | 50.279 | — | [stdout](game-0001/simulation.stdout.log), [stderr](game-0001/simulation.stderr.log), [peak&#95;rss](game-0001/simulation.peak-rss-kib.txt) |
| 2 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 43 | won | Golgari Graveyard Recursion | 18.95 | — | [stdout](game-0002/simulation.stdout.log), [stderr](game-0002/simulation.stderr.log), [peak&#95;rss](game-0002/simulation.peak-rss-kib.txt) |
| 3 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 44 | won | Golgari Graveyard Recursion | 62.011 | — | [stdout](game-0003/simulation.stdout.log), [stderr](game-0003/simulation.stderr.log), [peak&#95;rss](game-0003/simulation.peak-rss-kib.txt) |
| 4 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 45 | won | Azorius Control | 40.764 | — | [stdout](game-0004/simulation.stdout.log), [stderr](game-0004/simulation.stderr.log), [peak&#95;rss](game-0004/simulation.peak-rss-kib.txt) |
| 5 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 46 | won | Green Ramp | 62.55 | — | [stdout](game-0005/simulation.stdout.log), [stderr](game-0005/simulation.stderr.log), [peak&#95;rss](game-0005/simulation.peak-rss-kib.txt) |
| 6 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 47 | won | Golgari Graveyard Recursion | 55.092 | — | [stdout](game-0006/simulation.stdout.log), [stderr](game-0006/simulation.stderr.log), [peak&#95;rss](game-0006/simulation.peak-rss-kib.txt) |
| 7 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 48 | won | Golgari Graveyard Recursion | 46.972 | — | [stdout](game-0007/simulation.stdout.log), [stderr](game-0007/simulation.stderr.log), [peak&#95;rss](game-0007/simulation.peak-rss-kib.txt) |
| 8 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 49 | won | Azorius Control | 37.317 | — | [stdout](game-0008/simulation.stdout.log), [stderr](game-0008/simulation.stderr.log), [peak&#95;rss](game-0008/simulation.peak-rss-kib.txt) |
| 9 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 50 | won | Green Ramp | 52.449 | — | [stdout](game-0009/simulation.stdout.log), [stderr](game-0009/simulation.stderr.log), [peak&#95;rss](game-0009/simulation.peak-rss-kib.txt) |
| 10 | Green Ramp, Red Aggro, Golgari Graveyard Recursion, Azorius Control | 51 | won | Azorius Control | 32.552 | — | [stdout](game-0010/simulation.stdout.log), [stderr](game-0010/simulation.stderr.log), [peak&#95;rss](game-0010/simulation.peak-rss-kib.txt) |
