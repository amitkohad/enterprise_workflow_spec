# F04 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md)

**Prerequisite checkpoint:** F03 image runs both roles and proves encrypted mTLS Workflow
round trips. Implement the eight local tasks in [tasks.md](tasks.md); these task IDs are
local to this feature and replace the corresponding global planning-reference items.

## Major capability

Extend the same application with durable, acknowledged Kafka publication. Use existing
settings, route selection, converter, client builder, Worker factory and lifecycle. No
additional persistence, gateway route or deployment role is introduced.

| Area | Change |
| --- | --- |
| `app/temporal/models.py` | `WorkflowInput`, immutable route snapshot, outbound event and receipt models |
| `app/events/producer.py` | Bounded producer bridge, callback futures, cancellation/drain ownership |
| `app/temporal/activities/system_activities.py` | `publish_event` with route checks, heartbeat and typed acknowledged receipt |
| `app/temporal/workflows/enterprise_event_workflow.py` | Deterministic event construction and one Activity invocation |
| `app/temporal/registry.py`, Worker factory | Production registration; qualification echo remains test-only |
| `tests/{unit,workflow,integration}/` | Callback, retry, determinism, broker and encryption evidence |

Create the producer once at Worker startup; do not instantiate it per Activity attempt.
Its owning thread services broker callbacks and completes asyncio futures safely.
Bound pending publishes by the configured Activity capacity. Await delivery acknowledgment
under the Activity deadline while heartbeating, and propagate cancellation cleanly.

The Workflow records the output topic in its encrypted input and constructs stable event
bytes from recorded input. Clock, UUID generation, Kafka, key access and live configuration
remain outside Workflow code. Activity retries may publish duplicates. The downstream
contract identity is `(tenant_id,publish_id)` even when output topics are aggregated.

## Checkpoint deployment and smoke

Generate `config/checkpoints/f04/` with path-only environment/config placeholders and
`docs/checkpoints/F04.md` with reproducible `docker build` / `docker run --env-file`
commands for the same image, mounted certificate/keyring/Kafka credentials and one
namespace/queue. Use `python -m app.main`; the smoke client is an operator script, not
a third application role.

Keep the synthetic checkpoint at `APP_ENV=test` with F03's explicitly qualified bounded
test Worker configuration; production PINNED version routing is delivered in F15. The
reference Workflow is the real reviewed business registration, while echo qualification
registration is disabled for this checkpoint. This testing profile never relaxes mounted
mTLS, encrypted payloads or authenticated broker connections.

Generate `scripts/checkpoints/f04_smoke.py` with explicit route/message ID/profile inputs.
It starts the registered Workflow using the shared client, verifies the broker event,
binds the selected run for the completed receipt, checks raw history for a sensitive
sentinel, and exits nonzero on failure. All data is synthetic. Record actual image digest
and broker/server versions; do not substitute mocked broker delivery for staging evidence.

## Rollback and production gate

Stop new F04 starts. Retain an F04-compatible Worker while accepted reference executions
remain open; the F03 production registry cannot execute the new Workflow type. A downgrade
to F03 is safe only when no F04 execution still requires polling, or when an explicitly
retained compatible F04 pool handles it. Never reset histories or delete keys to enable
rollback. Demonstrate both safe completed-run rollback and refusal of an unsafe active-run
downgrade in the checkpoint procedure.

Preserve F03 smoke evidence and add broker TLS, acknowledgment/retry/cancellation and
encrypted-history evidence. This checkpoint is controlled-staging eligible; general
production requires the cumulative release gates in the shared verification contract.
