# Platform Specification: Temporal Enterprise Workflow Core

Parent platform contract: `001-enterprise-workflow-platform`  
Suggested implementation branch: `codex/001-enterprise-workflow-platform` (not created)  
Created: 2026-10-01 | Status: Ready for implementation planning and review  
Project: `temporal-enterprise-framework`  
Input: Enterprise workflow foundation using Python, Temporal, FastAPI, Confluent Kafka,
Prometheus, Kubernetes, KEDA and mTLS; one application with ingestion and worker roles.

## Product boundary

Deliver a standardized, deployable core that accepts authorized REST requests and Kafka
events, starts registered Workflows, executes durable Activities, encrypts sensitive
Temporal data and exposes operational telemetry. Build one repository and one container
image, deployed with two role configurations. A deployment may contain multiple replicas,
tenant-specific Worker deployments and retained versions of that same image.

The initial registered Workflow is `EnterpriseEventWorkflow`: validate a versioned input,
publish one `workflow.processed` event through the reusable `publish_event` Activity and
return the acknowledged publish receipt. That event reports processing, not successful
Workflow completion. This provides a real end-to-end contract and a template for adding
reviewed Workflow definitions without designing an arbitrary workflow interpreter.

This release includes authenticated ingestion, tenant routing, encrypted payloads,
standard Worker construction, safe retries, logs/metrics/tracing, deployment artifacts,
runbooks and automated acceptance tests. Workflow authors extend registered Python code
and schemas through normal releases. Priorities below sequence delivery; every listed
requirement is mandatory for the production v1 release.

Excluded: a UI, runtime code upload, user-authored DSL, business workflow library, billing,
a bespoke deduplication database, a public codec server, standalone activity execution,
schedules/signals/updates/cancellation REST APIs, object-storage offloading, multi-region
active/active orchestration, and provisioning Temporal/Kafka/identity infrastructure.
These may become later amendments; they must not be invented during code generation.

## Feature decomposition

The user confirmed deployment as increments of this same application. The canonical
[roadmap](roadmap.md) divides delivery into 16 micro-level feature packages, each containing
its own specification, corresponding implementation plan and small executable tasks.
Every increment produces a deployable image version plus role configuration and a smoke
proof. Dependencies are explicit and included in that image. Early checkpoints are
synthetic qualification deployments; the complete platform becomes production eligible
only after the cumulative security, deployment, recovery and capacity gates pass.
This parent document remains the shared FR/SC contract, not one giant implementation task.

## User Scenarios & Testing

### US1 — Protect and isolate enterprise execution (P1)

As a platform security owner, I need validated credentials, encrypted histories and tenant
boundaries so business payloads do not leak through platform features.

Independent test: inspect real server history for a known sensitive sentinel and attempt
starts/reads with wrong-tenant tokens, invalid certificates and tampered ciphertext.

Acceptance scenarios:

1. Given valid mounted certificates and key material, when either role connects, then
   server identity and client authentication are verified and all sensitive Payloads are
   encoded with the current encryption key.
2. Given a Workflow failure containing a sensitive message, when history is inspected,
   then message and stack are codec protected, and logs/public API errors contain only
   approved reason codes.
3. Given a tenant A identity, when it requests tenant B execution or status, then no start
   occurs and no existence, status or result information is disclosed.
4. Given historical ciphertext using key A and current writes using key B, when a Worker
   replays the old execution, then key A remains available and decoding succeeds.

### US2 — Execute a durable registered workflow (P1)

As a workflow author, I need a standard deterministic execution environment and reusable
Kafka publishing Activity so I can add business logic with explicit failure semantics.

Independent test: execute the reference Workflow in Temporal's test environment, retry a
failed Activity and replay a recorded history using the same converter and registration.

Acceptance scenarios:

1. Given a validated input on an allowlisted route, when a Worker polls its Task Queue,
   then the registered Workflow calls the publish Activity and returns its delivery receipt.
