# Data model and behavioral contracts

This document describes one application, one container image, and two runtime roles: `INGESTION` and `WORKER`. Temporal, Kafka, the OIDC provider, and secret/key provisioning are external services. There is no application database or separately deployed coordinator in this release. Fields and examples are normative unless labeled illustrative.

## Contract files

| Contract | Purpose |
| --- | --- |
| `contracts/openapi.yaml` | OpenAPI 3.1 contract for start, status, health, and metrics |
| `contracts/event-envelope.schema.json` | Draft 2020-12 Kafka start intent |
| `contracts/outbound-event.schema.json` | Draft 2020-12 reference workflow publication |
| `contracts/dlq-record.schema.json` | Draft 2020-12 metadata-only quarantine record |
| `contracts/routing.schema.json` | Draft 2020-12 route configuration shape |
| `contracts/routing.example.yaml` | Illustrative finite route inventory; replace before deployment |

Schema validation is necessary but insufficient. Implement the byte, nesting, identity, authorization, canonicalization, and cross-field checks below. JSON Schema cannot compare Kafka keys to JSON fields, prove grant membership, or enforce byte size and a recursive nesting ceiling.

## Shared primitive types and limits

| Name | Rule |
| --- | --- |
| `message_id`, `workflow_id`, REST `Idempotency-Key` | Lowercase canonical UUID string, supported UUID version 1–8 and RFC variant; opaque, never derived from PII; exactly 36 ASCII characters |
| `run_id` | UUID assigned by Temporal; selects one execution, never substitutes for `workflow_id` |
| `tenant_id`, `domain` | Opaque lowercase slugs, 1–63 characters, start with a letter, hyphen-separated alphanumeric segments; no customer/person identifiers |
| `workflow_type` | Explicit compiled registry allowlist; v1 contains only `EnterpriseEventWorkflow` |
| `namespace`, `task_queue`, Kafka topics | Configuration values only; finite allowlists, non-PII, maximum 128 characters |
| `schema_version` | String `"1"`; reject unknown versions; do not silently coerce integer `1` |
| `payload` | JSON object; JSON arrays and scalars are allowed inside it |
| `traceparent` | Optional W3C version `00` trace context, lowercase, 55 characters; nonzero trace and parent identifiers; treat as untrusted correlation, never authorization |
| Maximum request/event bytes | 262,144 bytes (256 KiB) of UTF-8 JSON, including envelope/request fields; reject before parsing |
| Maximum outbound business bytes | 262,144 bytes of serialized outbound event |
| Maximum encoded Temporal payload | 524,288 bytes (512 KiB) for each encoded Payload, including encryption framing/metadata; fail before RPC |
| Maximum JSON nesting | 32 container levels; top-level object counts as level 1, each nested object/array increments it |
| Business-input JSON parsing | UTF-8 only; reject duplicate property names, lone Unicode surrogates, NaN, infinity, and integer values outside `[-9007199254740991, 9007199254740991]`; finite numbers must fit IEEE 754 binary64; exact money/high-precision values use strings |

