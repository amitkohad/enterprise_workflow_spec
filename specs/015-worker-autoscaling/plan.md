# F14 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md) | Parent: [roadmap.md](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans)

## Capability implementation

Prometheus recording rules normalize actual exporter units and associate scrapes with Kubernetes worker build identities. Use measured slot capacity demand plus an independently tested scheduling-delay pressure rule under one owner. Test Value/AverageValue dimensional correctness; do not feed a p95 ratio into replica arithmetic without qualifying its response. Missing samples are unknown. Synthetic latency mechanism occupies activity slots; workflow timer duration is not a substitute.

**Affected implementation paths:** worker chart KEDA/recording rules, workload/qualification scripts, tests/integration/test_feature_f14.py, docs/runbooks/worker-scaling.md.

Use the predecessor's runnable role entry point and integration fixture as prerequisites. Add only this capability to the cumulative image; existing completed capabilities remain active. Configuration selects finite trusted routes/profiles and secrets are mounted. Infrastructure provisioning is a declared external prerequisite, not a hidden new application role.

## Executable verification contract

The generator creates the named tests in [tasks.md](tasks.md), then runs:

- python -m pytest tests/integration/test_feature_f14.py
- docker build -t temporal-enterprise-framework:f14-worker-autoscaling .

Use the exact node IDs in the task list for the smallest check. Register any optional markers in pytest configuration; these commands do not rely on feature-name selection or an empty marker filter. For Kubernetes features, the integration job provisions a policy-enforcing supported staging cluster and chart prerequisites, plus KEDA when scaler resources are tested; absence is blocked, not success.

## Checkpoint evidence and configuration

Write safe role/route configuration and secret references under config/checkpoints/f14/ and record the checkpoint in docs/checkpoints/F14.md. The explicitly named checkpoint pytest node is the roadmap's executable smoke equivalent; it must launch the candidate image, exercise both roles and preserve rollback evidence rather than test only imported functions.

Build/deploy cumulative F14 image/config with worker recording rules and distinct per-build ScaledObjects. Run real scheduling/capacity smoke using both role images, capture exporter names/units, query result/replicas and lifecycle effects. Production remains blocked until F15 PINNED multi-Deployment promotion and F16 rotation plus complete V gates.

The checkpoint records git revision/image digest, exact commands, runtime/SDK/broker/server/controller versions, role selection, namespace/queue/binding/build configuration, route revision, retention/key IDs without values, assertions and pass/fail/blocked results. Actual command execution occurs during implementation; these are generation requirements.

## Rollback and production eligibility

Restore qualified fixed replicas>=2 through the sole scaling owner per retained build before reverting rules/values. Keep every Worker Deployment needed by pinned executions; never delete a version because its recent scheduling histogram is empty. Preserve image/key/namespace/queue compatibility and operator evidence.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Task-size and dependency rule

Execute the local tasks sequentially. Each action and its named smallest meaningful test is one reviewable change. Refine oversized work into small tasks, renumber contiguous local IDs and update dependencies while keeping at most 8 tasks. If that exceeds microfeature scope, update the roadmap/decomposition and validator limits explicitly before implementation; do not create unregistered suffix IDs. Every prerequisite must pass local acceptance before dependent work; final umbrella gates close only on complete evidence.

