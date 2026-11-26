# homelab

A single-node homelab rebuilt as a learning project: Proxmox, Terraform,
k3s, Flux (GitOps), Prometheus/Loki/Tempo/OpenTelemetry, and a Python agent
harness that triages alerts with the Claude API.

- [Plan](docs/PLAN.md): goals, architecture, phases, costs
- [Decisions](docs/adr/): architecture decision records
- [Learning index](LEARNING.md): what's hand-written and what it teaches

## Layout

| Path | What |
|---|---|
| `harness/` | Python agent harness |
| `scripts/` | Repo tooling (pre-commit hooks) |
| `docs/` | Plan, ADRs, runbooks |

## Setup

```bash
uv tool install pre-commit
pre-commit install
```

Values that are private but not secret (real IPs, hostnames) are never
committed. Add regexes for them to `~/.config/homelab/private-patterns.txt`
and the `check-private` hook blocks any commit that contains them.
