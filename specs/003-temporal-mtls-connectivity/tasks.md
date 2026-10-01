# F02 tasks — Execute sequentially

Prerequisite: completed F01 deployable checkpoint. All paths are future implementation paths in the same repository. Mark a task complete only with its scoped evidence.

- [ ] T001 Verify and lock the TLS/client API contract in `docs/compatibility.md` and `tests/unit/test_sdk_api.py`.
  - Accept: selected SDK supports required TLS/name/namespace operations; one direct API probe passes; no business Workflow call. Scope: F02-01/F02-05, V-001.
- [ ] T002 Implement role settings and path-only credentials in `app/config/settings.py`, `credentials.py` with parser tests.
  - Depends: T001. Accept: missing pair/CA, invalid production override and untrusted profile references fail with redacted codes. Scope: F02-01/F02-05, unit portion V-006.
- [ ] T003 Implement standardized TLS builder and bounded atomic registry in `app/temporal/client/builder.py` with concurrent/cache isolation tests.
  - Depends: T002. Accept: one initialization per namespace/profile/snapshot; no cross-loop sharing or secret-value logging. Scope: F02-02, V-001.
- [ ] T004 Wire cached bounded preflight to both-role readiness and shutdown in `app/main.py`, `app/api/health.py`.
  - Depends: T003. Accept: startup/outage/recovery/drain states pass a controlled lifecycle test; no detached retry task or per-probe RPC. Scope: F02-03/F02-04, V-022.
- [ ] T005 Add `scripts/smoke/temporal_connectivity.py` and real TLS integration cases.
  - Depends: T004. Accept: valid synthetic connection passes; wrong CA/hostname/pair/expiry/namespace fails without downgrade; smoke result sanitized and bounded. Scope: F02-03/F02-05, V-006.
- [ ] T006 Build/deploy the same image in both roles and record the checkpoint report in `docs/checkpoints/F02.md`.
  - Depends: T005. Accept: both roles reach expected readiness with mounts; outage and SIGTERM behavior observed; image/config/version evidence recorded; business-traffic eligibility remains blocked. Scope: all F02, V-006/V-022.
