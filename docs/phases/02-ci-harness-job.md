# 02: CI job for lint, types and tests

- Plan phase: 1 (repo skeleton)
- Tags: CI

## Goal

Add a GitHub Actions job that lints, type-checks and tests the harness
package and the pre-commit hook on every push and pull request. Then see
it go green, and red on purpose.

## Context

- The repo is on GitHub as `rumbogs/homelab`, remote `origin`. There is
  no branch protection yet; that's phase 03.
- Nothing is committed yet. The phase 01 skeleton is staged; the user
  commits and pushes it to `main` first (step 1 of the runbook).
- `.github/workflows/ci.yml` already has a `secrets` job (gitleaks). The
  new `harness` job sits beside it.
- `harness/` is a uv project: `pyproject.toml`, `uv.lock`, and a
  `.python-version` that uv reads to install Python 3.13. Dev tools
  (ruff, pyright, pytest) are in the `dev` dependency group, which
  `uv sync` installs by default.
- `scripts/test_check_private.py` (phase 01) runs with `uvx pytest
  scripts` from the repo root. In CI there is no private patterns file,
  which is fine: the tests make their own in `tmp_path`.
- Actions are pinned to a commit SHA with the version in a comment.
- All harness checks already pass locally, so once the blanks are
  filled, the job should be green on the first push.

## Files

- `.github/workflows/ci.yml`: fill in the 6 `...` blanks in the
  `harness` job. Each one is a single value or command.

## Concepts

- Workflow triggers (`on:`): which events start a run. Here, every PR
  and every push to `main`.
- Jobs run in parallel on fresh VMs. Steps in a job run in order and
  share the VM's filesystem.
- `defaults.run.working-directory` and overriding it per step.
- `uses:` (run an action) vs `run:` (run a shell command).
- Why pin actions to a SHA (a tag can be moved, a SHA can't).
- Why `uv sync --locked`: CI must fail when `uv.lock` is stale, not
  silently test different versions from the ones you ran locally.
- Check vs fix: in CI, formatters and linters only report. Fixing is
  your job, locally.

## Runbook

1. Commit and push the skeleton (if not done yet):
   `git add -A && git commit -m "Repo skeleton" && git push -u origin main`
2. Fill the blanks. Reproduce the job locally before pushing:
   `cd harness && uv sync --locked && uv run ruff check . &&
   uv run ruff format --check . && uv run pyright && uv run pytest &&
   cd .. && uvx pytest scripts`
3. On a branch: `git switch -c ci-harness-job`, commit, push, and open
   a PR: `gh pr create --fill`. Watch it with `gh pr checks --watch`.
4. Prove it can fail: push a commit that breaks one harness test, see
   the job go red, read the log (`gh run view --log-failed`), then
   revert the commit and see it go green again.
5. Merge the PR: `gh pr merge --squash --delete-branch`.

## Check

```sh
gh pr checks          # both `secrets` and `harness` pass
```

## Done when

The `harness` job is green on the PR, the user saw it go red on a broken
test, and can say in one sentence why `--locked` matters.
