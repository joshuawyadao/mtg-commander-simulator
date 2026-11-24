# Simulation run reports

This folder is the long-term archive for Markdown results from Commander simulation batches. Each GitHub Actions attempt has its own path.

```text
reports/runs/<run-id>/attempt-<attempt>/summary.md
```

Open the folder for a workflow run ID, then choose its attempt number. Use **Re-run all jobs** to generate another batch under the same run ID. GitHub increments the attempt number, and the archive keeps the previous report. [GitHub Actions run identifiers](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#github-context)

Each summary records the run settings, per-deck results, and per-game outcomes. For CSV and JSON exports and raw logs, open the Actions run linked in the summary and download its artifact during the configured retention window. GitHub can remove an earlier artifact when you rerun all jobs. Download any files you want to retain before rerunning. Git keeps the Markdown summaries from both attempts. [GitHub Actions artifact retention](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts)

Dashboard reports open with the goal deck when one is selected, followed by batch health and deck standings. Expand **Run settings and deck versions** or **Game results and logs** for the underlying evidence.

Deck version comparisons use the comparison workflow's own run ID and attempt. Their dashboard links to both source simulations and shows matched seed outcomes, paired metrics, and shared settings. [How to compare two deck versions](../../README.md#compare-two-deck-versions)

The archive job publishes each generated summary on a unique `archive/commander-<run-id>-attempt-<attempt>` branch, including summaries from failed batches. Use the run summary's **Open the archive pull request** link to open or find the report PR. Review the exact Markdown change and merge it after **CI Verify** passes. Only merged reports appear in the default branch's archive.

Re-running only the archive job reuses the branch when it contains the same report. If the report is already merged, the job finishes without preparing another PR. If the simulation stops before it generates a summary, check the job logs and any uploaded diagnostics. [Reporting requirements](../../PROJECT_SPEC.md#8-required-reporting)
