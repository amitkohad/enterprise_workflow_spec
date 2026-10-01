# F03 plan — Run and inspect a protected finite Workflow

Implement the corresponding [F03 specification](spec.md) after its accepted prerequisite checkpoint.

The major capability is SDK-integrated payload/failure protection demonstrated by a deployed worker and a real encrypted history.

## Implementation surfaces

| File | Purpose |
|---|---|
| `app/config/key_provider.py` | Strict immutable SEC-KEYS namespace snapshots/active expiry |
| `app/temporal/converter.py` | Full-Payload AEAD envelope and typed/failure converter factory |
| `app/temporal/client/builder.py` | Inject namespace-scoped factory into every data-bearing client |
| `app/temporal/worker/__init__.py`, `factory.py` | Finite qualification registration and bounded worker lifecycle |
| `app/temporal/workflows/qualification_echo_workflow.py` | Sandbox-safe, finite test-only Workflow |
| `app/temporal/activities/qualification_activity.py` | Synthetic echo/heartbeat/failure paths with explicit deadlines |
| `scripts/smoke/encrypted_roundtrip.py` | Bounded start/result/raw-history/replay qualification command |
| `tests/unit/test_codec_*.py`, `test_failure_converter.py`, `test_key_provider.py` | Crypto construction/parser/semantic cases |
| `tests/workflow/test_qualification_echo.py`, `tests/integration/test_encrypted_history.py` | Actual SDK conversion and raw-history evidence |

Implement the keyring/envelope exactly as shared security specifies, including namespace scope, 12-byte OS-random nonce and complete authentication tag. Serialize the whole Payload before encryption; restore its metadata before typed conversion. Enforce encoded-size limits and strict parsing. Configure encoded failure common attributes and keep exposed operational type names safe. Do not catch all failures and return a fake successful value.

The finite Workflow schedules one synthetic Activity. Its test-only input selects echo or intentional failure; arbitrary code/topic/namespace selection is forbidden. Activity heartbeats use the production converter and a bounded wait; no broker dependency is required. The Workflow uses deterministic SDK APIs, keeps the sandbox enabled and never reads keys/settings. Registration is gated by explicit test profile and absent from production registry.

Test-server workers may use an explicitly documented unversioned qualification configuration when the selected time-skipping server lacks production versioning APIs. This verifies encryption/replay, not production Worker Deployment routing; F15 establishes that separately against a qualified service.

## Deploy, smoke and rollback

Build one image and deploy a secure WORKER plus the operational INGESTION instance using F02 mounts and additional synthetic keyring. Use an isolated namespace/queue so production consumers cannot acquire qualification tasks. A smoke client independently loads its authorized key snapshot, submits the finite Workflow and reads its result under deadlines. A raw-history reader retrieves wire history without business decoding; it requires approved test access but no business data key to inspect ciphertext. Inspect Payload content, Memo, failure details and safe public metadata separately. The Activity's finite heartbeat wait provides a sampling window: poll a bounded raw Describe response while it remains pending and inspect its last heartbeat details before completion. Do not claim that ordinary heartbeats appear as permanent History events.

Capture a success and intentional-failure encrypted synthetic fixture and replay using the actual namespace/factory/fixture keys. No production keys or decrypted data enter Git. Fixed publicly known fixture keys may be used only for clearly synthetic test fixtures and never mounted into production; production key provenance remains external.

Rollback stops new qualification submissions and returns to the F02 operational image after synthetic executions finish. If a fixture/test run remains open, retain the reader keys and worker image needed to finish or clean it through authorized test tooling. Never roll back a later business release to this pre-business checkpoint; production migration is governed by the final versioning/retention contract.

## Scoped verification and eligibility

Run the F03 portions of V-002–V-005/V-019/V-020 with actual SDK workers and real TLS history inspection. Unit round-trip alone does not satisfy confidentiality. Record version/namespace/key IDs, observed outcomes and missing gates without values. Full ingestion, Kafka, OIDC, production registry/versioning and capacity are later features.
