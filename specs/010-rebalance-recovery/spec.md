# F09 — Recover ownership across bounded consumer fleets

**Status:** specified; no implementation, build, deployment or smoke has been executed by this document.

**Roadmap entry:** [F09 in the parent feature index](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).

**Predecessor:** F08: DLQ disposition (009). **Program boundary:** the same temporal-enterprise-framework repository/image with APP_ROLE=INGESTION or WORKER. Feature IDs denote deployable increments, not independent microservices.

## Outcome and scope

Ingestion preserves acknowledged source ordering and retained workflow identity as assignments move between instances, starts complete after revocation, commits fail or lose responses, and a consumer thread fails. This checkpoint runs one trusted tenant binding per process with at least two ingestion instances. F10 introduces deployed multi-profile/binding/client selection.

The selected consumer owns one thread; partition operations share global admission/buffering and the INGESTION supervisor. Qualify at least two ingestion instances against a real broker using that one binding. Unit-test finite future multiplexing/fairness state without claiming deployed multi-tenant selection before F10. This unlocks later Kubernetes/scaling increments but remains staging-only until production release gates.

## Functional contract

- **F09-R01:** Tag every admitted record/start/DLQ completion/commit with binding, partition and assignment generation. New assignment means new generation; obsolete completion cannot advance current fences.
- **F09-R02:** On revoke stop intake for affected partitions and commit only already-settled owned positions within callback deadline. Lost ownership never commits; a transmitted start that finishes later is fenced out.
- **F09-R03:** Current owner redelivers from retained group positions and reconciles the same UUID/memo. Failed/ambiguous commits never authorize discarding unresolved source work.
- **F09-R04:** Poll/rebalance/control service continues while data is paused or queue full. Pin a qualified broker protocol and explicit poll/max.poll.interval/callback/retry budgets.
- **F09-R05:** F09 runs exactly one trusted binding/profile/client per ingestion process, one unresolved record per partition and global Kafka 32 active starts/256 buffered source records. Partition fairness prevents blocked work monopolizing all permits. Future multiplexing unit tests preserve the final16-binding/client bound; actual multi-profile deployment/tenant isolation belongs to F10.
- **F09-R06:** Fatal consumer/coordinator exit reaches asyncio supervision, makes INGESTION unready, closes every bridge/HTTP resource and exits nonzero. Transient remote outage retains liveness and bounded retry.
- **F09-R07:** Shutdown stops intake, targets90s normal drain and 110s hard process exit; only current eligible fences commit. Consumer close/thread join never blocks the event loop and unresolved work is redelivered.

## Acceptance and evidence

Run >=2 instances on one trusted binding; repeatedly add/remove one while starts/DLQ acknowledgments are delayed. Capture actual commits and source inventory: no stale-generation commit, skipped offset or second retained execution. Force failed/uncertain commit, fatal consumer-thread teardown and slow partition under global saturation; peers recover, polling progresses and bounds/shutdown targets hold. Full distinct-tenant authorization and deployed multi-binding selection are qualified by F10.

Each task supplies its local scoped evidence; referenced umbrella V IDs are traceability to final release gates. A passing local case does not mark unrelated future cases complete. Real service/cluster checks cannot be satisfied by mocks. Tests use synthetic data and injected secrets, never production histories or committed keys.

## Deployable checkpoint

Build cumulative F09 image and run both roles plus >=2 INGESTION instances on the same single selected synthetic binding. Record protocol/version, assignment generations, offsets, memory/task bounds, smoke results and digest/config. Kubernetes is not required to demonstrate this checkpoint; independent image containers/processes suffice.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Rollback contract

Pre-F09 images are qualified only for one active consumer instance. Suspend intake, drain and reduce the fleet to its predecessor's supported shape before restoring compatible F07/F08 digest. Preserve groups/offsets/routes/source retention/keys and pending records for a qualified consumer; do not downgrade a live multi-instance fleet without restriction.

## Shared normative references

[Platform specification](../001-enterprise-workflow-platform/spec.md), [roadmap](../001-enterprise-workflow-platform/roadmap.md), [data model/contracts](../001-enterprise-workflow-platform/data-model.md), [security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md), [verification](../001-enterprise-workflow-platform/verification.md). Resolve disagreement before implementation; this feature refines incremental scope without weakening final production requirements.

