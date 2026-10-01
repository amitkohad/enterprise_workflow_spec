# F16 plan — Rotate material while preserving readers and workers

Implement the corresponding [F16 specification](spec.md) after its accepted prerequisite checkpoint.

The major capability is coordinated staged-key/certificate rollout across both roles and every retained pinned worker build.

## Implementation surfaces

| File | Purpose |
|---|---|
| `app/config/key_provider.py`, `credentials.py` | Strict startup snapshots and expiry validation; no hot reload |
| `app/api/health.py`, `app/observability.py` | Active-key/certificate expiry readiness/alerts with safe metadata |
| `scripts/qualify/material_rotation.py` | Reader inventory/preflight/verified restart/writer switch/history/retirement evidence |
| `deploy/helm/temporal-enterprise-framework/` | Secret-reference/checksum rollout of same image/build per release |
| `tests/integration/test_rotation.py` | Real history/key/certificate overlap/negative/recovery cases |
| `docs/runbooks/material-rotation.md` | External provisioning, cutoff, rollback and lost-key recovery decisions |

Read the exact namespace manifest in SEC-KEYS. Provisioned IDs never change bytes; old expired write keys remain valid decrypt keys. Check active write expiry at bootstrap and encoding; readiness fails on missing/expired active key, while retained-key decode is not time-expired. Bound secret parsing and maintain only approved namespace snapshots. Telemetry shows safe expiry/outcome/scope values; no raw key, certificate or request digest.

The verifier builds a reader inventory from the bounded route/worker release configuration: all ingestion instances, current/ramping/retained worker releases and authorized replay jobs. A partial reader rollout cannot authorize the active writer switch. Secret material is provisioned externally and mounted read-only. Helm checksum/reference changes trigger restart of the **same** immutable image/build; rotating secrets must not assign old pinned executions to new code. Client pools rebuild from startup namespace/profile/certificate snapshots.

## Key deployment, smoke and rollback

Generate synthetic A histories/results/failures and hold one run open. Provision A+B with A active; restart every reader release and prove both keys decode. Provision B active and restart writers while readers retain A+B. Verify B writes plus A historical read/replay and workflow continuation. Retained old pods may write A during overlap; the capacity/key-usage budget includes that overlap. Stop/suspend business admission if readiness cannot establish a valid active key.

Rollback to A as writer is allowed only while A remains within its approved encryption lifetime/budget and every reader keeps B. Never remove B merely because writer routing returned to A. If A can no longer encrypt safely, keep B and correct reader deployment instead. A key deletion is irreversible unless an approved protected backup exists; restoration needs the exact old bytes/ID/scope and authorized provisioning, not regeneration with the same ID.

## Certificate deployment, smoke and rollback

Provision new client credentials and server trust/authorization overlap before restarting ingestion, current/ramping and retained workers. Keep endpoint verification correct throughout; mount update does not reload an existing gRPC connection. Verify new TLS/namespace access and scoped start/poll/read behavior, then retire old credentials only after the reader inventory is complete. Test unknown CA/wrong hostname/expired/rejected identities with a real enforcing service. If renewal fails, preserve healthy overlapping pods and restore approved prior references while still valid; never disable TLS checks.

## Retirement and final evidence

Retirement requires the longest open-run/result/closed-retention/archive/restore/reset/replay need and the external secret recovery policy to be satisfied. The tool fails closed when evidence is absent; no automatic key destruction on Workflow completion or encrypt expiry. Aggregate nonce/key usage and certificate lead times are installation-approved values, not resettable process-counter proofs.

Run V-004/V-006/V-020/V-022/V-029 against the built image and production-equivalent staging. Record original/new secret references and key IDs, immutable image/build identities, namespaces, preflight/replay/drain outcomes and remaining blocked gates. Business data and credentials never enter the report. Final production readiness requires the roadmap's complete evidence, including capacity/outage qualification owned elsewhere.
