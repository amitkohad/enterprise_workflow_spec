# F12 tasks

**Prerequisite:** F11: correlated telemetry (012) completed and its runnable checkpoint available. IDs below are local to F12; execute in numeric order.

Each task implements one named behavior and runs the exact pytest node below. Create the test alongside the behavior; register optional unit/integration markers in pytest configuration if used. Cited V IDs are scoped evidence mappings, not claims that every final gate is already complete.

- [ ] T001 Build reproducible non-root cumulative image.
  - Depends: F11: correlated telemetry (012). Evidence: V-023; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_image_security`
  - Accept: locked/hash dependencies, no secret/test fixture content and both roles run under read-only root.
- [ ] T002 Render role Deployments with immutable Worker build identities.
  - Depends: T001. Evidence: V-023/V-028; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_role_and_build_resources`
  - Accept: same candidate digest, unique build selectors/names, explicit role config and no old-image replacement.
- [ ] T003 Add secret/profile mounts and private service/scrape contracts.
  - Depends: T002. Evidence: V-023; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_secret_service_boundaries`
  - Accept: path-only references, no token by default and distinct8080/9090 private scrape jobs.
- [ ] T004 Add probes/resources/PDB/topology and 120s grace.
  - Depends: T003. Evidence: V-022/V-023; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_probe_resource_contract`
  - Accept: finite process-wide allocations, min 2, exact status probes and 90/110s lifecycle settings.
- [ ] T005 Add ingress TLS and role-specific least-privilege NetworkPolicy.
  - Depends: T004. Evidence: V-024; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_rendered_network_contract`
  - Accept: only explicit API path exposed; DNS/advertised brokers/OIDC/OTLP/monitoring/probe allowances configurable.
- [ ] T006 Validate actual allowed/blocked network traffic on restricted cluster.
  - Depends: T005. Evidence: V-024; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_cluster_network_boundaries`
  - Accept: real CNI proves broker/DNS/TLS/JWKS/scrapes work and unrelated egress/public metrics fail.
- [ ] T007 Exercise actual cluster startup/outage/drain and encrypted smoke.
  - Depends: T006. Evidence: V-022/V-023; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_cluster_lifecycle_smoke`
  - Accept: same image role flow, correct readiness/liveness and recoverable current-fence shutdown.
- [ ] T008 Publish F12 chart checkpoint and prove compatible rollback preservation.
  - Depends: T007. Evidence: V-030; applicable F12-R requirements.
  - Run: `python -m pytest tests/integration/test_feature_f12.py::test_checkpoint_and_rollback`
  - Accept: image/config/cluster evidence recorded, old named Worker resources retained and F15/F16/full-gate production block explicit.

Do not mark the checkpoint task complete without candidate-image deployment, real smoke and rollback evidence. Record missing external prerequisites as blocked. Maintain the umbrella roadmap's production eligibility block until later versioning/rotation/full-release gates pass.

