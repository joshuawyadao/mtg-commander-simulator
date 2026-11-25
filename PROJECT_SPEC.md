# MTG Commander Simulation Framework
## Project Specification — v0.1

**Status:** Phase 4 Meren comparison verified on GitHub-hosted Ubuntu\
**Target environment:** Public GitHub repository + GitHub Actions  
**Primary technologies:** Java, Forge MTG, Python  
**Development workflow:** Codex  
**Initial milestone:** Generic 10-game Commander simulation proof of concept

---

## 1. Project Overview

Build a reusable, automated Magic: The Gathering Commander simulation framework using the open-source Forge rules engine.

The framework should accept Commander decklists, run AI-versus-AI games without a graphical interface, and produce structured reports.

The initial goal is to validate the simulation infrastructure, not optimize any particular deck.

Eventually, the framework should support comparing deck versions, evaluating different playstyles, and identifying weaknesses in deck construction.

### Guiding Principles

- Reuse Forge's existing MTG rules engine.
- Avoid implementing MTG rules from scratch.
- Keep the infrastructure independent of deck archetype.
- Run simulations remotely to avoid consuming the user's MacBook resources.
- Prefer free infrastructure and open-source software.
- Prioritize reproducibility and reliable results.
- Keep the first implementation intentionally small.
- Never confuse AI simulation performance with actual human multiplayer performance.

## 2. Proof-of-Concept Goal

Given four valid Commander decklists, automatically run ten multiplayer Commander games using Forge on GitHub Actions.

Generate a report containing:

- Number of games attempted and completed
- Winning deck for each completed game
- Total and per-game execution time
- Errors, crashes, and timeouts
- Forge version and simulation configuration
- Raw logs for debugging

The entire process should run without requiring the user's MacBook to execute simulations.

## 3. Architecture

```text
GitHub Repository
    |
    | Decklists + Configuration
    v
GitHub Actions (Manual Trigger)
    |
    v
Forge Headless Simulation
    |
    | Game Logs + Results
    v
Python Results Parser
    |
    v
CSV / JSON / Markdown Reports + Raw Logs
    |
    v
GitHub Actions Artifacts + Markdown Run Archive
```

### Technology Choices

| Component | Technology |
|---|---|
| Version control | GitHub |
| CI / Cloud execution | GitHub Actions |
| MTG rules engine | Forge |
| Game automation | Python / Shell |
| Results processing | Python |
| Configuration | YAML |
| Output | CSV, JSON, Markdown |
| Storage | GitHub Actions artifacts and a Git-tracked Markdown run archive |

Do not introduce a database, frontend, API server, or container orchestration unless a concrete technical requirement emerges.

## 4. Proposed Repository Structure

```text
mtg-commander-simulator/
├── .github/
│   └── workflows/
│       └── simulate.yml
├── decks/
│   ├── ramp.dck
│   ├── aggro.dck
│   ├── midrange.dck
│   └── control.dck
├── reports/
│   └── runs/
│       └── <run-id>/attempt-<attempt>/summary.md
├── scripts/
│   ├── setup_forge.sh
│   ├── run_simulation.py
│   └── parse_results.py
├── tests/
│   └── test_parser.py
├── config.yaml
├── README.md
└── PROJECT_SPEC.md
```

This structure is provisional and may be adjusted after inspecting Forge's actual requirements.

## 5. Implementation Stages

### Stage A — Forge Feasibility

Research and verify:

1. Forge's current supported Java version.
2. Official release and download mechanisms.
3. Headless simulation command syntax.
4. Commander deck import format.
5. Multiplayer AI support.
6. Logging and result-output capabilities.
7. Supported operating systems and resource requirements.

Then run one headless Commander game using four supported decks.

**Acceptance criteria:**
- Forge launches without a GUI.
- All four decks load successfully.
- The game completes or produces a diagnosable failure.
- A winner can be identified from a successful game.
- Logs are retained.

### Stage B — Ten-Game Batch

Create a reusable script that:

1. Accepts deck paths and a requested game count.
2. Validates basic configuration.
3. Launches Forge.
4. Detects failures and timeouts.
5. Parses available results.
6. Produces CSV, JSON, and Markdown summaries.

The system must distinguish completed games from failed or timed-out games.

Do not fabricate results or silently count failures as losses.

