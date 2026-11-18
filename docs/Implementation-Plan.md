# Plan

Define a durable Markdown results archive and give it a visible location in the repository before simulation work begins.

## Scope

- **In scope** · The archive path, project reporting requirements, an archive guide, and a link from the README.
- **Later stages** · Generating reports, publishing them from GitHub Actions, and executing simulations.

## Action items

- [ ] Confirm how the current specification handles reports, artifacts, and the proof of concept's completion criteria.
- [ ] Define how the Markdown report is named and retained across workflow runs and reruns in `PROJECT_SPEC.md`.
- [ ] Add an archive guide under `reports/runs/` and link it from the repository README.
- [ ] Check that the specification, archive guide, and README agree, that their local links resolve, and that the diff contains documentation only. This change adds no executable behavior and needs no automated test files.
- Publish `main` and confirm the remote commit matches the local commit.

## Open questions

None.
