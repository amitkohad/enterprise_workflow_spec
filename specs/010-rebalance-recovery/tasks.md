# F09 tasks

**Prerequisite:** F08: DLQ disposition (009) completed and its runnable checkpoint available. IDs below are local to F09; execute in numeric order.

Each task implements one named behavior and runs the exact pytest node below. Create the test alongside the behavior; register optional unit/integration markers in pytest configuration if used. Cited V IDs are scoped evidence mappings, not claims that every final gate is already complete.

- [ ] T001 Tag records/completions with immutable assignment generations.
  - Depends: F08: DLQ disposition (009). Evidence: V-014; applicable F09-R requirements.
  - Run: `python -m pytest tests/unit/test_assignment_generations.py::test_stale_completion_fenced`
  - Accept: obsolete start/DLQ completion cannot advance a new generation fence.
- [ ] T002 Implement separate bounded revoke and lost handlers.
  - Depends: T001. Evidence: V-014; applicable F09-R requirements.
  - Run: `python -m pytest tests/unit/test_assignment_generations.py::test_revoke_and_lost_commit_rules`
  - Accept: revoke commits only eligible owned prefix; lost never commits and intake stops.
- [ ] T003 Recover failed/uncertain commits through current-owner reconciliation.
  - Depends: T002. Evidence: V-012/V-013; applicable F09-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f09.py::test_uncertain_commit_recovery`
  - Accept: real source redelivery skips nothing and preserves retained execution identity.
- [ ] T004 Bound global partition admission and unit-test future multiplexing fairness.
  - Depends: T003. Evidence: V-016; applicable F09-R requirements.
  - Run: `python -m pytest tests/unit/test_assignment_generations.py::test_partition_fairness_and_future_multiplexing_bounds`
  - Accept: deployed F09 remains one trusted binding, global 32/256 limits hold across partitions and future bounded multiplexing state passes unit checks; F10 owns actual multi-profile selection/tenant isolation.
- [ ] T005 Surface one thread fatal exit through joint role teardown.
  - Depends: T004. Evidence: V-016/V-022; applicable F09-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f09.py::test_fatal_thread_joint_teardown`
  - Accept: HTTP/selected bridge close, exit nonzero and peer instance recovers source work.
- [ ] T006 Qualify real multi-instance rebalances and old-owner delay.
  - Depends: T005. Evidence: V-014; applicable F09-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f09.py::test_multi_instance_rebalances`
  - Accept: repeated scale-up/down preserves fences, polling and reconciled inventory.
- [ ] T007 Qualify saturation/outage and 90/110s shutdown.
  - Depends: T006. Evidence: V-016/V-022/V-027; applicable F09-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f09.py::test_saturation_and_shutdown`
  - Accept: finite memory/tasks, responsive controls and recovery of unacknowledged work.
- [ ] T008 Build F09 fleet checkpoint and validate restricted rollback.
  - Depends: T007. Evidence: V-030; applicable F09-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f09.py::test_image_smoke_and_rollback`
  - Accept: >=2 image instances on one binding prove reassignment; predecessor fleet restriction/offset retention tested.

Do not mark the checkpoint task complete without candidate-image deployment, real smoke and rollback evidence. Record missing external prerequisites as blocked. Maintain the umbrella roadmap's production eligibility block until later versioning/rotation/full-release gates pass.