**Acceptance criteria:**
- Ten games can be requested.
- Each game is accounted for.
- Completed games have identifiable results.
- Failed games have diagnostic information.
- Reports can be generated automatically.

### Stage C — GitHub Actions

Create a manually triggered GitHub Actions workflow.

Requirements:

- Standard Ubuntu hosted runner
- Pinned Java and Forge versions
- No persistent server
- No automatic scheduled execution
- Configurable game count, initially limited to ten
- Job and process timeouts
- Downloadable reports and logs
- A Git-tracked Markdown summary for each batch attempt that produces one
- Minimal GitHub token permissions
- No unnecessary paid infrastructure

**Acceptance criteria:**
- A user can launch a batch from GitHub Actions.
- Simulations run entirely on GitHub-hosted resources.
- Results are downloadable.
- A run and its rerun appear in separate folders in the Markdown archive.
- Failed runs provide actionable diagnostics.
- The workflow stays within the intended free-resource limits.

## 6. Initial Test Decks

Use four simple, AI-friendly Commander archetypes.

| Archetype | Purpose |
|---|---|
| Mono-green creature ramp | Mana development and creature combat |
| Mono-red aggro | Early pressure and combat |
| White-black midrange | Removal and incremental value |
| Blue-white control | Interaction and longer games |

These are placeholders, not finalized decklists.

Select actual commanders and lists only after verifying Forge support.

Prefer straightforward cards and avoid complicated combos in the initial PoC.

## 7. Simulation Configuration

The configuration should eventually support:

```yaml
simulation:
  format: commander
  games: 10
  players: 4
  timeout_minutes: 10

decks:
  - decks/ramp.dck
  - decks/aggro.dck
  - decks/midrange.dck
  - decks/control.dck

reporting:
  formats:
    - csv
    - json
    - markdown
  retain_logs: true
```

This YAML is an illustrative target interface, not a confirmed Forge-native configuration format.

The implementation must translate configuration into the actual supported Forge command-line arguments.

## 8. Required Reporting

### Minimum Metrics

- Game identifier
- Deck names
- Winner
- Completion status
- Runtime
- Failure reason, if applicable
- Simulation engine version

### Markdown Run Report

- **Run summary.** Record the start time with time zone, run ID and attempt, workflow run URL, source commit, Forge and Java versions, settings, total runtime, and counts of attempted games, completions, draws, timeouts, and failures.
- **Goal deck dashboard.** Highlight the designated seat with its win rate, record, pros and cons, and game-by-game outcomes. Use completed games that included the goal deck to summarize its win count relative to its opponents and identify the most frequent winners in its losses. The alternate lineups default to seat three and the run can explicitly select any seat.
- **Gameplay telemetry.** For completed games with recognized Forge logs, record each seat's first logged commander cast on the game turn number, land plays during its own first four turns, the number of those turns observed, and combat damage taken by the player. Show goal deck coverage and per-game values. Calculate the early-land median using games where the seat reached its fourth turn. Omit unavailable telemetry from aggregates and preserve recorded zero values.
- **Deck results.** Record each deck's name, version, archetype, AI profile, completed games played, wins, losses, draws, and win rate. Divide wins by completed games played and show the rate as unavailable when that count is zero. Surface timeouts and failures in batch health and in the game details.
- **Game results.** Record the seats, seed, runtime, and winner, draw, timeout, or failure for each attempt. Include the path of each available raw log within the downloadable artifact.

### Run Archive

Archive the Markdown summary at `reports/runs/<run-id>/attempt-<attempt>/summary.md` in Git. Use the GitHub Actions run ID and attempt number so each rerun has its own record. Preserve earlier summaries and save partial or failed-run summaries whenever they are generated.

Upload the Markdown summary, CSV and JSON exports, and available raw logs together as a GitHub Actions artifact. Git retains the Markdown record beyond the Actions retention window. In Stage C, give only the archive job repository write access. It prepares a one-report branch and links to the comparison. The owner opens and merges the archive pull request after CI Verify succeeds. [Run archive guide](reports/runs/README.md)

### Future Metrics

- Land and mana development
- Creatures and tokens on battlefield
- Damage dealt and received
- Card draw
- Board-wipe recovery
- Turn of elimination
- Combat versus noncombat wins

Do not implement future metrics until their availability through Forge logs or instrumentation has been verified.

## 9. Technical Risks

### Forge AI Quality

Forge's AI may struggle with complicated Commander strategies.

