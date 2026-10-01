# Superseded Task Reference: Initial Monolithic Breakdown

This backlog is retained for provenance only. It has been replaced by the 16 micro-level
feature packages in [roadmap.md](roadmap.md). Do not execute these old global IDs.
The feature-local task files are the canonical AI feed. No original task was implemented.

Feature: `001-enterprise-workflow-platform` | Status: Specification backlog; none implemented  
Inputs: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md),
[security.md](security.md), [operations.md](operations.md), [verification.md](verification.md), contracts.

In the original outline, tasks were intended in numeric order. Dependencies state the minimum prerequisite set; numeric
order is the safe default for sequential AI feeds. Every task is part of the same program.
No parallel markers are used because the requested handoff is sequential. One task means
one bounded behavior and its smallest meaningful verification, not an entire subsystem.
If a task exceeds one reviewable change, split it using suffixes (for example T040a/T040b),
retain traceability and update dependents before continuing.

For each task the generator MUST read the cited requirement/design section, implement
only the named behavior, run the corresponding test command from `verification.md` and
report changed files, pass/fail/blocked evidence and remaining risk. Mark `[x]` only when
acceptance passes. Mocks cannot satisfy real-service/staging acceptance. Paths below are
future implementation paths relative to repository root, not files already generated.

## Phase 1 — Setup and foundations

- [ ] T001 Verify the selected Python/Temporal SDK API and supported platform in `docs/compatibility.md` and `tests/unit/test_sdk_api.py`.
  - Depends: none. Requirements: FR-OPS-04, FR-WF-05. Verify: V-001, V-020, V-028.
  - Accept: lock a supported SDK candidate after checking converter, TLS, client start policies, Runtime metrics, Worker deployment/versioning, Replayer and wheel/test-server APIs; record any capability exception explicitly.
- [ ] T002 Create the package scaffolding and pytest configuration in `app/`, `tests/` and `pyproject.toml` using the plan's exact layout.
  - Depends: T001. Requirements: FR-CORE-01, FR-CORE-02. Verify: V-001.
  - Accept: both role names parse; all packages import without opening network connections or initializing secrets; no conflicting client.py/worker.py beside packages.
- [ ] T003 Resolve exact runtime/dev dependencies and hash locks in `requirements.in`, `requirements.txt`, `requirements-dev.txt`.
  - Depends: T002. Requirements: FR-OPS-04. Verify: V-030.
  - Accept: fresh Linux environment installs with required hashes; dependency integrity and supported Python version are recorded; no unbounded/latest versions.
- [ ] T004 Add contract validation tooling in `scripts/verify-contracts/` and `tests/unit/test_contracts.py`.
  - Depends: T003. Requirements: FR-CORE-03, FR-API-01, FR-KAFKA-01. Verify: V-001, V-011.
  - Accept: OpenAPI and all JSON schemas validate; routing example passes; invalid examples fail; contract changes are detected by CI.
- [ ] T005 Implement typed role-specific settings in `app/config/settings.py` and `tests/unit/test_settings.py`.
  - Depends: T003. Requirements: FR-CORE-03. Verify: V-001.
  - Accept: every plan setting has a finite validated default/constraint; missing production TLS/keyring fails, legacy KMS_ENCRYPTION_KEY is local/test only, diagnostics redact secrets.
- [ ] T006 Implement route-file parsing and cross-record invariants in `app/config/routing.py` and `tests/unit/test_routing.py`.
  - Depends: T004, T005. Requirements: FR-ROUTE-01, FR-ROUTE-02, FR-ROUTE-03. Verify: V-008.
  - Accept: route/tenant/broker/Worker bindings are consistent, one namespace per tenant, selected clients<=16, consumer bindings<=16, Worker queues<=4; caller queue/type/topic injection is rejected.
- [ ] T007 Implement path-only credential profile resolution in `app/config/credentials.py` and `tests/unit/test_credentials.py`.
  - Depends: T005, T006. Requirements: FR-SEC-04, FR-SEC-07, FR-CORE-03. Verify: V-001, V-006.
  - Accept: selected Temporal/Kafka profile resolves allowed mounted cert/CA/key/secret files; role credentials remain least privilege; multi-profile mapping contains no key/password values.

## Phase 2 — US1: Security and tenant isolation

- [ ] T008 Implement startup keyring snapshots in `app/config/key_provider.py` and `tests/unit/test_key_provider.py`.
  - Depends: T007. Requirements: FR-SEC-03. Verify: V-004.
  - Accept: SEC-KEYS manifest enforces namespace maps/size/count bounds,32-byte unique keys and active encrypt_not_after; expired active key fails writes/readiness, retained expired keys decode, no cross-scope reuse or per-task KMS calls.
