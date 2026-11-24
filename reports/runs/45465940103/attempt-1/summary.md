# Commander A/B simulation dashboard

**A · Golgari Graveyard Recursion** · Meren of Clan Nel Toth · seat 3 · [Run 45463937991](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463937991) · attempt 1

**B · Golgari Graveyard Recursion (extra Swamp)** · Meren of Clan Nel Toth · seat 3 · [Run 45463934391](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463934391) · attempt 1

**10 / 10 matched seeds completed in both versions.** Each metric uses eligible matched pairs. B − A shows the observed difference.

## Scorecard

| Goal deck metric | A · baseline | B · card swap | B − A | Paired sample |
| --- | ---: | ---: | ---: | ---: |
| Win rate | **50%** | **60%** | +10 pp | 10 pairs |
| Commander cast rate | **100%** | **100%** | +0 pp | 10 pairs |
| Median first cast | **Turn 17.5** | **Turn 15.5** | -2 turns | 10 pairs |
| Median early land plays | **4 plays** | **4 plays** | +0 plays | 10 pairs |
| Median combat damage taken | **42.5 damage** | **38 damage** | -4.5 damage | 10 pairs |

## Matched seed outcomes

🟩 Win · 🟥 Loss · 🟨 Draw · ⚠️ Failed · ⏱️ Timeout · ⬜ Missing

| Seed | A · baseline | B · card swap |
| ---: | --- | --- |
| 42 | 🟥 Loss | 🟩 Win |
| 43 | 🟩 Win | 🟩 Win |
| 44 | 🟩 Win | 🟩 Win |
| 45 | 🟥 Loss | 🟥 Loss |
| 46 | 🟩 Win | 🟩 Win |
| 47 | 🟩 Win | 🟥 Loss |
| 48 | 🟩 Win | 🟥 Loss |
| 49 | 🟥 Loss | 🟩 Win |
| 50 | 🟥 Loss | 🟩 Win |
| 51 | 🟥 Loss | 🟥 Loss |

<details>
<summary>How to read the scorecard</summary>

A matched pair uses the same seed and completes in both versions (win or draw). Failed, timed out, or missing games appear above but do not enter paired metrics. Win rate counts goal deck wins among paired completed games; a draw is not a win. Commander cast rate counts games with an observed cast among pairs with telemetry in both versions. First cast medians include pairs with a cast observed in both versions. Early land play medians include pairs with all four early own turns observed in both versions. Combat damage medians include pairs with telemetry in both versions. Each row's sample is the number of pairs eligible for that specific metric. **No cast** means a completed game had telemetry but no commander cast; **Unavailable** means telemetry was missing; **0** is a measured zero. Percent deltas use percentage points (pp).

</details>

<details>
<summary>Game details and exclusions</summary>

| Seed | A result · winner | B result · winner | A first cast | B first cast | A early lands | B early lands | A damage | B damage | Reason / exclusion |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 42 | 🟥 Loss · Red Aggro | 🟩 Win · Golgari Graveyard Recursion (extra Swamp) | Turn 13 | Turn 17 | 4 / 4 own turns | 4 / 4 own turns | 56 | 35 | — |
| 43 | 🟩 Win · Golgari Graveyard Recursion | 🟩 Win · Golgari Graveyard Recursion (extra Swamp) | Turn 24 | Turn 12 | 4 / 4 own turns | 4 / 4 own turns | 0 | 18 | — |
| 44 | 🟩 Win · Golgari Graveyard Recursion | 🟩 Win · Golgari Graveyard Recursion (extra Swamp) | Turn 13 | Turn 13 | 4 / 4 own turns | 4 / 4 own turns | 41 | 26 | — |
| 45 | 🟥 Loss · Azorius Control | 🟥 Loss · Azorius Control | Turn 16 | Turn 28 | 4 / 4 own turns | 4 / 4 own turns | 47 | 42 | — |
| 46 | 🟩 Win · Golgari Graveyard Recursion | 🟩 Win · Golgari Graveyard Recursion (extra Swamp) | Turn 18 | Turn 18 | 4 / 4 own turns | 4 / 4 own turns | 44 | 41 | — |
| 47 | 🟩 Win · Golgari Graveyard Recursion | 🟥 Loss · Red Aggro | Turn 17 | Turn 9 | 4 / 4 own turns | 4 / 4 own turns | 13 | 58 | — |
| 48 | 🟩 Win · Golgari Graveyard Recursion | 🟥 Loss · Azorius Control | Turn 18 | Turn 14 | 4 / 4 own turns | 3 / 4 own turns | 25 | 46 | — |
| 49 | 🟥 Loss · Azorius Control | 🟩 Win · Golgari Graveyard Recursion (extra Swamp) | Turn 33 | Turn 37 | 3 / 4 own turns | 3 / 4 own turns | 47 | 0 | — |
| 50 | 🟥 Loss · Green Ramp | 🟩 Win · Golgari Graveyard Recursion (extra Swamp) | Turn 19 | Turn 23 | 4 / 4 own turns | 4 / 4 own turns | 66 | 29 | — |
| 51 | 🟥 Loss · Azorius Control | 🟥 Loss · Azorius Control | Turn 10 | Turn 14 | 3 / 4 own turns | 4 / 4 own turns | 26 | 45 | — |

</details>

<details>
<summary>Sources, deck versions, and shared settings</summary>

- A: [Run 45463937991](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463937991), attempt 1; goal deck SHA-256 `087865b6a6ae0474294818b01586400bccf5dae7c10289f4dfe0aacbf46baf2a`
- B: [Run 45463934391](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45463934391), attempt 1; goal deck SHA-256 `d731932ba16f6ef4799f59b4857c6e187720ed28bb0d83446199ecf433008bd1`
- Seed range: 42 through 51
- Forge: 2.0.16; Java: OpenJDK Runtime Environment Temurin-17.0.21+9 (build 17.0.21+9)
- Source commit: 4ccd935a94640d8aa99904138d6fd249869db306
- AI profile: Forge default
- Game clock: 600 s; process deadline: 720 s

| Opponent seat | Deck | SHA-256 |
| ---: | --- | --- |
| 1 | Green Ramp | `cb545ee7c5cae13ecce3a10ffaab16d9f3d01cbc52ec698f83fa34ae18f22f8a` |
| 2 | Red Aggro | `e061729e12052512f5db503efd5455780aa5572ccf062149939d2fb1a79a1fda` |
| 4 | Azorius Control | `5dbc7cafb6ea042ff94448d6c4ada903b9d0c7854f6b9a716055657a3f1cc73c` |

</details>
