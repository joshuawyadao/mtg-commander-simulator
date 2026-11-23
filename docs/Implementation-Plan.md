# Plan

Preserve Stage C report archiving on protected main by preparing each report on its own branch for a checked pull request.

## Scope

- In: the isolated archive job, report publisher, real-Git tests, and Stage C guides. Keep reports in the existing archive path after merge.
- Out: simulation execution, dispatch inputs, new credentials, Actions-wide PR creation/approval settings, and automatic report merges.

## Action items

- [x] Inspect verified Stage C behavior, actual GitHub repository settings, and the required-check conflict with its direct main push.
- [ ] Prepare the report on a unique run/attempt branch. Validate reused branches and never force-push or write directly to main.
- [ ] Publish a link in the job summary so the owner can open a normal pull request with CI Verify.
- [ ] Update the README, archive guide, specification, and rehearsal notes to distinguish the new path from previous direct-push evidence.
- [ ] Exercise real disposable Git remotes for branch isolation, identical retries, conflicts, and concurrent publication. Run the full suite and static workflow validation without running Forge.
- [ ] Open the stacked PR, run hosted verification and both reviews, and document the integration order with the CI and Stage C PRs.

## Open questions

None.
