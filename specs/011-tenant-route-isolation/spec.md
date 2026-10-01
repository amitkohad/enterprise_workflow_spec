# F10 — Bounded tenant routing and isolation

**Increment:** F10 | **Application:** `temporal-enterprise-framework`  
**Prerequisites:** deployed [F09 rebalance recovery](../010-rebalance-recovery/spec.md)
and verified [F06 authorized status/results](../007-authorized-status-results/spec.md)  
**Deliverable:** expand the same runnable application from its single-tenant checkpoint to a finite approved enterprise tenant inventory.

**Parent:** [feature roadmap](../001-enterprise-workflow-platform/roadmap.md) ·
[shared requirements](../001-enterprise-workflow-platform/spec.md). This increment completes
the multi-tenant portions of FR-ROUTE-01–04/FR-SEC-05 and applies FR-WF-04 and FR-KAFKA-01–05
to multiple bindings; later operational release gates remain pending.

## User outcome and scope

Operators configure several approved tenant namespaces, credential profiles, Kafka bindings
and domain queues. Existing REST starts/status and Kafka ingestion route each request to
its authorized tenant while keeping resources bounded. Callers retain the same wire format;
they cannot select a namespace, queue, output topic or credential. Use the
[shared data model](../001-enterprise-workflow-platform/data-model.md),
[routing schema](../001-enterprise-workflow-platform/contracts/routing.schema.json),
[example](../001-enterprise-workflow-platform/contracts/routing.example.yaml) and
[OpenAPI](../001-enterprise-workflow-platform/contracts/openapi.yaml) as authority.

The inventory is config-driven and finite. A rolling configuration deployment can add
approved routes after provisioning, but v1 has no live reload, namespace/topic creation,
wildcard tenant routing, administrative CRUD API, or per-message client creation.
External owners provision namespaces, broker ACLs and mounted credentials.

## Acceptance scenarios

1. Two approved tenants start the same UUID independently in their different namespaces;
   each status request reads only its authorized execution and its correct route receipt.
2. Replaying one tenant's UUID with matching content verifies its existing encrypted memo;
   changed content/binding conflicts. Another tenant's execution is not duplicate evidence.
3. A JWT tenant/domain mismatch produces no unauthorized Temporal RPC. An event tenant
   mismatch versus its configured input topic takes the existing safe metadata-only DLQ
   path; wrong broker credentials cannot read another tenant's input topic.
4. Route validation rejects shared cross-tenant namespaces, duplicate/unknown routes,
   missing profiles/registrations and unsafe namespace/queue/output-topic movement.
   An unrelated inventory revision change does not invalidate a matching duplicate.
5. Ingestion selects at most 16 consumer bindings and 16 namespace/profile clients; one
   owner thread per consumer. Global bridge budgets stay 32 in-flight starts/256 buffered
   records, with one unresolved record per partition across every binding.
6. Each WORKER process selects exactly one namespace and at most four queues. Aggregate
   process budgets remain Workflow tasks 32, Activities 64, cached Workflows 1000 and
   pending producer waits 64; selecting more queues must not multiply those budgets.
7. Outgoing events from two tenants using the same UUID remain distinct after topic
   aggregation under `(tenant_id,publish_id)`; repeated delivery within a tenant deduplicates.
8. Independent outage/rebalance in one binding respects its assignment fence and cannot
   commit/route another tenant's unresolved record; restart rebuilds only approved resources.

## Requirements

- **F10-01:** Validate trusted inventory and process selections before opening connections;
  enforce one preprovisioned namespace/Temporal profile per tenant isolation boundary.
- **F10-02:** Load path-only mounted profile mappings. Build/cache one client per approved
  namespace/profile/immutable startup credential snapshot/event-loop, with identical
  encryption policy and explicit bounds. Cleanup releases registry references and
  role-owned resources through the pinned SDK's supported lifecycle; do not invent `Client.close()`.
- **F10-03:** Route verified REST grants and topic-bound Kafka tenants through the same
  resolver. Record immutable namespace/queue/output snapshot and compare it on duplicates.
- **F10-04:** Instantiate each selected Kafka group/profile with dedicated consumer
  ownership while preserving F09 commit/rebalance state machines and global backpressure.
- **F10-05:** Allocate Worker capacities across selected queues so sums respect process
  budgets. Validate allocation before polling and share producer pending capacity.
- **F10-06:** Freeze existing namespace/queue/output-topic bindings throughout supported
  replay/retention. Add routes by controlled configuration rollout, never silently migrate
  existing IDs or remove required old credentials/keys/pollers.
- **F10-07:** Prove REST read/start isolation, broker ACL/topic binding, tenant-aware
  downstream identity, multi-binding recovery and configured-capacity limits.

## Deployable checkpoint and rollback

Build `temporal-enterprise-framework:f10-tenant-isolation`; deploy one bounded INGESTION configuration and
one or more tenant-specific WORKER pools using that same image. Each Worker still owns one
namespace. Run `scripts/checkpoints/f10_smoke.py` with two tenant/profile/token fixtures:
same-ID independent starts, own versus concealed cross-tenant reads, Kafka routing and
aggregate duplicate-event identities. Record commands/evidence in `docs/checkpoints/F10.md`.

Rollback first stops admission for affected new routes and preserves compatible Workers,
keys and readers for their accepted histories. A pre-F10 single-tenant image cannot replace
resources still required by newly admitted tenants. Downgrade only before those tenants
receive work, or retain an F10-compatible pool until the replay/retention obligation ends.
Controlled staging deployment is allowed; general production additionally needs cumulative
security, recovery, observability, Kubernetes/scaling and release qualification.
