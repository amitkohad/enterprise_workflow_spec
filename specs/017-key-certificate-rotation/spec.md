# F16 — Key and certificate rotation

**Status:** planned deployable increment; no implementation evidence yet.  
**Parent:** [roadmap entry F16](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).  
**Prerequisite:** F15 pinned Worker rollout (`016-pinned-worker-rollout`) and its prerequisite chain.  
**Program:** same repository/image and two role types; retained worker versions are included in every reader rollout.

Deliver an executable security-material rotation procedure that restarts the same image/build safely, changes the active encryption key only after all readers support it, renews mTLS certificates with an overlap window, and preserves historical decode/replay. This is an operational deployment checkpoint with end-to-end evidence, not a new KMS service or hot-reload subsystem.

## Scoped requirements

| ID | Required behavior | Core traceability |
|---|---|---|
| F16-01 | Strict SEC-KEYS namespace manifest/immutable IDs/expiry; active expiry blocks writes without expiring retained historical reads | FR-SEC-03 |
| F16-02 | Stage old+new keys to ingestion, current/retained workers and replay readers before writer switch | FR-SEC-01/03, FR-OPS-03 |
| F16-03 | Same-image rolling restart applies new material; no in-process secret/client reload or code-version replacement | FR-SEC-04, FR-ROUTE-04 |
| F16-04 | Certificate trust/authorization overlap, verified identity and bounded outage/drain; no verification bypass | FR-SEC-04/07, FR-CORE-04 |
| F16-05 | Retirement respects open runs, results, retention, archive/restore, reset and replay; loss/destruction is explicit and fails safely | FR-SEC-03, FR-OPS-03 |
| F16-06 | Safe expiry/rotation alerts and sanitized per-stage evidence; final qualification eligibility reported honestly | FR-OBS-04, FR-OPS-04 |

Temporal key management requires a rotation strategy and retaining keys needed to read older executions. [Key management guidance](https://docs.temporal.io/key-management). Retrieved 2026-10-01. The exact v1 keyring/envelope and restart-only process semantics are authoritative in [security.md](../001-enterprise-workflow-platform/security.md).

## Acceptance scenarios

1. Keep a synthetic run open under key A, stage A+B to every authorized reader, then switch active writers to B by same-image restart. New envelopes carry B; the old run and completed A result/failure/Memo/history still decode and replay.
2. Retained pinned worker build A receives the new reader keyring without changing its code/image identity. Routing/build identity remains unchanged through secret restart.
3. Expired active key blocks new writes/readiness with an approved code; the same expired key retained for decryption reads old history. Cross-scope keys/unknown IDs never fall back.
4. Stage renewed client certificates with server trust/authorization overlap, restart both roles and retained worker versions, and prove valid new connections. Wrong CA/hostname/expired/rejected old credentials fail after the approved cutoff.
5. Request old-key retirement while any historical/recovery obligation remains; tooling/runbook refuses. A deliberate missing-key test demonstrates explicit decode/replay failure without false success or plaintext fallback.
6. Rotate under admitted workload; offsets/unknown starts remain recoverable, bounded drain succeeds, live pinned runs retain compatible workers, and evidence contains key IDs/expiry timestamps only.

## Runnable checkpoint and eligibility

Deploy staged secret versions and run `python -m scripts.qualify.material_rotation --config <non-secret-config> --operation verify-readers`; use the individually documented `switch-writer`, `verify-history`, `renew-certificates` and `retire` operations in their authorized stages. The installation supplies secret provisioning and Temporal authorization changes; this tool verifies/conducts only explicitly authorized restart/release steps. It adds no deployed role or cloud-specific KMS adapter. Production eligibility requires this checkpoint and all preceding [roadmap](../001-enterprise-workflow-platform/roadmap.md) gates plus passing final load/recovery/release evidence; a successful rotation smoke alone is insufficient.
