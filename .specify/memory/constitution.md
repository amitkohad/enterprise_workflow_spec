# Temporal Enterprise Framework Constitution

Version: 1.1.0 | Ratified: 2026-10-01 | Last amended: 2026-10-01

## I. One application, two roles

The repository MUST produce one versioned application and one immutable container image.
`APP_ROLE=INGESTION` runs HTTP ingress and Kafka ingestion together; `APP_ROLE=WORKER`
runs registered Temporal Workers. Capability modules MUST remain inside this application.
Temporal Service, Kafka, identity, secret management and observability infrastructure are
external dependencies. Adding a database, third runtime role or independently deployable
service requires an explicit specification amendment.

## II. Durable execution and honest delivery guarantees

Workflow code MUST be deterministic and replay compatible. External I/O, encryption,
wall-clock measurements and blocking libraries MUST execute outside Workflow code.
Activities MUST declare bounded timeouts and retry behavior. Side effects MUST tolerate
re-execution. Kafka ingestion MUST provide at-least-once delivery of start intent with
explicit partition commit fences. No component may claim end-to-end exactly-once effects.
Workflow ID deduplication MUST disclose its namespace and history-retention boundary.

## III. Security at every boundary

Production clients MUST enforce authenticated TLS and certificate verification. Sensitive
Temporal Payloads and encoded failure attributes MUST be encrypted before transmission.
Sensitive values MUST NOT appear in IDs, Search Attributes, log fields, trace attributes,
metric labels or unencrypted failure fields. Encryption key rotation MUST preserve the
ability to replay and read retained histories. Authentication, tenant authorization and
allowlisted routing MUST precede starts and reads. Secret material MUST never enter source
control, images, fixtures, logs or diagnostic output.

## IV. Bounded resources and operability

Queues, in-flight operations, executors, namespace clients, payload sizes and RPC deadlines
MUST have documented finite bounds. Startup validation MUST fail closed; failed critical
background tasks MUST terminate the role. Readiness MUST reflect dependency availability
without causing liveness restart storms. Both roles MUST provide structured telemetry,
health probes, graceful shutdown and measurable capacity qualification.

## V. Contracts before implementation

Each public API, event format and configuration boundary MUST have a versioned contract.
User outcomes belong in `spec.md`; implementation choices belong in `plan.md` and its
supporting documents. Tasks MUST cite requirements, concrete file paths and observable
acceptance conditions. A task MUST change one reviewable behavior. Schema changes MUST
include compatibility tests; SDK upgrades MUST include replay and integration checks.

## VI. Evidence, tests and small increments

Implementers MUST consult the referenced official documentation and verify APIs against
the locked SDK. Tests MUST exercise failure windows and contracts rather than merely
restate code. No task may be checked complete without its acceptance evidence. Release
gates MUST cover unit, real-service integration, history replay, security, container,
Kubernetes lifecycle and capacity behavior. Qualification targets MUST be reported with
the actual hardware and dependency quotas; they are not unsupported throughput promises.

## Development workflow

Use the SpecKit sequence: constitution, specification, clarification as needed, plan,
tasks, consistency analysis, bounded implementation batches and convergence. Maintain
the shared platform contract in `specs/001-enterprise-workflow-platform/` and one feature
directory per deployable increment listed in its `roadmap.md`. Each feature MUST have
its own `spec.md`, `plan.md`, `tasks.md`, dependency set and executable deployment proof.
An increment builds a complete version of the same application, including prerequisite
features; it is not an independently hosted microservice. Feed one feature-local task,
or a short dependency-complete batch, to an AI generator at a time.

The 1.1.0 amendment reflects the user's requested micro-level feature decomposition;
it changes planning granularity while preserving one repository/image and two roles.

## Governance

This constitution governs the feature specification and generated implementation.
An amendment MUST update affected requirements, design, tasks, contracts and tests in the
same review. Breaking principles or guarantees increments the major version; adding
principles increments the minor version; clarifications increment the patch version.
Reviews MUST identify any deviations and their justification. Production environment
configuration is supplied by the operator and validated by the application; it MUST NOT
silently weaken these principles. User instructions take precedence over this document.
