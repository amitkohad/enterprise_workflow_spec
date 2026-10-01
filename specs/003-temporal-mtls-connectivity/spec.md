# F02 — Temporal mTLS connectivity

**Status:** planned deployable increment; no implementation evidence yet.  
**Parent:** [roadmap entry F02](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).  
**Prerequisite:** [F01 runtime health](../002-role-runtime-health/spec.md).  
**Program:** the same repository/image with `APP_ROLE=INGESTION|WORKER`.

Deliver a running image that verifies its Temporal connection and selected namespace through mounted mTLS credentials, exposes the F01 health endpoints, and becomes unready when a required connection is unavailable. This checkpoint makes no business Workflow starts and adds no public endpoint, controller or third role. It can be deployed and smoke-tested before payload handling or ingestion is implemented.

## Scoped requirements

| ID | Required behavior | Core traceability |
|---|---|---|
| F02-01 | Strict endpoint/namespace/profile settings; mounted certificate, private key and trust CA; approved verified DNS identity | FR-CORE-03, FR-SEC-04 |
| F02-02 | One bounded process/event-loop client registry; key includes namespace, credential profile and startup certificate snapshot | FR-ROUTE-04 |
| F02-03 | Bounded handshake/namespace preflight outside Workflow code; safe reason codes and no secret contents | FR-SEC-04, FR-SEC-07 |
| F02-04 | Both roles report initialization/dependency/drain readiness correctly; dependency outages do not cause liveness restart storms | FR-CORE-04 |
| F02-05 | Production has no TLS downgrade or hostname-verification bypass; unsupported configuration fails before ready | FR-SEC-04 |

Use the current SDK's verified TLS configuration; its API exposes client identity, CA and certificate-name options. [TLSConfig reference](https://python.temporal.io/temporalio.client.TLSConfig.html). Retrieved 2026-10-01. Exact SDK/import/field availability is verified against the locked dependency, not inferred from a moving documentation page.

## Acceptance scenarios

1. With valid mounted credentials and an authorized synthetic namespace, deploy each role; `/health/ready` reaches 200 and the smoke script records endpoint/namespace/build identity without secret values.
2. With unknown CA, wrong verified hostname, missing/mismatched pair, expired client certificate or rejected namespace access, the preflight fails with an approved code and readiness remains 503. No insecure reconnect occurs.
3. Temporarily remove Temporal connectivity after startup; cached bounded readiness becomes degraded, liveness remains healthy, and readiness recovers when access returns.
4. Concurrent requests for the same approved connection initialize one client. A different profile/namespace never reuses that client's identity. Restart, rather than in-process reload, applies rotated material.
5. SIGTERM marks the process unready and closes owned resources according to supported SDK APIs; it does not invent a `Client.close()` method.

A successful DescribeNamespace or equivalent preflight establishes only the permissions actually exercised. It does not prove business start, worker poll or result-read authorization. Those become acceptance cases in their owning features.

## Runnable checkpoint and eligibility

Build the updated image; run one instance of each role with operator-supplied endpoint/profile mounts; execute `python -m scripts.smoke.temporal_connectivity --config <non-secret-config>`. The script performs only bounded connection/namespace checks and writes a sanitized JSON result. The runtime has operational routes only at this checkpoint. It is eligible for connectivity qualification deployment, not enterprise business traffic; encryption, tenant authorization, delivery, capacity and final release gates remain required.

Shared authority: [feature roadmap](../001-enterprise-workflow-platform/roadmap.md), [core spec](../001-enterprise-workflow-platform/spec.md), [transport security](../001-enterprise-workflow-platform/security.md#sec-transport--mtls-and-kafka-security), [verification V-001/V-006/V-022](../001-enterprise-workflow-platform/verification.md).
