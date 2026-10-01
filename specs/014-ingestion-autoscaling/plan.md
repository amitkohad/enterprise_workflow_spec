# F13 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md) | Parent: [roadmap.md](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans)

## Capability implementation

Default uses per-binding Kafka triggers plus REST rate demand under one HPA. REST rate threshold is benchmarked safe requests/second per pod with headroom, not arbitrary latency. A composite may normalize Kafka/REST requirements but must be tested using the selected KEDA version and correct Value/AverageValue semantics. Cap each binding's useful consumption separately; record idle consumers explicitly. Missing-series/outage tests use actual scaler responses.

**Affected implementation paths:** existing chart KEDA/TriggerAuthentication templates, Prometheus recording rules/qualification values, tests/integration/test_feature_f13.py, docs/runbooks/ingestion-scaling.md.

Use the predecessor's runnable role entry point and integration fixture as prerequisites. Add only this capability to the cumulative image; existing completed capabilities remain active. Configuration selects finite trusted routes/profiles and secrets are mounted. Infrastructure provisioning is a declared external prerequisite, not a hidden new application role.

## Executable verification contract

The generator creates the named tests in [tasks.md](tasks.md), then runs:

- python -m pytest tests/integration/test_feature_f13.py
- docker build -t temporal-enterprise-framework:f13-ingestion-autoscaling .

Use the exact node IDs in the task list for the smallest check. Register any optional markers in pytest configuration; these commands do not rely on feature-name selection or an empty marker filter. For Kubernetes features, the integration job provisions a policy-enforcing supported staging cluster and chart prerequisites, plus KEDA when scaler resources are tested; absence is blocked, not success.

## Checkpoint evidence and configuration

Write safe role/route configuration and secret references under config/checkpoints/f13/ and record the checkpoint in docs/checkpoints/F13.md. The explicitly named checkpoint pytest node is the roadmap's executable smoke equivalent; it must launch the candidate image, exercise both roles and preserve rollback evidence rather than test only imported functions.

Build/deploy cumulative F13 image/config and one ingestion ScaledObject with mounted TriggerAuthentication references. Record live query outputs/units, thresholds, per-binding partition counts, API per-pod capacity, desired/current replicas and independent demand smoke evidence. Production remains blocked by F15/F16/full gates.

The checkpoint records git revision/image digest, exact commands, runtime/SDK/broker/server/controller versions, role selection, namespace/queue/binding/build configuration, route revision, retention/key IDs without values, assertions and pass/fail/blocked results. Actual command execution occurs during implementation; these are generation requirements.

## Rollback and production eligibility

Pause/remove scaling through the single documented owner and restore measured fixed replicas>=2 before reverting compatible values/image. Preserve group offsets and route selection. Do not add a manual HPA alongside KEDA or scale pinned worker versions as part of ingestion rollback.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Task-size and dependency rule

Execute the local tasks sequentially. Each action and its named smallest meaningful test is one reviewable change. Refine oversized work into small tasks, renumber contiguous local IDs and update dependencies while keeping at most 8 tasks. If that exceeds microfeature scope, update the roadmap/decomposition and validator limits explicitly before implementation; do not create unregistered suffix IDs. Every prerequisite must pass local acceptance before dependent work; final umbrella gates close only on complete evidence.

