"""Prepare one workflow attempt's Markdown report for a checked pull request."""

import argparse
from pathlib import Path
import re
import subprocess
import sys


BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


class ArchiveError(Exception):
    """An archive could not be published safely."""


def git(*arguments, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *arguments], cwd=cwd, text=True, capture_output=True, check=False,
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise ArchiveError(f"git {' '.join(arguments)} failed: {detail}")
    return result


def positive_id(value: str, label: str) -> str:
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise ArchiveError(f"{label} must be a positive decimal integer")
    return value


def validate_branch(branch: str, cwd: Path) -> None:
    if git("check-ref-format", f"refs/heads/{branch}", cwd=cwd, check=False).returncode:
        raise ArchiveError("branch must be a valid Git branch name")


def clean_checkout(cwd: Path) -> None:
    top = git("rev-parse", "--show-toplevel", cwd=cwd).stdout.strip()
    if Path(top).resolve() != cwd.resolve():
        raise ArchiveError("run from the root of the isolated archive checkout")
    if git("status", "--porcelain", "--untracked-files=all", cwd=cwd).stdout:
        raise ArchiveError("archive checkout must have a clean worktree")


def destination_status(cwd: Path, relative: Path, report: bytes) -> str:
    current = cwd
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ArchiveError(f"archive path contains a symlink: {current}")
    destination = cwd / relative
    if destination.exists():
        if not destination.is_file():
            raise ArchiveError(f"archive path is not a regular file: {relative}")
        if destination.read_bytes() == report:
            return "identical"
        raise ArchiveError(f"archive already exists with different contents: {relative}")
    return "new"


def fetch_head(cwd: Path, ref: str) -> str:
    git("fetch", "--no-tags", "origin", ref, cwd=cwd)
    return git("rev-parse", "FETCH_HEAD", cwd=cwd).stdout.strip()


def reuse_report_branch(cwd: Path, ref: str, base_ref: str, relative: Path, report: bytes) -> bool:
    if not git("ls-remote", "origin", ref, cwd=cwd).stdout.strip():
        return False

    head = fetch_head(cwd, ref)
    base = fetch_head(cwd, base_ref)
    changes = git("diff", "--no-renames", "--name-status", f"{base}...{head}", cwd=cwd)
    if changes.stdout.splitlines() != [f"A\t{relative.as_posix()}"]:
        raise ArchiveError(f"existing report branch must add only {relative}")
    git("checkout", "--detach", head, cwd=cwd)
    return destination_status(cwd, relative, report) == "identical"


def archive(base_branch: str, run_id: str, attempt: str, summary: Path, cwd: Path) -> str | None:
    run_id = positive_id(run_id, "run ID")
    attempt = positive_id(attempt, "attempt")
    validate_branch(base_branch, cwd)
    if not summary.is_absolute():
        raise ArchiveError("summary must be an absolute file path")
    if summary.is_symlink() or not summary.is_file():
        raise ArchiveError(f"summary is missing or is not a regular file: {summary}")
    report = summary.read_bytes()  # Keep the exact artifact bytes before any checkout change.
    if not report:
        raise ArchiveError(f"summary is empty: {summary}")

    clean_checkout(cwd)
    relative = Path("reports") / "runs" / run_id / f"attempt-{attempt}" / "summary.md"
    report_branch = f"archive/commander-{run_id}-attempt-{attempt}"
    if base_branch == report_branch:
        raise ArchiveError("report branch must be distinct from the base branch")
    base_ref = f"refs/heads/{base_branch}"
    ref = f"refs/heads/{report_branch}"

    base = fetch_head(cwd, base_ref)
    git("checkout", "--detach", base, cwd=cwd)
    if destination_status(cwd, relative, report) == "identical":
        return None
    if reuse_report_branch(cwd, ref, base_ref, relative, report):
        return report_branch

    destination = cwd / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(report)
    git("add", "--", relative.as_posix(), cwd=cwd)
    staged = git("diff", "--cached", "--name-only", cwd=cwd).stdout.splitlines()
    if staged != [relative.as_posix()]:
        raise ArchiveError(f"unexpected staged paths: {staged}")
    git(
        "-c", f"user.name={BOT_NAME}", "-c", f"user.email={BOT_EMAIL}",
        "commit", "-m", f"Archive run {run_id} attempt {attempt} report", "--", relative.as_posix(),
        cwd=cwd,
    )

    pushed = git("push", "origin", f"HEAD:{ref}", cwd=cwd, check=False)
    if pushed.returncode == 0 or reuse_report_branch(cwd, ref, base_ref, relative, report):
        return report_branch
    detail = pushed.stderr.strip() or pushed.stdout.strip()
    raise ArchiveError(f"could not publish {relative}: {detail}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report_branch = archive(args.base_branch, args.run_id, args.attempt, args.summary, Path.cwd())
        if report_branch is None:
            print("Summary already archived on the base branch.", file=sys.stderr)
        else:
            print(report_branch)
    except (ArchiveError, OSError) as error:
        print(f"archive failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
