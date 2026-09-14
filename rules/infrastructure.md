---
paths:
  - "**/*.{tf,tfvars,hcl}"
  - "**/Dockerfile*"
  - "**/*.dockerfile"
  - "**/docker-compose*.{yml,yaml}"
  - "**/compose*.{yml,yaml}"
  - "**/.github/workflows/**"
  - "**/.gitlab-ci.yml"
  - "**/Jenkinsfile"
  - "**/k8s/**"
  - "**/kubernetes/**"
  - "**/helm/**"
  - "**/*.k8s.{yml,yaml}"
---

# Infrastructure, containers, CI

- Route the work through the `infrastructure-quality` skill: blast radius before
  edits, smallest safe change, format and validate, plan or dry-run, then review.
- Never apply, deploy, destroy, import, or mutate state without the user's
  explicit approval of that exact operation. A plan showing a destroy is not
  approval. The Terraform/OpenTofu half is enforced by the
  `block-destructive-iac.sh` hook; everything else relies on you.
- Terraform state, `state pull`, and `terraform show` output contain secrets.
  Never paste them into context, a review packet, a log, or a subagent prompt.
- Infrastructure changes are high-risk for the `adversarial-jury`: correctness,
  security, and (when boundaries move) architecture judges; reuse existing judges.
- Pin base images and third-party CI actions; run containers as non-root; give CI
  jobs the minimum `permissions`; never interpolate untrusted event input into a
  shell step.