Mitigation:
- Start with simple archetypes.
- Inspect representative game logs.
- Avoid treating simulated win rates as authoritative.

### Card Compatibility

Some cards may have incomplete or unsupported implementations.

Mitigation:
- Validate card availability.
- Record unsupported cards.
- Use known-supported decks for the initial PoC.

### Logging Limitations

Forge may not expose every desired metric.

Mitigation:
- Start with basic game outcomes.
- Investigate instrumentation only after the generic PoC works.

### Runtime and Resource Usage

Multiplayer Commander games may be computationally expensive.

Mitigation:
- Start with one game.
- Scale to ten only after successful validation.
- Apply timeouts.
- Measure memory and runtime.
- Avoid unbounded parallel execution.

### Reproducibility

AI behavior and random draws can introduce variance.

Mitigation:
- Pin Forge versions.
- Record decklist versions.
- Record simulation configuration.
- Investigate whether deterministic seeds are supported.
- Preserve relevant logs.

## 10. Explicitly Out of Scope

The initial PoC must not include:

- Custom MTG rules implementation
- Custom AI strategy engine
- Automated deck optimization
- Automatic card substitutions
- Web dashboard
- Database
- Cloud server
- Scheduled simulation jobs
- King of the Oathbreakers-specific logic
- Complex archetype-specific analytics

These features may be considered after validating the generic infrastructure.

## 11. Future Roadmap

### Phase 1 — Generic PoC
Run ten Commander games in GitHub Actions.

### Phase 2 — Multi-Archetype Validation
Validate graveyard recursion and spellslinger against three fixed baseline opponents. Both new lineups completed ten hosted games and produced Git-tracked summaries. [Phase 2 verification](docs/Phase-2-Verification.md)

### Phase 3 — Detailed Telemetry
Start with the first logged commander cast, early land plays, and combat damage taken. Further board state, token generation, combat, and resource-development metrics depend on reliable evidence from Forge.

### Phase 4 — Deck Version Comparison
Compare two versions using matched seeds and the same goal seat, opponents, AI profiles, engine, and simulation settings. Show paired win rates and telemetry deltas with explicit denominators and a seed-level audit trail. Archive the comparison through the report review process. The first comparison replaces Rise from the Grave with an additional Swamp in the Meren deck.

### Phase 5 — Strategic Evaluation
Start with Meren's targeted end-step recursion. Record the turn, target, matching resolution, and the return destination when same-card log evidence supports it. Show coverage, timing, and numbered log examples in the goal deck dashboard. Use hand-reviewed seed logs to document visible strategic tradeoffs and gaps in the decision context.

### Phase 6 — Optional Optimization
Suggest card changes based on collected evidence, with human approval before modifying decklists.

## 12. Initial Target Deck

The eventual first real-world project is:

**King of the Oathbreakers — Version 1.1**

Format: Commander  
Target power: Bracket 2  
Colors: White / Black  
Strategy: Spirit tribal, phasing, token generation, resource conversion, and combat finishers.

Preferred playstyle:
- Steady board development
- Defensive flying creatures
- Token doublers
- Sacrifice outlets for temporary mana acceleration
- Large finishing combat attacks
- No intentional infinite combos
- No sacrifice-drain-focused win condition

This deck is not part of the generic PoC.

Its existing list should be independently validated before later importing it.

## 13. Instructions for Codex

When beginning implementation:

1. Read this specification completely.
2. Research Forge's current documentation and repository.
3. Confirm that the proposed architecture is technically feasible.
4. Identify unsupported assumptions before writing implementation code.
5. Present any necessary architecture changes.
6. Implement Stage A first.
7. Validate Stage A before proceeding to Stage B.
8. Validate Stage B before proceeding to Stage C.
9. Add automated tests for result parsing and failure handling.
10. Document setup, operation, limitations, and troubleshooting.

**Do not claim simulations succeeded unless actual game results and logs confirm completion.**

Do not automatically proceed to advanced deck analytics or optimization.

### Project Definition of Done

The generic PoC is complete when a public GitHub repository contains a reproducible, manually triggered GitHub Actions workflow capable of running ten Forge Commander games and producing downloadable, trustworthy results. The reference run must have a Markdown summary in the run archive.

---

**Project status:** First Phase 4 comparison verified. See the [hosted runs and archive evidence](docs/Phase-4-Verification.md).