2. Given a Worker crash during publishing, when the Activity is retried, then the stable
   publish ID is preserved and downstream consumers can deduplicate repeated events.
3. Given a terminal business validation failure, when the Activity fails, then configured
   non-retryable handling applies and the Workflow reports a sanitized terminal status.
4. Given shutdown or cancellation while waiting for delivery, then the Activity observes
   cancellation through heartbeat/cancellation handling and releases its resources.

### US3 — Start and inspect workflows through REST (P1)

As an application integrator, I need an authenticated, retry-safe start API and bounded
status/result reads so network uncertainty does not create duplicate work.

Independent test: repeat a start request with the same idempotency key and content; repeat
with different content; inspect running/completed/failed states and cross-tenant reads.

Acceptance scenarios:

1. Given a valid scoped token and UUID `Idempotency-Key`, when a start is durably accepted,
   then return HTTP 202 with the same UUID as `workflow_id`, a `run_id` and status location.
2. Given a matching retained execution, when the same request is repeated, then return
   HTTP 200 marked duplicate without starting another execution.
3. Given the same ID with changed payload/type/tenant-domain binding, then return 409;
   a missing or invalid idempotency header returns 400.
4. Given an ambiguous start deadline, then return retryable 503 and instruct the caller
   to retry with the original key. Never silently substitute a new UUID.
5. Given a running Workflow, when status is read, then respond without waiting for its
   completion. Results are returned only on an authorized completed-result request.

### US4 — Ingest Kafka events reliably (P1)

As an event producer, I need replay-safe ingestion so acknowledged records either start
their intended Workflow or reach a controlled dead-letter outcome.

Independent test: kill ingestion after server acceptance but before offset commit, restart
and confirm a verified duplicate; also test poison messages and rebalances.

Acceptance scenarios:

1. Given a valid event whose UTF-8 Kafka key equals `message_id`, when consumed, then
   `workflow_id` equals that ID and no Workflow completion wait occurs.
2. Given a confirmed start or a verified matching duplicate, then commit only the next
   contiguous completed offset in that partition.
3. Given invalid schema, unauthorized tenant binding or ID-content conflict, then publish
   a sanitized DLQ record and commit only after its broker delivery acknowledgement.
4. Given transient/ambiguous Temporal or DLQ failure, then pause/retry with backoff while
   continuing group polling, retain the offset and keep memory/in-flight work bounded.
5. Given assignment revocation, then old assignment callbacks cannot commit offsets on
   a new assignment; replay safely reconciles any uncertain starts.

### US5 — Operate and observe both roles (P2)

As an operator, I need useful telemetry, bounded concurrency and coordinated lifecycles
so I can diagnose failures and scale without losing accepted work.

Independent test: scrape both roles, trace one REST and one Kafka request, kill a critical
task and terminate a busy pod; verify healthy bounded recovery.

Acceptance scenarios:

1. Given a request flowing into an Activity, then structured logs correlate trace ID,
   Workflow ID, run ID, type, queue and Activity attempt where those fields apply.
2. Given Workflow replay, then application logs/traces do not multiply per replay and
   metrics never use per-execution identifiers as labels.
3. Given loss of a required dependency, then readiness becomes false while liveness
   stays healthy; unrecoverable supervisor failure terminates the role.
4. Given SIGTERM, then new ingestion stops, eligible offsets are committed, Worker tasks
   drain within the configured grace period and remaining work recovers through Temporal.

### US6 — Release, qualify and recover the platform (P2)

As a platform engineering team, I need repeatable deployment, replay-compatible upgrades,
key rotation and recovery procedures so production changes preserve in-flight execution.

Independent test: deploy both roles from one image, run the qualification workload, rotate
keys/certificates, perform a versioned Worker rollout and recover from injected failures.

Acceptance scenarios:

