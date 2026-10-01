# F09 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md) | Parent: [roadmap.md](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans)

## Capability implementation

Use immutable ownership tokens and generation-indexed assignment state, settled versus committed fences and separate revoke/lost handlers. The single selected consumer thread exposes async terminal-status supervision. Global budgets are shared across its partitions, with reserved controls and bounded fairness. Unit tests exercise finite future multiplexing state, but F10 owns actual multi-profile/binding/client deployment. A zero-partition healthy consumer is valid. Tests launch independent image instances and delay completions beyond revoke using test-only barriers.

**Affected implementation paths:** app/events/bridge.py and consumer.py, existing role supervisor and selected-binding limits, tests/unit/test_assignment_generations.py and tests/integration/test_feature_f09.py.

Use the predecessor's runnable role entry point and integration fixture as prerequisites. Add only this capability to the cumulative image; existing completed capabilities remain active. Configuration selects finite trusted routes/profiles and secrets are mounted. Infrastructure provisioning is a declared external prerequisite, not a hidden new application role.

## Executable verification contract

The generator creates the named tests in [tasks.md](tasks.md), then runs:

- python -m pytest tests/unit/test_assignment_generations.py
- python -m pytest tests/integration/test_feature_f09.py
- docker build -t temporal-enterprise-framework:f09-rebalance-recovery .

Use the exact node IDs in the task list for the smallest check. Register any optional markers in pytest configuration; these commands do not rely on feature-name selection or an empty marker filter. For Kubernetes features, the integration job provisions a policy-enforcing supported staging cluster and chart prerequisites, plus KEDA when scaler resources are tested; absence is blocked, not success.

## Checkpoint evidence and configuration

Write safe role/route configuration and secret references under config/checkpoints/f09/ and record the checkpoint in docs/checkpoints/F09.md. The explicitly named checkpoint pytest node is the roadmap's executable smoke equivalent; it must launch the candidate image, exercise both roles and preserve rollback evidence rather than test only imported functions.

Build cumulative F09 image and run both roles plus >=2 INGESTION instances on the same single selected synthetic binding. Record protocol/version, assignment generations, offsets, memory/task bounds, smoke results and digest/config. Kubernetes is not required to demonstrate this checkpoint; independent image containers/processes suffice.

The checkpoint records git revision/image digest, exact commands, runtime/SDK/broker/server/controller versions, role selection, namespace/queue/binding/build configuration, route revision, retention/key IDs without values, assertions and pass/fail/blocked results. Actual command execution occurs during implementation; these are generation requirements.

## Rollback and production eligibility

Pre-F09 images are qualified only for one active consumer instance. Suspend intake, drain and reduce the fleet to its predecessor's supported shape before restoring compatible F07/F08 digest. Preserve groups/offsets/routes/source retention/keys and pending records for a qualified consumer; do not downgrade a live multi-instance fleet without restriction.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Task-size and dependency rule

Execute the local tasks sequentially. Each action and its named smallest meaningful test is one reviewable change. Refine oversized work into small tasks, renumber contiguous local IDs and update dependencies while keeping at most 8 tasks. If that exceeds microfeature scope, update the roadmap/decomposition and validator limits explicitly before implementation; do not create unregistered suffix IDs. Every prerequisite must pass local acceptance before dependent work; final umbrella gates close only on complete evidence.

