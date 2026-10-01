# F07 — Start workflows from one trusted Kafka binding

**Status:** specified; no implementation, build, deployment or smoke has been executed by this document.

**Roadmap entry:** [F07 in the parent feature index](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).

**Predecessor:** F06: authorized workflow status/result (007). **Program boundary:** the same temporal-enterprise-framework repository/image with APP_ROLE=INGESTION or WORKER. Feature IDs denote deployable increments, not independent microservices.

## Outcome and scope

INGESTION additionally consumes one selected tenant topic/group and durably starts the same registered encrypted workflow already reachable through REST. The Kafka canonical UUID key equals envelope message_id and is used verbatim as Temporal workflow ID. The common start service supplies policies, encrypted identity memo, routing and reconciliation.

Qualify exactly one trusted binding and one active consumer instance. Permanently invalid/proven-conflicting records pause their partition and emit a safe signal pending F08; they are never lost or implicitly quarantined. F09 qualifies multiple instances on that binding; F10 enables deployed multi-tenant bindings. This is a development/staging increment in the same image and roles.

## Functional contract

- **F07-R01:** Resolve topic/group/credential profile/tenant from trusted routes. Validate byte/depth/schema/UTF-8/canonical-key equality before any start; public data cannot select namespace, queue, credentials or output topic.
- **F07-R02:** One owning consumer thread performs create/subscribe/poll/pause/resume/commit/close. Disable automatic commit and offset storage; bounded bridges keep blocking broker calls off asyncio and retain control capacity when full.
- **F07-R03:** At most one unresolved record per partition,32 global Kafka starts and 256 global buffered source records; REST retains its separate finite admission limit. Polling continues during slow starts and paused partitions.
- **F07-R04:** Start acknowledgment or verified retained duplicate may settle a record. Ambiguous response, unavailable decrypt key/evidence and dependency outage stay retryable. Confirmed missing/incompatible identity memo or proven content/route conflict is a permanent identity conflict that pauses the record here until F08 disposition; absence is not confused with unavailable cryptographic evidence.
- **F07-R05:** Commit offset N+1 only for a contiguous acknowledged prefix through N under owned assignment. Commit failure/lost response never discards work; crash after durable start before commit redelivers and reconciles the same UUID.
- **F07-R06:** Invalid input pauses only its partition; safe blocked reason/source coordinates expose no value, JWT, sensitive header, digest or exception body. Other partitions and HTTP progress within limits.
- **F07-R07:** Lifespan jointly supervises consumer/HTTP resources; fatal bridge failure tears down INGESTION. Close/commit occur on the owner thread, and unconfirmed work remains available for redelivery.

## Acceptance and evidence

A real valid keyed record starts a workflow, advances offset+1 after acknowledgment and is readable through authorized status. Same content/UUID reconciles without another retained execution. Kill after start acknowledgment before commit and prove safe redelivery. Invalid input pauses uncommitted while another partition progresses; stalled Temporal leaves queues bounded and API/probes responsive.

Each task supplies its local scoped evidence; referenced umbrella V IDs are traceability to final release gates. A passing local case does not mark unrelated future cases complete. Real service/cluster checks cannot be satisfied by mocks. Tests use synthetic data and injected secrets, never production histories or committed keys.

## Deployable checkpoint

Build a cumulative immutable F07 image and run both roles with mounted synthetic TLS/key material and one selected binding. Smoke one REST and one Kafka start with distinct UUIDs, authorized status and acknowledged reference output. Capture digest/config/group/offset evidence.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Rollback contract

Drain/suspend Kafka intake before restoring the prior compatible digest/config. Preserve group offsets, namespace/route binding, histories, source retention and decrypt keys; leave pending intake suspended until a qualified consumer is available. Never reset a group or change UUIDs.

## Shared normative references

[Platform specification](../001-enterprise-workflow-platform/spec.md), [roadmap](../001-enterprise-workflow-platform/roadmap.md), [data model/contracts](../001-enterprise-workflow-platform/data-model.md), [security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md), [verification](../001-enterprise-workflow-platform/verification.md). Resolve disagreement before implementation; this feature refines incremental scope without weakening final production requirements.