1. Given the supplied Kubernetes chart/configuration, then both roles run non-root with
   probes, secret mounts, resource bounds, network restrictions and autoscaling.
2. Given an old pinned Workflow execution, then promoting a new Worker version retains
   the older version until no pinned executions or recoverable histories require it.
3. Given the qualification workload, then measured acceptance/scheduling latency, error
   rate, lag and bounded-resource criteria meet the documented release targets.
4. Given Kafka replay or Temporal history restore, then the runbook accounts for retained
   IDs and encryption keys and reports any possible duplicate effects or recovery gap.

## Requirements

Normative terms: MUST is required; SHOULD permits an explicitly recorded, tested deviation.
Supporting contracts refine these requirements. If artifacts disagree, resolve the conflict
in the specification and contracts before implementing either interpretation.

### Application and configuration

- **FR-CORE-01**: Produce one application/image with exactly the `INGESTION` and `WORKER`
  roles selected at startup; invalid roles/configuration fail before serving or polling.
- **FR-CORE-02**: Use the requested `/app` layout with `api`, `events`, `temporal`, `config`
  and `main.py`; client and worker are packages, without same-name competing module files.
- **FR-CORE-03**: Validate typed settings, mounted secrets, routes and role-specific
  dependencies; expose redacted configuration diagnostics and finite resource limits.
- **FR-CORE-04**: Coordinate startup, readiness, failure supervision and shutdown for all
  role-owned resources. One HTTP process per pod; no detached unobserved background tasks.

### Security and tenancy

- **FR-SEC-01**: Encrypt every supported Temporal business Payload before transmission,
  including inputs, results, Activity data, memo and heartbeat details; clients and Workers
  use the identical versioned converter. No plaintext compatibility fallback is allowed
  for supported business encodings in production.
- **FR-SEC-02**: Encode and encrypt failure messages/stacks through the FailureConverter;
  restrict exposed operational failure type names/codes to an allowlist while preserving
  protected business details and retry/cancellation semantics. Reject unsupported/malformed
  codec envelopes, unknown keys and failed authentication without returning plaintext.
- **FR-SEC-03**: Support active-write and retained-read encryption keys, authenticated
  versioned envelopes, rotation and restore/replay compatibility. Production keys come
  from mounted secret material; cloud KMS integration is an external provider boundary.
- **FR-SEC-04**: Require production Temporal mTLS using local certificate/private-key/CA
  mounts with trust and server-name checks; reject insecure production overrides. Require
  authenticated encrypted Kafka connections and TLS at the public API ingress.
- **FR-SEC-05**: Authenticate REST using validated enterprise OIDC JWTs and authorize
  tenant/scope before routing, starting or reading. Kafka topic routes bind producer data
  to configured tenant identities and supported workflow types.
- **FR-SEC-06**: Forbid sensitive data in IDs, routing labels, Search Attributes, clear
  metadata, logs, traces, metrics and DLQs. Validate size/shape before encoding; no payload
  or exception-body logging. Business data in Kafka is covered by broker access, TLS and
  operator-managed at-rest encryption, independently of the Temporal codec.
- **FR-SEC-07**: Use least-privilege credentials, non-root containers, read-only mounts,
  restricted network paths, private telemetry/probes and authenticated result access.

### Routing and client lifecycle

- **FR-ROUTE-01**: Resolve `(tenant_id, domain, workflow_type)` using versioned allowlisted
  configuration to a preprovisioned namespace, queue and output topic. Tenant namespaces
  are isolated one per tenant; domains share only their tenant namespace.
- **FR-ROUTE-02**: Reject unconfigured routes; callers cannot supply task queues,
  namespace credentials, arbitrary Workflow types or output topics.
- **FR-ROUTE-03**: Bound namespace clients and selected Worker queues, validate Workflow
  registrations and preserve ID-to-namespace bindings during the deduplication window.
- **FR-ROUTE-04**: Cache fully configured Temporal clients per process/event loop and
  namespace. Do not share clients across event loops or replace the converter per request.

