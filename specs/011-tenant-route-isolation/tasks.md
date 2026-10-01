# F10 tasks — bounded tenant routing and isolation

Prerequisites: F09 Kafka recovery and F06 authorized status/results checkpoints passed.
Local IDs are scoped to this directory. Extend the same cumulative runnable application.

- [ ] T001 — Validate inventory and selections. Implement full trusted route/profile
  shape and cross-field checks, finite selections and retention-safe binding validation.
  Test duplicate routes, shared cross-tenant namespace, missing profile/type, unknown
  worker queue and unsafe namespace/queue/output movement before connections open.
  - Depends: F09 and F06 accepted deployed checkpoints.
  - Accept: Invalid inventory/profile/selection and unsafe binding movement fail before any connection is opened.

- [ ] T002 — Bound namespace clients. Expand the existing builder into a registry keyed
  by approved namespace/profile/immutable startup credential snapshot/event-loop, max 16
  selected clients. Test profile isolation, identical converter policy, no per-message
  construction, supported lifecycle/reference cleanup and limit failure; do not invent `Client.close()`.
  - Depends: T001.
  - Accept: Client cache stays within 16, isolates namespace/profile/startup snapshot/event-loop and releases supported resources/references on shutdown.

- [ ] T003 — Route authorized REST operations. Expand existing start/read services to
  tenant/domain inventory resolution without wire changes. Test same UUID across two
  namespaces, own versus concealed cross-tenant reads, memo binding conflicts and unchanged
  binding with revised inventory; denied requests make no unauthorized backend calls.
  - Depends: T002.
  - Accept: Two tenants independently use the same UUID; own reads work, cross-tenant reads conceal, and revision-only change remains duplicate.

- [ ] T004 — Expand selected Kafka bindings. Create at most 16 owned group/profile
  consumers with global 32 in-flight/256 buffered limits and reserved control capacity.
  Test trusted-topic tenant checks, broker ACL denial, one unresolved record per partition,
  binding-local outage and cross-binding assignment/commit fences inherited from F09.
  - Depends: T003.
  - Accept: At most16 owned consumers preserve global 32/256 limits and per-partition/binding commit fences under outage/rebalance.

- [ ] T005 — Allocate aggregate Worker capacity. Support one namespace and at most4
  queues per Worker process, distributing Workflow 32/Activity 64/cache 1000 budgets across
  queues and producer wait 64 globally. Test over-allocation startup rejection, sum bounds,
  correct registrations and shared producer/lifecycle shutdown.
  - Depends: T004.
  - Accept: One-namespace maximum4-queue allocation sums remain within 32/64/1000 plus64 producer waits; over-allocation fails startup.

- [ ] T006 — Prove tenant-aware publication identity. Add a real-service two-tenant
  same-UUID scenario whose events are aggregated. Verify independent starts/results and
  `(tenant_id,publish_id)` downstream deduplication, including repeated Activity delivery.
  Retain prior encrypted-history, auth, DLQ and rebalance evidence without replacing it.
  - Depends: T005.
  - Accept: Aggregated same-UUID events remain distinct across tenants and repeated delivery deduplicates within (tenant_id,publish_id).

- [ ] T007 — Deploy and smoke multiple tenants. Generate `config/checkpoints/f10/`,
  `scripts/checkpoints/f10_smoke.py` and same-image container commands for one INGESTION
  plus tenant WORKER pools. Run own/cross-tenant REST, Kafka routes, aggregate events and
  capacity/recovery smoke; record actual image/config/dependency identities or blockers.
  - Depends: T006.
  - Accept: Same-image multi-tenant smoke records routing, authorized reads, Kafka events and bounded recovery evidence or explicit blockers.

- [ ] T008 — Record safe rollback and eligibility. Write `docs/checkpoints/F10.md`,
  preserving reader/poller/key/profile obligations for admitted tenants. Demonstrate
  unchanged-binding revision rollback and refusal to discard an active/newly retained
  tenant through a pre-F10 single-tenant downgrade. Map covered shared gate cases and
  explicitly leave later telemetry/Kubernetes/scaling/release qualification pending.
  - Depends: T007.
  - Accept: Unsafe tenant removal/pre-F10 downgrade is refused; unchanged-binding rollback preserves history/read/poller/key obligations.
