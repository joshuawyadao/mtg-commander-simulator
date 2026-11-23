# Plan

Publish the verified Stage B batch runner as a manual GitHub Actions workflow and archive the Markdown report from each attempt.

## Scope

- Stage C covers manual runs of one to ten games, artifact uploads, and a Git-tracked archive in the public repository.
- Rehearse the workflow on a temporary branch. GitHub enables the permanent dispatch after the workflow reaches the default branch.

## Action items

- [ ] Add the manual workflow with pinned Ubuntu tooling, input validation before Forge setup, and timeouts that preserve time to upload evidence.
- [ ] Upload the reports and logs for each attempt, including failed batches. Give a separate archive job permission to publish only the generated Markdown summary.
- [ ] Write reports to the existing run ID and attempt paths. Test idempotency, existing summary protection, missing summaries, and concurrent Git pushes with disposable repositories.
- [ ] Check workflow syntax and run the full unittest suite. Rehearse the ten-game path, reruns, and failure handling on hosted Ubuntu using an isolated archive branch.
- [ ] Document dispatch, reruns and artifact retention in the README and archive guide. Record the hosted evidence in the specification and verification notes.
- [ ] Publish the feature branch and open the pull request for CI and review.

## Open questions

None.
