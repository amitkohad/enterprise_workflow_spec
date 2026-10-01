# F04 — Acknowledged Kafka publication

**Increment:** F04 | **Application:** `temporal-enterprise-framework`  
**Prerequisite:** deployed and verified [F03 encrypted round trip](../004-encrypted-workflow-roundtrip/spec.md)  
**Deliverable:** a new version of the same application/image with an executable production-reference Workflow.

**Parent:** [feature roadmap](../001-enterprise-workflow-platform/roadmap.md) ·
[shared requirements](../001-enterprise-workflow-platform/spec.md). This increment implements
the reference-publication portions of FR-WF-01–05, FR-KAFKA-05 and FR-SEC-01–06; it does
not assert completion of those cumulative parent gates.

## User outcome and scope

An authorized operator starts `EnterpriseEventWorkflow` through the standardized encrypted
Temporal client and receives a publish receipt only after Kafka acknowledges its event.
The Workflow runs in the existing `WORKER` role. `INGESTION` remains deployable with its
existing health endpoints; public workflow routes and Kafka trigger consumption arrive
in later increments. This feature does not add an application service or container role.

`QualificationEchoWorkflow` from F03 remains test-only and cannot be registered by
production configuration. The registered reference Workflow consumes the shared typed
`WorkflowInput`, publishes `workflow.processed`, and returns `PublishReceipt`.
Use [shared data model](../001-enterprise-workflow-platform/data-model.md) and
[outbound schema](../001-enterprise-workflow-platform/contracts/outbound-event.schema.json)
as authoritative contracts.

## User scenario and acceptance

As an operator, I can deploy this version, run one synthetic Workflow, observe its
broker-acknowledged publication, and inspect the encrypted completed result.

1. A configured tenant/domain route yields the recorded namespace, queue and output
   topic. The Workflow reads the encrypted route snapshot, never live configuration.
2. Its immutable event has `publish_id=<workflow_id>:publish:0`, a deterministic
   `result={status:"processed"}`, and the input tenant identity; broker offsets appear
   only in the later receipt. Publication is not labeled Workflow completion.
3. `produce()` enqueue alone cannot complete the Activity. A successful delivery callback
   returns the actual topic/partition/offset; failed delivery follows the explicit retry
   policy and never reports success.
4. Restart or retry preserves event bytes and publish ID. Loss of the Activity completion
   acknowledgment can publish twice; downstream deduplication uses `(tenant_id,publish_id)`.
5. Heartbeats and cancellation remain responsive while waiting for delivery. A full
   producer buffer has bounded waiting, and shutdown drains only within its grace budget.
6. Raw Temporal history still protects arguments, results, heartbeat details and failure
   attributes with the F03 converter and retained read keys.

## Requirements and limits

- **F04-01:** Register only `EnterpriseEventWorkflow` and its reviewed Activity in the
  production worker registry. Keep Workflow imports free of settings/network clients.
- **F04-02:** Use a shared, bounded, callback-servicing producer owned by runtime lifecycle;
  enable idempotence and `acks=all`, authenticated broker TLS, and allowlisted destinations.
- **F04-03:** Validate typed input/result and byte limits; record the trusted route snapshot
  at start, and enforce the tenant/topic allowlist again inside the Activity.
- **F04-04:** Configure explicit Activity deadlines, heartbeat timeout, retryable/transient
  outcomes and non-retryable input failures from the shared plan; never retry indefinitely
  inside a single Activity attempt.
- **F04-05:** Never claim exactly-once side effects or global uniqueness of a publish ID.
  Downstream aggregation must preserve tenant identity.
- **F04-06:** Preserve the F03 image/config, old key material and compatible Worker until
  rollback can safely account for every accepted F04 execution.

Input validation, route mismatch, cancellation, broker outage, callback failure, producer
queue saturation and acknowledgment loss are mandatory cases. Kafka trigger ingestion,
REST starts/status, multi-tenant deployment expansion and autoscaling are outside F04.

## Runnable checkpoint and eligibility

Build `temporal-enterprise-framework:f04-acknowledged-publication`, run `python -m app.main` with
`APP_ROLE=WORKER` using the existing mounted security configuration and one approved
queue, and run the unchanged `INGESTION` health-only role from the same image if desired.
Use `APP_ENV=test` for this synthetic checkpoint and the explicitly qualified bounded
test Worker configuration from F03 until F15 adds production pinned-version routing.
Disable qualification-echo registration here and register the real reference Workflow;
test environment never bypasses configured mTLS, encryption or broker authentication.
The generated `scripts/checkpoints/f04_smoke.py` starts a synthetic reference Workflow
through the shared encrypted client, reads its acknowledged event, and verifies the
completed receipt plus raw-history protection. `docs/checkpoints/F04.md` records commands,
external dependency identities, image digest, evidence and rollback procedure.

This is deployable to controlled staging independently of later increments. It is not
eligible for general enterprise production until cumulative security, recovery,
observability and operational release gates pass. No deployment is asserted by this spec.
