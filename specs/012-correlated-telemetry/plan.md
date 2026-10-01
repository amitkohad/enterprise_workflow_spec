# Implementation Plan: F11 Correlated Telemetry

Spec: [spec.md](spec.md) | Design: [research](../001-enterprise-workflow-platform/research.md),
[security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md)

## Major capability

Wire correlation and telemetry into the existing paths; no new runtime role, aggregator
service or public decoding endpoint. Use structlog, prometheus-client and supported pinned
Temporal OpenTelemetry client/Worker integration. Initialize one Runtime before clients
and inject it into the existing client pool and Worker factory. Separate application and
SDK registries/listeners, even when one Worker process polls multiple queues.

Files: `app/observability.py`, `app/temporal/interceptors.py`, client builder/Worker factory,
API/Event boundary adapters and health router; `tests/unit/test_telemetry_context.py`,
`tests/integration/test_observability.py`, `docs/dashboards/`,
`config/checkpoints/f11/`, `scripts/checkpoints/f11_smoke.py`, `docs/checkpoints/F11.md`.

## Design constraints

Activity interception can measure wall time and must reset context in finally/re-raise
cancellation/errors. Workflow interception uses replay-aware supported facilities without
I/O, wall-clock calls or changed command ordering. Trace metadata is safe plaintext and
validated; it is never used as authorization. Application outcomes are bounded enums.
SDK metric names/units/prefixes come from observed pinned runtime, not guessed dashboards.

Thread bridges explicitly transfer safe correlation context; no process-global mutable
current-workflow fields. Prometheus labels include bounded configured route identifiers;
tenant count is bounded by the inventory, and raw exception strings/offsets/UUIDs stay out.
OTLP batching/export buffers/deadlines are finite with safe drop/error metrics.

## Deployment, validation and rollback

Build cumulative image and launch existing role configurations with private app 8080 and
Worker9090 targets plus a disposable OTLP receiver/Prometheus fixture. Run
`python -m pytest tests/unit/test_telemetry_context.py tests/integration/test_observability.py`
and `python scripts/checkpoints/f11_smoke.py` with approved fixture endpoint options.
Capture sample redacted logs/spans/series and replay-negative/privacy results. Dashboards
are importable data artifacts; installing enterprise monitoring infrastructure is external.
Rollback retains current read keys and prior compatible Workflow registrations. Production
eligibility remains blocked by F12–F16 and cumulative release qualification.
