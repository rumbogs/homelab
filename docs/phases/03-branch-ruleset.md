# 03: Branch ruleset and a leak test PR

- Plan phase: 1 (repo skeleton)
- Tags: CI, SEC

## Goal

Protect `main` with a ruleset kept in git, so every change goes through
a PR with green checks. Then open a PR that leaks a fake secret and watch
it fail to merge. That is the exit test for plan phase 1.

## Context

- The repo is public on GitHub as `rumbogs/homelab`, remote `origin`.
  Public repos get rulesets on the free plan.
- There are no rulesets yet (`gh api 'repos/{owner}/{repo}/rulesets'`
  returns `[]`).
- PR #1 (`ci-harness-job`) adds the `harness` job and is green, but not
  merged. Merge it first (runbook step 1), so the job is on `main`.
- `.github/workflows/ci.yml` has two jobs, `secrets` (gitleaks) and
  `harness` (lint, types, tests). Their job names are the check names.
- Gitleaks also runs as a pre-commit hook, so a local commit with a
  secret is blocked before it reaches GitHub. CI is the second layer,
  for anyone who skips or never installed the hooks.
- `gh api` fills `{owner}` and `{repo}` from the current repo's remote.
- GitHub secret scanning push protection is on for this repo (GitHub
  enables it by default on public repos). It may refuse the leak push
  itself, before gitleaks in CI ever runs.

## Files

- `.github/rulesets/main.jq`: fill in the 6 `...` blanks. jq builds the
  JSON body for the rulesets API; it's used because JSON can't hold
  comments. Each blank is one value.

## Concepts

- Ruleset vs classic branch protection: rulesets stack, can target
  several branches, and can be read and written as JSON through the API.
- Required status checks: a PR can't merge until the named checks pass.
  `strict` also requires the branch to be up to date with `main`; when
  `main` moves, run `gh pr update-branch` and wait for checks again.
- A required check is matched by exact name. A typo, or a job that never
  runs on the PR, leaves it "Expected" forever and the PR can't merge.
  That's why the jobs must exist on `main` and have reported once.
- Bypass list: who may skip the rules. Empty means nobody, the owner
  included. An admin can still edit or delete the ruleset, but that is a
  deliberate, logged act, not a silent skip.
- Blocking force-pushes and deletion: `main`'s history can only grow.
- Defence in depth: pre-commit blocks the leak locally, CI blocks it at
  the PR, the ruleset makes CI's verdict binding.
- GitHub push protection vs gitleaks: push protection is server-side and
  can't be skipped with `--no-verify`, but only knows provider patterns
  and can be bypassed with a stated reason. Gitleaks runs offline, takes
  custom rules, and scans the whole history in CI.
- Not used here, but worth knowing: `required_signatures` (signed
  commits), CODEOWNERS review (`require_code_owner_review`), and merge
  queues (test the merged result of several PRs before landing).
- A pushed secret is public even if the PR is closed: GitHub keeps PR
  refs. A real leak means rotating the secret, not deleting the commit.

## Runbook

1. Merge PR #1 and update local `main`:
   `gh pr merge 1 --squash --delete-branch && git switch main &&
   git pull`
2. Fill the blanks, then check the JSON builds:
   `jq -n -f .github/rulesets/main.jq`
3. Create the ruleset:
   `jq -n -f .github/rulesets/main.jq |
   gh api -X POST 'repos/{owner}/{repo}/rulesets' --input -`
   Note the `id` in the response. To change it later, use
   `-X PUT 'repos/{owner}/{repo}/rulesets/<id>'` with the same body.
4. Prove a direct push to `main` is refused: commit the ruleset file
   and this brief on `main` and `git push`. Expect
   `GH013: Repository rule violations`. Then move the commit to a branch
   and point local `main` back at `origin/main` (this doesn't touch the
   working tree, so uncommitted files are safe):
   `git switch -c branch-ruleset && git push -u origin branch-ruleset &&
   git branch -f main origin/main`, open a PR (`gh pr create --fill`),
   and merge it once both checks pass.
5. Leak test, on a fresh branch from `main`:
   `git switch main && git pull && git switch -c leak-test`
   `echo "token = ghp_$(openssl rand -hex 18)" > leak.txt`
   `git add leak.txt && git commit -m "Leak test"`: pre-commit's
   gitleaks should block it. Read the output.
   `git commit --no-verify -m "Leak test"` skips the hooks, as a
   contributor without them would. Push and open a PR. If the push is
   refused with "Push cannot contain secrets", that is GitHub push
   protection: a third layer. Note it, then use the bypass link it
   prints ("used in tests") so the PR can reach CI.
6. Watch it: `gh pr checks --watch`. Expect `secrets` to fail. Then try
   `gh pr merge --squash` and expect it to be refused. Also check
   `gh pr view --json mergeStateStatus` (expect `BLOCKED`).
7. Clean up: `gh pr close --delete-branch` deletes the remote and local
   `leak-test` branch and switches you to `main`. The token is random and
   never worked, so nothing needs rotating.

## Check

```sh
gh api 'repos/{owner}/{repo}/rulesets'   # one ruleset, "main", active
gh pr view <leak PR> --json state,mergeStateStatus   # CLOSED, never merged
```

## Questions to answer

- Why can't `enforcement` be `evaluate` here, and when would you use it?
- Why is the required approval count 0, and what would you set on a team?
- What does `strict` cost you, and what does it protect against?
- Why pin a required check with `integration_id`?
- A teammate skips pre-commit and pushes a real token. Walk through which
  layer catches it and what you do next.
- Why is deleting the commit not enough after a secret is pushed?

## Done when

The ruleset is active and in git, a direct push to `main` is refused,
and the leak PR failed `secrets` and could not be merged. The user can
say why the bypass list is empty and why a pushed secret must be rotated.
