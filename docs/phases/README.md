# Phases

`docs/PLAN.md` is the why. This file is the order of work, split into
phases small enough for one tutor session (about 30–90 minutes).

## How a phase runs

```
Opus session          Tutor session (haiku/sonnet)         Opus session
/next-phase   ──►     /tutor                       ──►     /next-phase
writes brief NN       guides you through brief NN          reviews handoff NN,
+ code blanks         writes .handoff/NN-name.md           writes brief NN+1
```

- **Brief** (`docs/phases/NN-name.md`, public): self-contained. It holds
  everything the tutor needs, so the tutor never reads the plan or old
  conversations.
- **Handoff** (`.handoff/NN-name.md`, gitignored): what you did, where
  you struggled, and questions for the orchestrator.
- **State** (`.handoff/STATE.md`, gitignored): the only memory carried
  between Opus sessions. It holds the current phase, private facts about
  the server, decisions, and open follow-ups. `/next-phase` updates it
  each time.
- Briefs are written one at a time, just before the phase runs, because
  each one depends on the code the previous phases produced.

Kinds: **code** (fill blanks, tests check them), **ops** (you run
commands from a runbook; the tutor explains, never runs anything on the
server), **write** (prose like ADRs; the tutor critiques, never writes).

Tutor model: haiku for Python exercises and simple steps, sonnet where
debugging infra needs judgment. Start it with `claude --model <model>`.

## The list

Phases 01–04 don't need the server. 05–06 do, and block 07 onwards.

