# F07 tasks

**Prerequisite:** F06: authorized workflow status/result (007) completed and its runnable checkpoint available. IDs below are local to F07; execute in numeric order.

Each task implements one named behavior and runs the exact pytest node below. Create the test alongside the behavior; register optional unit/integration markers in pytest configuration if used. Cited V IDs are scoped evidence mappings, not claims that every final gate is already complete.

- [ ] T001 Validate one trusted binding and strict key/envelope rules.
  - Depends: F06: authorized workflow status/result (007). Evidence: V-008/V-011; applicable F07-R requirements.
  - Run: `python -m pytest tests/unit/test_kafka_trigger.py::test_trusted_binding_and_key`
  - Accept: valid intent resolves registered tenant route; malformed or mismatched keys/caller routes never start.
- [ ] T002 Create owning poll thread and bounded control/data bridge.
  - Depends: T001. Evidence: V-016; applicable F07-R requirements.
  - Run: `python -m pytest tests/unit/test_kafka_trigger.py::test_owned_poll_and_backpressure`
  - Accept: owner-only broker operations, reserved control/poll progress under saturation, observable fatal exit.
- [ ] T003 Implement ordered partition admission and global Kafka 32/256 bounds.
  - Depends: T002. Evidence: V-016; applicable F07-R requirements.
  - Run: `python -m pytest tests/unit/test_kafka_trigger.py::test_partition_admission_bounds`
  - Accept: one unresolved record per partition and no task-per-message growth/drop.
- [ ] T004 Adapt admitted records to existing common start service.
  - Depends: T003. Evidence: V-009/V-012; applicable F07-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f07.py::test_acknowledged_start_and_duplicate`
  - Accept: same UUID/digest/memo policy as REST; acknowledgment/verified duplicate only; no completion wait.
- [ ] T005 Implement eligible-prefix offset+1 commits and failed-commit recovery.
  - Depends: T004. Evidence: V-012/V-013; applicable F07-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f07.py::test_start_ack_before_commit_crash`
  - Accept: start-ack-before-commit crash redelivers to one retained execution; uncertainty never advances fence.
- [ ] T006 Pause invalid records and connect consumer supervision to lifespan.
  - Depends: T005. Evidence: V-011/V-016/V-022; applicable F07-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f07.py::test_invalid_partition_and_supervision`
  - Accept: safe alert, affected partition remains uncommitted, other partitions progress and fatal bridge tears down role.
- [ ] T007 Build/run F07 image checkpoint and validate restricted rollback.
  - Depends: T006. Evidence: V-030; applicable F07-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f07.py::test_image_smoke_and_rollback`
  - Accept: both roles prove REST/Kafka/status flow; digest/config recorded; offsets/keys/routes retained and production blockers explicit.

Do not mark the checkpoint task complete without candidate-image deployment, real smoke and rollback evidence. Record missing external prerequisites as blocked. Maintain the umbrella roadmap's production eligibility block until later versioning/rotation/full-release gates pass.

