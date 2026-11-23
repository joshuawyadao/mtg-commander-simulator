# Plan

Validate the Commander batch workflow with graveyard recursion and spellslinger lineups while keeping the original lineup available by default.

## Scope

- Use original Forge-native deck fixtures and put each new deck in seat three against the same three Stage A opponents.
- Keep the manual public GitHub Actions workflow and ten-game cap. Rehearse on an isolated branch, then retain the verified Git archives in the pull request.

## Action items

- [ ] Add single-commander Meren and Talrand decks with 99 main-deck cards each. Validate them in the pinned Forge release.
- [ ] Add three named lineup presets to the batch runner and wire a selector into GitHub Actions. Record the selected lineup and deck archetypes in the reports.
- [ ] Test selection, fixed seats, input rejection, and backward compatibility with explicit deck paths. Run unittest discovery, shell checks, and workflow lint.
- [ ] Run both alternate lineups on hosted Ubuntu. Verify ten attempts per lineup, check that the intended mechanics resolve in the raw logs, and compare each archived Markdown report with its artifact.
- [ ] Update the README and roadmap status, record the hosted evidence, and retain both archived summaries in Git.
- [ ] Publish the feature branch and open the pull request for CI and review.

## Open questions

None.