- [ ] T009 Implement full-Payload AES-GCM codec envelopes in `app/temporal/converter.py` and `tests/unit/test_codec_roundtrip.py`.
  - Depends: T008. Requirements: FR-SEC-01, FR-SEC-03. Verify: V-002.
  - Accept: async Sequence[Payload] roundtrip preserves original protobuf/data/metadata, uses namespace-scoped AAD and random12-byte nonce, never mutates input and enforces encoded-size bounds.
- [ ] T010 Add codec corruption and cross-key tests in `tests/unit/test_codec_rejection.py`.
  - Depends: T009. Requirements: FR-SEC-02, FR-SEC-03, FR-SEC-06. Verify: V-003, V-004.
  - Accept: altered AAD/nonce/tag/ciphertext, unknown versions/keys/scopes, malformed or oversized envelope and plaintext input all fail closed without leaked values.
- [ ] T011 Assemble the typed DataConverter and protected FailureConverter in `app/temporal/converter.py` and `tests/unit/test_failure_converter.py`.
  - Depends: T010. Requirements: FR-SEC-01, FR-SEC-02. Verify: V-005.
  - Accept: failure message/stack move into encrypted common attributes, visible error types are allowlisted, client and Worker share the exact converter factory.
- [ ] T012 Build verified production Temporal TLS configuration in `app/temporal/client/builder.py` and `tests/unit/test_tls_config.py`.
  - Depends: T007, T011. Requirements: FR-SEC-04. Verify: V-006.
  - Accept: mounted cert/key/CA and verified server identity configure the pinned SDK; absent trust/client identity or production insecure override cannot connect.
- [ ] T013 Implement bounded atomic namespace/profile client caching in `app/temporal/client/builder.py` and package exports.
  - Depends: T012. Requirements: FR-ROUTE-04, FR-ROUTE-03. Verify: V-001, V-008.
  - Accept: concurrent same-route calls initialize one compatible client, no cross-loop sharing, no more than16 clients; every client includes converter, TLS and supported interceptors/runtime hooks.
- [ ] T014 Implement bounded OIDC JWT/JWKS verification in `app/api/auth.py` and `tests/unit/test_oidc.py`.
  - Depends: T005. Requirements: FR-SEC-05. Verify: V-007.
  - Accept: signature/algorithm/issuer/audience/time checks and bounded refresh/cache pass; token-controlled URL/algorithm cannot drive trust; missing/invalid tokens fail safely.
- [ ] T015 Implement tenant/scope authorization and concealed read denial in `app/api/auth.py` and `tests/unit/test_authorization.py`.
  - Depends: T006, T014. Requirements: FR-SEC-05, FR-SEC-06, FR-ROUTE-02. Verify: V-008.
  - Accept: starts require tenant grant and start scope, result reads require read/result scope; cross-tenant lookup returns contract404 without querying unauthorized execution.
- [ ] T016 Add sensitive-data boundary fixtures and regression tests in `tests/unit/test_privacy_policy.py`.
  - Depends: T010, T011, T015. Requirements: FR-SEC-06, FR-SEC-07. Verify: V-003, V-005, V-007.
  - Accept: representative logs/errors/headers/memo metadata/Search Attribute policies contain no synthetic sensitive sentinel or secret; full raw-history integration remains T061.

## Phase 3 — US2: Durable Workflow and standardized Worker

- [ ] T017 Implement versioned durable input/result models and static registry in `app/temporal/models.py`, `registry.py` and model/registry unit tests.
  - Depends: T004, T006. Requirements: FR-WF-01, FR-WF-05. Verify: V-008, V-019.
  - Accept: WorkflowInput wraps StartIntent and immutable namespace/queue/output-topic/revision snapshot; EnterpriseEventWorkflow/publish_event are approved, unknown definitions fail and serialization is sandbox/replay compatible.
- [ ] T018 Implement a bounded producer callback bridge in `app/events/producer.py` and `tests/unit/test_producer_bridge.py`.
  - Depends: T007. Requirements: FR-KAFKA-05, FR-WF-04. Verify: V-016, V-017.
  - Accept: one owning poll thread per selected producer services callbacks, safely resolves asyncio futures and propagates fatal errors; event loop never executes blocking flush/poll.
