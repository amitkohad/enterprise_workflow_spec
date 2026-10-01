# Security and replay contract

**Feature:** `001-enterprise-workflow-platform`  
**Date:** 2026-10-01  
**Status:** normative project design supporting the central functional requirements

All requirements below are **project decisions** unless a paragraph is explicitly marked **SDK fact**. Section labels are stable traceability targets for `FR-SEC-*`, `FR-WF-*` and `FR-OBS-*` requirements in `spec.md`; they do not create a separate application or feature. The trusted execution boundary consists of authenticated callers, the two application roles and the installation's secret/identity providers. Temporal/Kafka storage and visibility operators must not need business-payload decryption keys for service operation.

## SEC-BOUNDARY — Protection scope and threat model

Protect business payload confidentiality and integrity in Temporal history, protect transport to Temporal/Kafka, prevent unauthorized cross-domain execution or result access, and keep secret values out of public metadata and telemetry. Threat cases include a history/storage reader, altered ciphertext, an unauthorized API caller, a forged route, a poison Kafka record, a lost acknowledgement, accidental logging, stale-key rollout and incompatible workflow code.

Payload encryption does not protect data in a compromised authorized process or endpoint. Authorized application memory contains plaintext during execution. Kafka input/output record values have their own access, transport and broker-at-rest requirements; the Temporal codec does not encrypt the Kafka topic automatically. The v1 application does not add a Kafka content-encryption protocol. Platform operators must provision broker encryption at rest, ACLs and TLS for sensitive topics. If the organization's threat model requires end-to-end encrypted Kafka values, define that as a separate event-contract capability before permitting that data class.

| Surface | Mandatory policy |
|---|---|
| Workflow/Activity inputs, outputs, result payloads | Codec protected before SDK sends them to Temporal |
| Failure details/common message and stack | Codec protected using the failure-converter contract |
| Heartbeat business detail, supported signal/query/update payloads | Same converter where supported; include only required bounded content; test SDK coverage |
| Workflow/run/event/correlation IDs and type/queue/namespace names | Opaque, non-sensitive identifiers; no email, account number, human name or free text |
| Search Attributes | Allowlisted operational values only; never secrets or PII |
| Headers/tracing/baggage | Approved non-sensitive trace/correlation fields only; never tokens or business input |
| Memo | Only the encrypted `enterprise_identity_v1` identity record defined in data-model.md; no arbitrary caller memo |
| Summaries/static descriptions | Approved fixed operational text only; no business payload |
| API errors, logs, metrics, traces, DLQ metadata | Sanitized codes and approved identifiers; no payload, request digest or secret dump |
| Certificates, data keys, API/Kafka credentials | Mounted secrets or trusted identity integration; never repository/image/configmap |

