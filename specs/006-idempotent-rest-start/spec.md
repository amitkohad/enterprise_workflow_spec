# F05 — Authenticated idempotent REST start

**Increment:** F05 | **Application:** `temporal-enterprise-framework`  
**Prerequisite:** deployed and verified [F04 publication](../005-acknowledged-kafka-publication/spec.md)  
**Deliverable:** same image/version exposes a secure, retry-safe REST start for one configured tenant route.

**Parent:** [feature roadmap](../001-enterprise-workflow-platform/roadmap.md) ·
[shared requirements](../001-enterprise-workflow-platform/spec.md). This increment owns
FR-API-01, start-related FR-API-03/FR-ING-01–03 and single-route FR-SEC-05 portions;
multi-tenant/full operational gates remain cumulative.

## User outcome and scope

A scoped application identity submits a JSON request and stable UUID to
`POST /v1/workflows/start`. It receives a Workflow/run reference as soon as Temporal
durably accepts the start. A retry with equivalent business content returns the verified
existing execution; changed content conflicts. The deployed `WORKER` from the same image
executes the F04 reference Workflow and publishes its acknowledged event.

This is the first business route in `INGESTION`. It includes full OIDC verification and
tenant/domain grants from day one. The checkpoint uses one approved tenant/domain route,
one namespace client/profile and one queue. General route expansion arrives in F10;
unauthenticated or cross-tenant access is never an intermediate release behavior.
Status/result reads arrive in F06 and Kafka trigger consumption in later increments.

## Acceptance scenarios

1. Valid token, scope/grant, canonical UUID `Idempotency-Key` and conforming body yield
   `202`, the exact submitted UUID as `workflow_id`, returned `run_id`, `Location`, and
   `acceptance=STARTED`. The HTTP call does not wait for Workflow completion.
2. Repeating equivalent content with that key yields `200` and `ALREADY_EXISTS` only
   after encrypted memo/type/route comparison. Reordered JSON keys or changed trace context
   do not change identity; changed business data yields `409` without another start.
3. Concurrent equivalent starts yield one new execution and verified duplicate responses.
   Timeout after possible server acceptance yields `503` when reconciliation is uncertain;
   callers retain the same key and no replacement UUID is created.
4. Missing/invalid key yields `400`; body and depth limits, strict JSON/JCS constraints,
   unsupported representation and local admission limits follow the shared OpenAPI.
5. Missing/invalid token yields `401`; insufficient start scope or tenant/domain grant
   yields sanitized `403` before any Temporal RPC. Unknown routes are rejected.
6. A restarted gateway can verify a retained execution without an in-memory idempotency
   cache. Closed histories outside namespace retention are outside the dedup guarantee.

## Requirements

- **F05-01:** Follow the start operation in
  [shared OpenAPI](../001-enterprise-workflow-platform/contracts/openapi.yaml) and the
  [data model](../001-enterprise-workflow-platform/data-model.md); no new response format.
- **F05-02:** Verify configured JWT issuer/audience/asymmetric algorithm, signature,
  expiry/not-before, subject and mapped grants. Bound JWKS TTL, keys and refresh attempts;
  unknown `kid` cannot create unbounded requests. No token-issuance endpoint is added.
- **F05-03:** Normalize to `StartIntent`, hash RFC8785 canonical business identity, and
  atomically start with encrypted `enterprise_identity_v1` memo and `WorkflowInput` route
  snapshot. Use conflict `FAIL` and reuse `REJECT_DUPLICATE` explicitly.
- **F05-04:** Share one start service independent of HTTP for later Kafka use. Bound start
  and reconciliation deadlines; ambiguous/unavailable evidence stays retryable.
- **F05-05:** Initialize the configured client/auth cache in FastAPI lifespan, supervise
  the existing role lifecycle, and close resources without accepting new starts on drain.
- **F05-06:** Preserve no-store responses, sanitized correlated errors and key reuse after
  retryable outcomes. IDs do not enter metric labels; payloads, JWTs and digests do not
  enter log bodies. Approved opaque IDs may correlate redacted logs.

Missing/corrupt identity memo cannot be accepted as a duplicate. Key/service unavailability
returns retryable failure. Route revision alone is not a conflict if binding is unchanged.
Do not add a database, pre-start describe race, terminating/reusing existing IDs, or a
Kafka consumer in this feature.

## Deployable checkpoint and rollback

Build `temporal-enterprise-framework:f05-idempotent-rest-start`; run both existing roles with one approved route,
mounted mTLS/keyring/broker profiles and a trusted OIDC issuer. Run
`scripts/checkpoints/f05_smoke.py` against the gateway with a token file: new start,
matching retry, changed-content conflict, invalid token/key and observed Kafka publication.
Record reproducible deployment/smoke commands in `docs/checkpoints/F05.md`.

Rollback stops admission, drains HTTP start work, and restores the F04 gateway image/config
while retaining compatible reference Workers for all accepted runs. Keep histories, route
bindings and keys. This checkpoint is deployable to controlled staging; general enterprise
production remains subject to cumulative operational/security/recovery gates.
