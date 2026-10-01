# Tasks: F11 Correlated Telemetry

Feature-local IDs `F11/T001` onward; execute in order after F10 acceptance. Task-local
checks cover the stated behavior; full V-021 is closed only after T007 integration evidence.

- [ ] T001 Add redacted JSON logging and scoped context binding/reset in `app/observability.py` with concurrent-context unit tests.
  - Accept: standard safe fields and fixed errors, no cross-request/thread context leakage or sensitive values. Covers F11-01, FR-OBS-01.
- [ ] T002 Add deterministic replay-aware Workflow and wall-clock Activity interceptors in `app/temporal/interceptors.py`.
  - Depends: T001. Accept: Activity attempt/duration logged, Workflow replay suppresses duplicate execution events, cancellation/errors propagate unchanged. Covers F11-01/02, FR-WF-02.
- [ ] T003 Wire validated trace propagation through API/Kafka/client/Worker/Activity boundaries using pinned supported integration.
  - Depends: T002. Accept: same logical flow correlates and only safe traceparent enters headers; invalid context is safely ignored/rejected per contract, no baggage. Covers F11-02.
- [ ] T004 Initialize one Runtime SDK exporter9090 for WORKER and app metrics8080 for both roles in bootstrap/client/factory.
  - Depends: T003. Accept: multiple queues/clients do not duplicate registry/listeners; INGESTION never binds9090; both private scrape jobs succeed. Covers F11-03.
- [ ] T005 Add finite acceptance/Kafka/publish/dependency metrics and observed SDK scheduling/capacity series with unit documentation.
  - Depends: T004. Accept: relevant paths produce expected outcome counters/histograms, no UUIDs/offsets/sensitive labels and exporter buffers remain bounded. Covers F11-04.
- [ ] T006 Add importable dashboard/alert definitions and collector-outage/replay/privacy tests under `docs/dashboards/` and `tests/integration/test_observability.py`.
  - Depends: T005. Accept: actual metric names/units work, concurrent tenant/retry/replay privacy passes and collector outage does not block Workflow progress. Covers V-021.
- [ ] T007 Build/deploy cumulative image with `config/checkpoints/f11/`, run `scripts/checkpoints/f11_smoke.py` and record `docs/checkpoints/F11.md`.
  - Depends: T006. Accept: end-to-end REST/Kafka execution remains functional with correlated telemetry, all F11 checks have real evidence and rollback is replay compatible.
