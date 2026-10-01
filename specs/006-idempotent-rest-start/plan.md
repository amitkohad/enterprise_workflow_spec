# F05 implementation plan

Spec: [spec.md](spec.md) | Tasks: [tasks.md](tasks.md)

**Prerequisite checkpoint:** F04 reference Workflow publishes acknowledged events with
encrypted input/result. Implement the eight local tasks in [tasks.md](tasks.md).

## Major capability

Activate authenticated asynchronous REST admission within the existing `INGESTION` role.
Use one trusted route/client first; the API and authorization contracts are final-shaped,
so F10 expands inventory/client selection without changing callers' wire format.

| Area | Change |
| --- | --- |
| `app/temporal/client/start_service.py` | Transport-neutral validation/digest/start/reconciliation outcomes |
| `app/api/models.py` | Authoritative start/error response and request models |
| `app/api/auth.py` | OIDC signature/claim validation and grant/scope dependencies |
| `app/api/main.py` | POST route, limits, deadlines, lifespan ownership and no-store errors |
| `app/config/{settings,routing}.py` | Single approved route, OIDC/cache/admission settings |
| `tests/{unit,integration}/` | JWT/JWKS, canonical identity, concurrent/uncertain start and HTTP checks |

Parse the bounded UTF-8 body strictly before canonicalization. Normalize the header UUID
and body to the shared identity; reject malformed values rather than silently coercing
them. A conforming RFC8785 library is required. Construct encrypted memo and internal
route snapshot from trusted configuration in the same start RPC.

Authenticate and authorize before any Temporal RPC. Fail closed on invalid or expired
verification keys; a bounded valid cache may bridge provider outage within its TTL.
Resolve only the one configured grant/route. The start service reports `started`,
`duplicate`, `conflict`, `retryable_unknown` and `permanent_invalid` internally; the HTTP
adapter maps them to the shared contract. Never rely on an already-started exception alone.

## Deployment and smoke

Generate `config/checkpoints/f05/` and same-image build/container commands in
`docs/checkpoints/F05.md`. Both roles use `python -m app.main`. `INGESTION` has POST plus
existing management routes; omit status business route and Kafka consumer until their
features. Token material is read from a supplied file and never printed or embedded in
config examples. Keep the port 8080 management endpoints private at any ingress.

Retain the predecessor's synthetic `APP_ENV=test` checkpoint configuration until cumulative
production gates pass. JWT/mTLS/payload/broker security is fully exercised; no test-profile
authentication bypass is allowed for this business route.

`scripts/checkpoints/f05_smoke.py --base-url <gateway> --token-file <mounted-token>` must
exercise 202/200/409/400/401, confirm the same returned UUID on replay, and use a privileged
synthetic observation fixture to verify one reference execution and its Kafka event.
That fixture observes backend evidence; it is not an added production API. Concurrent and
ambiguous-start tests use a real Temporal service and a controlled response-loss seam.

## Rollback and release eligibility

Reject new admission during drain, resolve or leave caller-retryable starts under their
original IDs, restore the F04 gateway, and retain F04/F05-compatible Worker pollers. Removing
the POST endpoint does not cancel already accepted Workflows. Test rollback with an accepted
run still open and verify it completes/publishes after the gateway downgrade. Namespace
retention, keys and route binding remain unchanged. Controlled staging may deploy this
increment; general production requires cumulative release qualification, including later
Kafka recovery/observability/deployment gates where those capabilities are enabled.
