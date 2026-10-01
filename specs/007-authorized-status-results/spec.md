# F06 — Authorized status and completed results

**Increment:** F06 | **Application:** `temporal-enterprise-framework`  
**Prerequisite:** deployed and verified [F05 REST start](../006-idempotent-rest-start/spec.md)  
**Deliverable:** same application/image adds bounded status and authorized result reads.

**Parent:** [feature roadmap](../001-enterprise-workflow-platform/roadmap.md) ·
[shared requirements](../001-enterprise-workflow-platform/spec.md). This increment owns
FR-API-02, read-related FR-API-03 and authorized single-route FR-SEC-05 portions;
complete multi-tenant and production evidence remains cumulative.

## User outcome and scope

An authorized caller starts a Workflow through the existing POST, follows its returned
location, sees current state without waiting for completion, and explicitly requests the
completed publish receipt when granted result access. The existing INGESTION/WORKER roles
and F04 publication behavior remain unchanged.

Implement `GET /v1/workflows/{workflow_id}` with required `tenant_id`/`domain`, optional
`run_id`, and `include_result=false` by default. Follow the
[shared OpenAPI](../001-enterprise-workflow-platform/contracts/openapi.yaml) and
[data model](../001-enterprise-workflow-platform/data-model.md). Keep the configured
single-tenant route/client checkpoint; multi-tenant expansion arrives in F10. No listing,
query DSL, signal/update, cancellation, termination or synchronous execution API is added.

## Acceptance scenarios

1. A read-scoped/granted caller receives state and selected Workflow/run IDs promptly
   for a running execution, with `result_available=false` and no result fetch/wait.
2. Completed execution returns `result_available=true`; only an explicit authorized
   `include_result=true` adds the typed F04 `PublishReceipt`. Result scope is required
   in addition to read scope even when the selected execution is not yet completed.
3. An explicit run ID selects exactly that run. Without it, supported SDK handle semantics
   resolve the latest run in the execution chain; the returned describe run ID binds any
   later result request, with run following disabled and no unbounded traversal.
4. Failed/canceled/terminated/timed-out executions return their status and at most the
   fixed sanitized terminal error. Raw failure message, stack or payload is never exposed.
5. Ungranted tenant/domain, mismatched identity memo/run and absent execution return the
   same generic `404`. Authentication failures are `401`; missing required scopes are
   `403`. Denied tenant lookups do not query Temporal.
6. Describe/result/key dependency failure returns sanitized `503` within the shared
   total read deadline. Responses are no-store and remain bounded after service restart.

## Requirements and edge cases

- **F06-01:** Reuse the F05 JWT verifier, shared namespace client and route resolver;
  verify grants before describing and decrypted identity/type after describing.
- **F06-02:** Expose only the authoritative state/result/error response shape; preserve
  canonical UUID/query validation, correlation, limits and response headers.
- **F06-03:** Select latest or explicit run under the read budget, then bind the selected
  run for an optional completed-result RPC; never await a running result.
- **F06-04:** Handle terminal state/result races and run selection using qualified SDK
  behavior, not a custom loop. Invalid or unproven identity is concealed, never guessed.
- **F06-05:** Keep F05 start/duplicate behavior and F04 output/receipt compatibility;
  adding status must not change recorded Workflow command order or argument schema.

Mandatory cases include running/completed/failed/canceled/timed-out/terminated states,
wrong tenant/domain/run, missing scope, wrong-key memo/result, total read deadline and
latest-run selection. Retry/Continue-As-New chains are exercised with a test-only fixture;
the production reference Workflow does not acquire those features in this increment.

## Deployable checkpoint and rollback

Build `temporal-enterprise-framework:f06-status-results` and deploy both same-image roles using the F05
security/route configuration. `scripts/checkpoints/f06_smoke.py` starts a synthetic
Workflow through POST, performs immediate status reads, and requests its completed receipt
with the proper token; invalid-grant/result-scope tests use supplied fixture identities.
Record deployment/smoke commands and evidence in `docs/checkpoints/F06.md`.

Rollback drains API requests and restores F05-compatible images/config; POST remains
available and accepted Workflows continue on compatible Workers. GET clients temporarily
lose this new capability, so document that impact. Retain keys/history/bindings. This is
controlled-staging deployable; general production requires cumulative release gates.
