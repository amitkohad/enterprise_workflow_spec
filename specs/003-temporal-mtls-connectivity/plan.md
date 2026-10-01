# F02 plan — Verified connection in a running image

Implement the corresponding [F02 specification](spec.md) after its accepted prerequisite checkpoint.

The major capability is secure connection bootstrap and its effect on runtime health. Extend F01 without creating another binary, image or role.

## Implementation surfaces

| File | Purpose |
|---|---|
| `app/config/settings.py` | Validated endpoint, namespace, deadlines and certificate/profile references |
| `app/config/credentials.py` | Path-only mounted credential profiles; redacted validation |
| `app/temporal/client/__init__.py`, `builder.py` | Verified TLS builder and atomic bounded startup-snapshot client registry |
| `app/api/health.py`, `app/main.py` | Cached preflight state and supervised retry/shutdown integration |
| `scripts/smoke/temporal_connectivity.py` | One-shot bounded connection/namespace evidence; no Workflow start |
| `tests/unit/test_tls_config.py`, `test_client_registry.py` | Configuration, redaction and lifecycle cases |
| `tests/integration/test_temporal_connectivity.py` | Actual TLS/namespace positive and negative checks |

Read profile paths only from trusted configuration. Validate certificate/key/CA files and the exact SDK TLS options before connection. Use endpoint DNS matching the server certificate; an approved explicit verification name retains chain/name validation. All required profiles are resolved once at bootstrap; client registry keys include namespace/profile/certificate snapshot and are confined to one process/event loop. Certificates change through rolling process restart.

Preflight uses a bounded supported namespace/service operation selected in the SDK compatibility check. It records only allowlisted outcomes and refreshes cached readiness on a finite interval/backoff. Do not call Temporal on every health request. Startup/readiness fail on invalid credentials; temporary dependency errors degrade readiness without failing liveness. This release has no business ingress handlers or Workflow registrations, so a pre-encryption client cannot accidentally send business payloads.

## Deploy, smoke and rollback

Deploy the F01 image/run configuration updated with certificate/profile mounts for both roles and an external TLS-enabled Temporal target. Local/CI tests may provision synthetic certificates and namespaces on a disposable service. These are test prerequisites, not an additional production application role. Mount secrets read-only and retain private operational access on 8080.

Run the connectivity smoke module against the same settings as each deployed role; collect the image digest, SDK/version matrix, namespace, approved outcome and probe transitions. Exercise negative certificates/trust/hostname as separate runs with bounded cleanup. A mock TLS object cannot satisfy the integration gate.

Rollback to the previous checkpoint image and its approved configuration; it remains a health-only runtime. No Workflow histories or business side effects are created by this feature. Before accepting later business traffic, retain this transport policy and add the subsequent converter/authorization gates.

## Verification boundary

Use the scoped cases in V-001/V-006/V-022. Unit tests establish parser/registry behavior; real service checks establish TLS and namespace access. Record unverified platform/SDK/server combinations explicitly. A partial checkpoint must never be labeled production platform ready.