Apply the same JSON rules to REST and Kafka before computing a digest. RFC 8785 defines canonical number serialization, UTF-16 property sorting, and preservation of Unicode strings. `json.dumps(sort_keys=True)` alone is not a conforming canonicalizer. Use a maintained implementation and its conformance vectors. These wire choices and size/depth limits are platform policy. [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785), [W3C Trace Context](https://www.w3.org/TR/trace-context/).

## StartIntent

| Field | Type | Source / invariant |
| --- | --- | --- |
| `schema_version` | `"1"` | Kafka supplied; REST adapter injects it |
| `message_id` | UUID | Kafka supplied; REST adapter copies `Idempotency-Key` |
| `tenant_id` | TenantSlug | Must agree with verified REST grants or topic's configured tenant |
| `domain` | DomainSlug | Must resolve to an allowed route |
| `workflow_type` | RegisteredWorkflowType | Compiled registration must agree with route allowlist |
| `payload` | JSONObject | Business data; encrypted before entering Temporal |
| `traceparent` | TraceParent, optional | Propagated through an explicitly allowed tracing header; excluded from identity digest |

The workflow ID is exactly `message_id`; there is no tenant prefix, partition/offset suffix, or generated replacement. Temporal uniqueness is scoped to a namespace. A UUID can legitimately exist in two different tenant namespaces. All status and duplicate checks therefore start with a verified tenant/domain route.

`StartIntent` carries no caller-supplied namespace, queue, output topic, credentials, retry policy, timeout, or arbitrary callable name. Reject additional fields. All routing and execution policy comes from trusted configuration.

REST `POST` body contains only `tenant_id`, `domain`, `workflow_type`, and `payload`; optional tracing comes from the `traceparent` header. Kafka value contains the full event envelope. Kafka key MUST be present, valid UTF-8, and byte-for-byte equal to the canonical `message_id` string. A null Kafka value (tombstone), absent key, uppercase/malformed UUID, or mismatched key is a permanent invalid input and takes the metadata-only DLQ path. Do not derive identity from offset or invent an ID for invalid input.

## WorkflowInput

The shared start service constructs `WorkflowInput={intent:StartIntent, execution_route:{namespace,task_queue,output_topic,route_revision}}`. This internal model has no additional fields and is passed as one encrypted workflow argument. `execution_route` is the immutable resolved configuration snapshot, never caller data. It contains no credential profile contents or secret paths. The workflow uses that recorded output topic when scheduling its Activity; it never reads environment variables, route files, or a live routing service. The Activity independently verifies the recorded topic belongs to its trusted tenant allowlist and fails closed rather than silently choosing a different destination. Retain required route/topic allowlists while compatible old histories can replay.

## RouteProfile

The resolver maps `(tenant_id, domain, workflow_type)` to one immutable binding:

| Field | Meaning |
| --- | --- |
| `namespace` | Preprovisioned namespace for the tenant isolation boundary |
| `task_queue` | Preconfigured queue polled by compatible workers |
| `input_topic` | Topic dedicated to the configured tenant identity |
| `output_topic` | Allowed reference activity output topic |
| `dlq_topic` | Metadata-only quarantine topic for the input topic |
| `credential_profile` | Mounted credential profile for that tenant; not a credential value |
| `revision` | Inventory revision for diagnosis; not part of logical request identity |

Configuration additionally supplies a unique `group_id` for each input-topic consumer group and a `consumer_profile` for its mounted Kafka credentials. Different domains for one tenant may share an input topic; each topic MUST resolve to exactly one tenant and one consumer binding. Distinct tenants MUST use distinct namespaces and tenant-scoped credential profiles. Task queues are routing controls; a queue does not provide tenant authorization.

The inventory and active process selection are separate. An ingestion process selects at most 16 consumer bindings and 16 Temporal namespace/credential-profile clients. A WORKER process selects exactly one namespace and at most four Worker queue assignments within it. Every selected binding references inventory values exactly and agrees with its tenant, topic, group and mounted profile. Each Confluent consumer has one owning thread for poll, pause/resume, commits, callbacks, and close. Global process budgets are 32 in-flight starts and 256 buffered records, with one unresolved record per partition; limits apply across all selected consumer bindings. Never multiply these budgets by the number of consumers. `CREDENTIAL_PROFILES_PATH` maps profile names to locally mounted certificate/CA/key paths; it never embeds secret material. Top-level `MTLS_*` settings represent the compatible default profile. Single-binding fixture aliases such as `KAFKA_GROUP_ID` do not override production inventory bindings.

There are no wildcard tenant routes, dynamic topic creation, namespace creation, or per-message queues. Duplicate route keys, one tenant mapped to multiple namespaces, two tenants sharing a namespace, missing workflow registrations, and route/topic tenant disagreement are startup errors. Worker assignments are explicit finite `(namespace, task_queue)` bindings from this inventory. Reject assignments containing a workflow not registered for that route.

Freeze an existing route's namespace, queue, and output topic binding for at least the supported deduplication/history-retention window. A revision may change documentation or add routes without changing existing bindings. Moving existing identities between namespaces can create another execution with the same message ID and is forbidden. A changed queue/output topic in the same namespace must not bypass duplicate comparison; return `409` when existing memo binding differs. Migration requires a separately reviewed compatibility plan. Namespace creation, credentials, retention, and broker ACLs are platform provisioning responsibilities.

## IdentityMemo

Write one `enterprise_identity_v1` memo value atomically in the workflow start RPC:

```text
{
  "schema_version": "1",
  "message_id": "<canonical UUID>",
  "tenant_id": "<opaque tenant slug>",
  "domain": "<opaque domain slug>",
  "workflow_type": "EnterpriseEventWorkflow",
  "request_digest": "<64 lowercase SHA-256 hex characters>",
  "namespace": "<resolved namespace>",
  "task_queue": "<resolved task queue>",
  "output_topic": "<resolved output topic>",
  "route_revision": "<configured revision>"
}
```

`request_digest = lower_hex(SHA256(RFC8785_UTF8({schema_version, message_id, tenant_id, domain, workflow_type, payload})))`. Exclude `traceparent`, `route_revision`, transport source metadata, and receipt timestamps so equivalent REST/Kafka starts and retry deliveries agree. Array order remains significant. Do not log or expose the digest; a hash of predictable business data can disclose information. Memo is a Payload and MUST use the same encrypted data converter as workflow inputs. It is not a Search Attribute. Compare verified decoded fields and resolved namespace/queue/output-topic binding as well as digest; workflow description type must agree. `route_revision` alone does not make a conflict when binding is unchanged. Missing or corrupt memo is not a verified duplicate.

Temporal guarantees one open execution per ID within a namespace and applies reuse checks only to retained closed histories. Therefore the supported deduplication window is the actual namespace history-retention window; this release does not claim an eternal idempotency ledger. Operators must set namespace retention to cover maximum Kafka replay, API retry, and rollback horizons. Archive existence does not create a start-time uniqueness check. [Temporal Workflow ID and Run ID](https://docs.temporal.io/workflow-execution/workflowid-runid).

### Start state transitions

| Condition | Action | REST | Kafka offset |
| --- | --- | --- | --- |
| Valid authorized new intent | Start with `WorkflowIDConflictPolicy.FAIL` and `WorkflowIDReusePolicy.REJECT_DUPLICATE`; write encrypted identity memo in same RPC | `202` with ID and returned run ID | Eligible only after successful durable start |
| Start reports already started | Describe in resolved namespace; decode memo; compare logical identity, digest, type, and binding | `200` only when all checks match | Eligible after verified duplicate |
| Existing ID has different identity/digest/type/binding or no identity memo | Preserve existing execution; reject | `409` generic conflict | Permanent rejection; eligible only after confirmed DLQ delivery |
| Start timed out / transport response lost | Retry/reconcile using the SAME ID and explicit policies under a bounded deadline | `503` if acceptance remains ambiguous; client retries same key | Do not commit; leave record available for replay |
| Describe unavailable or memo cannot decrypt because dependency/key is unavailable | Treat as transient, never invent another ID | `503` | Do not commit |
| Invalid envelope, forbidden route/topic tenant, unsupported version, size/depth breach | Reject without starting | `400` / `413` / `422` as contract specifies | Eligible only after confirmed metadata-only DLQ delivery |
| Process crash after start but before commit | Next owner receives event and reconciles | N/A | Replay is expected |
| Closed history has expired | Service can accept ID again | No perpetual duplicate guarantee | Operators prevent replay outside documented window |

Do not use `USE_EXISTING`, unconditional acceptance of `WorkflowAlreadyStartedError`, terminating existing workflows, workflow completion waits, or a pre-start describe-only check. A describe-before-start race is not an atomic deduplication mechanism. Describe is for reconciliation after a conflict/ambiguous outcome. [Temporal Python policy enums](https://github.com/temporalio/sdk-python/blob/main/temporalio/common.py).

## KafkaSourceMetadata and commit frontier

Internal source metadata is `{topic, partition, offset}` with optional broker timestamp. Topic is from the allowlist, partition/offset are nonnegative integers. Broker offsets and publication receipts use losslessly parsed signed-int64 metadata; the business-input safe-integer/JCS rule does not apply to these excluded transport fields. No raw key, raw body, token, arbitrary headers, or unsanitized exception text enters logs or DLQ records. A validated opaque message ID may be included. Source metadata is excluded from digest and never substitutes for message identity.

Consumer uses `enable.auto.commit=false` and `enable.auto.offset.store=false`. Offset commits are synchronous and explicit, and commit the next offset. A record is terminal for ingestion only after durable start, verified duplicate, or acknowledged DLQ publication. Commit only the highest contiguous terminal offset plus one per partition; never skip over an unresolved earlier record. V1 processes at most one unresolved record per partition, while independent partitions may progress concurrently. Transient failures pause the affected partition and retry with bounded backoff while continuing polls for group membership and other partitions. Maintain a bounded in-flight set.

On revoke/shutdown, fence work by assignment generation; do not commit a result from an obsolete assignment. Commit a still-owned contiguous terminal frontier, cancel/drain remaining work within the grace budget, and close the consumer. Commit failure causes replay; do not roll back a workflow already accepted. Kafka processing plus Temporal start has no cross-system transaction, so this is at-least-once ingestion with retention-bounded start deduplication. [Confluent Python delivery guarantees](https://docs.confluent.io/kafka-clients/python/current/overview.html), [Confluent Consumer commit API](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html).

## PublishRequest, outgoing event, and receipt

The reference `EnterpriseEventWorkflow` builds a deterministic outgoing event and calls the reusable `publish_event` activity with the route's output topic. Its publication means processing intent was handled; it is not proof that the workflow had already completed. Use `event_type="workflow.processed"`.

| Outbound event field | Rule |
| --- | --- |
| `schema_version` | `"1"` |
| `event_type` | `"workflow.processed"` |
| `message_id`, `workflow_id` | Both exactly original message ID |
| `tenant_id`, `domain`, `workflow_type` | Inherited validated logical identity |
| `publish_id` | Exactly `<workflow_id>:publish:0`, stable across activity retries and worker restarts |
| `result` | `{ "status": "processed" }`; immutable deterministic value |
| `traceparent` | Optional verified correlation context |

Kafka publication key is `publish_id`. `Producer.produce()` only queues a record. Await its delivery callback while servicing producer polling; success requires acknowledged delivery. Enable producer idempotence and `acks=all`, but document that an activity can publish again after broker success and loss of its completion acknowledgment. Downstream consumers MUST deduplicate by the composite `(tenant_id, publish_id)`. The same workflow UUID and therefore publish ID are valid in different tenant namespaces; output topics may be shared or aggregated downstream, so topic separation is not a sufficient deduplication identity. Producer idempotence does not give an exactly-once Temporal side effect. Heartbeat bounded waiting loops and observe cancellation.

The activity returns `PublishReceipt = {publish_id, topic, partition, offset, status:"published"}` only after delivery success. The workflow returns that receipt after activity completion. The outbound event cannot include broker offsets, which are unknown when its bytes are constructed. Enforce output-topic allowlisting and tenant binding inside the activity even when invoked directly. [Confluent Producer delivery API](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html).

## DlqRecord

Metadata-only record fields are `schema_version="1"`, `reason_code`, `source={topic,partition,offset}`, `observed_at` (UTC RFC 3339 ending `Z`), and optional `message_id` only if it passed UUID validation. `tenant_id` is copied from the trusted topic mapping, never from an invalid body. Allowed reasons are `INVALID_JSON`, `SCHEMA_INVALID`, `UNSUPPORTED_SCHEMA_VERSION`, `MESSAGE_KEY_INVALID`, `MESSAGE_KEY_MISMATCH`, `TENANT_MISMATCH`, `ROUTE_NOT_ALLOWED`, `PAYLOAD_TOO_LARGE`, `DEPTH_EXCEEDED`, `IDEMPOTENCY_CONFLICT`, and `TOMBSTONE`.

No business payload, original Kafka value/key, JWT, arbitrary header, stack trace, or digest is permitted. DLQ key is `<source.topic>:<source.partition>:<source.offset>`, stable across replay; DLQ duplicates are possible. Delivery callback success is required before advancing source offset. DLQ outage pauses the partition; it never authorizes discarding the record. Operators can inspect source offsets using a separate privileged process; automatic raw-payload republication is outside this application.

## AuthorizationContext

REST uses an external OIDC issuer and signed bearer access JWTs. Validate the configured issuer, audience, signature, algorithm allowlist, expiry, not-before, required subject, and configured grant claims before route lookup or any Temporal RPC. Do not take issuer/JWKS URL or algorithms from caller headers. An untrusted `kid` must not create unbounded network traffic: use bounded TTL/size caches, one bounded refresh for an unknown key, and fail closed. Provider outage may use still-valid cached signing keys within the documented cache policy; it must not disable token validation. The platform neither issues tokens nor implements a password login flow. [FastAPI security scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/), [JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725).

Validated context contains subject (internal only), tenant/domain grants, and scopes. `workflows:start`, `workflows:read`, and `workflows:result` are separate scopes; result retrieval also requires read. Validate grant membership for every POST/GET. Missing/invalid credentials return `401` with `WWW-Authenticate: Bearer`; insufficient start scope/grants return generic `403`. Status lookups for ungranted tenant/domain or a run belonging to another route return the same generic `404` as an absent workflow. Never use workflow ID knowledge as authorization. Health and metrics use network-level access restrictions and return no secrets.

## StatusResponse and workflow state

GET requires `tenant_id` and `domain`, accepts optional `run_id`, and defaults `include_result=false`. It resolves the authorized namespace and describes the selected execution. The encrypted identity memo must match route tenant/domain and registered workflow type; otherwise return concealed `404`. Temporal states are `RUNNING`, `COMPLETED`, `FAILED`, `CANCELED`, `TERMINATED`, `TIMED_OUT`, and `CONTINUED_AS_NEW`.

Return `{workflow_id,run_id,workflow_type,status,result_available}` plus `result` only when explicitly requested, result authorization passes, and the selected execution is `COMPLETED`. `result_available` is true for a completed execution whether or not the caller requested its result. An explicit `run_id` binds that run. When omitted, supported SDK handle semantics resolve the latest run in the execution chain; describe supplies the exact selected run ID, which is then bound for any result fetch with run following disabled. Never block waiting for completion or implement an unbounded chain traversal. Reference workflow result conforms to `PublishReceipt`. Failures may include only an optional `error={code,message}` derived from the allowlisted terminal state with a fixed sanitized message; never expose serialized Temporal failure details. Dependency/result-decryption failure returns `503`. No listing, query DSL, signal/update, cancel, terminate, or synchronous execute endpoint is included in v1.

## Lifecycle and health

FastAPI lifespan initializes shared route config, client registry, authentication key cache, and the supervised Kafka subsystem before accepting requests. Startup does not happen at module import. All background work is owned and monitored; a failed required Kafka loop marks readiness false and triggers coordinated shutdown/restart. Shutdown stops admission, drains owned ingestion work, commits only safe offsets, and releases registry references/role-owned resources through supported SDK lifecycle APIs rather than assuming `Client.close()`. Keep synchronous Confluent calls off the ASGI event loop in bounded executor/thread ownership. [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).

Liveness reports process/event-loop health without restarting healthy pods for external outages. Startup reports initialization completion. Readiness reflects role initialization, valid routes/certificates/keys, viable required connections, assignment/poller readiness, and shutdown state; it returns `503` during startup/drain/fatal subsystem failure. Both roles expose protected management health and application Prometheus `/metrics` on port 8080. Worker SDK metrics use a separate `/metrics` listener on port 9090; Prometheus scrapes both. Metrics labels use finite route/workflow/activity/outcome dimensions; IDs, subject, message data, raw exception text, and trace IDs never become metric labels.

## Required contract acceptance cases

1. Lowercase canonical UUID accepted; absent/uppercase/malformed key rejected with no start.
2. REST and Kafka intents with the same logical content produce the same digest despite object property order, JSON whitespace, or changed trace/source metadata.
3. Array reordering or business data mutation produces a conflict for a retained ID.
4. Concurrent identical requests yield one new start and verified duplicate responses; differing requests yield one start and a conflict.
5. Lost start response followed by replay returns the same workflow ID; no regenerated ID.
6. Completed/failed/canceled retained workflows all reject new starts through reuse policy; retention-expired IDs are documented as outside the guarantee.
7. Tenant/topic and tenant/JWT mismatches cause no cross-tenant Temporal RPC; unauthorized status returns concealed `404`.
8. Oversized/deep/duplicate-key/non-finite/lone-surrogate JSON fails before codec/start; safe-integer and RFC 8785 vectors are tested.
9. Unresolved partition offset N prevents committing N+1; other partitions can advance.
10. DLQ enqueue without a successful delivery callback does not advance offsets; neither does a stale assignment callback.
11. Activity retry preserves outgoing bytes and `publish_id`; injected acknowledgment loss demonstrates why downstream deduplication by `(tenant_id,publish_id)` is required. Two tenants using the same UUID remain distinct when their outgoing events are aggregated; repeated delivery for one tenant is deduplicated.
12. Status of a running workflow returns immediately with no result; completed result requires the extra result scope.
13. Route namespace movement is rejected at validation/migration review; queue/memo mismatch cannot be counted as an idempotent success.
14. Fatal supervised consumer task changes readiness and reaches the process supervisor; graceful drain never commits unresolved work.
