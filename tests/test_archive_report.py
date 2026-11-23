"""Real-Git integration tests for publishing workflow reports."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "archive_report.py"


def command(*args, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if check and result.returncode:
        raise AssertionError(f"{args}: {result.stdout}\n{result.stderr}")
    return result


def git(cwd: Path, *args: str) -> str:
    return command("git", *args, cwd=cwd).stdout.strip()


class ArchiveReportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.remote = self.root / "remote.git"
        self.seed = self.root / "seed"
        self.seed.mkdir()
        git(self.remote.parent, "init", "--bare", str(self.remote))
        git(self.seed, "init", "-b", "main")
        git(self.seed, "config", "user.name", "Test Author")
        git(self.seed, "config", "user.email", "test@example.com")
        (self.seed / "README.md").write_text("initial\n")
        git(self.seed, "add", "README.md")
        git(self.seed, "commit", "-m", "Initial commit")
        git(self.seed, "remote", "add", "origin", str(self.remote))
        git(self.seed, "push", "-u", "origin", "main")
        git(self.remote, "symbolic-ref", "HEAD", "refs/heads/main")
        self.archive = self.clone("archive")
        self.summary = self.root / "summary.md"
        self.summary.write_bytes(b"# A report\n")

    def clone(self, name: str) -> Path:
        destination = self.root / name
        git(self.root, "clone", str(self.remote), str(destination))
        return destination

    def run_archive(self, *, checkout: Path | None = None, run_id: str = "123", attempt: str = "1",
                    summary: Path | None = None, branch: str = "main") -> subprocess.CompletedProcess[str]:
        return command(
            sys.executable, "-B", str(SCRIPT), "--branch", branch, "--run-id", run_id,
            "--attempt", attempt, "--summary", str(summary or self.summary),
            cwd=checkout or self.archive, check=False,
        )

    def remote_file(self, relative: str) -> bytes:
        return subprocess.run(
            ["git", "show", f"main:{relative}"], cwd=self.seed, capture_output=True, check=True,
        ).stdout

    def refresh_seed(self):
        git(self.seed, "fetch", "origin", "main")
        git(self.seed, "reset", "--hard", "FETCH_HEAD")

    def test_independent_attempts_preserve_prior_reports_and_unrelated_commits(self):
        first = self.run_archive()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.summary.write_bytes(b"# Second attempt\n")
        second = self.run_archive(attempt="2")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.refresh_seed()
        self.assertEqual(self.remote_file("reports/runs/123/attempt-1/summary.md"), b"# A report\n")
        self.assertEqual(self.remote_file("reports/runs/123/attempt-2/summary.md"), b"# Second attempt\n")
        self.assertEqual((self.seed / "README.md").read_text(), "initial\n")
        self.assertEqual(git(self.seed, "log", "-1", "--format=%an <%ae>"),
                         "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")

    def test_identical_rerun_is_noop_and_different_bytes_fail(self):
        self.assertEqual(self.run_archive().returncode, 0)
        before = git(self.seed, "ls-remote", "origin", "refs/heads/main").split()[0]
        same = self.run_archive()
        self.assertEqual(same.returncode, 0, same.stderr)
        self.assertIn("already archived", same.stdout)
        self.assertEqual(git(self.seed, "ls-remote", "origin", "refs/heads/main").split()[0], before)
        self.summary.write_bytes(b"different\n")
        conflict = self.run_archive()
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("different contents", conflict.stderr)
        self.assertEqual(git(self.seed, "ls-remote", "origin", "refs/heads/main").split()[0], before)

    def test_missing_empty_and_invalid_inputs_fail(self):
        self.assertIn("missing", self.run_archive(summary=self.root / "missing.md").stderr)
        self.summary.write_bytes(b"")
        self.assertIn("empty", self.run_archive().stderr)
        self.summary.write_bytes(b"ready\n")
        for options in ({"run_id": "0"}, {"attempt": "../2"}, {"branch": "bad..name"}):
            with self.subTest(options=options):
                self.assertNotEqual(self.run_archive(**options).returncode, 0)
        self.assertEqual(git(self.archive, "status", "--porcelain"), "")

    def test_dirty_checkout_and_symlink_path_fail_without_writing_outside(self):
        (self.archive / "dirty.txt").write_text("dirty")
        self.assertIn("clean worktree", self.run_archive().stderr)
        (self.archive / "dirty.txt").unlink()
        outside = self.root / "outside"
        outside.mkdir()
        (self.seed / "reports").symlink_to(outside, target_is_directory=True)
        git(self.seed, "add", "reports")
        git(self.seed, "commit", "-m", "Add a symlink")
        git(self.seed, "push", "origin", "main")
        result = self.run_archive()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_retries_when_an_unrelated_commit_wins_the_first_push(self):
        competitor = self.clone("competitor")
        git(competitor, "config", "user.name", "Other Author")
        git(competitor, "config", "user.email", "other@example.com")
        hook = self.archive / ".git" / "hooks" / "pre-push"
        hook.write_text(
            "#!/bin/sh\n"
            "rm -- \"$0\"\n"
            f"printf 'concurrent\\n' > '{competitor}/OTHER.md'\n"
            f"git -C '{competitor}' add OTHER.md\n"
            f"git -C '{competitor}' commit -m 'Concurrent unrelated commit' >/dev/null\n"
            f"git -C '{competitor}' push origin main >/dev/null\n",
        )
        hook.chmod(0o755)
        result = self.run_archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.refresh_seed()
        self.assertEqual((self.seed / "OTHER.md").read_text(), "concurrent\n")
        self.assertEqual(self.remote_file("reports/runs/123/attempt-1/summary.md"), b"# A report\n")


if __name__ == "__main__":
    unittest.main()
