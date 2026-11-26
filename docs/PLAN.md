# homelab-v2 plan

Status: draft for review, 2026-11-25.

## Goals

1. Rebuild the M70q homeserver with job-relevant tooling: Kubernetes,
   Terraform, GitOps, CI/CD, and a modern observability stack.
2. Keep everything in a public GitHub repo (`rumbogs/homelab`) with no
   PII, secrets, or private topology.
3. Serve a public, anonymised dashboard from the server, focused on how the
   AI agent behaves (tokens, cost, latency, tool calls, SLOs, evals).
4. Replace Hermes (CT 107) with a lean Python agent harness that monitors the
   services. It doubles as the CCDV-P practice project and replaces the
   separate "Aphelion" app from the study plan.
5. Learn by doing: Python wherever possible, important concepts implemented
   by hand, and everything documented as blog material.
6. Keep running costs low. The Claude API is the only real spend.

## Ground rules

### Markers in the code

| Marker | Meaning |
|---|---|
| `TODO(you) [TAG]` | You write this. The comment explains the concept, links the doc, and says how to check it works (usually a failing test). |
| `LEARN [TAG]` | Boilerplate I wrote, but you should understand it well enough to explain it in an interview. |

Tags: `[K8S]` `[TF]` `[GITOPS]` `[CI]` `[OBS]` `[SEC]` `[DB]` `[PY]`, and
`[CCDV-P x.y]` for exam skills. `LEARNING.md` in the repo root indexes every
marker with its file and line, so you can see what's open per topic.

Triage rule: a concept becomes `TODO(you)` only if it's something you'd be
asked to reason about in an interview or on the exam. YAML wiring, Helm
values, Dockerfiles, dashboard JSON and test fixtures are mine.

### Public repo hygiene

- **Secrets** are encrypted in git with SOPS + age. The age private key never
  leaves your Mac and the cluster.
- **Private but not secret values** (LAN CIDR, IPs, hostnames, disk serials,
  the tunnel hostname) live in one SOPS-encrypted file. Flux substitutes them
  into manifests at deploy time (`${LAN_CIDR}`), and Terraform reads them from
  a gitignored `*.auto.tfvars`. The repo itself only has placeholders.
- **Scanning:** gitleaks runs as a pre-commit hook and in CI.
- **Terraform state** is never in git, because it holds plaintext secrets and
  resource IDs. It lives in an S3 bucket (see ADR list).
- **Never in the repo:** the CCDV-P course corpus (marked "do not republish"),
  the employer's name, the DuckDNS domain, and anything from the private
  journal.

### Documentation

| What | Where | Why |
|---|---|---|
| ADRs (decisions + trade-offs), runbooks, `LEARNING.md`, this plan | repo `docs/` | Public, shows engineering judgment to recruiters |
| Session journal, blog drafts, raw notes, screenshots | private journal folder outside the repo (iCloud-synced) | Private, may hold unredacted details |
| Blog seed list | `homelab-v2-journal/blog-seeds.md` | One line per idea, linked to the journal entry |

Journal entries are one file per session, `YYYY-MM-DD-topic.md`, using the
same template: goal, what we did, what broke and why, what you learned,
blog angle. I write the draft at the end of each session and you edit it.

A database for docs would be artificial; markdown is the right tool. Database
learning comes from Postgres where it's genuinely needed (the harness, see
phase 4).

## Architecture (target state)

```
Proxmox host (M70q, 32GB)
├── VM k3s-01 (Debian, Terraform-provisioned, cloud-init)
│   ├── Flux (GitOps)          ← pulls from github.com/rumbogs/homelab
│   ├── MetalLB (L2, .200–.210)  Traefik (Gateway API)  cert-manager
│   ├── Platform: kube-prometheus-stack, Loki, Tempo, OTel Collector,
│   │             CloudNativePG, ntfy
│   ├── Apps: Blocky, Homepage, Uptime Kuma, Navidrome
│   │         (later Immich, Nextcloud, Jellyfin with iGPU)
│   ├── harness (Python)  + mcp-homelab (Python)  + Postgres
│   └── dashboard (Python, public via Tailscale Funnel)
├── host dirs → VM via virtiofs: hdd-data, usb-hdd, usb-music
└── legacy LXCs, retired one by one as services move
```

