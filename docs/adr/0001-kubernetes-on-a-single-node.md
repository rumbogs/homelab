# 0001: Kubernetes on a single node

- Status: accepted
- Date: 2026-11-25

## Context

Currently, I have multiple LXC containers each having nested Docker containers
and setup is complicated, for example, Docker inside an LXC needs AppArmor
unconfined and nesting turned on and an apt upgrade has broken bridge NAT
before. I have to maintain multiple Docker compose files which are nested deep
inside LXC containers.

The concrete pain is that I can't easily see the status of each container in a
centralized place, I have to ssh into each container manually. Logs and health
status are not exposed automatically because of nesting. Also configuration is
difficult because duplicated config options have to be rewritten and maintained
separately.

Constraints: one machine which is maintained in my free time by one person (me),
therefore maintenance needs to be performed quickly.

Scale is not the reason here because I run one of each container instead of many
and there's a single consumer so a single node is enough.

One specific pain point is file system permissions. LXC requires a certain
permission for the files that are mounted inside a container, while Docker
requires a different one. This relies on memory or documentation to set it up
every time and maintaining it whenever you need to mount another volume.

## Decision

Move to k3s, one node in a single VM, with Flux. The main thing is the
reconciliation loop, which restarts containers if they become unhealthy or if
the config has changed, based on preconfigured health checks. Today, when a
container hangs or becomes unhealthy, I have to manually ssh into the server and
dig through nested containers to find out what happened and restart them.
Another improvement is having a single API to work with, as opposed to one for
LXC, one for docker and one for setting up file permissions. And GitOps, which
allows version locked config files stored in GitHub to be used for recovery,
while data has to live on a different storage provider along with the secrets
encryption key.

## Alternatives considered

| Option                   | Why not                                                                                                                                                                          |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| docker-compose on one VM | it doesn't have reconciliation, just plain restarts when containers die, and compose doesn't have a built in way to pull config from git                                         |
| Nomad                    | Kubernetes has Flux, RBAC and ServiceAccounts and a huge ecosystem of ready-made manifests and operators                                                                         |
| plain LXC                | workarounds with AppArmor and config is manually duplicated across many containers                                                                                               |
| Talos                    | maybe later, I need to be able to ssh into the machine for other services I need to run on the server, I also need to be able to debug any issues with my Kubernetes setup first |

## Consequences

ServiceAccount is especially useful for monitoring agent's access, where we can
only expose limited permissions, for example read-only, so that if the AI agent
leaks the token by mistake, it doesn't have such a large blast radius and is
auto-rotated by default.

RAM usage increases though, because of the control plane, but 32GB should be
more than enough since the control plane uses about 1.5GB. There are more moving
parts such as control plane, Flux and RBAC.

Another cost is having a single node, if it dies, there's nothing to restart it
or cover for it. This is not worse than today and could be mitigated by a second
control-plane node.
