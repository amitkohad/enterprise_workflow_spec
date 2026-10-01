# F16 tasks — Execute sequentially

Prerequisite: F15 versioned-release checkpoint and its full prerequisite chain. Secret provisioning remains external; tool operations never invent a KMS service.

- [ ] T001 Implement/readiness-test active-key/certificate expiry metadata and startup snapshot policy.
  - Accept: active encrypt expiry blocks writes/readiness, retained expired keys decode, safe lead-time alerts; no in-process client/key reload. Scope: F16-01/F16-03/F16-06, V-004/V-022.
- [ ] T002 Implement complete authorized reader/build inventory and read-only preflight in `scripts/qualify/material_rotation.py`.
  - Depends: T001. Accept: ingestion/current/ramping/retained workers/replayer identified; missing reader evidence blocks switch; report has no secret contents. Scope: F16-02/F16-06.
- [ ] T003 Add staged keyring references and same-image/build restart operations with writer-switch guard.
  - Depends: T002. Accept: A+B staged before B active, immutable worker identity unchanged, incomplete stage cannot switch writers. Scope: F16-02/F16-03.
- [ ] T004 Execute live old/new-key history/result/failure/Memo/heartbeat/replay qualification.
  - Depends: T003. Accept: new writes B, old A run/read/replay work; missing A fails explicitly; rollback writer retains B and respects A expiry/budget. Scope: F16-01/F16-02/F16-05, V-004/V-020/V-029.
- [ ] T005 Add certificate overlap/preflight/restart/cutoff procedure and actual TLS negatives.
  - Depends: T004. Accept: all role/build connections renew with validation, old cutoff enforced, wrong CA/hostname/expiry rejected; failed renewal preserves valid overlap. Scope: F16-03/F16-04, V-006/V-029.
- [ ] T006 Implement evidence-gated retirement checks and lost-key recovery runbook.
  - Depends: T005. Accept: historical/reset/restore obligations block removal; encrypt expiry never deletes a decrypt key; recovery requires exact original material and authorized provisioning. Scope: F16-05.
- [ ] T007 Qualify key/certificate rolling restart under admitted workload and pinned-run retention.
  - Depends: T006. Accept: bounded drain, no skipped offsets/false acknowledgments, each pinned build keeps its image, unknown starts reconcile and new connections recover. Scope: F16-02/F16-03/F16-04, V-022/V-029.
- [ ] T008 Deploy the rotation checkpoint and record `docs/checkpoints/F16.md` plus operator commands/evidence.
  - Depends: T007. Accept: all material stages/rollback/retirement refusal demonstrated; sanitized reproducible evidence and complete-roadmap production gate status delivered. Scope: all F16.