Exposure: LAN and WireGuard as today for `*.lan`. Only the dashboard is
public, through a Tailscale Funnel (no open router ports, no domain needed).

## Decisions (ADRs)

Each becomes `docs/adr/NNNN-title.md`. Short reasons here.

### ADR-0001: Kubernetes on a single node

You're right that horizontal scaling isn't a reason here: one replica of
each, one machine. The case for it is everything else:

- **Desired state + reconciliation.** You declare what should run and a
  controller converges to it: restarts on crash, liveness/readiness probes,
  rollout and rollback. Today each LXC is a hand-maintained snowflake.
- **One API for everything.** Deploy, config, secrets, networking, storage
  and permissions all work the same way for every service, instead of ten
  different docker-compose files and LXC configs.
- **GitOps.** The git repo *is* the server. Rebuilding after a disk failure
  becomes "install k3s, point Flux at the repo, restore data".
- **Identity and least privilege.** The harness gets a ServiceAccount with a
  read-only Role. That's CCDV-P skill 7.3 done properly, not simulated.
- **It removes your Docker-in-LXC workarounds** (AppArmor unconfined, bridge
  NAT broken by `apt upgrade`, nesting), because containers run in a normal VM.
- **It's what job postings ask for**, and `kubectl` skills transfer directly
  to EKS/GKE/AKS.

Honest costs, which go into the ADR too: ~1–1.5GB RAM of control-plane
overhead, a lot more moving parts, and no HA (if the node dies, everything
dies, same as today). The ADR states it's chosen for operability and
learning, not scale.

Distribution: **k3s** (lightweight, single binary, most common in homelabs,
CNCF-conformant). Talos Linux is the main alternative (immutable, API-only)
and is noted as a possible later experiment. A second worker VM can be added
later to learn scheduling, taints and drains.

### Other ADRs

| # | Decision | Reason |
|---|---|---|
| 0002 | Terraform with the `bpg/proxmox` provider, state in S3 with native locking (`use_lockfile`), versioning + encryption on | State has secrets so it can't go in git; S3 costs cents and is AWS practice. A tiny `terraform/bootstrap` stack creates the bucket. |
| 0003 | Flux for GitOps | Pull-based: GitHub never holds credentials into your network. Lighter than Argo CD on one node; native SOPS support. |
| 0004 | SOPS + age for secrets | Encrypted in the repo, decrypted only in the cluster. No external vault to run. |
| 0005 | Traefik with Gateway API, cert-manager with a CA issuer | Gateway API is the successor to Ingress (ingress-nginx is retired). Importing Caddy's existing root CA into cert-manager means your devices don't need re-trusting. |
| 0006 | MetalLB in L2 mode on the reserved `.200–.210` range | Gives Blocky a real LAN IP on port 53. Teaches how LoadBalancer services work outside the cloud. |
| 0007 | virtiofs to pass host disks into the VM | Replaces LXC bind mounts. Data stays on the host disks, so a VM rebuild never touches it. |
| 0008 | Tailscale Funnel for the public dashboard | Free, no domain, no open ports, still served from the server. Quick Cloudflare tunnels change URL on every restart; named ones need a domain. |
| 0009 | Custom Messages API harness, not Managed Agents | You're learning to build the loop; it runs where the data is. A Managed Agents comparison run later is a good 1.3 "architecture bake-off" exercise. |
| 0010 | CloudNativePG for Postgres | The operator pattern is a core K8s concept; built-in backups to S3-compatible storage. |
| 0011 | Python tooling: uv, ruff, pytest, pyright | Fast, modern, terminal-friendly. |

## Phases

Each phase ends with an exit check and a journal entry. Phases 3–4 run
alongside cert study weeks 1–3 (Domain 2 and 3 material is the same).

### Phase 0: Safety net (blocks phase 2, not phase 1)

- ✅ vzdump images of every LXC, and a copy of personal files.
- ❌ Bind-mounted data is **not** backed up (vzdump logs confirm
  "excluding bind mount point", 2026-11-25). Copy to the cold backup
  drive and verify with `diff -r`:
  - `hdd-data/photos` (Immich iOS uploads, likely the only copy)
  - `hdd-data/photo-archive` (unless already on the cold drive)
  - `hdd-data/nextcloud`
- ⏳ Identify the CT with a bind mount at `/data` (seen in the vzdump log).
- ⏳ Fix the doc drift: the fstab still mounts part 2 as `usb-personal` ro,
  WireGuard `/32` should be `/24`, CPU is likely an i5-10500.
