# F03 — Encrypted Workflow round trip

**Status:** planned deployable increment; no implementation evidence yet.  
**Parent:** [roadmap entry F03](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).  
**Prerequisite:** F02 Temporal mTLS connectivity (`003-temporal-mtls-connectivity`).  
**Program:** the same repository/image and `INGESTION|WORKER` roles.

Deliver a running worker and a one-shot qualification smoke that execute a finite, encrypted Temporal Workflow through the secure connection builder. Establish confidentiality/integrity for full Payload objects and encoded failures using independent writer/reader instances. This is an executable security checkpoint, not just a converter library.

`QualificationEchoWorkflow` and its bounded synthetic Activity are available only under `APP_ENV=test` with explicit qualification registration. They are not part of the production business registry. Production rejects qualification registration. No public start endpoint, Kafka trigger consumer or new application role is introduced here. The later registered `EnterpriseEventWorkflow` uses these same converter/client contracts.

## Scoped requirements

| ID | Required behavior | Core traceability |
|---|---|---|
| F03-01 | Async PayloadCodec encrypts/restores the complete original protobuf Payload and metadata; strict v1 envelope/namespace AAD/size rules | FR-SEC-01/02/03 |
| F03-02 | Mounted immutable namespaced keyring follows SEC-KEYS, active expiry and retained decrypt keys; no per-payload KMS RPC | FR-SEC-03 |
| F03-03 | Failure common message/stack and details are protected without changing retry/cancellation semantics | FR-SEC-02 |
| F03-04 | Every data-bearing starter/worker/replayer uses the same factory with independent codec instances and historical namespace | FR-SEC-01, FR-WF-02 |
| F03-05 | Deployed finite qualification flow exercises input/result, Activity input/result, encrypted Memo, heartbeat details and an intentional failure path | FR-SEC-01/02/06, FR-WF-03 |
| F03-06 | Raw server history/log/error inspection finds no synthetic sensitive marker; public identity/headers remain safe | FR-SEC-06 |

The exact envelope/keyring are normative in [security.md SEC-PAYLOAD/SEC-KEYS](../001-enterprise-workflow-platform/security.md). `PayloadCodec` accepts and returns Payload sequences, not business dictionaries/raw bytes. [SDK codec API](https://python.temporal.io/temporalio.converter.PayloadCodec.html). Failure common attributes require explicit conversion for codec protection. [FailureConverter API](https://python.temporal.io/temporalio.converter.DefaultFailureConverter.html). Retrieved 2026-10-01.

## Acceptance scenarios

1. Deploy WORKER with synthetic namespace/test keys and mTLS; one-shot smoke starts the finite Workflow, awaits its bounded completion and verifies the decoded echo/result through a separately constructed protected client.
2. A qualification Activity heartbeats a synthetic marker during a bounded wait and returns it; a failure variant raises an approved `ApplicationError` with sensitive synthetic message/detail. Sample pending Activity heartbeat details through the raw Describe response before the Activity finishes; heartbeat details are not assumed to be durable History events. Raw History and sampled pending details contain no plaintext marker in Payload bytes, Memo or failure message/stack; authorized readers reconstruct the expected values/semantics.
3. JSON, bytes, typed values and protobuf Payload metadata round-trip; empty/multiple sequences preserve cardinality/order; input objects are unchanged. Fresh nonces are observed, without treating a smoke test as a uniqueness proof.
4. Tampered key ID/scope/version/nonce/tag/ciphertext, unknown keys/encodings, plaintext fallback and malformed/oversized envelopes fail closed with sanitized errors.
5. Expired active key prevents writes/readiness; retained expired keys still decrypt. Cross-namespace reuse is rejected. Independent worker/starter/replayer snapshots exchange data.
6. Encrypted synthetic success/failure histories replay with the same factory and actual namespace; a deliberate nondeterministic Workflow change fails replay. Production startup cannot register the qualification flow.

Plain unexpected Workflow exceptions may fail/retry Workflow Tasks rather than terminate the execution; intentional qualification failure uses `ApplicationError`. Decoder/schema failures are tested with bounded observation rather than waiting indefinitely for a terminal result. [Python error handling](https://docs.temporal.io/develop/python/best-practices/error-handling). Retrieved 2026-10-01.

The raw execution description exposes the underlying protobuf; `PendingActivityInfo` carries heartbeat Payloads and the last heartbeat time. This supplies the pending-heartbeat sampling surface. [Python description API](https://python.temporal.io/temporalio.client.WorkflowExecutionDescription.html), [Temporal API schema](https://github.com/temporalio/api/blob/master/temporal/api/workflow/v1/message.proto). Retrieved 2026-10-01.

## Runnable checkpoint and eligibility

Run the image with `APP_ROLE=WORKER`, `APP_ENV=test`, an isolated namespace/task queue and qualification registration; INGESTION remains the secure operational runtime. Execute `python -m scripts.smoke.encrypted_roundtrip --config <non-secret-config> --case success`, then repeat with `--case failure`. This smoke is a one-shot test command, not a third deployed container role. It creates only synthetic executions, uses deadlines and writes sanitized evidence. The checkpoint is deployable for encryption qualification; business traffic remains blocked until its authorization, durable business registration, ingress/delivery and release gates pass. See the [feature roadmap](../001-enterprise-workflow-platform/roadmap.md) for the cumulative release contract.
