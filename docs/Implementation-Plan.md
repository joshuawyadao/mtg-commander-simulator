# Plan

Validate Stage A by running one headless four-player Commander game on GitHub-hosted Ubuntu and retaining evidence of the four seats and winner.

## Scope

- **In scope** · Four Commander fixtures, pinned Forge and Java setup, a single-game runner, a hosted workflow, evidence review, and a pull request.
- **Later stages** · Batch scheduling, full CSV and JSON reports, deck comparison, and automatic report archiving.

## Action items

- [x] Pin and verify the Forge desktop archive, Java distribution and build, and GitHub Actions runner and dependencies.
- [x] Create four Forge-native decks and verify card resolution, deck sizes, color identity, singleton rules, and commander eligibility.
- [x] Add a single-game runner that records the command, inputs, raw logs, timings, memory, and process result. Require positive evidence of the expected pod and winner, and preserve diagnostics on failure.
- [x] Add focused tests for fixture validation and unambiguous winner, draw, timeout, and error handling. Check shell and workflow syntax and run the tests locally.
- [x] Run the one-game job on the feature branch before opening a PR. Inspect the downloadable evidence and remove the temporary branch trigger.
- [x] Document launch, evidence, troubleshooting, and the observed result. [Hosted verification](Stage-A-Feasibility.md#hosted-verification)
- Publish the branch and shepherd the PR through review and relevant checks.

## Open questions

None.