- Exit: every folder on hdd-data has a verified second copy.

### Data safety rules (apply to every phase)

1. Copy, never move. Old data stays in place until the new service has
   run correctly for a while and a backup of the new location exists.
2. New mounts start read-only. Write access is granted per service only
   when it needs it.
3. Kubernetes never owns the data: host folders via virtiofs, PVs with
   `persistentVolumeReclaimPolicy: Retain`, so deleting a PVC or a whole
   app from git can't delete files.
4. Terraform resources holding data get `lifecycle { prevent_destroy =
   true }`, and every `plan` is read for `destroy` before `apply`.
5. Deleting anything is its own explicit step in a runbook, done by you,
   never as a side effect of a migration or an automated job.
6. The harness has no delete or write tools on storage. Ever.

### Phase 1: Repo and tooling

- Repo skeleton, pre-commit (gitleaks, ruff, terraform fmt, yamllint),
  `LEARNING.md`, ADR template, journal template.
- CI: lint + tests on every PR.
- `TODO(you) [CI]`: write the first workflow job yourself (lint + test).
- Exit: a PR that leaks a fake secret gets blocked.

### Phase 2: Terraform + k3s + Flux

- `terraform/bootstrap`: the S3 state bucket.
- `terraform/proxmox`: the k3s VM with cloud-init, virtiofs mappings,
  and `import` blocks for 2–3 existing LXCs (to learn state and drift).
- Ansible playbook (Python-based) for host config: fstab, the fstrim cron,
  and the k3s install on the VM.
- Flux bootstrap, SOPS, MetalLB, Traefik, cert-manager.
- `TODO(you) [TF]`: the VM resource, variables/outputs design, the
  `import` blocks, reading a `plan` diff to fix drift.
- `TODO(you) [K8S]`: hand-write the Navidrome Deployment, Service, PVC,
  probes, and resource requests/limits (no Helm). It's the first app.
- CI: `terraform validate` + `plan` + tflint + trivy on PRs; kubeconform
  on manifests.
- Exit: `git push` deploys Navidrome; `kubectl delete pod` heals itself.

### Phase 3: Observability

- kube-prometheus-stack, Loki, Tempo, OTel Collector, pve-exporter,
  Grafana provisioned from git, Alertmanager → ntfy.
- Migrate Blocky, Homepage, Uptime Kuma.
- `TODO(you) [OBS] [CCDV-P 3.2]`: define SLIs for DNS and HTTPS services,
  write multiwindow burn-rate alerts (14.4×/1h, 6×/6h, 1×/3d), and the disk
  alert for hdd-data at 93%.
- Exit: you get a phone notification for a real (induced) outage, and
  monitoring CT 109 + Uptime Kuma CT 101 are retired.

### Phase 4: Harness v1 (monitoring agent)

Python package `harness/`, raw Messages API, deployed as a Deployment with
its own ServiceAccount.

- **Triggers:** Alertmanager webhook (event-driven, the fix for Hermes'
  token waste) and a daily digest CronJob using the Batch API (50% off).
- **Tools (read-only):** PromQL query, Loki query, Kubernetes get/describe/
  logs, service health. Write actions (restart a deployment) come later,
  behind a deny-by-default gate.
- **Storage:** Postgres (CloudNativePG) for runs, checkpoints, cost ledger.
- **Telemetry:** OTel GenAI spans to Tempo, metrics to Prometheus.

What you write:

| TODO(you) | Concept | Tag |
|---|---|---|
| The agent loop: send, branch on `stop_reason`, run tools, return all `tool_result`s in one message | How every agent works | `[CCDV-P 1.1/4.1]` |
| Error classifier: 429 with/without `retry-after`, 5xx, refusal (HTTP 200), `max_tokens`; retry budget at one layer | Reliability | `[CCDV-P 2.1]` |
| Circuit breaker around the API client | Reliability | `[CCDV-P 2.1]` |
| Per-run and per-day budget enforcement | Cost | `[CCDV-P 2.2/6.1]` |
| Prompt caching layout and verifying `cache_read_input_tokens` | Cost | `[CCDV-P 6.1]` |
| Span attributes and summing tokens from one source | Telemetry | `[CCDV-P 3.1]` |
| Postgres schema + migrations (Alembic) for runs and the cost ledger; a query for cost per completed task | Databases | `[DB] [CCDV-P 6.1]` |
| Checkpoint and resume of a run | Durable execution | `[CCDV-P 1.2]` |
| RBAC Role for the harness ServiceAccount | Least privilege | `[K8S] [CCDV-P 7.3]` |

