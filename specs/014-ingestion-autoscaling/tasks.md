# F13 tasks

**Prerequisite:** F12: Kubernetes release (013) completed and its runnable checkpoint available. IDs below are local to F13; execute in numeric order.

Each task implements one named behavior and runs the exact pytest node below. Create the test alongside the behavior; register optional unit/integration markers in pytest configuration if used. Cited V IDs are scoped evidence mappings, not claims that every final gate is already complete.

- [ ] T001 Benchmark safe per-pod API and simultaneous-binding Kafka demand.
  - Depends: F12: Kubernetes release (013). Evidence: V-025/V-026; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_capacity_baseline`
  - Accept: capacity/headroom/partition/profile/report known; no total-partition shortcut.
- [ ] T002 Add one ingestion ScaledObject and scoped broker authentication.
  - Depends: T001. Evidence: V-025; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_single_scaling_owner`
  - Accept: one HPA owner, each selected binding represented and TLS/read permissions least privilege.
- [ ] T003 Add independent REST Prometheus demand and aggregation policy.
  - Depends: T002. Evidence: V-025; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_rest_and_combined_demand`
  - Accept: zero Kafka lag still scales API; simultaneous tenant demand uses qualified max/composite rule.
- [ ] T004 Configure baseline/max/stabilization and justified idle-consumer behavior.
  - Depends: T003. Evidence: V-025; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_replica_partition_policy`
  - Accept: min 2, finite max, per-binding useful consumers distinguished from REST replicas and no scale-to-zero.
- [ ] T005 Implement absent-series/scaler-error fallback and single-owner manual recovery.
  - Depends: T004. Evidence: V-025; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_metric_outage_fallback`
  - Accept: finite scalar/TLS checked; missing data visible and qualified fallback never below2.
- [ ] T006 Qualify actual Kafka-only/API-only/mixed scaling and rebalance integrity.
  - Depends: T005. Evidence: V-014/V-025/V-026; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_independent_scaling_load`
  - Accept: decision/startup/drain timings reported, source inventory reconciles and shared bounds hold.
- [ ] T007 Publish F13 cumulative image/config checkpoint and rollback smoke.
  - Depends: T006. Evidence: V-030; applicable F13-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f13.py::test_checkpoint_and_rollback`
  - Accept: one-owner fixed-capacity fallback proven; offsets/routes preserved and later production blockers listed.

Do not mark the checkpoint task complete without candidate-image deployment, real smoke and rollback evidence. Record missing external prerequisites as blocked. Maintain the umbrella roadmap's production eligibility block until later versioning/rotation/full-release gates pass.

