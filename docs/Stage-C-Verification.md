# Stage C hosted verification

GitHub registers a new manual workflow when it reaches the default branch. To test before merge, the rehearsal used the existing manual workflow's path on a temporary branch and directed archive commits to that branch. The failure case supplied the ramp deck twice to exercise Forge validation. The production workflow accepts dispatches from the default branch.

| Case | Observed result |
| --- | --- |
| Ten requested games | All ten completed with verified winners on Ubuntu 24.04, Forge 2.0.16, and Temurin 17.0.21+9. The CSV and JSON agreed with the raw logs, and the archived Markdown matched the artifact byte-for-byte. [Ten-game run](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45243352500) · [Reports and logs](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45243352500/artifacts/14852264459) |
| Eleven requested games | GitHub rejected the input before Java or Forge setup, uploaded the validation diagnostics, and skipped the archive job. [Rejected dispatch](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45243356329) |
| One game and a full rerun | Both attempts completed. The Git archive contained `attempt-1/summary.md` and `attempt-2/summary.md` under the same run ID. Retrying the archive job kept both paths and reused the producing attempt. [Rerun rehearsal](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45243356463) |
| Duplicate deck | The simulation failed validation and uploaded the raw diagnostic. The archive job saved a byte-for-byte copy of the Markdown summary with the duplicate deck name. [Failure rehearsal](https://github.com/joshuawyadao/mtg-commander-simulator/actions/runs/45243896832) |

GitHub removed the first downloadable artifact when the workflow was fully rerun. Both Markdown summaries remained in the archive. Download earlier CSV, JSON, and logs before rerunning if you want to retain them.

The first dispatch from `main` after merge will verify that GitHub registered the new workflow and that the archive job publishes to the default branch.
