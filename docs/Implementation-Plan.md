# Plan

Run the existing fast CI Verify job on pull requests and main pushes while keeping Forge gameplay manually dispatched.

## Scope

- In: the Stage A workflow triggers, README guidance, existing fast tests, and current-head pull request verification.
- Out: simulation logic, dependencies, and the separate Stage C branch. The live branch-rule change must preserve Stage C report publication.

## Action items

- [x] Compare main with the Stage C branch, confirm the missing main-push trigger and confirm GitHub has no required check on main.
- [x] Trigger verification on main pushes and unfiltered pull requests targeting main. Keep Forge setup and gameplay behind manual dispatch.
- [x] Update the README to describe automatic fast checks and the manual gameplay boundary.
- [x] Check workflow syntax and event routing. Run shell syntax and existing unittest discovery. The trigger-only change needs no additional simulation test.
- [ ] Open the PR, confirm the hosted fast job ran and the gameplay job was skipped, and complete both review passes.
- [ ] Coordinate live enforcement with Stage C. Its report publisher pushes directly to main, so enabling a required check before that publisher has a compatible route would break report archiving.

## Open questions

None for the workflow change.