**SDK fact.** Search Attributes bypass a custom codec and remain readable for indexing. [Temporal Search Attributes](https://docs.temporal.io/search-attribute). Retrieved 2026-10-01. Treat this as a permanent metadata classification rule even when the SDK gains additional converter capabilities.

## SEC-PAYLOAD — Authenticated payload protection

### Interface and composition

`app/temporal/converter.py` owns a converter factory and an `EnterprisePayloadCodec` compatible with the selected SDK. Its public signatures are:

```text
async encode(payloads: Sequence[Payload]) -> list[Payload]
async decode(payloads: Sequence[Payload]) -> list[Payload]
```

**SDK fact.** These methods operate on serialized protobuf payloads and must not mutate caller-owned payloads. [PayloadCodec API](https://python.temporal.io/temporalio.converter.PayloadCodec.html). Retrieved 2026-10-01.

The factory combines the typed business serializer, this codec and a failure converter with encoded common attributes. Every data-bearing Temporal client operation uses the same factory. All workers use standardized clients. All tests and replay tools explicitly inject it. Data keys, nonce generation and cryptography stay outside Workflow business code and its deterministic sandbox. Client and converter dependencies are constructed at process bootstrap.

### Encoding algorithm

For each input payload, in order:

1. Validate the original payload's bounded serialized size. Serialize the **complete original protobuf `Payload`**, including original metadata, into bytes using protobuf serialization. Do not assume JSON, lose the `encoding` entry, or encode only `.data`.
2. Resolve the namespace-scoped active encryption key from the initialized immutable key provider. Require exactly 32 key bytes and an approved key ID.
3. Generate a fresh 12-byte nonce from the operating system CSPRNG for this encryption operation. Never use a timestamp, Workflow ID, UUID substring, retry counter, zero nonce, deterministic workflow random generator or process-local incrementing counter.
4. Construct the public envelope fields and canonical authenticated additional data (AAD) described below.
5. Encrypt the original payload bytes with AES-256-GCM. Use the library's complete 16-byte authentication tag; never truncate it or invent a separate MAC.
6. Produce a new `Payload(metadata={"encoding": b"binary/enterprise-aes256gcm-v1"}, data=envelope_bytes)`. The metadata allowlist has exactly this codec discriminator in v1. Original payload metadata exists only inside ciphertext.

Empty input returns an empty list. The codec preserves one input payload to one output payload and order. Caller-owned objects and byte arrays are unchanged. Re-encoding an already encrypted outer payload is rejected as a configuration error to expose accidental double-codec construction.

### Version 1 envelope

Envelope data is UTF-8 JSON with no BOM. Keys use the exact names below; UTF-8 encoding, sorted object keys and separators `,`/`:` define canonical serialization. Strings are limited to the approved ASCII character set. Duplicate JSON keys, missing/extra fields and noncanonical representations are rejected. Standard base64 values include padding; their decoded lengths are validated before allocating/decrypting large buffers.

| Field | Type/constraint | Meaning |
|---|---|---|
| `version` | integer, exactly `1` | Format version |
| `algorithm` | string, exactly `AES-256-GCM` | Cipher suite identifier |
| `key_id` | string, 1–64 approved ASCII characters | Immutable key version; no secret value |
| `scope` | string, exactly the approved Temporal namespace, maximum 128 ASCII characters | Prevents decoding under a different configured namespace |
| `nonce` | standard base64 of exactly 12 bytes | Fresh nonce |
| `ciphertext` | standard base64 of ciphertext with 16-byte tag appended | Encrypted original `Payload` |

`AAD = b"temporal-enterprise-framework/payload\x00" + canonical_json_bytes({"version": 1, "algorithm": "AES-256-GCM", "key_id": key_id, "scope": scope})`.

AAD fields and the encoding marker are public operational metadata. They must not contain PII. `key_id` uses `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`; `scope` equals the exact namespace selected by the standardized client, never a caller-supplied alias. Decode requires the exact encoding marker and exact v1 fields before decryption. Canonical JSON binds the field interpretation without depending on host dictionary order. The nonce is authenticated by the AEAD operation; changing it also invalidates the tag. The encoder calculates encrypted envelope size and rejects it above the platform's configured 512 KiB payload limit, accounting for base64/JSON/metadata overhead. API ingress limits are 256 KiB. Do not rely on the plaintext byte count alone.

**SDK/library fact.** AESGCM returns ciphertext with the tag appended and authenticates supplied AAD; altered ciphertext, key, nonce or AAD causes validation failure. [cryptography AESGCM](https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM). Retrieved 2026-10-01.

This envelope binds the exact Temporal namespace, not a Workflow ID or caller identity. v1 does not rely on optional SDK serialization-context APIs. Authorization prevents payload copying across requests; the envelope alone does not prove provenance of a caller or prevent ciphertext replay within one namespace. A future context-binding format needs a new version and cross-operation replay compatibility tests. Replayer must receive the actual historical namespace rather than its SDK default.

### Decoding and fail-closed behavior

Decode validates envelope bounds/canonical form, checks that `scope` equals the decoder's configured scope, selects the retained key by exact `key_id`, authenticates/decrypts, and parses a new protobuf `Payload` from the resulting bytes. The downstream payload converter then uses the restored original metadata/type hints. Do not mutate the encrypted input or return unauthenticated partial plaintext.

Unknown encoding/version, unknown key ID, cross-scope envelope, tag failure, malformed base64/JSON/protobuf and oversized input fail with sanitized internal codes. There is no automatic plaintext fallback and no retry through a different key until one happens to work. These are not successful business results. An API client receives a bounded operational error without ciphertext, key material or exception message. A worker must not silently convert decryption errors into empty payloads or successful workflow completion. Startup catches missing required keyring configuration; runtime failures alert operators and preserve Temporal's recovery behavior.

Plaintext imports or legacy envelope formats require an explicit migration procedure with a narrow allowlist, retained keys and test fixtures. Such migration is outside v1; production cannot enable a permissive decode switch.

## SEC-FAILURE — Exception confidentiality

Use `DefaultFailureConverterWithEncodedAttributes` as `failure_converter_class`, or a tested subclass equivalent to `DefaultFailureConverter(encode_common_attributes=True)` compatible with the selected SDK. It must retain retry/cancellation/timeout semantics and protect common message/stack attributes as well as payload details. It must not replace all exceptions with a generic retryable error. Check nested causes and non-retryable application failures.

**SDK fact.** Encoded common attributes are how the Python failure converter makes message and stack trace available to the codec. [DefaultFailureConverter API](https://python.temporal.io/temporalio.converter.DefaultFailureConverter.html). Retrieved 2026-10-01.

Use constant error-type names and public error codes because operational failure metadata is not wholly hidden. The Activity/workflow interceptor records only `error_code`, allowlisted `error_type`, outcome and approved execution identifiers. Unrestricted `exc_info`, `repr(exception)`, `str(exception)`, frame-local variables and nested payload logging are prohibited in production. A private diagnostic facility, if later added, requires separate access and retention policy; it is not an excuse to emit payloads to normal logs.

## SEC-KEYS — Provisioning, rotation and retention

### Mounted provider baseline

Production selects the mounted, read-only `ENCRYPTION_KEYRING_PATH`. The secret contains a versioned manifest with one entry per approved namespace. Each entry has one active key ID and retained immutable key IDs. Manifest parsing is strict and bounded. Reject duplicate IDs, an active key absent from the map, invalid key sizes, ambiguous scopes and unsupported manifest versions. Provisioning must never change key bytes under an existing ID; cross-version rotation tests enforce this invariant because a new process cannot independently reconstruct an old secret. Secret values never appear in the settings representation or validation errors.

The v1 keyring shape is fixed below. Angle-bracket strings are illustrative placeholders, never usable secret defaults:

```json
{
  "version": 1,
  "namespaces": {
    "<configured-temporal-namespace>": {
      "active_key_id": "<approved-key-id>",
      "keys": {
        "<approved-key-id>": {
          "key_b64": "<standard-base64-of-32-secret-bytes>",
          "encrypt_not_after": "<YYYY-MM-DDTHH:MM:SSZ>"
        }
      }
    }
  }
}
```

All object levels reject unknown/duplicate keys. File bytes are limited to 256 KiB; namespace entries are bounded by the configured client inventory (default maximum 16); each namespace permits 1–64 retained keys. A WORKER snapshot contains only its selected namespace. INGESTION may contain the approved namespaces in its bounded route inventory. Every configured namespace has an active key; extra unapproved namespaces are rejected. Values under `namespaces` define the exact envelope `scope`; the same key bytes must not be reused in another namespace/environment. `key_b64` must be canonical standard base64 decoding to exactly 32 bytes. `encrypt_not_after` is a required UTC timestamp; it limits new encryption under that ID and does not expire historical decryption. An expired retained key may decode history; an expired active key blocks new writes and marks the role unready without fallback. Check active-key expiry at bootstrap and encoding and alert before its deadline. Retention/recovery needs determine when decrypt-only keys may be removed, never this timestamp alone.

The installation provisions AES keys using an approved generator, restricts namespace access, mounts only authorized scopes and rotates by replacing the secret and rolling the same application image. The application creates an immutable in-memory snapshot at startup. In-place hot reload is outside v1; a new pod reads the new keyring. A mounted secret may originate from the organization's KMS/secret engine, but Kubernetes ConfigMaps, source control, `.env` examples and image layers are forbidden locations for production keys. Kubernetes secret protection is an installation responsibility; base64 is serialization, not encryption.

The `KeyProvider` protocol exposes initialization/validation, active `(key_id, key_bytes)` lookup and exact retained-key lookup by scope. This is a dependency boundary, not a new network service. A future KMS adapter can unwrap a DEK at bootstrap and cache approved retained DEKs without changing the envelope contract. No cloud-specific adapter, KEK management service or per-payload KMS RPC is required in v1. Disallow accidental network calls from Workflow code or on the async hot path.

If legacy `KMS_ENCRYPTION_KEY` support is provided, it means a 32-byte base64 local development key and is allowed only in an explicitly selected development/test profile. Production rejects it even if a valid keyring is also present, so ambiguity cannot silently select an environment secret. Development keys are generated locally and excluded from Git; specification examples contain placeholders only.

### Rotation protocol

1. Provision a new immutable key ID with new random key bytes in the same namespace scope. Add it as decrypt-capable while keeping the previous active key.
2. Roll all ingestion/worker versions that may read histories so both IDs are available. Include older pinned worker deployments and replay jobs.
3. Change the active key ID for new encryption and roll new pods. Old pods may still encrypt with the old ID during the overlap; this is expected and budgeted.
4. Verify new envelopes use the new ID; verify old histories/results/failures still decode and replay; verify rollback images can read the new ID.
5. Mark the old key decrypt-only for future pod configurations. Retain it until no running execution, result read, retention/archival restore, reset or approved replay can need it.
6. Remove/destroy an old key only using the installation's documented retention and recovery decision. Key destruction intentionally makes its ciphertext unreadable and cannot be undone by this program.

Key encryption lifetimes and usage budgets are mandatory installation values. Estimate aggregate encryptions across all namespaces/pods/activity retries/replays that write new data; rotate before the approved bound and alert before expiry. Temporal's key guidance discusses a roughly `2^32` AES-GCM invocation bound; this project requires a security-approved lower budget with fleet capacity and rotation overlap accounted for. [Temporal key management](https://docs.temporal.io/key-management). Retrieved 2026-10-01. Do not claim nonce uniqueness or durable usage accounting from a resettable process counter. Where a strict fleet-wide limit cannot be established, the installation must enforce a conservative capacity/time bound or supply a provider with durable accounting.

Data keys are kept only in process memory for normal operation. Python garbage collection does not prove zeroization; avoid copying keys unnecessarily and do not claim guaranteed memory erasure. Disable core dumps and unneeded diagnostic access in production.

## SEC-TRANSPORT — mTLS and Kafka security

`app/temporal/client/__init__.py` exposes the standardized builder from `builder.py`; retain the requested client package directory. The builder reads locally mounted client certificate/private key and approved trust roots through the trusted credential profiles, then configures the pinned SDK's `TLSConfig`. `CREDENTIAL_PROFILES_PATH` defines path-only profiles; each route refers to a profile ID. The process/event-loop-scoped pool key includes namespace, credential profile and certificate snapshot so a client cannot accidentally reuse another namespace's identity. Production must authenticate the server certificate chain and expected hostname and present its client certificate. The endpoint's transport configuration is an operator value; request bodies cannot override it.

**SDK fact.** The current API provides `client_cert`, `client_private_key`, `server_root_ca_cert`, `domain` and `verification_server_name`. [TLSConfig API](https://python.temporal.io/temporalio.client.TLSConfig.html). Retrieved 2026-10-01. Verify exact field/import availability against the pinned SDK before code generation. No `skip_verify` equivalent may be introduced.

Reject missing/unreadable certificate pairs at startup. Verify certificate expiry/pair consistency during bootstrap where supported and test actual handshakes; a settings test cannot establish handshake validity. Custom root CAs and verification-name override require explicit approved configuration. Preserve SNI/authority routing and do not substitute a namespace string for the certificate DNS name. Certificate rotation uses overlapping validity/trust windows and rolling restarts of both roles, including retained worker versions. Monitor impending expiry using safe timestamps, not certificate contents.

Kafka production configuration requires broker TLS and the installation's approved authentication mode (mTLS or SASL over TLS). Broker certificate/hostname verification remains enabled. Credential references come from mounted secrets. Ingestion credentials permit read/group operations only on approved trigger topics and acknowledged write to the approved dead-letter topic. Worker producer credentials permit writes only to approved output topics. Client-supplied topic strings must be resolved through the publish allowlist, never passed directly to a privileged producer.

## SEC-AUTHZ — Identity, domain isolation and result access

The API validates a token against configured issuer/audience/trust material with a strict algorithm allowlist, expiry/not-before checks and bounded clock skew. Unknown/missing credentials are rejected before any Temporal call. Credentials and raw tokens never enter workflow input, headers, logs or Kafka messages. The installation supplies the identity provider; the application adds no login UI or identity control plane.

An approved mapping associates caller/service identity with permitted domains and operations. Ingestion resolves domain to namespace, task queue and registered workflow contract using immutable trusted configuration. A Kafka topic/producer service identity has an approved route; a record body alone cannot select a privileged domain. Worker registration and output-topic allowlists follow that same route inventory. Arbitrary Python module imports, user-supplied workflow class names, arbitrary task queues and user-provided retry/security settings are rejected.

For status/result reads, resolve the authenticated allowed domain first, derive/validate the expected opaque identity and use only that domain's namespace/client. Fetching by Workflow ID is not authorization. Return a consistent not-found response for inaccessible and unknown executions as defined in the API contract, so metadata cannot expose another domain's existence. Require the result-read permission before decrypting or returning business results. Public status responses contain no business payload by default. Bound result size and request deadline, and never wait for an open workflow to finish in an HTTP status call.

Namespaces and task queues are routing/isolation tools, not full authorization boundaries by themselves. Distinct tenants require distinct namespaces, tenant-scoped credential profiles and namespace-scoped data keys. Temporal namespace permissions, client identities, Kafka ACLs, Kubernetes service accounts and network policy must agree with the application's allowlist. An ingestion pod serving several approved tenants can access its configured scopes; this is an explicit process trust choice. A WORKER deployment selects one namespace and bounded queues. Stronger process isolation uses separate ingestion deployments/credentials/key mounts while retaining the same image and two role types; tenants never share a namespace as an implicit optimization.

## SEC-LOGS — Observability without disclosure or replay side effects

Use structured JSON with approved fields: timestamp, severity, service, environment, role, code version, trace/correlation ID, namespace/domain, task queue, workflow ID/type/run ID, activity ID/type/attempt where relevant, outcome, public error code and bounded duration. Null/not-applicable fields are acceptable. Validate/truncate caller-supplied identifiers and prevent newline/control-character injection. Context variable tokens are restored in `finally`; task/thread propagation is explicit and tested.

Workflow interception uses replay-safe SDK information/time/logging and preserves returned values, raised exceptions and cancellation. It never uses a wall-clock monotonic timer, direct network exporter or global structlog context that leaks between workflows. Activity/client/API interception may measure monotonic elapsed time outside workflow execution. Logging must distinguish execution time, attempt time and Workflow Task processing; a wall-clock span across durable sleeps is not a worker processing measurement.

Runtime owns SDK metrics configuration and the WORKER-only SDK Prometheus listener at 9090. Both roles expose application `prometheus-client` metrics and health probes at 8080; INGESTION has no SDK exporter in v1. The two registries are separately scraped and never compete for one port. Fixed bounded labels never include workflow/event IDs, trace IDs, customer IDs, Kafka offsets, raw exception names or arbitrary routes. Readiness/liveness/metrics are internal operational endpoints; network policy restricts their reachability. The worker health listener contains only health/operational routes, not the ingestion start API.

The v1 DLQ contains only the metadata defined in `contracts/dlq-record.schema.json`: approved source coordinates, validated opaque identity where available and sanitized reason codes. Raw key/body, business payload, request digest, authorization fields and arbitrary headers are forbidden. Operators retain the restricted source topic for approved recovery; a DLQ entry is not sufficient by itself to reconstruct the discarded business input. Do not log a poison record to compensate for failure to produce its metadata-only DLQ entry. A DLQ acknowledgement is a delivery event, not authorization to broaden source-topic access.

## SEC-REPLAY — Compatible code and key changes

Replay configuration explicitly uses the production converter, expected namespace scope and compatible worker interceptors. Use synthetic fixtures for source-controlled histories. CI/deployment verification may read encrypted histories only in the authorized installation and never exports keys or decrypted production data into the repository. Conversion/envelope/failure-converter changes require golden compatibility fixtures in addition to Workflow command replay.

A worker image is eligible for production only after replay compatibility and selected service/SDK feature checks pass. The reference Workflow is pinned to an immutable Worker Deployment Version; retain old worker images and keys while assigned executions need them. Promotion/rollback and reachability checks are performed by the platform deployment pipeline against the same worker role. No third container role or controller is introduced. If the installation explicitly uses unversioned workers, patching plus replay is mandatory before replacing code that may process existing executions. Silent fallback after a versioning error is forbidden.

## SEC-VERIFY — Required security evidence

Each row is an independently understandable acceptance case. Tests use synthetic markers and locally generated test certificates/keys; no production material is required in unit fixtures.

| Case | Expected evidence |
|---|---|
| JSON, bytes, typed model and protobuf payloads | Inputs/results restore value and all original metadata |
| Empty and multiple payload sequences | Order/cardinality preserved; caller objects unchanged |
| Same plaintext encrypted twice | Distinct fresh nonces/ciphertexts; both decrypt |
| Ciphertext/tag/nonce/key-ID/scope alteration | Authentication/validation failure; no partial plaintext |
| Unknown encoding/version/key; plaintext payload | Strict rejection with a sanitized code |
| Oversized envelope or malicious JSON/base64 | Bounded rejection before unbounded allocation or SDK send |
| Nested exception with sensitive message/stack/details | Marker absent in raw Temporal history; authorized decoding preserves expected failure semantics |
| Rotate active key during running workflow | New writes use new key; old state/failure/result decodes and replay succeeds |
| Missing historical key | Clear readiness/configuration or runtime failure; no fallback/false success |
| Valid mTLS | Real TLS-enabled Temporal connection and workflow lifecycle succeed |
| Wrong trust root/hostname/expired certificate | Connection fails; no insecure reconnect |
| Missing certificate or key | Bootstrap fails before listeners report ready |
| Unauthenticated/unauthorized start or read | No Temporal request; contract error without route/identity disclosure |
| Cross-domain workflow ID/result attempt | No result decryption or business data disclosure |
| Arbitrary queue/workflow/output topic | Validation rejects before privileged client operation |
| Sensitive input and malformed IDs | No marker/token/key/ciphertext dump in logs/metrics/traces/errors |
| Replay/cache eviction/worker restart | Compatible commands; replay-safe telemetry; no context leakage |
| Activity cancellation and retry | Cancellation propagates; bounded broker wait; stable duplicate-safe output identity |
| Secure container/manifests | Non-root process, read-only secret mounts, bounded resources, restricted network/service-account permissions |

Passing a codec round-trip alone does not prove the confidentiality claim. Raw-history inspection, failure coverage, metadata classification, TLS handshakes, authorization tests and retained-key replay evidence are release requirements.
