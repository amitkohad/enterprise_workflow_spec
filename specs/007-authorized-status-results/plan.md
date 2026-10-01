# F06 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md)

**Prerequisite checkpoint:** F05 authenticated idempotent start and F04 acknowledged
reference Workflow execute in deployed same-image roles. Implement eight local tasks.

## Major capability

Add an authorized, bounded execution read service and GET adapter. Reuse existing JWT
validation, single approved route/client, converter, no-store/sanitized error handling and
role lifecycle. A status read does not create a Worker or another service.

| Area | Change |
| --- | --- |
| `app/api/models.py` | Status/optional result/fixed terminal error schemas |
| `app/api/auth.py` | Read and conditional result scopes; concealed tenant/domain authorization |
| `app/temporal/client/read_service.py` | Bounded describe, selected-run identity check, optional completed receipt |
| `app/api/main.py` | GET route and shared error/header mapping |
| `tests/{unit,integration}/` | States, scopes, deadlines, identity concealment and qualified run semantics |

An explicit `run_id` binds the requested run. Otherwise obtain the latest through supported
SDK semantics and use describe's exact selected ID for a later result fetch. Test-only
chain fixtures qualify this behavior against the pinned SDK/server. Use the shared total
read budget for describe, memo conversion and optional result decode; no separate unbounded
budget per hop. Confirm `COMPLETED` before result retrieval, set run following false, and
return the selected run in all responses.

Scope checks occur before backend lookup. Tenant/domain denials become generic 404;
missing scopes are 403. Backend memo must match the authorized route and registered type.
Do not return raw Temporal failure details. Terminal error code/message derives only from
allowlisted status, and no result appears for noncompleted states.

## Checkpoint deployment and smoke

Generate `config/checkpoints/f06/`, same-image `docker build`/`docker run --env-file`
commands and `scripts/checkpoints/f06_smoke.py --base-url <gateway> --token-file <token>`.
The script accepts separate read-only, result-authorized and wrong-grant token fixtures,
never prints tokens, and proves start → immediate status → completed receipt plus
authorization failures. Result polling in this synthetic smoke script has a finite deadline;
the production GET operation itself never waits for completion.

Record image digest, environment/config identities, real-service state and scope checks,
and retained F05 start/duplicate evidence in `docs/checkpoints/F06.md`. Mark individual
shared verification cases covered here; do not claim complete V-010/V-011 or production
qualification while tenant expansion and other cumulative requirements remain pending.

## Rollback and production eligibility

Drain GET requests and deploy the F05-compatible image/config. Retain production reference
Workers and encryption read keys; this read-only feature changes no durable command order.
Demonstrate one accepted Workflow completing after the downgrade and F05 POST/duplicate
smoke still succeeding. Record loss of GET availability for callers as an operational
rollback effect. Independent controlled staging deployment is allowed; production approval
uses cumulative implemented-capability security, recovery and operational evidence.
