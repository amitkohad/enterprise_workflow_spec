# Temporal Enterprise Workflow Framework — Feature Specifications

A comprehensive SpecKit-style specification package for one Python application and
one image with `INGESTION` and `WORKER` roles, using Temporal, FastAPI, Confluent Kafka,
Prometheus, Kubernetes, KEDA and mTLS.

The [roadmap](specs/001-enterprise-workflow-platform/roadmap.md) divides the platform
into **16 micro-level deployable increments**. Each feature has its own specification,
corresponding plan, small tasks, explicit dependencies, executable smoke checkpoint and
rollback conditions. Prerequisite features are included in the same versioned application.

| Feature group | Deployable outcome |
|---|---|
| F01–F04 | Role runtime, mTLS, encrypted execution and acknowledged Kafka publication |
| F05–F10 | REST start/status, Kafka trigger/DLQ/recovery and tenant isolation |
| F11–F14 | Correlated telemetry, Kubernetes deployment and ingestion/Worker scaling |
| F15–F16 | Pinned Worker rollouts and key/certificate rotation |

Start with [AI handoff](specs/001-enterprise-workflow-platform/ai-handoff.md) and
[F01 tasks](specs/002-role-runtime-health/tasks.md). Feed one feature-local task to
your generator at a time. The parent monolithic task list has been superseded.

Shared design artifacts:

- [Constitution](.specify/memory/constitution.md)
- [Platform requirements](specs/001-enterprise-workflow-platform/spec.md)
- [Architecture and configuration](specs/001-enterprise-workflow-platform/plan.md)
- [Official-source research](specs/001-enterprise-workflow-platform/research.md)
- [Security/keyring contracts](specs/001-enterprise-workflow-platform/security.md)
- [Data model](specs/001-enterprise-workflow-platform/data-model.md) and
  [OpenAPI/event/routing schemas](specs/001-enterprise-workflow-platform/contracts/)
- [Operations](specs/001-enterprise-workflow-platform/operations.md) and
  [30 verification gates](specs/001-enterprise-workflow-platform/verification.md)
- [Quickstart](specs/001-enterprise-workflow-platform/quickstart.md) and
  [specification quality review](specs/001-enterprise-workflow-platform/checklists/requirements.md)

Documentation researched on 2026-10-01 using official primary sources. This repository
contains specifications and contracts; application implementation, runtime tests and
deployment have not been performed. Early feature checkpoints are synthetic qualification
releases; production eligibility requires all cumulative security, recovery and capacity gates.

The planning model follows [GitHub SpecKit](https://github.github.com/spec-kit/).
No SpecKit CLI installation is required to consume the files with an AI coding tool.
