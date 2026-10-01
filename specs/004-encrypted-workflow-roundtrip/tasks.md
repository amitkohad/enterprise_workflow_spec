# F03 tasks — Execute sequentially

Prerequisite: completed F02 deployed connectivity checkpoint. All tests use synthetic input and controlled test keys; no business ingress is enabled.

- [ ] T001 Implement SEC-KEYS keyring snapshots in `app/config/key_provider.py` and focused parser/expiry tests.
  - Accept: exact namespaced manifest, bounds,32-byte keys/immutable IDs, cross-scope isolation, active write expiry and retained expired-key decoding; no hot reload. Scope: F03-02, V-004.
- [ ] T002 Implement the full-Payload v1 AES-GCM codec in `app/temporal/converter.py` and multi-format round-trip tests.
  - Depends: T001. Accept: original metadata/order restored, no mutation, namespace AAD/fresh12-byte nonce/full tag/size bounds enforced. Scope: F03-01, V-002.
- [ ] T003 Add strict corruption/plaintext/unknown-key/version/cross-scope negative cases.
  - Depends: T002. Accept: finite rejection without fallback/leaked values; empty/multiple sequences and independent readers covered. Scope: F03-01/F03-02, V-003/V-004.
- [ ] T004 Assemble protected typed/failure converter and inject it into starter/worker/replay clients.
  - Depends: T003. Accept: message/stack/nested failure details protected, public types approved, semantic retry/cancellation preserved and namespace mismatch rejected. Scope: F03-03/F03-04, V-005.
- [ ] T005 Add finite test-only qualification Workflow/Activity and worker registration.
  - Depends: T004. Accept: one bounded Activity with heartbeat/echo/explicit ApplicationError variants; production rejects registration; sandbox execution passes. Scope: F03-05, V-019.
- [ ] T006 Implement one-shot encrypted smoke plus real raw-history inspection.
  - Depends: T005. Accept: deploy WORKER and run success/failure cases through independent secure client; sample raw pending-Activity heartbeat details during its finite wait; no synthetic marker in protected history/pending fields/logs; authorized values decode. Scope: F03-05/F03-06, V-005.
- [ ] T007 Add encrypted fixture replay and an incompatible negative control.
  - Depends: T006. Accept: actual historical namespace and keys/factory used; fixtures synthetic; positive replay passes, negative fails, no external side effects. Scope: F03-04/F03-06, V-020.
- [ ] T008 Build/deploy both-role checkpoint and record `docs/checkpoints/F03.md`.
  - Depends: T007. Accept: image/config/security smoke evidence reproducible, deadlines/cleanup/rollback demonstrated; qualification-only production eligibility stated. Scope: all F03, scoped V-002–V-005/V-019/V-020.