- [ ] T019 Implement confirmed Kafka delivery, finite buffer waits and idempotent producer config in `app/events/producer.py`.
  - Depends: T018. Requirements: FR-WF-03, FR-WF-04. Verify: V-017.
  - Accept: enqueue cannot report success; ack/error/deadline each settle once, BufferError stays bounded, acks=all/enable.idempotence validated and stable event key supplied.
- [ ] T020 Implement injected-resource `publish_event` in `app/temporal/activities/system_activities.py`.
  - Depends: T017, T019. Requirements: FR-WF-01, FR-WF-03, FR-WF-04. Verify: V-018.
  - Accept: only allowlisted route topics publish; typed receipt returned after ack, bounded heartbeats while waiting, cancellation re-raised and no per-attempt client creation.
- [ ] T021 Test publish Activity heartbeat, terminal errors and cancellation in `tests/unit/test_publish_activity.py`.
  - Depends: T020. Requirements: FR-WF-03, FR-WF-04. Verify: V-017, V-018.
  - Accept: ActivityEnvironment observes expected heartbeat/cancellation and stable publish ID across attempts; producer failure never returns a receipt.
- [ ] T022 Implement deterministic reference Workflow in `app/temporal/workflows/enterprise_event_workflow.py`.
  - Depends: T017, T021. Requirements: FR-WF-01, FR-WF-02, FR-WF-03. Verify: V-019.
  - Accept: constructs workflow.processed event and '<workflow_id>:publish:0', schedules one Activity with explicit retry/deadline/cancellation options and returns acknowledged receipt.
- [ ] T023 Test reference Workflow with independent codecs in `tests/workflow/test_enterprise_event_workflow.py`.
  - Depends: T011, T022. Requirements: FR-WF-02, FR-WF-03, FR-SEC-01. Verify: V-019.
  - Accept: real SDK WorkflowEnvironment success, transient retry, permanent failure and cancellation pass with sandbox imports and converter actually exercised.
- [ ] T024 Implement EnterpriseWorker construction in `app/temporal/worker/factory.py` and package exports.
  - Depends: T013, T023. Requirements: FR-WF-05, FR-ROUTE-03. Verify: V-001, V-019.
  - Accept: one selected namespace/up to4 queues, approved registrations, finite task/cache limits, required sync executor and compatible concurrency options; metrics supplied by Runtime, not invalid Worker arguments.
- [ ] T025 Test Worker factory bounds and registration behavior in `tests/unit/test_worker_factory.py`.
  - Depends: T024. Requirements: FR-WF-02, FR-WF-05, FR-CORE-03. Verify: V-001, V-019.
  - Accept: invalid queues/types/executor/tuner combinations fail early; one valid test Worker executes without unsafe Workflow imports.
- [ ] T026 Add Worker Deployment Version configuration and authoring guidance in `app/temporal/worker/factory.py` and `docs/workflow-authoring.md`.
  - Depends: T001, T025. Requirements: FR-WF-05, FR-WF-06, FR-OPS-03. Verify: V-020, V-028.
  - Accept: baseline PINNED and immutable build identity configure verified APIs, eager start disabled; documented fallback requires replay/patch compatibility and capability exception; schema/Continue-As-New guidance is concrete.
- [ ] T027 Generate representative synthetic encrypted history fixtures in `tests/fixtures/histories/` with a controlled fixture-key source.
  - Depends: T026. Requirements: FR-SEC-03, FR-WF-05. Verify: V-004, V-020.
  - Accept: fixtures cover success/retry/failure and supported old schema/key paths, record namespace/version, contain no production data or committed real keys.
- [ ] T028 Add encrypted-history replay runner and negative control in `tests/replay/test_histories.py`.
  - Depends: T027. Requirements: FR-WF-02, FR-WF-05, FR-OPS-04. Verify: V-020.
  - Accept: all approved histories replay with converter/namespace/old keys; intentionally incompatible code fails; replay cannot emit broker side effects.

## Phase 4 — US3: Retry-safe REST ingestion

- [ ] T029 Implement strict canonical start-intent digest in `app/temporal/client/start_service.py` and `tests/unit/test_start_identity.py`.
  - Depends: T017. Requirements: FR-ING-01, FR-ING-02, FR-SEC-06. Verify: V-009, V-011.
  - Accept: RFC8785-compatible REST/Kafka content yields same digest, retry metadata excluded; duplicate keys/nonfinite/unsafe numbers/lone surrogates/depth overflow rejected.
