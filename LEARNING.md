# Learning index

`TODO(you)` = write it yourself. `LEARN` = generated, but know it well enough
to explain in an interview. Find them all with:

```bash
grep -rn --exclude-dir=.venv -E "TODO\(you\)|LEARN \[" .
```

## Open TODO(you)

| Tag | Where | What |
|---|---|---|
| ARCH K8S | `docs/adr/0001-kubernetes-on-a-single-node.md` | Argue for (and against) Kubernetes: 4 blanks (phase 04) |

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
| CI SEC | Ruleset for main, leak PR blocked (phase 03) | 2026-11-26 |