### Durable execution

- **FR-WF-01**: Supply the registered `EnterpriseEventWorkflow` and `publish_event`
  Activity, versioned typed inputs/results and a documented registration extension path.
- **FR-WF-02**: Keep Workflow orchestration deterministic and sandboxed; forbid blocking
  I/O, SDK clients, environment reads, encryption and wall-clock duration measurement in
  Workflow code. Replay-aware interceptors must not alter command ordering.
- **FR-WF-03**: Declare Activity retry, start-to-close, schedule-to-close and heartbeat
  deadlines; distinguish transient, terminal and cancellation outcomes without swallowing
  cancellation. Bound in-flight publish waits and Activity/executor concurrency.
- **FR-WF-04**: Wait for Kafka delivery acknowledgement inside the Activity; maintain a
  stable logical publish ID across retries. Broker producer idempotence does not eliminate
  duplicate side effects across Activity attempts; downstream deduplication uses the
  composite `(tenant_id, publish_id)` because equal UUIDs are valid in distinct namespaces.
- **FR-WF-05**: Register only approved definitions and retain compatibility for in-flight
  executions with replay checks and versioned Worker deployment policy. Eager Workflow
  start is disabled in the baseline. Pinned builds use distinct immutable Kubernetes
  Worker Deployments retained simultaneously; replacing the old image in place is forbidden.
- **FR-WF-06**: Document safe schema evolution, patching and Continue-As-New for future
  long-running workflows; do not introduce unnecessary infinite loops in the reference.

### Shared start and deduplication

- **FR-ING-01**: Use the validated UUID message/idempotency key verbatim as Workflow ID,
  unique within the tenant namespace. Configure FAIL for open conflicts and REJECT_DUPLICATE
  for retained closed runs; never terminate/reuse an existing ID automatically.
- **FR-ING-02**: On already-started or uncertain starts, describe the execution and verify
  encrypted canonical request digest, tenant/domain/type and immutable route binding before
  treating it as a duplicate. Conflicts are explicit; unavailable evidence stays retryable.
- **FR-ING-03**: Bound all start/read/reconciliation RPCs and retries; report ambiguity
  without claiming acceptance. Do not wait for Workflow completion on ingestion paths.
- **FR-ING-04**: Disclose that ID deduplication ends when relevant Temporal history is
  deleted/expired. Require a deployment retention/replay policy; indefinite deduplication
  is outside this release without an additional durable ledger.

### REST ingress

- **FR-API-01**: Implement `POST /v1/workflows/start` with the versioned body, mandatory
  UUID `Idempotency-Key`, scopes, limits and 202/200/400/409/413/422/429/503 error semantics
  in `contracts/openapi.yaml`. Callers generate and retain the UUID before submitting.
- **FR-API-02**: Implement `GET /v1/workflows/{workflow_id}` with authorized tenant/domain
  context, optional run ID, bounded describe, explicit state and optional completed result.
  Follow the latest run in a chain when run ID is omitted; do not block on running results.
- **FR-API-03**: Hide inaccessible execution existence; return sanitized errors, no-store
  responses and correlation IDs. Configure body/depth limits, request deadlines and local
  per-pod admission/rate bounds; enterprise ingress supplies aggregate tenant rate limits.

### Kafka ingress

- **FR-KAFKA-01**: Consume configured trigger topics with manual offset storage/commit,
  validated envelope and key equality; maintain one unresolved start per partition and
  bounded overall in-flight/buffer counts while group polling remains responsive.
- **FR-KAFKA-02**: Commit only contiguous completed offsets after durable start, verified
  duplicate or acknowledged DLQ; commit offset+1, respect assignment generations and retry
  failed commits without skipping unresolved records.
- **FR-KAFKA-03**: Classify schema/key/tenant/route/content conflicts as permanent record
  failures; publish metadata-only DLQ with deterministic record identity. Dependency/auth
  outages are recoverable operator failures, never bulk DLQ causes.