- [ ] T030 Implement bounded shared start RPC with explicit ID policies and encrypted memo in `app/temporal/client/start_service.py`.
  - Depends: T013, T026, T029. Requirements: FR-ING-01, FR-ING-03. Verify: V-009.
  - Accept: exact UUID ID, FAIL/REJECT_DUPLICATE, immutable route/digest memo and configured deadlines used; no completion wait or automatic ID replacement.
- [ ] T031 Implement existing/ambiguous execution reconciliation in `app/temporal/client/start_service.py`.
  - Depends: T030. Requirements: FR-ING-02, FR-ING-04. Verify: V-009.
  - Accept: describe/memo proves matching identity+binding before duplicate; mismatch conflict; unavailable evidence retryable; unrelated route revision/trace change does not conflict.
- [ ] T032 Test start concurrency, identity conflicts and ambiguous outcomes in `tests/unit/test_start_service.py`.
  - Depends: T031. Requirements: FR-ING-01, FR-ING-02, FR-ING-03. Verify: V-009.
  - Accept: known exception paths map typed outcomes, deadline reconciliation does not claim unknown starts accepted and no local cache is relied on for durability.
- [ ] T033 Implement HTTP request/response models and POST handler in `app/api/models.py`, `app/api/main.py`.
  - Depends: T015, T032. Requirements: FR-API-01. Verify: V-009.
  - Accept: mandatory UUID header, authorization before route/start, contract202/200/conflict/errors, Idempotent-Replayed/Location fields and same Workflow ID returned.
- [ ] T034 Implement bounded authorized status/result handler in `app/api/main.py`.
  - Depends: T033. Requirements: FR-API-02, FR-SEC-05. Verify: V-010.
  - Accept: tenant/domain resolution, optional specific run, latest chain run when omitted, describe-first state, completed-result-only fetch and sanitized terminal errors; no wait for running result.
- [ ] T035 Add HTTP body/depth/deadline/admission/rate bounds and no-store errors in `app/api/main.py`.
  - Depends: T034. Requirements: FR-API-03, FR-SEC-06. Verify: V-007, V-010, V-016.
  - Accept: oversized/chunked bodies bounded before full buffering,429 Retry-After for saturation, bounded tenant buckets and safe request IDs; failed requests release admission slots.
- [ ] T036 Test API auth/contract/status/privacy with ASGI client in `tests/unit/test_api.py`.
  - Depends: T035. Requirements: FR-API-01, FR-API-02, FR-API-03. Verify: V-007, V-008, V-009, V-010.
  - Accept: all declared normal/error statuses and tenant concealment pass; wrong-tenant request never reaches start/result client; running GET stays within deadline.
- [ ] T037 Verify generated OpenAPI against the committed contract in `tests/unit/test_openapi_compatibility.py`.
  - Depends: T036. Requirements: FR-API-01, FR-API-02. Verify: V-030.
  - Accept: route schemas/security/status/header contract matches; internal Worker health surface remains separate and no undocumented public operation appears.

## Phase 5 — US4: Kafka ingestion and recovery

- [ ] T038 Implement strict event/key/topic-binding validation in `app/events/models.py` and `tests/unit/test_event_validation.py`.
  - Depends: T006, T029. Requirements: FR-KAFKA-01, FR-KAFKA-03, FR-SEC-05. Verify: V-011.
  - Accept: UUID UTF-8 key exactly matches envelope ID, tenant matches trusted input topic, size/depth/type validation precedes starts and errors contain no body.
- [ ] T039 Implement consumer-owned polling/control bridge in `app/events/bridge.py`.
  - Depends: T007, T038. Requirements: FR-KAFKA-05, FR-KAFKA-01. Verify: V-016.
  - Accept: each selected binding owns one consumer thread, manual storage/commit, bounded shared handoff queues and reserved control capacity; no blocking broker call in asyncio.
- [ ] T040 Implement per-partition assignment generation and one-unresolved-record state in `app/events/consumer.py`.
  - Depends: T039. Requirements: FR-KAFKA-01, FR-KAFKA-04. Verify: V-014, V-016.
  - Accept: assignment epoch fences stale outcomes, bounded pending records and partition pause/resume; polls continue during backpressure/reconciliation.
- [ ] T041 Implement contiguous settled watermark and acknowledged commit commands in `app/events/consumer.py`.
  - Depends: T040. Requirements: FR-KAFKA-02. Verify: V-013.
  - Accept: commit offset+1 only for settled prefix under current ownership; unresolved earlier record blocks advancement; failed/ambiguous commits do not discard records.
