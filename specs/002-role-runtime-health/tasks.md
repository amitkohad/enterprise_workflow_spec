# Tasks: F01 Role Runtime and Health

Execute T001–T007 in order. These IDs are feature local; identify tasks as `F01/T001`.
Every acceptance below is required to check the task complete. Full V gates are traceability
targets, not claims that the entire final platform exists at this checkpoint.

- [ ] T001 Scaffold the requested packages, pytest config and locked minimal runtime dependencies in `app/`, `tests/`, `pyproject.toml`, `requirements.txt`.
  - Accept: clean installation/import succeeds without I/O or secret reads. Covers F01-01, FR-CORE-02.
- [ ] T002 Implement validated role/environment/HTTP/deadline settings in `app/config/settings.py` with `tests/unit/test_runtime_settings.py`.
  - Depends: T001. Accept: two roles only, finite bounds and safe errors; invalid role cannot start. Covers F01-01/02, V-001 portion.
- [ ] T003 Add startup/live/ready routes and safe state model in `app/api/health.py` with route tests.
  - Depends: T002. Accept: init/drain/readiness transitions differ from liveness and expose no config. Covers F01-02, V-022 portion.
- [ ] T004 Implement observed server lifecycle and SIGTERM shutdown in `app/main.py` with process-level tests.
  - Depends: T003. Accept: essential task failure exits nonzero and cancels siblings; both roles terminate without orphan resources. Covers F01-03.
- [ ] T005 Add one non-root image build in `Dockerfile`/`.dockerignore` with dependency hashes and read-only launch checks.
  - Depends: T004. Accept: identical image launches both roles, contains no secrets, and runs non-root/read-only. Covers F01-04, V-023 portion.
- [ ] T006 Create mounted synthetic role configurations and executable container probe/termination smoke in `config/checkpoints/f01/`, `scripts/checkpoints/f01_smoke.py`.
  - Depends: T005. Accept: each role passes smoke on distinct host ports; malformed role exits before listening. Covers F01-01–04.
- [ ] T007 Record actual image digest/commands/results and rollback in `docs/checkpoints/F01.md`; add these checks to fast CI.
  - Depends: T006. Accept: clean checkout reproduces the checkpoint, incomplete production eligibility is explicit, no task is closed without evidence.
