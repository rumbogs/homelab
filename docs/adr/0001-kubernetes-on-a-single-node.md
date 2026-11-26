# 0001: Kubernetes on a single node

- Status: proposed
- Date: 2026-11-25

<!--
TODO(you) [ARCH] [K8S]: write this ADR in your own words, using the
template sections below. This is the question every interviewer will ask
about this project: "why Kubernetes for one machine?"

Points to cover (from the plan, but argue them, don't copy them):
- Why horizontal scaling is NOT the reason here.
- Reconciliation: what "desired state" means and what a controller does.
- One API for deploy, config, secrets, networking, storage and identity,
  compared with today's LXC + docker-compose setup.
- GitOps: what rebuilding the server looks like afterwards.
- Identity: why a ServiceAccount for the agent beats an API token in a file.
- The honest costs: RAM overhead, complexity, still no HA.
- Alternatives: docker-compose on one VM, Nomad, staying on LXC, Talos
  instead of k3s. One line each on why not.

Check: could you say the Decision section out loud in 30 seconds?
-->

## Context

## Decision

## Alternatives considered

| Option | Why not |
|---|---|

## Consequences
