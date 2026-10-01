# F07 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md) | Parent: [roadmap.md](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans)

## Capability implementation

Represent source coordinate, validated intent, ownership token and typed disposition separately. Maintain one unresolved record and settled/committed fence per partition. Introduce conservative ownership-token fencing but do not claim full F09 rebalance qualification. Reuse existing profile resolver/start service/producer; no execute_workflow or per-record client creation. Real failpoints are test-only and cannot be enabled in production.

**Affected implementation paths:** app/events/models.py, app/events/bridge.py, app/events/consumer.py, existing app/main.py/FastAPI lifespan, tests/unit/test_kafka_trigger.py and tests/integration/test_feature_f07.py.

Use the predecessor's runnable role entry point and integration fixture as prerequisites. Add only this capability to the cumulative image; existing completed capabilities remain active. Configuration selects finite trusted routes/profiles and secrets are mounted. Infrastructure provisioning is a declared external prerequisite, not a hidden new application role.

## Executable verification contract

The generator creates the named tests in [tasks.md](tasks.md), then runs:

- python -m pytest tests/unit/test_kafka_trigger.py
- python -m pytest tests/integration/test_feature_f07.py
- docker build -t temporal-enterprise-framework:f07-kafka-trigger-start .

Use the exact node IDs in the task list for the smallest check. Register any optional markers in pytest configuration; these commands do not rely on feature-name selection or an empty marker filter. For Kubernetes features, the integration job provisions a policy-enforcing supported staging cluster and chart prerequisites, plus KEDA when scaler resources are tested; absence is blocked, not success.

## Checkpoint evidence and configuration

Write safe role/route configuration and secret references under config/checkpoints/f07/ and record the checkpoint in docs/checkpoints/F07.md. The explicitly named checkpoint pytest node is the roadmap's executable smoke equivalent; it must launch the candidate image, exercise both roles and preserve rollback evidence rather than test only imported functions.

Build a cumulative immutable F07 image and run both roles with mounted synthetic TLS/key material and one selected binding. Smoke one REST and one Kafka start with distinct UUIDs, authorized status and acknowledged reference output. Capture digest/config/group/offset evidence.

The checkpoint records git revision/image digest, exact commands, runtime/SDK/broker/server/controller versions, role selection, namespace/queue/binding/build configuration, route revision, retention/key IDs without values, assertions and pass/fail/blocked results. Actual command execution occurs during implementation; these are generation requirements.

## Rollback and production eligibility

Drain/suspend Kafka intake before restoring the prior compatible digest/config. Preserve group offsets, namespace/route binding, histories, source retention and decrypt keys; leave pending intake suspended until a qualified consumer is available. Never reset a group or change UUIDs.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Task-size and dependency rule

Execute the local tasks sequentially. Each action and its named smallest meaningful test is one reviewable change. Refine oversized work into small tasks, renumber contiguous local IDs and update dependencies while keeping at most 8 tasks. If that exceeds microfeature scope, update the roadmap/decomposition and validator limits explicitly before implementation; do not create unregistered suffix IDs. Every prerequisite must pass local acceptance before dependent work; final umbrella gates close only on complete evidence.

