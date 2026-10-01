# F08 — Acknowledge metadata-only DLQ disposition

**Status:** specified; no implementation, build, deployment or smoke has been executed by this document.

**Roadmap entry:** [F08 in the parent feature index](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).

**Predecessor:** F07: Kafka trigger start (008). **Program boundary:** the same temporal-enterprise-framework repository/image with APP_ROLE=INGESTION or WORKER. Feature IDs denote deployable increments, not independent microservices.

## Outcome and scope

Permanent invalid input or proven identity conflict gains an acknowledged metadata-only DLQ disposition, allowing its source partition to progress safely. Existing valid records remain on F07's common workflow-start path. Enterprise Kafka supplies topics/ACLs/retention/TLS; no quarantine service or application replay endpoint is introduced.

Extend the existing unresolved-record state machine and confirmed producer inside INGESTION. Full multi-instance ownership qualification remains F09. The cumulative same-image checkpoint is development/staging eligible until later production gates.

## Functional contract

- **F08-R01:** Only schema/key/size/depth/topic-tenant/route violations and proven identity conflicts, including confirmed missing/incompatible identity memo, are permanent record failures. Temporal/broker/auth/key/unknown-outcome outages remain transient/operator conditions, never bulk-DLQ causes.
- **F08-R02:** Validate the committed DLQ schema and include only its defined fields. Deterministic identity comes from source topic/partition/offset; safe fields include its allowlisted reason, approved source coordinates/timestamps and configured tenant_id. Do not invent route/domain fields forbidden by the schema.
- **F08-R03:** Never put source values, business headers, digest, JWT, decrypted data, stack or raw exception body into DLQ/logs. Safe metadata must not be inferred from invalid untrusted business content.
- **F08-R04:** Publish only to the binding's configured DLQ using its mounted tenant-scoped producer profile. Enqueue is not acknowledgment; failed/ambiguous/deadline delivery keeps the source unresolved.
- **F08-R05:** Confirmed DLQ delivery enters the existing contiguous offset fence; no commit before acknowledgment and no later record skipping an unresolved prefix.
- **F08-R06:** Crash after DLQ acknowledgment before source commit may repeat the same deterministic DLQ identity. Consumers/tools deduplicate by that identity; no distributed exactly-once transaction is promised.
- **F08-R07:** Unavailable DLQ pauses affected partitions with bounded retry and ongoing poll/control service. Operator replay requires the original retained protected source record and approved enterprise tooling, not reconstruction from metadata-only DLQ.

## Acceptance and evidence

Malformed key/schema yields schema-conforming safe DLQ bytes acknowledged before source offset advances. DLQ outage retains original offset, bounded memory and other-partition progress; restoration settles safely. Ack-before-commit crash repeats the same DLQ ID without loss. Valid data during Temporal/key/auth outage never becomes a bulk permanent disposition.

Each task supplies its local scoped evidence; referenced umbrella V IDs are traceability to final release gates. A passing local case does not mark unrelated future cases complete. Real service/cluster checks cannot be satisfied by mocks. Tests use synthetic data and injected secrets, never production histories or committed keys.

## Deployable checkpoint

Build the cumulative F08 image; run both roles with one selected binding and configured DLQ/profile. Smoke valid workflow start plus invalid-record acknowledged disposition, scan for sensitive markers and record source/DLQ coordinates and image/config.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Rollback contract

Drain/suspend before restoring compatible F07 behavior. Preserve source/DLQ records, group offsets, retained IDs and keys; pending invalid records return to F07 pause/alert. No automatic replay, topic deletion or offset reset.

## Shared normative references

[Platform specification](../001-enterprise-workflow-platform/spec.md), [roadmap](../001-enterprise-workflow-platform/roadmap.md), [data model/contracts](../001-enterprise-workflow-platform/data-model.md), [security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md), [verification](../001-enterprise-workflow-platform/verification.md). Resolve disagreement before implementation; this feature refines incremental scope without weakening final production requirements.

