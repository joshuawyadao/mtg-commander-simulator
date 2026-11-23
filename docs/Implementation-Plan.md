# Plan

Validate the Commander batch workflow with graveyard recursion and spellslinger lineups while keeping the original lineup available by default.

## Scope

- Use original Forge-native deck fixtures and put each new deck in seat three against the same three Stage A opponents.
- Keep the manual public GitHub Actions workflow and ten-game cap. Rehearse on an isolated branch, then retain the verified Git archives in the pull request.

## Action items

- [x] Add single-commander Meren and Talrand decks with 99 main-deck cards each. Validate them in the pinned Forge release.
- [x] Add three named lineup presets to the batch runner and wire a selector into GitHub Actions. Record the selected lineup and deck archetypes in the reports.
- [x] Test selection, fixed seats, input rejection, and backward compatibility with explicit deck paths. Run unittest discovery, shell checks, and workflow lint.
- [x] Run both alternate lineups on hosted Ubuntu. Verify ten attempts per lineup, check that the intended mechanics resolve in the raw logs, and compare each archived Markdown report with its artifact. [Hosted verification](Phase-2-Verification.md)
- [x] Update the README and roadmap status, record the hosted evidence, and retain both archived summaries in Git.
- [x] Prepare the verified feature branch for publication and pull request review.

## Open questions

None.
