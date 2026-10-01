# F15 tasks — Execute sequentially

Prerequisites: F12 Kubernetes release, F14 Worker autoscaling and F11 telemetry checkpoints and their prerequisite chain. The same image/roles remain the deployment unit.

- [ ] T001 Verify selected real service/SDK versioning APIs and immutable identity settings.
  - Accept: WorkerDeploymentConfig/VersioningBehavior and supported routing/reachability operations established; unsupported mode blocks PINNED startup; no silent fallback. Scope: F15-01/F15-06, capability portion V-028.
- [ ] T002 Wire PINNED reference registration, immutable build identity and disabled eager start in the worker/client factories.
  - Depends: T001. Accept: focused config test and real worker registration prove the selected version identity; incompatible config fails early. Scope: F15-01/F15-04.
- [ ] T003 Make Helm Worker releases/resources immutable per build and version-scope KEDA/scrapes.
  - Depends: T002. Accept: render A+B side by side; same build cannot change image digest; names cannot collide; scalers select exactly their build and preserve retained floors. Scope: F15-02/F15-03, V-023/V-025.
- [ ] T004 Implement read-only release verifier and encrypted replay gate in `scripts/qualify/worker_rollout.py`.
  - Depends: T003. Accept: correct namespace/converter/retained keys used; negative replay/control rejects promotion; readiness alone cannot pass. Scope: F15-04, V-020.
- [ ] T005 Add bounded canary/promote/ramp operations using supported routing controls.
  - Depends: T004. Accept: authorized staging canary and assigned-version evidence pass before routing change; secrets never in reports. Scope: F15-04, V-028.
- [ ] T006 Add routing rollback and evidence-based retire operations.
  - Depends: T005. Accept: rollback affects new runs only; B-pinned runs still served; open/reachable/retention obligations refuse unsafe retirement; delete exact approved release only. Scope: F15-05, V-028.
- [ ] T007 Execute A/B rollout/rollback/scale/retirement integration and document explicit compatible-rolling/authoring guidance.
  - Depends: T006. Accept: old held run completes on A, new B run survives rollback, both scale independently, unsafe retirement fails; exception uses patch/replay evidence; docs/workflow-authoring.md covers typed schema evolution and bounded Continue-As-New without adding production loops. Scope: all F15, FR-WF-06, V-025/V-028.
- [ ] T008 Deploy the versioned release checkpoint and record commands/evidence in `docs/checkpoints/F15.md` and rollout runbook.
  - Depends: T007. Accept: reproducible same-program release, retained image/key inventory and rollback procedure delivered; remaining roadmap gates explicit. Scope: all F15.