- [ ] T042 Implement typed outcome classification and jittered pause/retry in `app/events/consumer.py`.
  - Depends: T031, T041. Requirements: FR-KAFKA-03, FR-KAFKA-04, FR-ING-03. Verify: V-011, V-016.
  - Accept: record validation/conflict can DLQ; credential/service/unknown-start/DLQ outages remain uncommitted retries; other partitions progress and retries remain bounded in memory.
- [ ] T043 Implement metadata-only deterministic DLQ publishing in `app/events/models.py`, `consumer.py`.
  - Depends: T019, T042. Requirements: FR-KAFKA-03, FR-KAFKA-02, FR-SEC-06. Verify: V-015.
  - Accept: source-coordinate identity, allowlisted reason and approved timestamps match DLQ schema; no source settle before broker ack and no raw payload/stack.
- [ ] T044 Connect Kafka coordinator to shared start service in `app/events/consumer.py`.
  - Depends: T043. Requirements: FR-KAFKA-01, FR-ING-01, FR-ING-02. Verify: V-012.
  - Accept: all transport paths use same digest/route/ID semantics; new/verified duplicate settles, conflict DLQs, unknown retries; Workflow completion never awaited.
- [ ] T045 Test commit/retry/rebalance state machine and buffer saturation in `tests/unit/test_consumer_state.py`.
  - Depends: T044. Requirements: FR-KAFKA-02, FR-KAFKA-04, FR-KAFKA-05. Verify: V-013, V-014, V-016.
  - Accept: controlled interleavings show no skipped offset/stale commit, polling stays responsive and no task/queue exceeds configured process bounds.
- [ ] T046 Add real Kafka start-before-commit crash test in `tests/integration/test_ingestion_crash.py`.
  - Depends: T045, T060. Requirements: FR-KAFKA-02, FR-ING-04. Verify: V-012.
  - Accept: failpoint after server ack/before commit causes redelivery and exactly one retained execution; source offset advances only after verified reconciliation.
- [ ] T047 Add real group rebalance and failed commit tests in `tests/integration/test_rebalance.py`.
  - Depends: T045, T060. Requirements: FR-KAFKA-02, FR-KAFKA-04. Verify: V-013, V-014.
  - Accept: multiple ingestion instances with delayed old-owner start/commit never skip offsets; current owner resolves uncertain starts safely.
- [ ] T048 Add DLQ outage/ack-crash test in `tests/integration/test_dlq_recovery.py`.
  - Depends: T045, T060. Requirements: FR-KAFKA-03, FR-SEC-06. Verify: V-015.
  - Accept: unavailable DLQ leaves source uncommitted; ack-crash produces repeat DLQ identity without loss or raw data leakage.
- [ ] T049 Add cross-transport and multi-instance ID tests in `tests/integration/test_idempotency.py`.
  - Depends: T037, T046. Requirements: FR-ING-01, FR-ING-02, FR-ING-04. Verify: V-009, V-012.
  - Accept: REST/Kafka same content/UUID reconciles across pods; changed content conflicts; separate tenant namespace safe; history-expiry boundary documented and observed.

## Phase 6 — US5: Observability and role lifecycle

- [ ] T050 Initialize redacted JSON logging and context binding/reset in `app/observability.py`.
  - Depends: T016. Requirements: FR-OBS-01, FR-SEC-06. Verify: V-021.
  - Accept: standard fields are consistent with safe reason codes; concurrent record/request contexts reset; no payload/token/key/exception-body logging.
- [ ] T051 Implement replay-aware Worker/Activity logging interceptors in `app/temporal/interceptors.py`.
  - Depends: T024, T050. Requirements: FR-OBS-01, FR-OBS-02, FR-WF-02. Verify: V-021.
  - Accept: Activity wall duration/context/attempt recorded, Workflow telemetry uses deterministic/replay-safe SDK facilities; exceptions re-raised and command order unchanged.
- [ ] T052 Wire supported trace propagation into client/Worker and REST/Kafka boundaries in `app/observability.py`, `interceptors.py`.
  - Depends: T051. Requirements: FR-OBS-02, FR-SEC-06. Verify: V-021.
  - Accept: validated traceparent correlates one end-to-end operation; no baggage/PII; unsupported header codec behavior cannot leak sensitive fields; collector failures are bounded.
- [ ] T053 Configure one process Runtime and distinct app/SDK metric exporters in `app/observability.py`, client builder and Worker factory.
  - Depends: T052. Requirements: FR-OBS-03. Verify: V-021.
  - Accept: app metrics8080 both roles; Worker Runtime SDK 9090 once; no duplicate Runtime registry/port collision per queue/client; ingestion does not bind9090.
