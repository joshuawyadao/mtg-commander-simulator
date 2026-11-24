# Plan

Compare two Meren deck versions using the same pod and seed schedule, then archive a dashboard backed by both hosted runs.

## Scope

- In: The existing Meren deck as A, a version B that replaces Rise from the Grave with one Swamp, a Markdown A/B dashboard, and hosted comparison and archiving.
- Out: Additional deck changes, larger batches, and edits to past archives.

## Action items

- [x] Add B as a selectable preset and verify the exact one-card difference.
- [ ] Build a comparator for two batch JSON reports and reject incompatible settings, opponents, and seed schedules.
- [ ] Render paired outcomes and telemetry with sample counts and no-data states. Test compatibility checks, incomplete pairs, and the dashboard.
- [ ] Add a manual comparison workflow that reads existing artifacts and uses the checked report-branch archive process.
- [ ] Document the comparison inputs, metric denominators, and archive path.
- [ ] Verify one hosted game per version, then two ten-game batches and a byte-identical hosted comparison archive.
- [ ] Open the feature PR with the verified comparison and complete review and CI.

## Open questions

None.
