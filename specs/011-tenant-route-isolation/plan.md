# F10 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md)

**Prerequisites:** F09 deployed Kafka recovery and F06 authorized status/results. The
current cumulative image already runs one tenant through REST/Kafka and executes the
acknowledged reference Workflow. Implement eight local tasks; extend existing behavior.

## Major capability

Replace the single selected fixture route with approved bounded inventory/profile selection.
Preserve API/event schemas, encrypted payload/memo semantics, manual commit frontiers and
role boundaries. No new role, application service, database or control plane is introduced.

| Area | Change |
| --- | --- |
| `app/config/{routing,credentials,settings}.py` | Full inventory/profile and per-process selection validation |
| `app/temporal/client/builder.py` | Bounded namespace/profile/event-loop client registry |
| start/read service and API auth | Authorized route resolution, memo binding and concealed reads |
| `app/events/{consumer,bridge}.py` | Selected per-binding owners with shared process budgets |
| Worker factory/main | One namespace, 1–4 queues, aggregate capacity allocation and lifecycle |
| `tests/{unit,integration}/` | Cross-tenant routing, profile/ACL, resource and recovery evidence |

Each selected consumer binding has its configured topic/group/profile and one owning
thread. Data buffers and start semaphores are global, not per binding. Retain reserved
control/rebalance capacity from F09. A stale callback from one assignment/binding cannot
settle another binding's offsets or unlock its request under the wrong tenant context.

Build clients from the trusted mounted profile map once per approved namespace/profile/
immutable startup credential snapshot/event-loop key; do not select
credentials from JWT fields, events, URLs or arbitrary headers. Ingestion allows at most
16 namespace/profile clients and 16 selected consumers. Worker selects one namespace;
at most four approved queues receive explicit allocations whose sums are at most 32
Workflow tasks, 64 Activities and 1000 cached Workflows. Share at most 64 producer waits
across the process. For example, four equal queues receive 8/16/250 each, not the full
per-process defaults four times. Validate allocations before any worker starts polling.

Role shutdown releases registry references and any role-owned resources using the pinned
SDK's supported lifecycle. Qualify the available cleanup API; `Client.close()` must not be
assumed or generated when the selected SDK does not provide it. Mounted-file changes do
not silently mutate an existing client/snapshot; rotation is a controlled restart.

The internal route snapshot and encrypted memo keep namespace/queue/output binding stable;
inventory revision is diagnostic only when the binding is unchanged. Existing bindings
cannot move through an ordinary reload/rollout. Multiple tenant events may share output
topics or aggregate downstream, so verify the composite `(tenant_id,publish_id)` identity.

## Checkpoint deployment and smoke

Generate `config/checkpoints/f10/` with at least two synthetic tenant/profile/binding
examples and same-image commands in `docs/checkpoints/F10.md`. Deploy one INGESTION and
two WORKER namespace configurations using `python -m app.main`; these are repeated pools
of the two existing roles, not added programs. Credentials/tokens remain mounted files.

`scripts/checkpoints/f10_smoke.py` accepts route/profile/token fixture paths, starts the
same UUID for both tenants through REST/Kafka, verifies correct independent namespace
references and authorized results, and confirms concealed cross-tenant status. It observes
outgoing events with a synthetic authorized consumer and validates tenant-aware aggregate
deduplication. Run negative broker ACL checks using scoped external credentials, not an
application admin client. Inject a binding-local outage/rebalance and verify other binding
commit frontiers plus the global buffer/capacity ceiling.

## Rollback and production eligibility

Configuration rollback cannot discard accepted tenant histories. Stop new affected-route
admission, retain their F10-compatible reader/Worker/profile/keyring pools, and restore only
proven compatible configurations. A pre-F10 single-tenant downgrade is allowed only if no
new tenant obligation exists; otherwise keep the compatible F10 version until the stated
retention/replay window has ended. Test that unsafe removal/downgrade is refused and that
an unchanged-binding revision rollback preserves duplicate recognition.

Record actual image/config identities, tenant/binding/capacity evidence and covered shared
verification cases. This increment provides the multi-tenant portions of the shared
security/routing/recovery gates; it does not claim that future telemetry, Kubernetes,
scaling or complete release qualification has already passed.
