# F15 — Pinned Worker rollout

**Status:** planned deployable increment; no implementation evidence yet.  
**Parent:** [roadmap entry F15](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).  
**Prerequisites:** F12 Kubernetes release (`013`), F14 Worker autoscaling (`015`), F11 telemetry (`012`), plus their prerequisite chain.  
**Program:** same repository/image; multiple versions of the existing WORKER role may run simultaneously.

Deliver an executable release procedure that deploys a new immutable Worker Deployment Version while older pinned executions keep running on their assigned build. Promote/ramp/rollback new execution routing with explicit evidence, then retire old Kubernetes deployments only after the retention/reachability criteria are satisfied. This adds no controller, deployment microservice or third application role.

## Scoped requirements

| ID | Required behavior | Core traceability |
|---|---|---|
| F15-01 | Qualified SDK/service Worker Deployment Version APIs and immutable build/image identity; reference Workflow explicitly PINNED | FR-WF-05, FR-OPS-03 |
| F15-02 | Separate Kubernetes WORKER Deployment per immutable build/version; never replace old version's image with new code | FR-OPS-01/03 |
| F15-03 | Version-scoped autoscaling/scrapes/readiness; retained old versions have sufficient floor capacity | FR-OPS-02, FR-OBS-03/04 |
| F15-04 | Replay and synthetic canary gate before routing promotion; no eager Workflow start | FR-WF-02/05, FR-OPS-04 |
| F15-05 | Rollback changes routing for new runs; existing pinned runs keep their required workers; old-version retirement requires explicit evidence | FR-OPS-03 |
| F15-06 | COMPATIBLE_ROLLING is an explicit capability exception with patch/replay evidence, never a silent downgrade | FR-WF-05/06, FR-OPS-03 |

FR-WF-06 authoring guidance is also delivered here: document compatible typed schema
evolution, patching and bounded Continue-As-New for future long-running workflows, using
supported deterministic APIs and historical key/replay obligations. The reference Workflow
remains finite; do not add a new production loop or arbitrary runtime workflow interpreter.

Temporal's current deployment guide recommends Worker Versioning for supported deployments and separates pinned executions by code version. Production versioning requires compatible service/SDK versions. [Worker Versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning), [Python Worker configuration](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning/configure-worker). Replay is a deployment gate; eager start must remain disabled for this baseline. [Safe deployment guidance](https://docs.temporal.io/develop/safe-deployments). Retrieved 2026-10-01.

## Acceptance scenarios

1. Deploy build A, hold a synthetic execution open through a supported test fixture, then deploy build B with a different immutable Kubernetes Deployment name. A remains available and its run finishes on A; new canary runs prove B serves its own version.
2. Replay the approved encrypted corpus with B and the correct historical namespaces/keys. A deliberately incompatible change is rejected for shared/auto-upgrade histories; a separately pinned new version is isolated and may advance only under an explicit reviewed compatibility decision.
3. Set the supported Current/Ramping version through controlled platform tooling; new starts route as configured, while A's assigned runs are unaffected. App readiness alone does not authorize promotion.
4. Roll new-execution routing back to A. B executions already pinned to B continue on B; no Kubernetes image replacement tries to replay B histories with A.
5. Request A retirement with an open/reachable run; tooling refuses. After draining and satisfying reset/replay/retention obligations, authorized retirement removes only A's Kubernetes resources.
6. Old/new scaler and scrape selectors remain separate; scaling B never counts A as interchangeable capacity or scales A below its retained floor.

## Runnable checkpoint and eligibility

Deploy immutable worker versions using the same chart/image contract, then run `scripts/qualify/worker_rollout.py --config <non-secret-config> --operation verify|canary|promote|rollback|retire`. Operations that mutate live routing require the platform release authorization already provided by its deployment process. `verify` is read-only; `retire` fails closed on missing evidence. The command is platform tooling, not a deployed third role. The checkpoint completes versioned-release capability; production business eligibility still requires the complete roadmap's security/delivery/rotation/load/recovery evidence.

Authority: [feature roadmap](../001-enterprise-workflow-platform/roadmap.md), [core compatibility policy](../001-enterprise-workflow-platform/plan.md), [security replay contract](../001-enterprise-workflow-platform/security.md#sec-replay--compatible-code-and-key-changes), [V-020/V-023/V-025/V-028](../001-enterprise-workflow-platform/verification.md).
