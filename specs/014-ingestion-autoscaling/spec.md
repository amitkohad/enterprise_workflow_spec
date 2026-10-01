# F13 — Scale coupled API/Kafka ingestion with one controller

**Status:** specified; no implementation, build, deployment or smoke has been executed by this document.

**Roadmap entry:** [F13 in the parent feature index](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).

**Predecessor:** F12: Kubernetes release (013). **Program boundary:** the same temporal-enterprise-framework repository/image with APP_ROLE=INGESTION or WORKER. Feature IDs denote deployable increments, not independent microservices.

## Outcome and scope

One KEDA ScaledObject/HPA per ingestion Deployment sizes the coupled API/Kafka process from its selected topic/group lag plus independent REST demand. Scaling is qualified against simultaneous tenants and partition assignments; API-only demand cannot be hidden by an empty Kafka topic.

Add chart/scaler configuration and measured capacity thresholds to the deployed F12 application. Use existing metrics and F09 bounded multi-binding runtime. No second ingestion service, second HPA, HTTP polling sidecar or scale-to-zero baseline. KEDA/Prometheus credentials and controllers are enterprise dependencies.

## Functional contract

- **F13-R01:** Exactly one ScaledObject and managed HPA owns each INGESTION Deployment; no competing HPA or independent controller writes its scale. Kafka bindings use explicit group/topic/profile scopes and REST uses a validated Prometheus request-rate signal.
- **F13-R02:** Production minReplicaCount2 and no idleReplicaCount0. Overall max/fallback/stabilization are finite and recorded. polling30/cooldown300 are illustrative; cooldown concerns scale-to-zero, while HPA stabilization governs nonzero scale-down.
- **F13-R03:** Kafka-only useful consumers are bounded by each binding's partitions; aggregate partition count across tenant groups is not a single group's pod parallelism. REST may justify replicas above partitions with explicit allowIdleConsumers policy and measured headroom.
- **F13-R04:** Qualify simultaneous tenant demand and shared process/API capacity. Multiple independent lag triggers yield maximum demand and may understate aggregate load; use tested conservative thresholds or a verified aggregate/composite signal in the same owner.
- **F13-R05:** Prometheus queries select the intended deployment and return one finite nonnegative scalar; measured healthy zero differs from absent/stale series. Required metrics use ignoreNullValues=false and qualified fallback >=2.
- **F13-R06:** Scaler credentials permit only relevant broker metadata/group-offset reads and approved Prometheus access, independent of application credentials; TLS and network allowances are explicit.
- **F13-R07:** API-only, Kafka-only and mixed burst/sustained tests verify replica decision, startup delay, partition assignment, lag/latency and source integrity. No claim that polling30 guarantees30s recovery.

## Acceptance and evidence

On real KEDA/Prometheus/Kafka cluster, Kafka-only backlog scales useful consumers, REST-only traffic can scale API capacity with zero Kafka lag, and combined tenant load does not overwhelm shared budgets. No absent metric or scaler outage sends fleet below2; observe qualified fallback/stabilization and no skipped offsets during rebalances. Report API/Kafka latency and actual replica/capacity limits.

Each task supplies its local scoped evidence; referenced umbrella V IDs are traceability to final release gates. A passing local case does not mark unrelated future cases complete. Real service/cluster checks cannot be satisfied by mocks. Tests use synthetic data and injected secrets, never production histories or committed keys.

## Deployable checkpoint

Build/deploy cumulative F13 image/config and one ingestion ScaledObject with mounted TriggerAuthentication references. Record live query outputs/units, thresholds, per-binding partition counts, API per-pod capacity, desired/current replicas and independent demand smoke evidence. Production remains blocked by F15/F16/full gates.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Rollback contract

Pause/remove scaling through the single documented owner and restore measured fixed replicas>=2 before reverting compatible values/image. Preserve group offsets and route selection. Do not add a manual HPA alongside KEDA or scale pinned worker versions as part of ingestion rollback.

## Shared normative references

[Platform specification](../001-enterprise-workflow-platform/spec.md), [roadmap](../001-enterprise-workflow-platform/roadmap.md), [data model/contracts](../001-enterprise-workflow-platform/data-model.md), [security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md), [verification](../001-enterprise-workflow-platform/verification.md). Resolve disagreement before implementation; this feature refines incremental scope without weakening final production requirements.