- [ ] T054 Add bounded business/operational counters, histograms and private health router in `app/observability.py`, `app/api/health.py`.
  - Depends: T053. Requirements: FR-OBS-04, FR-CORE-04. Verify: V-021, V-022.
  - Accept: finite outcome/reason/route labels, no execution IDs; startup/liveness/readiness distinguish init/drain/dependency states with cached bounded checks.
- [ ] T055 Implement supervised INGESTION startup/resources using `app/main.py` and FastAPI lifespan.
  - Depends: T044, T054. Requirements: FR-CORE-01, FR-CORE-04. Verify: V-022.
  - Accept: one Uvicorn process plus bounded selected consumers start once, all critical tasks observed, fatal consumer/HTTP failure tears down role; no detached task.
- [ ] T056 Implement supervised WORKER startup/probe server using `app/main.py`.
  - Depends: T026, T054. Requirements: FR-CORE-01, FR-CORE-04. Verify: V-022.
  - Accept: only selected Worker queues/probe endpoints run, essential Worker failure cancels siblings; no public start/status routes or ingestion consumer in Worker role.
- [ ] T057 Implement SIGTERM admission stop/drain/cleanup deadlines in role supervisors, consumer bridge and Worker factory.
  - Depends: T055, T056. Requirements: FR-CORE-04, FR-KAFKA-05, FR-WF-03. Verify: V-022.
  - Accept: not-ready before stop, eligible current-epoch commits only, producer/executor resources close; normal drain<=90s, hard exit<=110s and unconfirmed work remains recoverable.
- [ ] T058 Add role startup/fatal failure/outage/shutdown integration tests in `tests/integration/test_lifecycle.py`.
  - Depends: T057, T060. Requirements: FR-CORE-01, FR-CORE-04, FR-OBS-03. Verify: V-016, V-022.
  - Accept: no orphan resources, outage does not fail liveness, fatal paths exit nonzero, actual process signals preserve recovery and ports match roles.
- [ ] T059 Add trace/log/metric privacy and replay regression tests in `tests/integration/test_observability.py`.
  - Depends: T058. Requirements: FR-OBS-01, FR-OBS-02, FR-OBS-03, FR-OBS-04. Verify: V-021.
  - Accept: concurrent tenant contexts never leak, replay does not multiply application events, every intended scrape series is observable and no high-cardinality/sensitive labels appear.

## Phase 7 — US6: Deployment and release qualification

T060 is an integration prerequisite. Build its disposable fixture tooling before running
T046–T049 or T058; it does not introduce another production application role. All earlier
unit/Workflow tasks can execute in numeric order without integration credentials.

- [ ] T060 Add a pinned disposable local/CI Temporal+Kafka stack and orchestration commands in `scripts/local-stack/`.
  - Depends: T003, T007. Requirements: FR-OPS-04. Verify: V-005, V-006, V-012.
  - Accept: synthetic namespaces/topics/TLS credentials provision reproducibly without real secrets; real-clock and time-skip environments separated; supported platform/download prerequisites documented.
- [ ] T061 Add raw-history, failure privacy and real mTLS/Kafka TLS negative integration tests in `tests/integration/test_security.py`.
  - Depends: T011, T012, T060. Requirements: FR-SEC-01, FR-SEC-02, FR-SEC-04. Verify: V-005, V-006.
  - Accept: actual server history lacks sensitive sentinel, authorized client decodes it; absent/expired/wrong-host/untrusted/unauthorized credentials fail without downgrade.
- [ ] T062 Add real retried-publish and cancellation recovery tests in `tests/integration/test_publish_recovery.py`.
  - Depends: T021, T060. Requirements: FR-WF-03, FR-WF-04. Verify: V-017, V-018.
  - Accept: ack-before-completion crash can duplicate event with stable publish ID; sink dedups; cancellation/heartbeat and producer delivery deadlines verified with real clocks.
- [ ] T063 Build one reproducible non-root image via `Dockerfile` and `.dockerignore`.
  - Depends: T003, T057. Requirements: FR-OPS-01, FR-SEC-07. Verify: V-023.
  - Accept: both roles launch from same image digest, runtime dependency hashes verified, no keys/test data/build tools/unused caches, read-only root works.
