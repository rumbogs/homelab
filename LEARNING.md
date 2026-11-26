# Learning index

`TODO(you)` = write it yourself. `LEARN` = generated, but know it well enough
to explain in an interview. Find them all with:

```bash
grep -rn --exclude-dir=.venv -E "TODO\(you\)|LEARN \[" .
```

## Open TODO(you)

| Tag | Where | What |
|---|---|---|
| CI SEC | `.github/rulesets/main.jq` | Ruleset for main: 6 blanks (phase 03) |
| ARCH | `docs/adr/0001-kubernetes-on-a-single-node.md` | Argue for (and against) Kubernetes in your own words |

## LEARN

| Tag | Where | What |
|---|---|---|
| SEC | `.github/workflows/ci.yml` | Least-privilege `permissions`, SHA-pinned actions |
| CI | `.github/workflows/ci.yml` | Parallel jobs, per-step working-directory |
| SEC | `.github/rulesets/main.jq` | Empty bypass list, required checks |
| SEC | `scripts/check_private.py` | Secret scanning vs a personal denylist |
| CI | `.pre-commit-config.yaml` | Same checks locally and in CI |

## Done

| Tag | What | Journal |
|---|---|---|
| PY SEC | Tests for check_private (phase 01) | 2026-11-26 |
| CI | Harness CI job, `uv sync --locked` (phase 02) | 2026-11-26 |
