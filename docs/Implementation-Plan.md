# Plan

Validate Stage A by running one headless four-player Commander game on GitHub-hosted Ubuntu and retaining evidence of the four seats and winner.

## Scope

- **In scope** · Four Commander fixtures, pinned Forge and Java setup, a single-game runner, a hosted workflow, evidence review, and a pull request.
- **Later stages** · Batch scheduling, full CSV and JSON reports, deck comparison, and automatic report archiving.

## Action items

- [ ] Pin and verify the Forge desktop archive, Java distribution and build, and GitHub Actions runner and dependencies.
- [ ] Create four Forge-native decks and verify card resolution, deck sizes, color identity, singleton rules, and commander eligibility.
- [ ] Add a single-game runner that records the command, inputs, raw logs, timings, memory, and process result. Require positive evidence of the expected pod and winner, and preserve diagnostics on failure.
- [ ] Add focused tests for fixture validation and unambiguous winner, draw, timeout, and error handling. Check shell and workflow syntax and run the tests locally.
- [ ] Run the one-game job on the feature branch before opening a PR. Use a temporary branch-only push trigger because manual dispatch requires the workflow on the default branch. Inspect the downloadable evidence and remove the temporary trigger for the final PR.
- [ ] Document launch, evidence, troubleshooting, and the observed result. Publish the branch and shepherd the PR through review and relevant checks.

## Open questions

None.
