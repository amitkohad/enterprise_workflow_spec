# F14 — Scale worker capacity from task pressure and scheduling delay

**Status:** specified; no implementation, build, deployment or smoke has been executed by this document.

**Roadmap entry:** [F14 in the parent feature index](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).

**Predecessor:** F13: ingestion autoscaling (014). **Program boundary:** the same temporal-enterprise-framework repository/image with APP_ROLE=INGESTION or WORKER. Feature IDs denote deployable increments, not independent microservices.

## Outcome and scope

Each worker capacity/build Deployment obtains a single qualified KEDA owner using actual SDK scheduling-delay and capacity metrics. Ingestion trigger lag is excluded: it can disappear immediately after start while workflow/activity tasks remain queued. Worker builds remain separately identifiable for later PINNED version retention.

Use process-wide 32 Workflow/64 Activity/1000 cache allocations and shared producer waits64 across 1-4 configured queues. Capture SDK metrics on 9090 separately from application8080. Enterprise Prometheus/KEDA are external; no backlog database, custom scheduler service or fabricated SDK gauge.

## Functional contract

- **F14-R01:** Each active worker Deployment/build has one ScaledObject/HPA, baseline2 and finite maximum/fallback; no baseline scale-to-zero. Filter series by actual Kubernetes scrape build/deployment labels plus configured namespace/queues so old/new fleets cannot hide each other's demand.
- **F14-R02:** Inspect real pinned SDK metric names/prefixes/labels/units and retain capture evidence. Queries use workflow/activity schedule-to-start histograms and slots used/available; do not invent backlog gauges or assume all SDK versions emit identical series.
- **F14-R03:** Capacity is measured against per-process allocated budgets and safe per-pod demand with headroom. Sum queue allocations <=32/64/1000 and producer wait cap64; no per-queue multiplication of a64-slot default.
- **F14-R04:** Scheduling p95 is a delayed signal observed only for picked-up tasks; it cannot alone establish queue emptiness or discover an entirely absent fleet. Combine qualified scheduling pressure with capacity and missing-poller/series alerts; keep two baseline replicas.
- **F14-R05:** Every scaler query returns one finite nonnegative scalar with tested histogram units/window/zero/missing behavior. Absent/stale series enters visible qualified fallback>=2 instead of appearing healthy zero.
- **F14-R06:** Scaling protects each route/namespace/build under skew; report per-route workflow AND activity scheduling p95 rather than one aggregate percentile. Test SDK/API port distinction and production probe health independently.
- **F14-R07:** Do not size workers from trigger-topic consumer lag or workflow completion rate alone. Initial steady qualification target is scheduling p95<=2s and healthy accepted-work integrity under declared resources/quotas.

## Acceptance and evidence

Generate controlled real workflow/activity load with approximately1s measured activity occupancy. Confirm actual SDK series, slots and scheduling distribution per route/build. Saturate one queue, then another, and observe qualified scale-up without masking skew; after quiet period scale down only to2. Lose metrics/one worker and verify fallback/poller alerts. Captured workload remains bounded, replay-compatible and source-integrity preserving.

Each task supplies its local scoped evidence; referenced umbrella V IDs are traceability to final release gates. A passing local case does not mark unrelated future cases complete. Real service/cluster checks cannot be satisfied by mocks. Tests use synthetic data and injected secrets, never production histories or committed keys.

## Deployable checkpoint

Build/deploy cumulative F14 image/config with worker recording rules and distinct per-build ScaledObjects. Run real scheduling/capacity smoke using both role images, capture exporter names/units, query result/replicas and lifecycle effects. Production remains blocked until F15 PINNED multi-Deployment promotion and F16 rotation plus complete V gates.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Rollback contract

Restore qualified fixed replicas>=2 through the sole scaling owner per retained build before reverting rules/values. Keep every Worker Deployment needed by pinned executions; never delete a version because its recent scheduling histogram is empty. Preserve image/key/namespace/queue compatibility and operator evidence.

## Shared normative references

[Platform specification](../001-enterprise-workflow-platform/spec.md), [roadmap](../001-enterprise-workflow-platform/roadmap.md), [data model/contracts](../001-enterprise-workflow-platform/data-model.md), [security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md), [verification](../001-enterprise-workflow-platform/verification.md). Resolve disagreement before implementation; this feature refines incremental scope without weakening final production requirements.