- **FR-KAFKA-04**: Pause affected partitions on transient failure, use jittered bounded
  retries and resume without dropping records. Recover safely from rebalances, pod crashes,
  broker errors and starts acknowledged after assignment revocation.
- **FR-KAFKA-05**: Run Confluent blocking consumer/producer polling through bounded
  thread/executor bridges; callbacks hand results back safely to the asyncio event loop.
  Confirm broker deliveries, flush within shutdown bounds and release group membership.

### Observability and deployment

- **FR-OBS-01**: Emit structured redacted JSON logs with trace/workflow/run/type/queue and
  Activity type/attempt fields where applicable; bind and reset per-operation context.
- **FR-OBS-02**: Use replay-aware Workflow telemetry and supported trace propagation from
  REST/Kafka through client/Worker/Activity interceptors; do not measure Workflow wall time
  inside deterministic code. Never expose a public arbitrary codec decoding endpoint.
- **FR-OBS-03**: Expose private `/metrics` and probes on port 8080 for both roles, and a
  process-wide Temporal SDK Prometheus exporter on WORKER port 9090. Document both scrape
  targets and stable low-cardinality metric dimensions.
- **FR-OBS-04**: Measure acceptance outcome/latency, Kafka lag/retries/commit/DLQ outcomes,
  publish outcome/latency, dependency state and worker scheduling/capacity; provide alerts
  and dashboards that exclude business data.
- **FR-OPS-01**: Supply one reproducible image and Kubernetes deployment configuration
  for both roles with secrets, TLS, health probes, resource limits, disruption budgets,
  graceful termination, network policies and finite routing/capacity configuration.
- **FR-OPS-02**: Provide KEDA autoscaling aligned with Kafka partitions and independent
  REST demand for ingestion, and scheduling delay/capacity for Workers. One scaling owner
  per deployment; production minimum two replicas and no baseline scale-to-zero.
- **FR-OPS-03**: Gate supported Worker Deployment Version use on SDK/server capability;
  retain pinned versions, replay fixtures and keys, and provide rollout/rollback/rotation
  and recovery runbooks. Version promotion is an external operator release step.
- **FR-OPS-04**: Lock supported dependencies and provide unit, time-skipping Workflow,
  real-service integration, encrypted history replay, security, load and lifecycle evidence.

## Key Entities

- Start intent: validated UUID, tenant/domain/type and canonical business payload; shared
  by API and event ingress and independent of transport retry metadata.
- Route: immutable resolved namespace/queue/output-topic binding and versioned config.
- Execution reference: namespace, Workflow ID, run ID, status and protected request memo.
- Encrypted Payload: authenticated versioned envelope carrying a serialized original
  Temporal Payload, key ID and cryptographic material.
- Partition state: assignment epoch, contiguous completed watermark and bounded retry state.
- Publish receipt: stable logical publish ID and acknowledged topic/partition/offset.
- DLQ record: sanitized source coordinates, deterministic ID and bounded reason code.

Exact schemas and invariants are in [data-model.md](data-model.md) and [contracts](contracts/).

## Edge Cases

