# Plan

Put the designated testing deck's observed pros and cons next to its record so readers can skim what went well and where it struggled.

## Scope

- In: The goal deck section of generated Markdown and its documentation in README.md and PROJECT_SPEC.md.
- Out: New gameplay telemetry, historical archive rewrites, and structured export changes.

## Action items

- [x] Check the available evidence in the goal deck record and the per-game outcomes.
- [x] Add a compact pros and cons table before the outcome strip. Show whether the goal led the lineup in wins and who won most often in its losses.
- [x] Cover ties, winless and lossless batches, no completed games, and games without the goal deck in the report tests.
- [x] Update README.md and PROJECT_SPEC.md to explain what the takeaways measure.
- [x] Run the report tests and the full suite. Re-render both verified ten-game lineups and check the GitHub Markdown output.
- [x] Prepare the change for the Phase 2 branch. Track hosted CI and review on [PR #6](https://github.com/joshuawyadao/mtg-commander-simulator/pull/6).

## Open questions

None.

## Required fast CI

- [x] Run CI Verify on main pushes and all pull requests targeting main, including report-only changes.
- [x] Preserve the Stage C verification step and keep Forge gameplay behind manual dispatch.
- [ ] Confirm hosted fast checks and review on the updated PR head.
- [ ] Enable the required check on main once the unfiltered workflow and Stage C's checked archive path are live.
