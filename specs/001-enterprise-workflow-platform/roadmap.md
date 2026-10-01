# Feature Roadmap: Deployable Increments of One Application

Date: 2026-10-01 | User-confirmed model: **deployable increments of one application**  
Application: `temporal-enterprise-framework` | Roles: `INGESTION`, `WORKER`  
Status: All feature specifications prepared for implementation; no feature implemented.

This is the parent roadmap in GitHub SpecKit's
[spec-of-specs approach](https://github.github.com/spec-kit/concepts/spec-of-specs.html).
Each entry is a complete feature package with its own spec, corresponding plan and small
task backlog. Parent FR/SC requirements, contracts, security and operations are shared.
Feature packages reference this roadmap so scope and dependencies can be traced both ways.

## Meaning of an executable/deployable feature

Each feature produces a complete image version of the same application, containing its
accepted prerequisites, plus explicit role configuration and a repeatable executable
smoke proof. A feature must demonstrate new externally observable behavior in that
deployment. A converter file, interceptor library or YAML template alone is not a feature.
These implementation details live inside a feature that exercises them end to end.

Features are cumulative: F06 includes F01–F05, and can be deployed without building
unimplemented F07–F16. They are not isolated services with separate production roles.
An individual feature is independently reviewable and testable after its stated prerequisites
are available. An early image is a qualification release, not a claim that the complete
enterprise platform's production guarantees have already been achieved.

Standard checkpoint output:

- One immutable image digest, built through the root Dockerfile; descriptive `fxx-*` tags
  are convenience labels, and deployment/evidence records the digest.
- `config/checkpoints/fxx/` with safe role/route fixture configuration and secret references.
- `scripts/checkpoints/fxx_smoke.py` or the equivalent explicitly named test command.
- `docs/checkpoints/Fxx.md` recording prerequisites, commands, result, image versions,
  observed behavior, rollback and production eligibility.
- Feature-local unit/integration tests proving acceptance. Finite smoke/load utilities
  are test/operator commands, not third application roles or permanent services.

## Feature index and corresponding plans

| ID | Micro-level feature / deployable behavior | Prerequisite | Spec | Plan | Tasks |
|---|---|---|---|---|---|
| F01 | Role process starts, probes and drains from one image | None | [Runtime health](../002-role-runtime-health/spec.md) | [Plan](../002-role-runtime-health/plan.md) | [Tasks](../002-role-runtime-health/tasks.md) |
| F02 | Both roles connect with verified Temporal mTLS and namespace preflight | F01 | [mTLS connectivity](../003-temporal-mtls-connectivity/spec.md) | [Plan](../003-temporal-mtls-connectivity/plan.md) | [Tasks](../003-temporal-mtls-connectivity/tasks.md) |
| F03 | Execute and replay a real encrypted synthetic Workflow round trip | F02 | [Encrypted execution](../004-encrypted-workflow-roundtrip/spec.md) | [Plan](../004-encrypted-workflow-roundtrip/plan.md) | [Tasks](../004-encrypted-workflow-roundtrip/tasks.md) |
| F04 | Reference Workflow publishes an acknowledged Kafka event and returns receipt | F03 | [Kafka publication](../005-acknowledged-kafka-publication/spec.md) | [Plan](../005-acknowledged-kafka-publication/plan.md) | [Tasks](../005-acknowledged-kafka-publication/tasks.md) |
| F05 | Authorized POST starts and reconciles retries by retained UUID | F04 | [REST start](../006-idempotent-rest-start/spec.md) | [Plan](../006-idempotent-rest-start/plan.md) | [Tasks](../006-idempotent-rest-start/tasks.md) |
| F06 | Authorized GET returns bounded status and optional completed result | F05 | [Status/results](../007-authorized-status-results/spec.md) | [Plan](../007-authorized-status-results/plan.md) | [Tasks](../007-authorized-status-results/tasks.md) |
| F07 | Valid Kafka trigger starts Workflow before committing its source offset | F06 | [Kafka trigger](../008-kafka-trigger-start/spec.md) | [Plan](../008-kafka-trigger-start/plan.md) | [Tasks](../008-kafka-trigger-start/tasks.md) |
| F08 | Invalid records reach metadata-only DLQ before source commit | F07 | [DLQ disposition](../009-dlq-disposition/spec.md) | [Plan](../009-dlq-disposition/plan.md) | [Tasks](../009-dlq-disposition/tasks.md) |
| F09 | Multiple consumers recover safely from crash, rebalance and stale callbacks | F08 | [Rebalance recovery](../010-rebalance-recovery/spec.md) | [Plan](../010-rebalance-recovery/plan.md) | [Tasks](../010-rebalance-recovery/tasks.md) |
| F10 | Existing ingress/execution paths isolate multiple configured tenant routes | F09, F06 | [Tenant routing](../011-tenant-route-isolation/spec.md) | [Plan](../011-tenant-route-isolation/plan.md) | [Tasks](../011-tenant-route-isolation/tasks.md) |
| F11 | Correlate traces/logs and scrape private app/SDK metrics | F10 | [Telemetry](../012-correlated-telemetry/spec.md) | [Plan](../012-correlated-telemetry/plan.md) | [Tasks](../012-correlated-telemetry/tasks.md) |
| F12 | Deploy the same image as restricted Kubernetes role workloads | F11 | [Kubernetes release](../013-kubernetes-release/spec.md) | [Plan](../013-kubernetes-release/plan.md) | [Tasks](../013-kubernetes-release/tasks.md) |
| F13 | Ingestion scales from Kafka and REST demand with one scaling owner | F12 | [Ingestion scaling](../014-ingestion-autoscaling/spec.md) | [Plan](../014-ingestion-autoscaling/plan.md) | [Tasks](../014-ingestion-autoscaling/tasks.md) |
| F14 | Worker fleet scales from scheduling delay/capacity and finite budgets | F13 | [Worker scaling](../015-worker-autoscaling/spec.md) | [Plan](../015-worker-autoscaling/plan.md) | [Tasks](../015-worker-autoscaling/tasks.md) |
| F15 | Promote/rollback pinned Worker builds while old deployments keep serving old runs | F14 | [Pinned rollout](../016-pinned-worker-rollout/spec.md) | [Plan](../016-pinned-worker-rollout/plan.md) | [Tasks](../016-pinned-worker-rollout/tasks.md) |
| F16 | Rotate mounted keys/certificates and retain historical replay/read compatibility | F15 | [Key/cert rotation](../017-key-certificate-rotation/spec.md) | [Plan](../017-key-certificate-rotation/plan.md) | [Tasks](../017-key-certificate-rotation/tasks.md) |

## Executable checkpoints and release stages

| Stage | Features | What can run after acceptance | Eligibility |
|---|---|---|---|
| Secure runtime foundation | F01–F04 | Same-image role shell, verified client, encrypted diagnostic execution, real registered publish Workflow via authorized smoke client | Synthetic qualification only; F03 diagnostic Workflow is test-profile-only |
| Durable ingestion | F05–F10 | Authorized REST start/read and multi-tenant Kafka trigger/DLQ/recovery paths | Staging qualification; deployment/scaling/version-retention gates still pending |
| Observable cluster platform | F11–F14 | Private telemetry, restricted role workloads and KEDA scaling | Production-shaped staging; no production promotion before F15/F16 and complete V gates |
| Safe production operations | F15–F16 | Versioned coexistence, promotion/rollback, rotation and historical replay | Production candidate only after all FR/SC and V-001–V-030 evidence passes |

The first features deliberately deploy with minimal safe functionality. F02 has live
connectivity but no business starts. F03 exercises an encrypted test-only diagnostic
Workflow; F04 provides the final registered reference Workflow. F07 pauses poison-record
partitions with visible errors until F08 adds the DLQ disposition; it never skips them.
Every later image preserves previously accepted behavior and expands only the named slice.

## Shared contract coverage

| Parent requirement family | Feature owners |
|---|---|
| FR-CORE-01–04 | F01, F02, F07, F09, F12 |
| FR-SEC-01–07 | F02, F03, F05, F06, F08, F10, F11, F12, F16 |
| FR-ROUTE-01–04 | F02 single-route foundation, F04 snapshot, F10 multi-tenant completion |
| FR-WF-01–06 | F03 deterministic/replay foundation, F04 reference Activity/Workflow, F15 compatibility/authoring |
| FR-ING-01–04 | F05 shared start and retention rules, F07/F09 event replay, F16 restore evidence |
| FR-API-01–03 | F05 start, F06 status/result, F11 correlation, F12 public/private exposure |
| FR-KAFKA-01–05 | F04 publication, F07 source start, F08 DLQ, F09 poll/rebalance/commit safety |
| FR-OBS-01–04 | F01 health, F11 full telemetry, F13/F14 metric-driven scaling |
| FR-OPS-01–04 | F01 image/CI, F12 deployment, F13/F14 capacity, F15 rollout, F16 rotation and cumulative qualification |

The original [task reference](task-reference.md) preserves the initial monolithic breakdown
for provenance only. It is superseded: execute each feature's tasks, not those old IDs.
Each feature-local `T001` is identified as `Fxx/T001`; completion is tracked in that feature.

## AI execution and production acceptance

Proceed F01 through F16 in table order; within each package execute its task list in order.
Read the constitution and parent contract, then only the selected feature plus referenced
shared designs. Do not ask the generator to implement the entire roadmap in one invocation.
At each checkpoint, record task-local evidence and cumulative regression results. A cited
V ID maps a task to the eventual gate; early unit acceptance is not a substitute for the
complete real-service/cluster gate. Do not stall an early unit task because a later gate
requires infrastructure that has not yet been built; close only its own stated acceptance.

After F16 run the complete [verification catalog](verification.md) and [success criteria](spec.md).
Use the qualification profile100 starts/s15min and 300/s60s burst, four tenants/eight
partitions/four routes,1KiB payload and measured approximately1s Activity, with REST/Kafka
and mixed variants. Require recorded resources/quotas, p95 latencies, healthy99.9% confirmed
starts, bounded resources, crash recovery, encrypted replay and 90s normal drain. Missing
dependencies or failed checks block production promotion; artifact creation alone is not
acceptance. Real production deployment/promotion remains an operator release action.

No per-feature change may silently add a database, service, runtime code loading, workflow
DSL or third production role. Decomposition changes delivery granularity, not architecture.
