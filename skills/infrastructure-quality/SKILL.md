---
name: infrastructure-quality
description: Routes infrastructure-as-code work - Terraform, AWS, Docker, GitHub Actions, Kubernetes, CI/CD. Use when a change touches infrastructure, deployment, or pipeline configuration.
---

# Infrastructure quality

Infrastructure changes fail differently from application changes: the blast
radius is real resources, the feedback loop is a deployment, and the undo button
often does not exist. This skill routes that work. It does not replace the
existing judges — it decides what evidence to gather and who reviews it.

**Only use this in repositories that actually contain infrastructure code.** Do
not apply it to application repos that merely have a Dockerfile for local dev.

## Route

```
requirements and the invariant that must hold
  -> inspect the EXISTING infrastructure (do not design from scratch)
  -> understand dependencies, state, and blast radius
  -> smallest safe change
  -> format + validate
  -> plan / dry-run where the tool supports it
  -> security review + blast-radius review
  -> final diff
```

**Blast radius first.** Before editing, answer: what resources does this touch,
what depends on them, is anything replaced rather than updated, is there data
loss, is it reversible, which environment and account, and who is paged if it
goes wrong. A change that quietly forces resource replacement is the single most
common infrastructure defect — look for it in the plan, not in the diff.

## Never apply automatically

Never run, without the user's explicit approval for that exact operation:

- `terraform apply` / `destroy` / `import` / `taint` / `force-unlock`
- `terraform state mv|rm|push|replace-provider`
- any deploy, rollback, cluster mutation, or DNS/traffic cutover
- destructive cloud CLI operations, however reasonable the plan looks

A plan that shows a destroy is **not** approval to destroy. Produce the plan,
show the user what it does, and stop.

*(A PreToolUse hook at `~/.claude/hooks/block-destructive-iac.sh` enforces the
Terraform/OpenTofu half of this deterministically. Guidance is not enforcement —
do not treat the hook's existence as permission for anything it does not cover.)*

**Terraform state is sensitive.** It contains plaintext secrets. Never print,
paste, commit, or send state or `state pull` output into a review packet, a log,
or a subagent prompt. `terraform show` and `state show` leak the same way.

## Deterministic evidence

Run what the repo actually has. Do not install scanners globally on spec; if a
tool is missing and would help, say so and let the user decide.

| Stack | Evidence, in order of strength |
|---|---|
| **Terraform** | `fmt -check` → `validate` → `plan` (save with `-out`, read the plan, count creates/updates/**replaces**/destroys) → `tflint` → `checkov`/`tfsec`/`trivy` *only if already configured* |
| **Docker** | `docker build` → configured scanner (`trivy`, `hadolint`) if present |
| **GitHub Actions** | `actionlint` if available → schema/YAML validation → read the workflow's permissions block |
| **Kubernetes** | `kubectl apply --dry-run=server` (or `--dry-run=client` with no cluster) → `kubeconform`/schema validation → `helm template` + `helm lint` |
| **Anything** | The repo's own CI workflow is the specification for what must pass |

Tool output outranks reviewer opinion, and a green plan is not proof the design
is right — it only proves the syntax and the provider agree.

## Review dimensions

Read these when reviewing the relevant surface. They are checklists for the
parent and for the review packet, not separate reviewers.

**AWS / cloud** — IAM least privilege (wildcards in `Action` or `Resource`,
`iam:PassRole` scope, trust policies); resource policies; network exposure
(0.0.0.0/0, public subnets, security group ingress); encryption at rest and in
transit; logging and audit trails (CloudTrail, access logs, retention);
secret handling (never in plaintext variables, tfvars, or environment blocks);
public access flags (S3 block-public-access, RDS/ELB public IPs); lifecycle and
deletion behavior (`prevent_destroy`, `force_destroy`, deletion protection,
final snapshots); cost-impacting changes (instance class, NAT gateways, cross-AZ
traffic, provisioned capacity); and region/account assumptions baked into
hardcoded ARNs or provider blocks.

**GitHub Actions** — `permissions:` set to the minimum (default is often too
broad); third-party actions pinned to a full commit SHA where the action is not
first-party; secrets never echoed, never passed to untrusted steps, never
available to fork PRs; `pull_request_target` treated as hostile — it runs with
write scope against attacker-authored code; untrusted input never interpolated
into `run:` (`${{ github.event.* }}` → shell injection; use an `env:` binding);
artifact and cache trust across jobs; OIDC role assumption with a
correctly-scoped `sub` condition rather than a wildcard; environment protection
rules on deploy jobs; and concurrency groups so deploys cannot race.

**Docker** — base image minimal and pinned by digest or specific tag, not
`latest`; runs as a non-root `USER`; no secrets in layers, `ARG`, or history
(use build secrets or runtime injection); reproducible builds (lockfiles, pinned
dependency versions consistent with the project's policy); `HEALTHCHECK` where a
supervisor uses it; `.dockerignore` excluding `.git`, secrets, and build cruft
so the context stays small and clean; and no unnecessary capabilities,
`--privileged`, or host mounts.

## Review routing

Infrastructure changes are **HIGH-RISK** by default in the `adversarial-jury`
sense. Reuse the existing judges — do not create infrastructure-specific ones:

- `correctness-adversary` — will this do what it claims, and what breaks on the
  failure path, on retry, on partial apply?
- `security-judge` — the existing independent security lens. **Do not add a
  second security reviewer.**
- `architecture-judge` — when the change moves boundaries: network topology,
  account/environment structure, service dependencies, module ownership.
- `test-judge` — when the infrastructure is genuinely testable (terratest,
  policy tests, CI assertions). Skip it when there is nothing to judge.
- `jury-arbiter` — on material disagreement.

Send the plan output as deterministic evidence in the packet. **Strip state,
secrets, account IDs, and ARNs you do not need** before it goes anywhere.

## Optional specialists

For a repo with substantial infrastructure, install narrow wshobson agents
**at project scope so they do not load in unrelated repositories**:

```
claude plugin install deployment-strategies@claude-code-workflows --scope project
```
→ `terraform-specialist`, `deployment-engineer` (2 agents, no skills)

```
claude plugin install deployment-validation@claude-code-workflows --scope project
```
→ `cloud-architect`

```
claude plugin install distributed-debugging@claude-code-workflows --scope project
```
→ `devops-troubleshooter`

Do not install `cloud-infrastructure` (7 agents + 7 skills), `cicd-automation`
(5 agents + 4 skills), or `incident-response` (6 agents, including duplicates of
built-in review/debug agents). They are broad packs, they duplicate each other's
agents, and their descriptions say "use PROACTIVELY" — at user scope they route
themselves into work that is not theirs.

Use a specialist for domain knowledge. Keep review with the existing judges.