| # | Phase | Plan | Kind | Tutor | Tags | Done when |
|---|---|---|---|---|---|---|
| 01 | Tests for check_private | 1 | code | haiku | PY SEC | 5 tests pass |
| 02 | CI job: lint, types, tests | 1 | code | haiku | CI | job green on a push |
| 03 | Branch ruleset + leak test PR | 1 | ops | haiku | CI SEC | a fake-secret PR can't merge |
| 04 | ADR-0001 in your words | 1 | write | sonnet | ARCH K8S | Decision fits in 30 seconds |
| 05 | Back up bind-mounted data | 0 | ops | sonnet | SEC | `diff -r` clean for every folder |
| 06 | Find the `/data` CT, fix doc drift | 0 | ops | haiku | | every bind mount mapped |
| 07 | S3 state bucket (bootstrap stack) + ADR-0002 | 2 | code | sonnet | TF | `terraform apply` creates it, state locks |
| 08 | Proxmox provider, API token, private tfvars | 2 | code | sonnet | TF SEC | `terraform plan` reads the node |
| 09 | Import two LXCs, read the drift | 2 | code | sonnet | TF | `plan` shows no changes |
| 10 | k3s VM with cloud-init | 2 | code | sonnet | TF | VM boots, SSH works |
| 11 | virtiofs mounts, read-only + ADR-0007 | 2 | code | sonnet | TF SEC | VM sees host dirs, can't write |
| 12 | Ansible: host config (fstab, fstrim) | 2 | code | sonnet | PY | playbook is idempotent |
| 13 | Ansible: install k3s, kubeconfig on Mac | 2 | code | sonnet | K8S | `kubectl get nodes` from the Mac |
| 14 | Flux bootstrap + SOPS/age + ADRs 0003–0004 | 2 | code | sonnet | GITOPS SEC | a push changes the cluster |
| 15 | MetalLB, Traefik Gateway, cert-manager + ADRs 0005–0006 | 2 | code | sonnet | K8S | a test page on HTTPS, trusted cert |
| 16 | Navidrome by hand (no Helm) | 2 | code | sonnet | K8S | `kubectl delete pod` heals |
| 17 | CI for infra: validate, tflint, trivy, kubeconform | 2 | code | haiku | CI | broken manifest fails the PR |
| 18 | kube-prometheus-stack, Grafana from git | 3 | code | sonnet | OBS | dashboards load from the repo |
| 19 | Loki, Tempo, OTel Collector | 3 | code | sonnet | OBS | logs and a trace in Grafana |
| 20 | Alertmanager → ntfy, pve-exporter | 3 | code | sonnet | OBS | a test alert reaches the phone |
| 21 | Migrate Blocky (LoadBalancer on :53) | 3 | code | sonnet | K8S | LAN resolves through the cluster |
| 22 | Migrate Homepage, Uptime Kuma | 3 | code | haiku | K8S | both served from the cluster |
| 23 | SLIs, burn-rate alerts, disk alert | 3 | code | sonnet | OBS CCDV-P 3.2 | alert rules pass `promtool test` |
| 24 | Induced outage, retire CTs 109 + 101 | 3 | ops | sonnet | OBS | phone alert for a real outage |
| 25 | Harness: API client, config, first call | 4 | code | haiku | PY | a test call logs tokens and cost |
| 26 | The agent loop | 4 | code | haiku | CCDV-P 1.1 4.1 | loop tests pass with a fake client |
| 27 | Tools: PromQL, Loki | 4 | code | haiku | PY OBS | tools tested against fixtures |
| 28 | Tools: Kubernetes + RBAC Role | 4 | code | sonnet | K8S CCDV-P 7.3 | `kubectl auth can-i` proves read-only |
| 29 | Error classifier + retry | 4 | code | haiku | CCDV-P 2.1 | each error class has a test |
| 30 | Circuit breaker | 4 | code | haiku | CCDV-P 2.1 | state transitions tested |
| 31 | Run and daily budgets | 4 | code | haiku | CCDV-P 2.2 6.1 | a run stops at its budget |
| 32 | Prompt caching | 4 | code | haiku | CCDV-P 6.1 | second call shows cache reads |
| 33 | Postgres (CloudNativePG) + Alembic + ADR-0010 | 4 | code | sonnet | DB | migrations up and down |
| 34 | Cost ledger, cost-per-task query | 4 | code | haiku | DB CCDV-P 6.1 | query matches hand math |
| 35 | Checkpoint and resume | 4 | code | haiku | CCDV-P 1.2 | a killed run resumes |
| 36 | OTel GenAI spans + metrics | 4 | code | haiku | OBS CCDV-P 3.1 | a run is one trace in Tempo |
| 37 | Image to GHCR, Deployment, alert webhook | 4 | code | sonnet | K8S CI | an alert starts a run |
| 38 | Daily digest via Batch API | 4 | code | haiku | CCDV-P 6.1 | digest arrives on ntfy |
| 39 | Exit check: outage → diagnosis, cost panel | 4 | ops | sonnet | OBS | diagnosis correct, cost in Grafana |
| 40 | Dashboard app skeleton | 5 | code | haiku | PY | page renders locally |
| 41 | Allowlist sanitiser + tests | 5 | code | haiku | SEC CCDV-P 7.2 | unknown label never reaches the page |
| 42 | Threat model + ADR-0008 | 5 | write | sonnet | SEC | reviewed by the orchestrator |
| 43 | Public via Tailscale Funnel | 5 | ops | sonnet | SEC | reachable from mobile data |
| 44 | MCP server | 6 | code | haiku | CCDV-P 2.3 | Claude Code on the Mac can use it |
| 45 | Golden set + code graders | 6 | code | haiku | CCDV-P 5.1 | eval runs, scores recorded |
| 46 | LLM judge + calibration | 6 | code | haiku | CCDV-P 5.2 | judge agrees with your labels |
| 47 | Eval gate in CI | 6 | code | haiku | CI CCDV-P 5.1 | a worse prompt fails the PR |
| 48 | Guardrails: deny rules, injection in logs | 6 | code | sonnet | SEC CCDV-P 7.1 7.2 | injected log line is ignored |
| 49 | Model routing experiment | 6 | code | haiku | CCDV-P 1.3 6.1 | model chosen on cost per task |
| 50 | Hermes parity decision | 6 | write | sonnet | ARCH | port list agreed |
| 51 | Immich into the cluster | 7 | code | sonnet | K8S DB | photos load, old CT untouched |
| 52 | Nextcloud into the cluster | 7 | code | sonnet | K8S DB | files load, old CT untouched |
| 53 | iGPU into the VM | 7 | ops | sonnet | K8S | `/dev/dri` visible in the VM |
| 54 | Jellyfin + GPU device plugin | 7 | code | sonnet | K8S | hardware transcode works |
| 55 | Retire Caddy and old LXCs (deletion runbook) | 7 | ops | sonnet | SEC | Proxmox runs only the VM (+ Hermes) |
| 56 | restic/Kopia to USB + B2 | 8 | code | sonnet | SEC | first snapshot offsite |
| 57 | Postgres backups + k3s snapshots | 8 | code | sonnet | DB | restore of one DB works |
| 58 | Full restore drill + runbook | 8 | ops | sonnet | SEC OBS | fresh VM serves everything |
