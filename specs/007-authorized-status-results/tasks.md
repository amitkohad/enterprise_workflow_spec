# F06 tasks — authorized status and results

Prerequisite: F05 checkpoint passed. Local IDs are scoped to this feature directory.
Execute sequentially; retain start/publication smoke at every runnable checkpoint.

- [ ] T001 — Status response models. Add authoritative state/result/fixed terminal
  error models. Test noncompleted responses cannot contain results and completed
  `result_available=true` does not itself imply requested/authorized result inclusion.
  - Depends: F05 accepted deployed checkpoint.
  - Accept: Wire model examples pass and noncompleted-result/incorrect availability combinations are rejected.

- [ ] T002 — Read and result authorization. Extend existing auth with
  `workflows:read`, conditional `workflows:result`, and concealed tenant/domain denial.
  Test 401/403/404 mappings and zero backend calls for denied tenant context.
  - Depends: T001.
  - Accept: Scope/grant matrix yields specified 401/403/404 and denied tenant reads make zero backend calls.

- [ ] T003 — Bounded describe service. Add `app/temporal/client/read_service.py` using
  the authorized route/client and optional run ID. Verify decrypted identity memo/type;
  conceal absent or mismatched execution and test the total deadline/key-unavailable path.
  - Depends: T002.
  - Accept: Authorized describe returns selected identity; mismatched identity is concealed and dependency deadline stays bounded.

- [ ] T004 — Completed result selection. Bind describe's exact run ID and fetch/decode
  only completed authorized results with run following disabled. Test running state has
  no result call, terminal failures expose no raw failure, and result deadline is bounded.
  - Depends: T003.
  - Accept: Running state performs no result RPC; completed authorized receipt binds selected run and terminal error never leaks failure text.

- [ ] T005 — GET contract adapter. Add the shared status endpoint, query defaults and
  validation, no-store/correlation headers and sanitized errors. Test exact wire examples
  plus explicit versus omitted run ID; keep F05 POST unchanged.
  - Depends: T004.
  - Accept: GET query/header/wire checks pass while prior POST/duplicate checks remain unchanged.

- [ ] T006 — Real-service state/run evidence. Exercise completed, running and terminal
  states plus wrong identity/memo/key. Use a test-only retry/Continue-As-New fixture to
  qualify latest-chain versus explicit-run SDK semantics; do not register that fixture
  in production. Record partial shared gate evidence without claiming full qualification.
  - Depends: T005.
  - Accept: Real status and test-only chain evidence proves latest versus explicit run selection without production fixture registration.

- [ ] T007 — Deploy and smoke status. Generate `config/checkpoints/f06/` and
  `scripts/checkpoints/f06_smoke.py`; build/run same-image f06 roles. Start through POST,
  read nonblocking status, fetch the completed receipt, and verify wrong-grant/read-only
  token outcomes against controlled dependencies. Record actual image/evidence.
  - Depends: T006.
  - Accept: Same-image smoke proves POST through nonblocking status to authorized completed receipt and negative grant/result scope outcomes.

- [ ] T008 — Rollback checkpoint record. Write `docs/checkpoints/F06.md` with exact
  commands, dependency/config identity and F05-compatible downgrade. Verify accepted
  reference work completes and prior POST/duplicate smoke passes after downgrade; record
  GET unavailability impact, retained keys/history, and production eligibility.
  - Depends: T007.
  - Accept: F05-compatible rollback is documented and prior start/duplicate plus accepted-run completion still pass.