- [ ] T064 Create chart metadata/values schema and separate role Deployments in `deploy/helm/temporal-enterprise-framework/`.
  - Depends: T063. Requirements: FR-OPS-01, FR-CORE-01. Verify: V-023.
  - Accept: one image reference, role-specific command/env/resources, startup/readiness/liveness probes, min 2, PDB/topology and 120s termination grace render and validate.
- [ ] T065 Add mounted credential/keyring/routes and private Services/ServiceMonitors to the chart.
  - Depends: T064. Requirements: FR-SEC-04, FR-SEC-07, FR-OBS-03. Verify: V-023.
  - Accept: externally supplied secret references only, profile scopes correct, public API excludes telemetry, Worker app 8080/SDK 9090 scraped separately; no serviceAccount token by default.
- [ ] T066 Add ingress TLS/auth boundary and least-privilege NetworkPolicy templates.
  - Depends: T065. Requirements: FR-SEC-05, FR-SEC-07. Verify: V-024.
  - Accept: only documented DNS/broker/Temporal/OIDC/OTLP/scrape/probe paths allowed, advertised brokers reachable, CNI/FQDN assumptions explicit; public Worker/metrics inaccessible.
- [ ] T067 Add one INGESTION KEDA ScaledObject with Kafka and REST demand in chart templates.
  - Depends: T066. Requirements: FR-OPS-02. Verify: V-025.
  - Accept: per-binding group/topic demand or tested aggregate, REST headroom and optional idle consumers documented; max/floor and HPA stabilization configured, no competing HPA.
- [ ] T068 Add WORKER scheduling-delay/capacity autoscaling and Prometheus recording rules.
  - Depends: T053, T067. Requirements: FR-OPS-02, FR-OBS-04. Verify: V-025.
  - Accept: actual SDK metric names/units verified, queue/namespace selection bounded, no trigger-topic lag proxy, absent-series fallback retains min 2; scaling response measured.
- [ ] T069 Add chart/schema/admission validation jobs and staging network/probe/scaling tests in `tests/integration/test_kubernetes.py`.
  - Depends: T068. Requirements: FR-OPS-01, FR-OPS-02. Verify: V-023, V-024, V-025.
  - Accept: rendered manifests pass validation and real restricted cluster demonstrates allowed/blocked paths, probe transitions and controlled scaling/drain.
- [ ] T070 Implement versioned Worker rollout/rollback validation tooling in `scripts/qualify/worker-rollout.*` and runbook.
  - Depends: T028, T069. Requirements: FR-OPS-03, FR-WF-05. Verify: V-028.
  - Accept: old pinned runs remain served, new runs route to promoted version, replay-negative change blocks promotion and rollback/retained-version retirement conditions are tested.
- [ ] T071 Add key/certificate rotation and restore checks in `tests/integration/test_rotation.py` and runbook.
  - Depends: T061, T070. Requirements: FR-SEC-03, FR-SEC-04, FR-OPS-03. Verify: V-029.
  - Accept: readers receive old+new keys before writer switch, old encrypted history/result replays, cert rolling renewal works and lost/retired key recovery failure is explicit.
- [ ] T072 Implement healthy workload generator/reporting in `tests/load/` and `scripts/qualify/`.
  - Depends: T062, T069. Requirements: FR-OPS-04. Verify: V-026.
  - Accept: 100 starts/s15min +300/s60s, four tenants/eight partitions/four routes/1KiB/~1s Activity, REST/Kafka/mixed variants, p95/SLO/success/resource evidence and actual hardware/quotas recorded.
- [ ] T073 Add dependency/crash/retention recovery scenarios to qualification tooling.
  - Depends: T049, T071, T072. Requirements: FR-ING-04, FR-KAFKA-04, FR-OPS-03. Verify: V-027.
  - Accept: injected Temporal/Kafka/OIDC/monitoring outages recover without offset loss or unbounded growth; expired history/replay/restore limitation and operator actions verified.
- [ ] T074 Add fast unit/contract/Workflow/replay CI gates in `.github/workflows/ci.yml`.
  - Depends: T028, T037, T045. Requirements: FR-OPS-04. Verify: V-020, V-030.
  - Accept: clean checkout runs locked dependencies and mandatory fast gates; replay fixtures use controlled keys; blocked/skipped required tests cannot report release success.
- [ ] T075 Add real-service, image and rendered-manifest CI gates.
  - Depends: T059, T061, T062, T069, T074. Requirements: FR-OPS-01, FR-OPS-04. Verify: V-005, V-006, V-023, V-030.
  - Accept: relevant paths/releases trigger integration and image gates, synthetic secrets masked, artifact retention/access bounded and dependency failures reported distinctly.
