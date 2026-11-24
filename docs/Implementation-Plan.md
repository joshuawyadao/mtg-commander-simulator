# Plan

Use Forge game logs to add three per-seat gameplay metrics and show the designated deck's results in the Markdown dashboard.

## Scope

- In: first commander cast by game turn, land plays during the seat's first four turns, and combat damage taken by that player.
- In: additive game telemetry in JSON, the goal deck's dashboard, and hosted verification of all three presets.
- Out: new Forge instrumentation, token and board-state metrics, changes to earlier archives, and changes to the production workflow.

## Action items

- [x] Check the pinned Forge event format and the retained Phase 2 logs.
- [x] Parse the three metrics independently of game outcome classification. Distinguish a confirmed zero or no cast from unavailable evidence.
- [x] Add a compact goal deck summary and per-game telemetry to the report.
- [x] Cover incomplete logs, rotating active players, and the reporting contract. Run unit tests and shell checks.
- [x] Update the README and project spec with units, eligibility, and limitations.
- [x] Run a one-game smoke check and then a ten-game hosted batch for each preset. Compare the generated report branches with their artifacts and preserve the verified dashboards on the feature branch.
- [x] Prepare the Phase 3 pull request. The GitHub pull request tracks CI and review.

## Open questions

None.
