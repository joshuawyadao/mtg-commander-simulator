# Simulation run reports

This folder is the long-term archive for Markdown results from Commander simulation batches. Each GitHub Actions attempt has its own path.

```text
reports/runs/<run-id>/attempt-<attempt>/summary.md
```

Open the folder for a workflow run ID, then choose its attempt number. Use **Re-run all jobs** to generate another batch under the same run ID. GitHub increments the attempt number, and the archive keeps the previous report. [GitHub Actions run identifiers](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#github-context)

Each summary records the run settings, per-deck results, and per-game outcomes. For CSV and JSON exports and raw logs, open the Actions run linked in the summary and download its artifact during the configured retention window. The Markdown summary stays in Git. [GitHub Actions artifact retention](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts)

The archive job publishes each generated summary to the default branch, including summaries from failed batches. If the simulation stops before it generates a summary, check the run's job logs and any uploaded diagnostics. [Reporting requirements](../../PROJECT_SPEC.md#8-required-reporting)
