# Research and architecture decisions

**Feature:** `001-enterprise-workflow-platform`  
**Research date:** 2026-10-01  
**Audience:** AI code generator and platform engineering team  
**Status:** specification evidence; no application has been implemented or benchmarked

This document distinguishes **documented facts** from **project decisions**. Temporal documentation and its generated API reference describe current behavior and can change independently of the dependency selected for this application. The implementation must verify the selected SDK against the exact deployed service; a documentation lookup does not establish runtime compatibility. These decisions apply to one repository, one container image and exactly two application roles: `INGESTION` and `WORKER`. Temporal Service, Kafka, Prometheus, Kubernetes, KEDA and the organization's identity/secrets infrastructure are external dependencies.

## R-01 — Data conversion and encryption

**Documented fact.** Temporal separates Python-value serialization from payload transformation. A `PayloadCodec` transforms protobuf `Payload` objects through asynchronous `encode` and `decode` methods. Both accept `Sequence[Payload]` and return `list[Payload]`; input objects must not be mutated. [Python data handling](https://docs.temporal.io/develop/python/data-handling), [PayloadCodec API](https://python.temporal.io/temporalio.converter.PayloadCodec.html). Retrieved 2026-10-01.

**Decision.** Keep business models in a typed payload converter and encrypt each fully serialized original `Payload`, including its original metadata, inside a replacement `Payload`. The replacement has only a public codec discriminator; its data carries a versioned, authenticated envelope. Preserve sequence ordering and cardinality, including an empty sequence. Configure the same converter factory on every authorized client, worker, test client and replayer. No module may construct an unprotected production client.

**Rejected approach.** A codec that takes business dictionaries or returns raw bytes is incompatible with the SDK contract. Encrypting only `payload.data` while dropping the original metadata breaks deserialization for non-JSON payloads and may expose metadata. Use the contract in [security.md](security.md#sec-payload--authenticated-payload-protection).

## R-02 — Failures need separate protection

**Documented fact.** `DefaultFailureConverter(encode_common_attributes=True)` moves the exception message and stack trace to failure encoded attributes, where a payload codec can protect them. The SDK provides `DefaultFailureConverterWithEncodedAttributes`. [DefaultFailureConverter API](https://python.temporal.io/temporalio.converter.DefaultFailureConverter.html), [encoded attributes converter API](https://python.temporal.io/temporalio.converter.DefaultFailureConverterWithEncodedAttributes.html). Retrieved 2026-10-01.

**Decision.** Require encoded common attributes, including nested failure causes, and test raw persisted history for synthetic sensitive markers. Error type names, retry classifications and public error codes must be approved constants. API responses and structured logs never expose `str(exception)`, exception arguments or unrestricted stack locals. Encryption is not a substitute for logging redaction.

## R-03 — Cryptography and key lifecycle

**Documented fact.** The `cryptography` AESGCM interface supports AES-256, authenticates additional data, appends a 16-byte tag and raises `InvalidTag` when integrity checks fail. A nonce must not be reused with the same key; 96-bit IVs are recommended. [AESGCM reference](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM). Temporal recommends namespace/environment separation, secure key storage and retaining keys needed for old histories. [Temporal key management](https://docs.temporal.io/key-management). Retrieved 2026-10-01.

**Decision.** AES-256-GCM uses a 32-byte data key, a fresh 12-byte operating-system random nonce and an untruncated 16-byte tag per payload. Authenticated additional data binds an immutable format/version, algorithm, key ID and configured namespace scope. A mounted keyring holds one active encryption key and retained decrypt-only keys. The application does not build a KMS service or call KMS from Workflow code. A `KeyProvider` boundary permits a later wrapped-DEK adapter; v1 implements the mounted provider. The misleading legacy `KMS_ENCRYPTION_KEY` name, if accepted, is a development-only base64 data key and is rejected in production.

**Consequence.** Random nonces make collisions extremely unlikely, not mathematically impossible. Rotation limits must account for all pods using a key; per-process counters cannot establish a durable fleet-wide usage count. Operators need a conservative key lifetime and aggregate usage budget before production. Keys remain available for running workflows, retention, archival/restore and replay needs.

## R-04 — mTLS is mutual authentication plus server validation

**Documented fact.** Current `TLSConfig` exposes client certificate/private-key bytes, a server root CA and server-name settings. Client certificate and private key must be supplied together. `domain` influences SNI/authority and the default verification name; `verification_server_name` changes only the certificate verification name and requires a configured root CA. [TLSConfig API](https://python.temporal.io/temporalio.client.TLSConfig.html). Retrieved 2026-10-01.

**Decision.** Read mounted certificate/key files at bootstrap, validate the configured trust material and connect through the standardized builder. Production has no insecure flag, no disable-verification switch and no silent fallback after TLS errors. Prefer the endpoint DNS name that matches the certificate. An explicitly configured verification name is permitted only when the pinned SDK supports it and the trust/hostname integration tests pass. Namespace access is constrained by Temporal-side authorization as well as application route authorization.

## R-05 — Determinism is an application invariant

**Documented fact.** Workflow execution reconstructs state through deterministic replay. Python workflows have replay-safe APIs for time, UUIDs, randomness and logging. The sandbox reduces risk but is not a security boundary or a complete determinism proof. [Workflow basics](https://docs.temporal.io/develop/python/workflows/basics), [Workflow definition](https://docs.temporal.io/workflow-definition), [Python sandbox](https://docs.temporal.io/develop/python/best-practices/python-sdk-sandbox). Retrieved 2026-10-01.

**Decision.** Workflow modules never read settings, certificates, files or secrets; never construct network clients; never publish Kafka records; and never read wall-clock time. Registry resolution and routing occur before workflow start. Inputs carry the validated workflow contract and bounded policy values. All external I/O and nondeterministic business work occurs in Activities. Keep the sandbox enabled. Approved passthrough imports contain deterministic models or Activity references, not runtime initialization.

**Telemetry rule.** A Workflow interceptor must not introduce wall-clock timers, shared mutable state or exporters into replay. Workflow duration uses workflow time or server/SDK metrics; actual Activity-attempt duration uses a monotonic clock outside Workflow code. Replay suppression controls telemetry only and never changes business commands. Context is restored in `finally` to prevent cross-execution leakage.

## R-06 — Activities have deadlines, retries and cancellation contracts

**Documented fact.** Activity invocation requires Start-to-Close or Schedule-to-Close. Schedule-to-Close covers the execution budget; Start-to-Close covers an attempt. Activity retries are enabled by default. Cancellation is delivered through heartbeat responses and may be delayed by SDK throttling. [Python Activity timeouts](https://docs.temporal.io/develop/python/activities/timeouts). Retrieved 2026-10-01.

**Decision.** Every reusable Activity declares a bounded attempt deadline and a total retry budget. Broker delivery waits have a shorter bounded timeout so cleanup and heartbeat loops can run. Retryable transient transport failures are distinguished from schema, authentication and authorization errors. The reference `publish_event` is an async-safe Activity: a dedicated producer owner thread performs every Confluent operation and sends delivery outcomes through a bounded async bridge; the Activity only awaits bridge futures and runs a heartbeat timer. It contains no synchronous Kafka calls. Heartbeats contain only opaque progress information. It never reports success merely because a producer accepted a record into local memory. Cancellation/timeout leaves a possible external side effect, so the publish contract includes a stable downstream idempotency identity.

**Consequence.** Retries can repeat side effects after acknowledgement loss or process death. Kafka producer idempotence does not establish exactly-once delivery across separate Activity attempts or Kafka-to-Temporal boundaries. Integration tests cover the ambiguous acknowledgement interval.

## R-07 — Blocking libraries need execution boundaries

**Documented fact.** Blocking calls in asynchronous Activities block the worker event loop. Temporal recommends synchronous Activities with an `activity_executor` for blocking libraries; async Activities are appropriate only for async-safe operations. [Python sync/async guidance](https://docs.temporal.io/develop/python/best-practices/python-sdk-sync-vs-async). Retrieved 2026-10-01.

**Decision.** Confluent Kafka produce/poll/delivery processing, synchronous commit and shutdown run in dedicated owner threads, outside the FastAPI/Temporal event loop. Async-to-thread communication is bounded. The consumer and producer each have one owning thread; operations whose ordering affects assignment/offset/delivery safety use that owner. The reference Activity uses only the async bridge; approved synchronous Activity extensions use a bounded worker executor whose capacity covers their configured concurrency. CPU-heavy extensions require a documented executor/process strategy and capacity evidence; they do not run inline in Workflow code.

## R-08 — Metrics belong to Runtime

**Documented fact.** Python SDK metrics are configured using `Runtime`, `TelemetryConfig` and `PrometheusConfig`, then passed to `Client.connect(runtime=...)`. Configure Runtime before a lazily created default runtime. [Python observability](https://docs.temporal.io/develop/python/platform/observability), [PrometheusConfig API](https://python.temporal.io/temporalio.runtime.PrometheusConfig.html). Retrieved 2026-10-01.

**Decision.** Bootstrap a process-scoped runtime before clients/workers. The worker factory accepts this runtime indirectly through its standardized clients; it does not invent a Worker Prometheus option. Both roles expose application `/metrics` and health probes on port 8080. The WORKER role additionally binds the SDK/Core Prometheus endpoint once per process at port 9090. INGESTION does not bind the SDK exporter in v1. Application `prometheus-client` metrics and SDK/Core metrics are separate registries and separate scrape targets; they do not automatically merge. A port has exactly one listener owner. Scrape configuration and NetworkPolicies include the appropriate target for each role.

**Cardinality rule.** Labels are bounded deployment/role/namespace/approved queue/workflow-type/outcome values. Workflow IDs, event IDs, Kafka offsets, trace IDs, arbitrary tenants and error text belong in sanitized logs, never metric labels. JSON logs record relevant workflow/run/activity identity but do not assert that an in-process context variable alone propagates across durable boundaries.

## R-09 — Trace propagation must be replay safe

**Documented fact.** Temporal offers Python tracing integrations. The earlier `TracingInterceptor` is supported; current documentation also describes an experimental OpenTelemetry plugin with a replay-safe provider. [TracingInterceptor API](https://python.temporal.io/temporalio.contrib.opentelemetry.TracingInterceptor.html), [OpenTelemetryPlugin API](https://python.temporal.io/temporalio.contrib.opentelemetry.OpenTelemetryPlugin.html). Retrieved 2026-10-01.

**Decision.** Structured correlation logs are mandatory in v1. Use the pinned SDK's supported interceptor integration when OTLP export is enabled; do not adopt an experimental plugin implicitly. Integration selection is one tested option, never both simultaneously. Accept a valid W3C trace context, create one at the ingestion boundary when absent, and propagate only safe trace/correlation fields through supported client/workflow/activity header hooks. Never derive trace IDs from PII. Propagated context contains no authorization token or arbitrary baggage. Replay/worker-restart tests verify no duplicate business telemetry and correct Activity-attempt correlation.

## R-10 — Payload protection does not hide identity or Visibility

**Documented fact.** Search Attribute names and values are visible and values bypass a custom payload codec. Temporal stores them unencrypted for search. [Search Attributes](https://docs.temporal.io/search-attribute). Retrieved 2026-10-01.

**Decision.** Workflow IDs, namespace and queue names, workflow/activity type names, correlation IDs, Search Attributes, public status, headers and envelope key IDs are non-sensitive by contract. Use only opaque approved identifiers. Reject incoming event keys containing business identity/PII rather than copying them into a Workflow ID. Memo is limited to the encrypted `enterprise_identity_v1` identity record; its business request digest is sensitive and must not appear in public metadata/telemetry. Summaries, headers, metric labels and logging context never contain business payloads. Do not describe the platform as making all data on Temporal Server secret. The precise guarantee is protection of codec-covered payload content and encoded failure common attributes; transport, access control and safe metadata policy protect the remaining surface.

## R-11 — Client lifecycle and routing

**Documented fact.** Temporal Python clients select a namespace when connecting and support `start_workflow` separately from awaiting workflow completion. [Client API](https://python.temporal.io/temporalio.client.Client.html). Retrieved 2026-10-01.

**Decision.** Maintain a bounded, process/event-loop-scoped client registry keyed by approved Temporal namespace, credential profile and startup certificate snapshot. Credential profiles come from the trusted path-only `CREDENTIAL_PROFILES_PATH` configuration; route records hold references, not secrets. Bootstrap it once and inject it into services and worker factories. Certificate/key/profile rotation uses rolling process restart; v1 has no in-process client or secret rotation. A singleton only works for one configured namespace and event loop; global mutable clients must not leak between pytest loops or forks. Use immutable approved domain-to-namespace/task-queue routes. Caller input never selects arbitrary queues or namespaces. Route bindings remain fixed through the supported deduplication window; namespace/queue migration requires an explicit migration design. `start_workflow` is awaited only for the service's acceptance response; the request path never awaits workflow completion.

## R-12 — History growth and replay tests

**Documented fact.** Continue-as-New keeps Workflow ID, starts a new Run ID and history, and accepts carried-forward state. Python exposes a suggestion API for history limits. `Replayer` accepts a data converter, namespace and interceptors. [Python Continue-as-New](https://docs.temporal.io/develop/python/workflows/continue-as-new), [Replayer API](https://python.temporal.io/temporalio.worker.Replayer.html). Retrieved 2026-10-01.

**Decision.** The bounded reference workflow completes without an unbounded event loop. Extension guidelines require Continue-as-New for stateful looping workflows before their documented budget or SDK suggestion. State passed forward is typed, bounded and encrypted; handlers must finish before continuation. Checked-in histories contain synthetic data only. Replay uses the same converter, namespace scope, registered Workflow types and compatible interceptors as production; the default `ReplayNamespace` and unencrypted default converter are unsuitable for scoped encrypted histories. Each key/cipher-envelope migration has historical decryption/replay fixtures.

## R-13 — Deployment versioning and compatibility gate

**Documented fact.** Temporal recommends Worker Versioning for supported deployments and replay testing for code changes. Current Python configuration uses `WorkerDeploymentConfig` with `WorkerDeploymentVersion` and `VersioningBehavior`. The current guide lists Python SDK 1.11+, and for self-hosted versioning Temporal Server 1.29.1+ and CLI 1.4.1+. Eager workflow start does not respect Worker Versioning. [Worker Versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning), [configure versioned Worker](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning/configure-worker), [safe deployments](https://docs.temporal.io/develop/safe-deployments). Retrieved 2026-10-01.

**Decision.** Production targets current Worker Deployment Version APIs with the reference Workflow explicitly pinned. Each release uses an immutable image digest and unique build ID; retain older Worker deployments while executions remain assigned to them. Disable eager start. A release capability gate checks the selected service/SDK combination, worker version registration, routing, drain status and rollback before promotion. Do not use legacy build-ID compatibility APIs as the production baseline. Unsupported versioning is an explicit installation decision with a tested patching/replay-compatible deployment procedure, never an automatic silent downgrade. This application does not install a separate Worker Controller.

**Verification.** CI replays representative synthetic open/closed/failure/cancellation histories using the proposed image before rollout. Deploy new workers without retiring assigned old workers; verify readiness and pollers; run synthetic canary; then ramp/promote through external platform tooling. Rollback routing affects new executions; do not assume it migrates already pinned executions. Retirement requires reachability/drain evidence plus the organization's replay/reset retention policy. These are deployment operations on the same image/WORKER role, not a third application role.

## R-14 — Dependency pinning is a deliverable

**Documented fact.** Temporal's official release page marks Python SDK `1.34.0` as the latest stable release during this research; its release notes were published on 2026-09-30. [SDK Python 1.34.0 release](https://github.com/temporalio/sdk-python/releases/tag/1.34.0). Temporal's index warns that current docs require compatibility verification for older SDKs. [Documentation index](https://docs.temporal.io/llms.txt). Retrieved 2026-10-01.

**Decision.** Use `temporalio==1.34.0` as the researched candidate, not as an assertion of a passing build. The implementation's initial compatibility task selects and locks exact runtime/dependency versions and image digest. The minimum supported Python is 3.11; one exact production minor/patch and OS/architecture are the release target. Lock FastAPI, Pydantic/Pydantic Settings, Confluent Kafka/librdkafka, cryptography, logging, tracing and test tools with transitive dependencies. No `latest` image tag or broad `>=` production install. Record the SDK/API/service/CLI/KEDA matrix, license and dependency-vulnerability evidence, and a reason for any candidate change. Existing histories must replay after every dependency/runtime upgrade.

## R-15 — Test servers do not validate production transport or scale

**Documented fact.** `WorkflowEnvironment` supports local and time-skipping tests; time skipping does not advance while Activities run. `ActivityEnvironment` can observe heartbeats. [Python testing](https://docs.temporal.io/develop/python/best-practices/testing-suite). Retrieved 2026-10-01.

**Decision.** Test each layer separately: settings/codec/failure conversion; routing/start semantics; real WorkflowEnvironment execution; Kafka offset/rebalance/duplicate failure injection; a TLS-enabled Temporal integration target; encrypted raw-history inspection; Kubernetes readiness/drain; and a repeatable load profile. A dummy workflow succeeding is necessary but insufficient. CI must cache/pin the local/test server binary and run required integration jobs explicitly. If a time-skipping binary is unavailable for an architecture, run full local-server timing tests instead; do not skip required coverage silently. Throughput and recovery objectives in the spec are acceptance targets to measure, not claims established by these documents.

## Implementation evidence checklist

Before marking a capability complete, attach concrete evidence to the task result:

| Concern | Required evidence |
|---|---|
| Codec | Multi-format/multi-payload round-trip; metadata preservation; tamper rejection; strict decode; empty-sequence behavior |
| Failures | Sensitive exception message/stack/details absent from raw history; authorized client can decode nested causes |
| Rotation | New ciphertext uses new key ID; old running/completed history decodes and replays; missing key fails safely |
| Transport | Valid mTLS works; unknown CA, wrong hostname, missing pair, expired/rejected client certificate fail |
| Replay | Production-equivalent converter/interceptors; representative histories; deliberate nondeterministic change fails |
| Versioning | Registration, synthetic pin, compatible ramp, drain and rollback on selected service/SDK combination |
| Activity execution | Correct retry classifications; bounded delivery wait; heartbeat/cancellation; duplicate-safe downstream contract |
| Metrics | Application families at 8080 both roles; SDK families at 9090 WORKER only; one listener per port; bounded labels |
| Ingestion | Never commit unresolved offsets; crash-after-start replay; assignment-loss safety; identity/content mismatch handling |
| Deployment | Same image starts both roles; secure manifests; readiness and graceful drain; measured capacity/recovery |

## Limits and decisions deferred to the installation

The core application deliberately excludes Temporal Server hosting, Kafka cluster administration, a new persistent database, a workflow designer UI, a tenant provisioning service and cloud-specific KMS adapters. The installation supplies approved namespace routes, certificates, keyring provisioning/retention, broker ACLs and external identity credentials. Capacity measurements must select concrete replica/resource limits and key rotation lifetime. These installation values do not change the specified behavior or permit weakening the security and delivery guarantees.