| Condition | Required behavior |
|---|---|
| Missing/null/non-UTF-8 key or mismatched event ID | Sanitized DLQ, then commit only on delivery ack |
| Same ID reused after success/failure | Matching retained request is duplicate; changed request is conflict |
| Server accepted start but response lost | Retry same ID; describe/reconcile before acknowledging |
| Duplicate verification memo absent/undecodable | Never assume success; conflict for invalid identity, retry for dependency failure |
| Completed history expired or deleted | Dedup no longer guaranteed; follow replay/retention policy |
| Route changes during replay | Preserve namespace binding; validate memo route; do not silently move IDs |
| DLQ unavailable | No source commit; pause/retry and alert |
| DLQ ack followed by crash before commit | Repeated DLQ record possible; stable ID enables dedup |
| Activity published but completion response lost | Repeated business event possible; stable publish ID enables dedup |
| Rebalance during slow start | No stale-epoch commit; new owner reconciles retained ID |
| Key/certificate invalid or expired | Fail startup or dependency readiness; no plaintext/TLS downgrade |
| Unknown Workflow type/queue | Reject before start; never invoke arbitrary uploaded code |
| Large/deep/invalid JSON | Reject before encryption/start; no object-storage feature invented |
| Failed/canceled/timed-out Workflow result requested | Return terminal state and bounded sanitized error, no stack |
| Scale down with in-flight Activities | Drain within grace; recover via Temporal timeout/retry if interrupted |
| Monitoring unavailable | Application remains safe; autoscaling fallback/minimum and alerts apply |

## Success Criteria

- **SC-01**: Both roles deploy from the same immutable image and the documented reference
  flow passes through API and Kafka to an acknowledged publish and completed Workflow.
- **SC-02**: All conflict/crash/rebalance tests show zero skipped source offsets and zero
  unintended second starts within the configured retained-history window.
- **SC-03**: Sensitive sentinels never appear in inspected history payloads/failure fields,
  captured logs/traces/metric labels or DLQs; tampering and wrong-tenant attempts are rejected.
- **SC-04**: Old encrypted history replays after a key rotation and a compatible/versioned
  release; incompatible replay blocks promotion; no secret is present in built images.
- **SC-05**: On the qualification profile in `verification.md` (100 starts/s for 15 minutes,
  300/s burst for 60 seconds, four tenants, eight partitions, four routes, 1 KiB payload,
  one approximately one-second Activity), API acceptance p95 is at most 500 ms, steady Kafka
  ingest lag p95 at most 5 seconds and task scheduling p95 at most 2 seconds. Report actual
  pod resources, replicas, external quotas, throughput and error rates; these are release
  targets, not an asserted capacity guarantee.
- **SC-06**: Valid unique starts have at least 99.9% confirmed success during the healthy
  sustained qualification interval; injected failures are measured separately. Resource
  usage stays within limits with no unbounded buffers, event-loop blocking or OOM restart.
- **SC-07**: SIGTERM drains within 90 seconds under the qualification workload and all
  unacknowledged/retryable work recovers; pod termination grace is at least 120 seconds.
- **SC-08**: Every mandatory requirement maps to implementation tasks and verification
  evidence; task checkboxes remain unchecked until implementation acceptance passes.

## Assumptions and explicit defaults

1. Infrastructure teams provide reachable supported Temporal/Kafka, preprovisioned tenant
   namespaces/topics, OIDC issuer/JWKS, secret mounts, monitoring and TLS ingress.
2. One configured Temporal endpoint is used per process; one namespace per tenant is the
   isolation baseline. Ingestion has at most 16 namespace clients; each Worker deployment
   selects one namespace and at most four queues. Increase only after qualification.
3. Opaque IDs are canonical lower-case UUIDs; no PII in tenant/domain slugs. Topic ACLs
   enforce approved producers; one topic binding supplies a trusted tenant context.
4. REST clients generate UUIDs and reuse them for retries. This deliberately strengthens
   the original server-generated UUID proposal, which cannot reconcile a lost response.
5. Production retention defaults to 30 days of closed history with Kafka replay limited
   to seven days. Operators must enforce and document a sufficient window, including
   long-running open executions, DLQ replay and archival/restore. Archives alone do not
   provide live duplicate rejection. Retention must cover actual replay/incident delays.
6. Key material is mounted from an external secret system; `KMS_ENCRYPTION_KEY` is a
   deprecated local-test compatibility input, never a production key-in-environment pattern.
7. No runtime deployment is performed by this specification package. Environment-specific
   values are validated operator inputs, not unresolved product behavior.
