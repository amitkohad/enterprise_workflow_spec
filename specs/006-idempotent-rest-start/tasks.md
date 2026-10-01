# F05 tasks — authenticated idempotent REST start

Prerequisite: F04 checkpoint passed. Execute these local IDs sequentially. Keep each
task's focused tests with its change; do not defer auth or duplicate checks to release.

- [ ] T001 — Normalize request identity. Add authoritative HTTP/start-intent models,
  strict bounded JSON parsing and RFC8785 digest calculation. Test safe-number/Unicode,
  duplicate-key/depth/size rejection, property-order equivalence and changed-content
  identity. Construct the trusted single-route snapshot and encrypted memo model.
  - Depends: F04 accepted deployed checkpoint.
  - Accept: Equivalent key order/trace differences preserve digest; strict JSON and changed-business-content cases behave as specified.

- [ ] T002 — Verify OIDC access JWTs. Implement configured issuer/audience/algorithm,
  signature/time/subject validation and bounded JWKS caching/refresh. Test wrong issuer,
  algorithm confusion, expiry, unknown-key floods and fail-closed cache expiry.
  - Depends: T001.
  - Accept: JWT/JWKS negatives fail closed, unknown-key refresh is bounded, and valid configured access JWT is accepted.

- [ ] T003 — Enforce start grants. Add `workflows:start` plus tenant/domain grant
  authorization for the configured route. Test 401/403 sanitization and prove denied
  requests make zero Temporal calls. No caller-supplied namespace or queue is accepted.
  - Depends: T002.
  - Accept: Unauthorized scope/grant cases return sanitized 401/403 with zero Temporal RPCs.

- [ ] T004 — Implement shared start reconciliation. Use the existing encrypted client
  with explicit FAIL/REJECT_DUPLICATE and atomic encrypted identity memo. Test equivalent,
  conflicting/missing-memo and unavailable-evidence outcomes, including matching closed
  runs and preserved key after ambiguous response; keep both RPC budgets bounded.
  - Depends: T003.
  - Accept: One retained logical intent yields one start; matching memo duplicates, mismatches conflict and uncertain evidence stays retryable.

- [ ] T005 — Expose the POST operation. Add the shared OpenAPI start route with exact
  202/200/400/409/413/415/422/429/503 behavior, response headers and sanitized errors.
  Test response models, mandatory header, admission bounds and no completion wait.
  - Depends: T004.
  - Accept: POST wire tests prove exact codes/headers, UUID preservation, admission bounds and no Workflow completion wait.

- [ ] T006 — Own gateway resources in lifespan. Initialize the single configured
  auth/client resources once, supervise startup/drain and close them cleanly. Test import
  has no connections, unhealthy startup is unready, and shutdown rejects new starts while
  preserving accepted execution. Do not add Kafka trigger consumption yet.
  - Depends: T005.
  - Accept: One lifespan owns resources; unhealthy startup and drain tests reject admission without losing accepted executions.

- [ ] T007 — Prove retained and uncertain starts. Add real-service HTTP/Temporal
  concurrent-equivalent versus changed-content tests and response-loss/restart recovery.
  Validate encrypted memo, F04 publication and no second retained start; document the
  retention boundary without claiming indefinite deduplication.
  - Depends: T006.
  - Accept: Real concurrent/response-loss/restart tests show one retained start and encrypted memo plus acknowledged F04 publication.

- [ ] T008 — Deploy, smoke and record rollback. Generate `config/checkpoints/f05/`,
  `scripts/checkpoints/f05_smoke.py` and `docs/checkpoints/F05.md`; build/run same-image
  version f05 and smoke valid/duplicate/conflict/unauthorized/malformed requests. Restore
  the F04 gateway while an accepted compatible Worker run completes; record image/config
  identities, actual evidence or blocked prerequisites, and production eligibility.
  - Depends: T007.
  - Accept: Built checkpoint smoke and F04 gateway rollback are recorded; an already accepted reference execution still completes.
