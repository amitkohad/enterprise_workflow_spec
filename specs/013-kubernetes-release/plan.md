# F12 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md) | Parent: [roadmap.md](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans)

## Capability implementation

Use one chart with role values plus worker deployment/build identity in resource names and selectors. Independent Helm releases/worker entries permit old/new builds to coexist without selector collision. Include checksum-triggered same-code secret/config restarts; maxUnavailable0/maxSurge1 applies ingestion and unchanged-code restarts, not overwriting PINNED code. Optional ServiceMonitors render only when their CRDs exist. Security/network smoke uses actual CNI with declared external address strategy.

**Affected implementation paths:** Dockerfile/.dockerignore, deploy/helm/temporal-enterprise-framework, deploy/qualification/values.yaml, tests/integration/test_feature_f12.py, docs/runbooks/kubernetes.md.

Use the predecessor's runnable role entry point and integration fixture as prerequisites. Add only this capability to the cumulative image; existing completed capabilities remain active. Configuration selects finite trusted routes/profiles and secrets are mounted. Infrastructure provisioning is a declared external prerequisite, not a hidden new application role.

## Executable verification contract

The generator creates the named tests in [tasks.md](tasks.md), then runs:

- python -m pytest tests/integration/test_feature_f12.py
- docker build -t temporal-enterprise-framework:f12-kubernetes-release .

Use the exact node IDs in the task list for the smallest check. Register any optional markers in pytest configuration; these commands do not rely on feature-name selection or an empty marker filter. For Kubernetes features, the integration job provisions a policy-enforcing supported staging cluster and chart prerequisites, plus KEDA when scaler resources are tested; absence is blocked, not success.

- helm template tef deploy/helm/temporal-enterprise-framework -f deploy/qualification/values.yaml
- helm upgrade --install tef deploy/helm/temporal-enterprise-framework -f deploy/qualification/values.yaml --namespace tef-qualification --create-namespace

Candidate Worker version names/resources must remain distinct from retained Worker builds. Production deployment/version promotion is outside automatic implementation acceptance.
## Checkpoint evidence and configuration

Write safe role/route configuration and secret references under config/checkpoints/f12/ and record the checkpoint in docs/checkpoints/F12.md. The explicitly named checkpoint pytest node is the roadmap's executable smoke equivalent; it must launch the candidate image, exercise both roles and preserve rollback evidence rather than test only imported functions.

Deliver immutable digest, Helm chart/qualification values, exact install/render commands and cluster smoke evidence. Candidate INGESTION and WORKER use the same artifact; retained historical Worker builds may have their prior digests. No automatic production promotion follows this checkpoint.

The checkpoint records git revision/image digest, exact commands, runtime/SDK/broker/server/controller versions, role selection, namespace/queue/binding/build configuration, route revision, retention/key IDs without values, assertions and pass/fail/blocked results. Actual command execution occurs during implementation; these are generation requirements.

## Rollback and production eligibility

Drain ingestion before compatible image/config rollback and preserve source offsets/routes/keys. Retain all named Worker build Deployments needed for pinned runs; never replace old image to mimic rollback. F15 supplies qualified routing rollback; here validate chart resource preservation and document the outstanding release block.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Task-size and dependency rule

Execute the local tasks sequentially. Each action and its named smallest meaningful test is one reviewable change. Refine oversized work into small tasks, renumber contiguous local IDs and update dependencies while keeping at most 8 tasks. If that exceeds microfeature scope, update the roadmap/decomposition and validator limits explicitly before implementation; do not create unregistered suffix IDs. Every prerequisite must pass local acceptance before dependent work; final umbrella gates close only on complete evidence.

