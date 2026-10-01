# F14 tasks

**Prerequisite:** F13: ingestion autoscaling (014) completed and its runnable checkpoint available. IDs below are local to F14; execute in numeric order.

Each task implements one named behavior and runs the exact pytest node below. Create the test alongside the behavior; register optional unit/integration markers in pytest configuration if used. Cited V IDs are scoped evidence mappings, not claims that every final gate is already complete.

- [ ] T001 Capture real SDK metric names/units/build and queue labels.
  - Depends: F13: ingestion autoscaling (014). Evidence: V-021/V-025; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_sdk_metric_contract`
  - Accept: 9090 series map recorded independently from8080 app metrics; absent samples visible.
- [ ] T002 Validate per-process queue allocation and capacity baseline.
  - Depends: T001. Evidence: V-001/V-026; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_process_capacity_budget`
  - Accept: sums<=32/64/1000, shared producer<=64 and safe per-pod pressure/headroom measured.
- [ ] T003 Add per-build single-owner capacity scaling query.
  - Depends: T002. Evidence: V-025; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_capacity_scaling_owner`
  - Accept: finite scalar with correct units/metricType and no cross-build/namespace aggregation.
- [ ] T004 Add scheduling-pressure signal and missing-poller alerts.
  - Depends: T003. Evidence: V-025/V-026; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_scheduling_signal_and_skew`
  - Accept: per-route workflow/activity p95 correct; completion delay/trigger lag not backlog surrogate.
- [ ] T005 Configure nonzero baseline/stabilization and missing-series fallback.
  - Depends: T004. Evidence: V-025; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_worker_metric_fallback`
  - Accept: real outage/zero distinguishes, fallback>=2 and retained fleets never scale-to-zero.
- [ ] T006 Qualify real saturation/skew/loss and bounded scale-down.
  - Depends: T005. Evidence: V-022/V-025/V-026/V-027; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_worker_scaling_load`
  - Accept: measured scheduling response, task/slot/resource limits and recovery without integrity loss.
- [ ] T007 Publish cumulative F14 image/config checkpoint and retained-build rollback.
  - Depends: T006. Evidence: V-030; applicable F14-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f14.py::test_checkpoint_and_rollback`
  - Accept: both roles real smoke, sole-owner fixed fallback proved, old Worker resources retained and production blockers explicit.

Do not mark the checkpoint task complete without candidate-image deployment, real smoke and rollback evidence. Record missing external prerequisites as blocked. Maintain the umbrella roadmap's production eligibility block until later versioning/rotation/full-release gates pass.

