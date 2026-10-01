# F08 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md) | Parent: [roadmap.md](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans)

## Capability implementation

Permanent outcomes move the same pending source record into awaiting_dlq_ack; only confirmed delivery becomes settled. Generation/contiguous fences stay authoritative. Use finite reason codes and schema-defined source-coordinate identity. Retries share Kafka 32/256 budgets and do not create another unbounded DLQ task pool. Real broker tests use synthetic secrets/data and a deterministic test-only crash barrier.

**Affected implementation paths:** app/events/models.py and consumer.py, reused app/events/producer.py, tests/unit/test_dlq_disposition.py and tests/integration/test_feature_f08.py.

Use the predecessor's runnable role entry point and integration fixture as prerequisites. Add only this capability to the cumulative image; existing completed capabilities remain active. Configuration selects finite trusted routes/profiles and secrets are mounted. Infrastructure provisioning is a declared external prerequisite, not a hidden new application role.

## Executable verification contract

The generator creates the named tests in [tasks.md](tasks.md), then runs:

- python -m pytest tests/unit/test_dlq_disposition.py
- python -m pytest tests/integration/test_feature_f08.py
- docker build -t temporal-enterprise-framework:f08-dlq-disposition .

Use the exact node IDs in the task list for the smallest check. Register any optional markers in pytest configuration; these commands do not rely on feature-name selection or an empty marker filter. For Kubernetes features, the integration job provisions a policy-enforcing supported staging cluster and chart prerequisites, plus KEDA when scaler resources are tested; absence is blocked, not success.

## Checkpoint evidence and configuration

Write safe role/route configuration and secret references under config/checkpoints/f08/ and record the checkpoint in docs/checkpoints/F08.md. The explicitly named checkpoint pytest node is the roadmap's executable smoke equivalent; it must launch the candidate image, exercise both roles and preserve rollback evidence rather than test only imported functions.

Build the cumulative F08 image; run both roles with one selected binding and configured DLQ/profile. Smoke valid workflow start plus invalid-record acknowledged disposition, scan for sensitive markers and record source/DLQ coordinates and image/config.

The checkpoint records git revision/image digest, exact commands, runtime/SDK/broker/server/controller versions, role selection, namespace/queue/binding/build configuration, route revision, retention/key IDs without values, assertions and pass/fail/blocked results. Actual command execution occurs during implementation; these are generation requirements.

## Rollback and production eligibility

Drain/suspend before restoring compatible F07 behavior. Preserve source/DLQ records, group offsets, retained IDs and keys; pending invalid records return to F07 pause/alert. No automatic replay, topic deletion or offset reset.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Task-size and dependency rule

Execute the local tasks sequentially. Each action and its named smallest meaningful test is one reviewable change. Refine oversized work into small tasks, renumber contiguous local IDs and update dependencies while keeping at most 8 tasks. If that exceeds microfeature scope, update the roadmap/decomposition and validator limits explicitly before implementation; do not create unregistered suffix IDs. Every prerequisite must pass local acceptance before dependent work; final umbrella gates close only on complete evidence.

