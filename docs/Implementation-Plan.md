# Plan

Make the generated Markdown a skimmable dashboard centered on the designated goal deck and the outcomes of its games.

## Scope

- Extend Phase 2 PR #6 with a GitHub-renderable Markdown dashboard and goal seat selection.
- Use archived Phase 2 data to review the dashboard layout. Keep the existing archived summaries as the original run evidence.

## Action items

- [x] Make the alternate deck the default goal for the two Phase 2 lineups and allow an explicit goal-seat override from the CLI and Actions.
- [x] Put the goal deck, win rate, outcomes by game, opponent results, and batch health at the top of the Markdown. Retain settings, deck hashes, individual game details, and log links.
- [x] Test goal selection, missing decks, zero completions, wins, losses, draws, timeouts, and failures. Verify shell syntax, workflow lint, and the full test suite.
- [ ] Review the rendered output on historical Phase 2 results and run a hosted smoke check of selection, reporting, and archiving.
- [ ] Document the dashboard and goal selection, then update PR #6 and verify CI and review status.

## Open questions

None.