- [ ] T076 Add dashboard/alert artifacts under `docs/dashboards/`.
  - Depends: T059, T068. Requirements: FR-OBS-04. Verify: V-021, V-025.
  - Accept: acceptance/lag/DLQ/commit/scheduling/capacity/key/TLS alerts use actual series and tested sustained thresholds; no business data or execution IDs in labels.
- [ ] T077 Write operator recovery/replay/drain/retention and dependency outage runbooks under `docs/runbooks/`.
  - Depends: T070, T071, T073, T076. Requirements: FR-ING-04, FR-OPS-03. Verify: V-027, V-029.
  - Accept: recovery order, same-ID retries, safe DLQ replay, old key/version retention and manual scaling fallback are concrete; destructive steps require operator review.
- [ ] T078 Replace implementation README with validated build/local/deploy/extension instructions and example configuration.
  - Depends: T063, T077. Requirements: FR-CORE-02, FR-WF-06, FR-OPS-01. Verify: V-030.
  - Accept: new operator reproduces both-role synthetic flow from clean checkout; examples align contracts and contain no secrets; unsupported environments and external prerequisites explicit.
- [ ] T079 Produce requirement-to-evidence release report in `docs/release-acceptance.md`.
  - Depends: T072, T073, T075, T078. Requirements: FR-OPS-04. Verify: V-030.
  - Accept: all FR/SC and V IDs have actual pass evidence or explicit release-blocking result, image/version/resource/load measurements attached; no fabricated proof.
- [ ] T080 Perform cross-artifact convergence and close only verified tasks.
  - Depends: T079. Requirements: FR-CORE-01, FR-OPS-04. Verify: V-030.
  - Accept: contracts/spec/plan/code match, all mandatory v1 gates pass, no scope expansion or unchecked implementation requirement; add small corrective tasks for gaps rather than declaring completion.

## Safe sequential feed order

The integration stack is needed before earlier integration tasks. Execute:

1. T001–T045.
2. T060 (disposable test prerequisites).
3. T046–T059.
4. T061–T080.

This is the canonical order for one-task AI feeds and overrides plain numeric ordering
at the explicit T060 prerequisite. There are no forward dependencies in that order.
Capability phases organize the plan; task order follows the dependency graph.

## Requirement coverage

| Requirements | Owning tasks |
|---|---|
| FR-CORE-01–04 | T002, T005–T007, T055–T058, T063–T065, T078–T080 |
| FR-SEC-01–07 | T007–T016, T029, T035, T038, T043, T050–T052, T061, T065–T066, T071 |
| FR-ROUTE-01–04 | T006–T007, T013, T015, T017, T024–T025 |
| FR-WF-01–06 | T017–T028, T062, T070, T078 |
| FR-ING-01–04 | T029–T032, T044, T046, T049, T073, T077 |
| FR-API-01–03 | T004, T033–T037 |
| FR-KAFKA-01–05 | T018–T019, T038–T048, T057, T073 |
| FR-OBS-01–04 | T050–T054, T059, T065, T068, T076 |
| FR-OPS-01–04 | T001, T003, T026–T028, T060–T080 |
| SC-01–08 | T023, T046–T049, T058–T062, T069–T073, T079–T080 |

## Mapping from the initial task outline

| Original task | Expanded tasks and corrections |
|---|---|
| TASK-1.1 Environment | T005–T008: role validation, route/credentials/keyring bounds |
| TASK-1.2 Encryption | T009–T011: Payload objects/full metadata, protected failures, rotation/tamper tests |
| TASK-1.3 Client | T012–T013: verified mTLS, namespace/profile client pool |
| TASK-2.1 Interceptors | T050–T053: replay safety, context isolation, Runtime exporter |
| TASK-2.2 Worker | T024–T028, T056: registrations, concurrency/versioning/replay |
| TASK-2.3 Publish Activity | T018–T023, T062: delivery ack, heartbeat/cancellation, duplicate effects |
| TASK-3.1 Kafka | T038–T049: message/key identity, commit fences, rebalance/DLQ recovery |
| TASK-3.2 REST | T014–T015, T029–T037: OIDC, retained caller UUID, reconciliation and bounded reads |
| TASK-4.1 Entry point | T055–T058: both-role supervised lifecycle and drain |
| TASK-4.2 Tests | Tests included per task plus T060–T062, T069–T075, T079: real history/TLS/replay/load evidence |
