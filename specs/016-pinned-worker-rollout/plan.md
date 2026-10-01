# F15 plan — Retain immutable workers while routing new runs

Implement the corresponding [F15 specification](spec.md) after its accepted prerequisite checkpoints.

The major capability is safe Worker version promotion/rollback with a physical deployment for every retained code version.

## Implementation surfaces

| File | Purpose |
|---|---|
| `app/config/settings.py`, `app/temporal/worker/factory.py` | Verified deployment name/build/versioning mode and PINNED registration |
| `deploy/helm/temporal-enterprise-framework/templates/` | Build-scoped immutable Worker Deployment/ScaledObject/scrape resources |
| `scripts/qualify/worker_rollout.py` | Verify/canary/promote/rollback/retire release operations and evidence |
| `tests/replay/test_histories.py` | Historical namespace/converter/keyring compatibility gate |
| `tests/integration/test_worker_rollout.py` | Real version routing, assigned-run retention and rollback |
| `docs/runbooks/worker-rollout.md` | Operator commands, retirement inventory and failure recovery |
| `docs/workflow-authoring.md` | Typed schema evolution, patching and bounded Continue-As-New extension guidance |

Choose one chart management convention and document it: a separate Helm release per Worker build is the baseline. Each release name includes a validated immutable build identifier; its Worker Deployment selectors/name bind that version and immutable image digest. Ingestion may roll independently. Same-code certificate/key mount restarts may roll pods within that build's Deployment, but an image/code change creates a new Worker release/Deployment. A chart upgrade that changes an existing worker build's image digest fails validation. Sanitize resource-name length and use a stable collision-resistant suffix rather than truncating two builds to the same name.

The Temporal Worker Deployment name is stable for one logical namespace/queue capacity pool; build IDs distinguish versions. All retained worker pods report the correct identity and poll only approved queues. Apply version-scoped KEDA/scrape selectors. Current/ramping and retained pinned versions need separately qualified capacities; missing version metrics never justify deleting a retained deployment. Keep the minimum production worker floor unless a later approved retained-version policy proves safe lower capacity.

The verifier inspects selected SDK/service capabilities, build/image identity, namespace/queue registrations, replay results and live version state. Canary starts use synthetic IDs/payloads under an approved staging route. Promotion/ramp mutates only supported Temporal routing controls, not workflow histories. No legacy pre-2025 build-ID compatibility API is substituted automatically. An explicitly selected COMPATIBLE_ROLLING mode must pass its own patch/replay and old-image rollback checks.

Publish authoring examples alongside the versioning policy: deterministic time/random APIs,
safe imports, backward-compatible typed schemas, explicit patch markers and Continue-As-New
before bounded histories grow indefinitely. Explain finishing message handlers before
continuation and retaining necessary state/read keys. Guidance reuses existing qualification
fixtures; it does not register another production Workflow.

## Deploy, smoke and rollback

Deploy A and capture encrypted synthetic open/completed/failure/retry histories. Deploy B in a separate release without touching A. Verify B registration, correct private health/metrics, replay and a bounded canary before routing promotion. Route new executions using Current/Ramping APIs supported by the selected service. Capture actual assigned deployment identity from execution metadata/history; pod labels alone do not establish pinning.

For rollback, restore new-run routing to A and preserve B for B-pinned runs. Do not assume routing rollback migrates those runs. A stuck B-pinned execution requires a compatible B fix/new recovery procedure and explicit replay evidence. Keep the appropriate namespace keys/cert access on all retained versions. Retirement verifies no open/assigned/reachable executions plus operator obligations for reset/replay/retention; absence of metrics alone is insufficient. Perform deletion only for the exact retired build/release.

## Verification and eligibility

F15 gates use the real qualified versioning service; WorkflowEnvironment tests alone cannot validate routing. Required evidence covers V-020/V-023/V-025/V-028 and includes a refused unsafe retirement and preserved B run after rollback. Partial absence of capability/evidence blocks promotion and leaves existing workers serving their assigned runs.
