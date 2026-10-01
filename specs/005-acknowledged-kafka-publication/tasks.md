# F04 tasks — acknowledged Kafka publication

Prerequisite: F03 checkpoint passed. Execute sequentially; a task is complete only after
its acceptance checks pass. IDs are local to this directory. Reuse the same image/roles.

- [ ] T001 — Typed publication contract. Add the shared internal `WorkflowInput`,
  immutable route snapshot, outgoing event and `PublishReceipt` models in
  `app/temporal/models.py`; validate against authoritative schemas. Test additional fields,
  topic allowlisting, size bounds and stable publish-ID cross-field rules.
  - Depends: F03 accepted deployed checkpoint.
  - Accept: Contract examples pass; invalid route, size and publish-ID cross-field cases fail without producing a valid model.

- [ ] T002 — Acknowledged producer bridge. Implement the bounded, lifecycle-owned
  producer in `app/events/producer.py`, including callback servicing and thread-safe
  futures. Test enqueue versus acknowledgment, delivery failure, full buffer and bounded
  close; no broker call blocks the event loop.
  - Depends: T001.
  - Accept: Enqueue-only futures remain pending; delivery callback success/failure and bounded close tests pass.

- [ ] T003 — Reusable publish Activity. Implement `publish_event` with tenant/topic
  checks, explicit deadlines/retries, heartbeat and cancellation. Test that no receipt
  returns before successful delivery and that invalid routes fail without publishing.
  - Depends: T002.
  - Accept: Only acknowledged delivery yields a receipt; invalid topic and canceled/expired attempt tests produce no false success.

- [ ] T004 — Deterministic reference Workflow. Implement `EnterpriseEventWorkflow`
  using recorded input/route only. Test immutable event bytes, stable publish ID,
  `workflow.processed` semantics and typed receipt in `WorkflowEnvironment`.
  - Depends: T003.
  - Accept: WorkflowEnvironment completes with the typed receipt and replay preserves recorded event bytes and publish ID.

- [ ] T005 — Worker registration and lifecycle. Register the reference Workflow and
  Activity, inject the shared producer, and exclude `QualificationEchoWorkflow` from
  production. Start the same Worker role, run one synthetic encrypted reference execution,
  and verify producer ownership/cancellation on shutdown.
  - Depends: T004.
  - Accept: Deployed reference execution returns encrypted receipt; production registration rejects qualification echo.

- [ ] T006 — Real broker retry evidence. Add integration checks for positive/negative
  broker TLS, delivery callback failure and broker success followed by lost Activity
  completion acknowledgment. Prove duplicate events preserve `(tenant_id,publish_id)`;
  document downstream tenant-aware deduplication and retain F03 history-protection checks.
  - Depends: T005.
  - Accept: Real TLS, delivery failure and acknowledgment-loss checks record at-least-once outcomes with tenant-aware dedup identity.

- [ ] T007 — Deploy and smoke the increment. Generate `config/checkpoints/f04/`,
  `scripts/checkpoints/f04_smoke.py` and exact same-image container commands. Build/run
  image `temporal-enterprise-framework:f04-acknowledged-publication` against controlled dependencies and verify
  acknowledged event, completed receipt, health and encrypted history. Record actual
  evidence or a clearly blocked external prerequisite; do not mark unrun checks passed.
  - Depends: T006.
  - Accept: Built same-image checkpoint records its digest and real acknowledged-event/receipt/history smoke, or an explicit unrun blocker.

- [ ] T008 — Rollback and release record. Write `docs/checkpoints/F04.md` with image
  digest, dependency/config identity, smoke results, safe completed-run downgrade and
  active-run rollback guard. Preserve F03-compatible checkpoint and F04 pollers/keys when
  required. Mark staging versus general-production eligibility explicitly.
  - Depends: T007.
  - Accept: Checkpoint documents safe completed-run downgrade and refuses unsupported active-run downgrade while preserving keys/pollers.
