# Plan

Turn the verified Stage A game into a reusable four-player Commander batch and verify ten attempts on hosted Ubuntu.

## Scope

- Stage B includes a Python CLI, four Forge-native decks per run, sequential execution, CSV, JSON and Markdown reports, automated tests, and one hosted verification run.
- Stage C delivers the permanent workflow and Git archive described in the reporting requirements.

## Action items

- [x] Reuse the pinned Forge setup, Java deck validation, process logging, and result parsing from Stage A. Preserve the single-game smoke command and evidence format.
- [x] Add a batch CLI for deck paths, game count, seed, and deadlines. Validate a staged copy of each deck, then run one isolated Forge process per game and keep raw diagnostics for each attempt.
- [x] Generate the three report formats from the same result records. Report verified wins, genuine draws, timeouts, and failures individually, and exclude timeouts and failures from deck win rates.
- [x] Test invalid configuration, mixed results, setup failure, and report consistency. Run the targeted batch suite, full unittest discovery, shell syntax check, and diff checks.
- [x] Fix the recovered AI decision timeout misclassified by the first hosted batch. Replay the captured game 8 logs and test that genuine game timeouts and unrelated exceptions still fail.
- [x] Document the command, report outputs, and troubleshooting in the README. Update the specification and hosted evidence after the ten-game run.
- [x] Verify ten attempts on hosted Ubuntu with the pinned toolchain. Download and reconcile the reports against the raw game logs. [Hosted verification](Stage-B-Verification.md)
- [x] Record the hosted evidence and restore the one-game dispatch before publishing the pull request.

## Open questions

None.