Exit: an induced outage produces a correct, cheap diagnosis in ntfy, and
the cost per run shows up in Grafana. Hermes keeps running in parallel.

### Phase 5: Public dashboard

- Small Python app (FastAPI + server-rendered HTML or a static page with a
  JSON endpoint) behind Tailscale Funnel.
- Reads from Prometheus and Postgres through an **allowlist** of metrics
  and labels. Shows agent runs, tokens, cost per task, latency (TTFT vs
  total), tool success rate, SLO status, uptime, eval scores.
- `TODO(you) [SEC] [CCDV-P 7.2]`: the allowlist sanitiser and its tests.
  The rule to internalise: deny by default, never strip by denylist.
- `TODO(you) [SEC]`: a short threat model in the ADR (what could leak,
  what an attacker can reach through the Funnel).
- Exit: a test proves an unknown label never reaches the page.

### Phase 6: Harness v2 (exam depth)

- `mcp-homelab/`: Python MCP server exposing the same tools. The harness
  uses it, and so can Claude Code on your Mac. `[CCDV-P 2.3]`
- Evals: golden set built from real incidents in phase 4, code graders
  first, an LLM judge only where needed. Gate in CI on changes to prompts
  or tools. `TODO(you) [CCDV-P 5.1/5.2]`: judge calibration against your
  own labels.
- Guardrails: deny rules for irreversible actions, prompt-injection
  handling for log content (logs are untrusted input). `[CCDV-P 7.1/7.2]`
- Model routing experiment: same eval suite across Haiku 5.5, Sonnet 5.5
  and Opus 5.5 at different effort levels; pick on cost per completed task.
  `[CCDV-P 1.3/6.1]`
- Exit: Hermes' monitoring jobs are covered; decide which of its other
  jobs (CalDAV, files, memory, quizzes) to port.

### Phase 7: Heavy stateful services

- Immich and Nextcloud into the cluster (Postgres via CloudNativePG, data
  via virtiofs; the UID-mapping lessons become `securityContext`).
- Jellyfin with the iGPU: GVT-g or full iGPU passthrough to the VM, then
  the Intel GPU device plugin. Hardest part of the project.
- Retire Caddy CT 105 and the remaining LXCs.
- Exit: Proxmox runs only the k3s VM (plus the Hermes LXC until phase 6
  says otherwise).

### Phase 8: Backups and disaster recovery

- restic (or Kopia) for host data to the USB disk and offsite (Backblaze
  B2), CloudNativePG backups, k3s etcd snapshots.
- `TODO(you) [SEC] [OBS]`: run a full restore drill on a fresh VM and
  write the runbook. A backup that was never restored is not a backup.

## Costs

| Item | Monthly |
|---|---|
| GitHub repo, Actions, GHCR (public repo) | €0 |
| Tailscale Funnel (Personal plan) | €0 |
| Terraform state in S3 | < €0.05 |
| Offsite backups, B2, ~300GB of personal data and photos | ~€2 (verify current price) |
| Claude API (estimate below) | ~€3–8 |
| **Total** | **~€5–10** |

Claude API estimate, using current list prices (Haiku 5.5 $0.10/$0.50,
Sonnet 5.5 $2/$10, Opus 5.5 $4/$20 per million tokens in/out):

- Alert triage on Haiku 5.5, ~15k in / 1k out per run ≈ $0.002;
  30 runs/day ≈ $2/month.
- Daily digest on Sonnet 5.5 through the Batch API ≈ $2/month.
- Evals only on PRs that change prompts or tools, plus a weekly batch run.

Controls: a monthly spend limit in the Console, the harness' own daily
budget (it stops and notifies, it doesn't keep retrying), caching, and
event-driven triggers instead of polling. Model choices are yours; the
phase 6 experiment gives you numbers to decide with.

## Interview story this produces

"I run a single-node k3s cluster managed with Terraform and Flux, with SLO
burn-rate alerting, and a Python agent that triages alerts with full cost
and trace telemetry, evaluated in CI." Each phase's journal is one blog post.
