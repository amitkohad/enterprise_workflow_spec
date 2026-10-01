# Feature Specification: F01 Role Runtime and Health

Feature: `002-role-runtime-health` | Date: 2026-10-01 | Priority: P1  
Parent: [platform roadmap](../001-enterprise-workflow-platform/roadmap.md) → F01  
Dependencies: none. Checkpoint: `f01-runtime-health`.

## User outcome

An operator can build one application image, launch either runtime role, observe startup,
liveness/readiness and safely terminate the process. This is the first deployable skeleton,
with no business ingestion or Workflow execution enabled yet. It is a synthetic
qualification checkpoint, not a production workflow platform.

## Scope and acceptance

- **F01-01**: One repository and one Dockerfile build an immutable Python image using
  locked dependencies. `python -m app.main` accepts only INGESTION or WORKER.
- **F01-02**: Both roles serve private startup/live/ready probes on 8080. Invalid settings
  fail before serving; readiness becomes false during drain. No public Workflow routes.
- **F01-03**: Startup owns all tasks/resources, essential failure exits nonzero and
  SIGTERM stops cleanly without orphan tasks/threads. Temporary readiness and liveness
  have distinct meanings.
- **F01-04**: The container runs non-root with a read-only root filesystem and injected
  config. No certificates, encryption keys or test data are baked into the image.

Independent acceptance: build the image; run each role on distinct local host ports with
`APP_ENV=test`; verify probes and SIGTERM exit; repeat with invalid APP_ROLE and observe
nonzero startup failure. WORKER is operational shell only until F03 provides a Worker.

Shared requirements: FR-CORE-01–04, FR-SEC-07, FR-OPS-01/04. V-001, V-022, V-023
are covered only for this shell scope; full platform gates remain cumulative.

## Deployable unit and edge cases

Artifact: application image version tagged for `f01-runtime-health`, an immutable digest,
`config/checkpoints/f01/`, `docs/checkpoints/F01.md` and executable smoke tests. It can run
without Temporal/Kafka/OIDC because none of their capabilities is enabled in this image.
Do not fabricate worker polling or authenticated-start readiness. Later production images
require all role-specific security/dependency validation from the parent contract.

Reject unknown roles, duplicate server ownership and hidden background failures. Probe
responses contain only a safe state/reason, never configuration values. Rollback replaces
the same-role image with its preceding compatible version; no durable data exists yet.
