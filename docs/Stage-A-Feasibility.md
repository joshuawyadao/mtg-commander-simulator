# Stage A feasibility review

Forge 2.0.16 loaded four legal Commander decks and produced a verifiable winner on GitHub-hosted Ubuntu. The source findings and the completed run evidence are recorded below.

## Findings

- **Headless Commander.** The desktop `sim` entry point enables headless Java graphics by default. The direct Commander path registers one AI per deck, loads the deck's commander, and starts the player at 40 life. Select `-f commander -n 1` and give `-d` four `.dck` basenames plus `-D` with their absolute directory. The `-p` flag controls tournament seat count. [Desktop entry point](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-gui-desktop/src/main/java/forge/view/Main.java) · [Simulation CLI](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-gui-desktop/src/main/java/forge/view/SimulateMatch.java) · [Commander registration](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-game/src/main/java/forge/game/player/RegisteredPlayer.java)
- **Release and Java.** Use the stable `forge-installer-2.0.16.tar.bz2` asset, approximately 287 MB, with a pinned Java 17 build. Verify the SHA-256 published on the release, extract the desktop JAR and its companion resources together, and launch the desktop JAR with `java -jar`. [Release assets and checksums](https://github.com/Card-Forge/forge/releases/expanded_assets/forge-2.0.16) · [Release packaging](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-installer/pom.xml) · [Java target](https://github.com/Card-Forge/forge/blob/forge-2.0.16/pom.xml)
- **Deck import.** Use Forge-native `.dck` files with `[metadata]` and a unique `Name`, `[Commander]`, and `[Main]`. For the first pod, use four decks with one eligible commander and 99 main-deck cards each. The simulation loader can accept a deck without a full legality check. An unrecognized card can become a placeholder, so verify card resolution and legality against the pinned release. [Deck serializer](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-core/src/main/java/forge/deck/io/DeckSerializer.java) · [Deck conformance](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-core/src/main/java/forge/deck/DeckFormat.java) · [Card resolution](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-core/src/main/java/forge/deck/CardPool.java)
- **Outcomes and timeouts.** Forge prints human-readable results and elapsed time. The built-in clock defaults to 120 seconds and can label a timeout as a draw. A deck-load failure can return exit status zero. Preserve both streams, check for timeout and failure diagnostics, and require a terminal result before counting a game. `-c` sets the game clock in seconds. Use a separate process deadline for startup and shutdown. `-s` seeds Forge's RNG. Exact replay remains unverified. [Simulation output and clock](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-gui-desktop/src/main/java/forge/view/SimulateMatch.java) · [Process exit behavior](https://github.com/Card-Forge/forge/blob/forge-2.0.16/forge-gui-desktop/src/main/java/forge/view/Main.java)
- **GitHub Actions.** The standard public `ubuntu-24.04` runner has 4 vCPUs, 16 GB RAM, and 14 GB of storage. Standard hosted runner compute is free for public repositories. The manually dispatched workflow needs to exist on the default branch before it can be triggered. Make logs available as artifacts and measure startup, game time, and peak memory to inform the later batch budget. [Hosted runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#standard-github-hosted-runners-for-public-repositories) · [Manual dispatch](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow) · [Artifact upload](https://github.com/actions/upload-artifact)

## Stage A plan

1. Pin `ubuntu-24.04`, a Java 17 build, and the Forge release archive and digest. Verify the desktop JAR and bundled resources after extraction.
2. Prepare four simple fixtures for the archetypes in the [project specification](../PROJECT_SPEC.md). Verify commander eligibility, card resolution, deck size, color identity, singleton rules, and legality.
3. Add a minimal manual smoke test job with isolated Forge data directories and read-only repository permissions. Start with a fixed seed, full logs, a 600-second game clock, and longer process and job deadlines. Reserve job time for uploading the logs.
4. Run one four-seat game. Save stdout, stderr, process status, wall time, peak memory, Forge and Java versions, the seed, and deck hashes. Retain available diagnostics if the run fails.
5. Verify that the four expected decks entered a Commander game and that its terminal result maps a winner to one of those decks. Record genuine draws, timeouts, and failures separately. A verified four-player game with a winner gates Stage B.

## Hosted verification

[GitHub Actions run 44415927221](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44415927221) passed on revision `1fa7dfd`. Forge validated all four decks and logged an outcome for each expected seat. The terminal result identified **Azorius Control**, led by **Isperia, Supreme Judge**, as the winner.

| Setting or measurement | Observed value |
|---|---|
| Runner and engine | Ubuntu 24.04, Forge 2.0.16, Temurin 17.0.21+9 |
| Pod | Green Ramp, Red Aggro, Orzhov Midrange, Azorius Control |
| Seed | `42` |
| Forge game duration | 24.297 s |
| Simulation process wall time | 30.001 s |
| Simulation process peak RSS | 1,130,084 KiB |

The [evidence artifact](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44415927221/artifacts/14479487796) contains deck hashes, commands, and raw logs. The downloaded evidence confirmed all four hashes match the checked-in decks. An earlier run exposed Forge's shared label for player outcomes, duration, and turn count. The corrected parser accepted that run's raw log and passed the repeated hosted test. [Earlier run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/44415532267)

The workflow used a temporary feature-branch trigger for this verification. The committed workflow runs the game on manual dispatch after merge, and pull requests run the lightweight checks.

## Implications for later stages

Start Stage B with one Forge process per game in a sequential batch so each attempt has its own seed, deadline, and logs. Feed those results into the Python reporting pipeline. Keep GitHub Actions focused on validating the framework and revisit hosting if deck analysis grows into a sustained compute workload. [GitHub Actions terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#actions)
