# Feature Specification: F11 Correlated Telemetry

Feature: `012-correlated-telemetry` | Date: 2026-10-01 | Priority: P2  
Parent: [platform roadmap](../001-enterprise-workflow-platform/roadmap.md) → F11  
Depends: F10 `011-tenant-route-isolation`. Checkpoint: `f11-correlated-telemetry`.

## User outcome

An operator can trace a REST or Kafka start through a tenant's Workflow and Activity,
scrape acceptance/lag/publish/worker metrics and diagnose failures without business data
leaking or replay multiplying telemetry. The complete preceding execution paths remain
runnable from this image. This is an observable qualification deployment of the same app.

## Scope and acceptance

- **F11-01**: Structured JSON logs include trace/workflow/run/type/queue and Activity
  type/attempt where meaningful. Context resets after concurrent operations; errors use
  safe codes, no bodies/tokens/keys/digests/stacks.
- **F11-02**: Validated W3C traceparent propagates across API/Kafka, standardized client,
  replay-safe Workflow interception and Activities. No caller baggage or sensitive headers.
- **F11-03**: App Prometheus `/metrics` is private8080 in both roles; one process Runtime
  exposes WORKER SDK metrics on 9090. Multiple namespace clients/queues never bind additional
  exporters. Metrics use finite route/type/outcome labels, never per-execution IDs.
- **F11-04**: Acceptance/start outcome/latency, broker lag/commit/DLQ/publish, dependency
  health and Worker scheduling/capacity are observable with documented units. Collector
  outages cannot block deterministic execution or create unbounded queues.

Independent test: deploy this image's ingestion and tenant Workers, send one REST and one
Kafka intent plus concurrent multi-tenant/retry/failure flows, inspect correlated spans/logs,
scrape both metric targets and replay a recorded encrypted history. No sensitive sentinel
appears and replay does not duplicate application execution events.

Shared requirements: FR-OBS-01–04, FR-SEC-06, FR-WF-02; V-021 and observability portions
of V-005/V-022. Kubernetes monitoring/scaling and final qualification remain later gates.

## Deployable unit and boundaries

Artifact: same application image at `f11-correlated-telemetry`, private telemetry role
configurations, scrape/OTLP examples, dashboard/alert definitions and end-to-end smoke.
Workflow logical duration uses deterministic SDK time; Activity wall duration uses a
monotonic clock. Telemetry failure is safe and bounded. Rollback uses the previous image
after replay validation and preserves histories, keys, route bindings and source offsets.
