# Implementation Plan: F01 Role Runtime and Health

Spec: [spec.md](spec.md) | Parent: [shared architecture](../001-enterprise-workflow-platform/plan.md)

## Major capability

Create a deployable, supervised role process. Use Python 3.11+, FastAPI/Uvicorn and typed
settings. Network clients and secrets are not initialized at import. An operational app
serves health for both role shells; later features attach business routers/consumer/Workers
to the same supervisor. There is one Uvicorn process per container.

Files: `app/main.py`, `app/config/settings.py`, `app/api/health.py`, package init files,
`pyproject.toml`, hash-locked requirements, `Dockerfile`, `.dockerignore`,
`tests/unit/test_runtime_settings.py`, `tests/integration/test_runtime_shell.py`.

## Lifecycle and artifact

Use one observed TaskGroup and explicit initialization/draining state. Configure an overall
hard exit deadline110s, leaving headroom in the later120s Kubernetes grace. Shell exits
promptly when idle. Production default remains fail closed; this incomplete release is
run only with explicit test configuration. Do not add a third role or feature-stage enum.

Build with `docker build -t temporal-enterprise-framework:f01-runtime-health .`, record
its digest, and document role-specific `docker run` commands with mounted fixture config,
read-only filesystem, non-root UID and distinct host port mappings. Create
`scripts/checkpoints/f01_smoke.py` to query probes, signal shutdown and validate process
exit; it is a finite test utility, not a deployed production service.

## Validation and rollback

Commands: `python -m pytest tests/unit/test_runtime_settings.py` and
`python -m pytest tests/integration/test_runtime_shell.py`; run the container smoke utility
for each role. Verify valid/invalid role, startup failure, non-root/read-only launch and
SIGTERM behavior. Publish `docs/checkpoints/F01.md` with real evidence. Production release
eligibility is explicitly false. Preserve this supervisor as features are added.
