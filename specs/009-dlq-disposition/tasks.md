# F08 tasks

**Prerequisite:** F07: Kafka trigger start (008) completed and its runnable checkpoint available. IDs below are local to F08; execute in numeric order.

Each task implements one named behavior and runs the exact pytest node below. Create the test alongside the behavior; register optional unit/integration markers in pytest configuration if used. Cited V IDs are scoped evidence mappings, not claims that every final gate is already complete.

- [ ] T001 Implement finite permanent/transient classification.
  - Depends: F07: Kafka trigger start (008). Evidence: V-011; applicable F08-R requirements.
  - Run: `python -m pytest tests/unit/test_dlq_disposition.py::test_error_classification`
  - Accept: only proven bad records/identity conflicts including confirmed missing memo can DLQ; dependency/auth/key/unknown cryptographic evidence remains retryable.
- [ ] T002 Build schema-conforming deterministic safe DLQ record.
  - Depends: T001. Evidence: V-015; applicable F08-R requirements.
  - Run: `python -m pytest tests/unit/test_dlq_disposition.py::test_safe_record_identity`
  - Accept: stable source-coordinate identity and no value/digest/token/exception text in body/headers.
- [ ] T003 Connect confirmed DLQ delivery to source disposition fence.
  - Depends: T002. Evidence: V-013/V-015; applicable F08-R requirements.
  - Run: `python -m pytest tests/unit/test_dlq_disposition.py::test_ack_required_to_settle`
  - Accept: enqueue/error/timeout cannot settle; acknowledgment allows eligible prefix only.
- [ ] T004 Implement paused bounded retry on DLQ outage.
  - Depends: T003. Evidence: V-015/V-016; applicable F08-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f08.py::test_dlq_outage_and_recovery`
  - Accept: offset retained while polls/unrelated partitions progress; restore leads to safe settlement.
- [ ] T005 Exercise real DLQ-ack-before-commit crash.
  - Depends: T004. Evidence: V-015; applicable F08-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f08.py::test_ack_crash_redelivery`
  - Accept: same DLQ ID repeats safely after restart and source never skipped.
- [ ] T006 Verify privacy and non-DLQ dependency failures using broker output.
  - Depends: T005. Evidence: V-005/V-011; applicable F08-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f08.py::test_dlq_privacy_and_dependency_failures`
  - Accept: sensitive sentinel absent; valid data during service/key/auth failure stays pending.
- [ ] T007 Build cumulative F08 checkpoint and prove rollback.
  - Depends: T006. Evidence: V-030; applicable F08-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f08.py::test_image_smoke_and_rollback`
  - Accept: valid/invalid flow, recorded image/config and preserved source/DLQ/offset/key state on prior-image rollback.

Do not mark the checkpoint task complete without candidate-image deployment, real smoke and rollback evidence. Record missing external prerequisites as blocked. Maintain the umbrella roadmap's production eligibility block until later versioning/rotation/full-release gates pass.

