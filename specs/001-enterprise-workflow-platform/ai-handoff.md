# AI Implementation Handoff: One Feature at a Time

The user confirmed **deployable increments of one application**. Follow the
[16-feature roadmap](roadmap.md), keeping one repository, one Dockerfile/image
and APP_ROLE=INGESTION|WORKER. Each accepted feature produces a deployable version
including its prerequisites. No feature is a separate microservice.

This package uses [GitHub SpecKit's spec-of-specs approach](https://github.github.com/spec-kit/concepts/spec-of-specs.html).
CLI integrations have not been installed or invoked here. Any AI tool can read
these artifacts; if SpecKit is already configured, use its analyze/implement/converge
steps scoped to one existing feature, using the invocation supported by that integration.

## Read order

1. `.specify/memory/constitution.md`.
2. `specs/001-enterprise-workflow-platform/spec.md` and `roadmap.md`.
3. The selected feature's `spec.md`, `plan.md` and `tasks.md`.
4. Referenced shared research/security/data-model/contracts/operations/verification sections.
5. Prerequisite checkpoint evidence from the generated `docs/checkpoints/Fxx.md`.

The parent `plan.md` is the shared architecture; feature plans define incremental work.
Parent `tasks.md` is an index. `task-reference.md` is superseded and must not be executed.
Resolve contradictions before coding. Official APIs are verified in F02 against locked
dependencies. Do not regenerate all feature specs or invent infrastructure services.

## Initial feature prompt

```text
Implement F01 from specs/002-role-runtime-health as a deployable increment of
temporal-enterprise-framework. Read its spec.md, plan.md, tasks.md, the constitution
and parent roadmap/platform contract.

Preserve one application/image and APP_ROLE=INGESTION or WORKER. Generate files
at repository root following app/api, app/events, app/temporal/{activities,
workflows,client,worker}, app/config and app/main.py. Do not add a database,
microservice, UI, DSL or third production role.

Implement F01/T001 only. Add its meaningful checks and report actual evidence.
Mark it complete only when its local acceptance passes. Stop before T002.
```

## Repeated task prompt

Replace feature path and local ID with the next unchecked task.

```text
Implement F05/T003 in specs/006-idempotent-rest-start/tasks.md only.
Read this feature's spec/plan, constitution, cited shared requirements/contracts
and prerequisite checkpoint evidence. Implement the smallest reviewable behavior.

Run the task-local checks and relevant earlier regressions. Report changed files,
exact commands/results, FR and V traceability, remaining risks and blocked evidence.
Do not substitute mocks for required real-service acceptance.
Check the task complete only when its own acceptance passes; do not claim the whole
V gate passes if this task covers only a unit portion. Stop before the next task.
```

At a feature's last task, build/deploy its cumulative image in the documented
synthetic checkpoint, execute its smoke proof and record image digest, role config,
acceptance and rollback in `docs/checkpoints/Fxx.md`. Never mark a feature accepted
because files were created. Early checkpoints are qualification releases only.

## Output for every task/checkpoint

```text
Feature/task: Fxx/Txxx
Requirements and acceptance: ...
Files changed: ...
Commands/results: passed | failed | blocked, with actual evidence
Verification coverage: task-local portion | complete named gate
Checkpoint image digest/config/smoke: ... (at feature completion)
Risks, prerequisites and production eligibility: ...
Completion: complete | incomplete
Next task/feature: ...
```

## Implementation invariants

- Codec returns Payload sequences and encrypts full original Payload metadata.
- Protect encoded failure messages/stacks; preserve retry/cancellation semantics.
- mTLS verifies trust/identity; production keys are mounted namespaced keyrings.
- Workflow code stays deterministic; all broker calls run in bounded owner threads.
- REST retains caller UUID; Kafka key equals message_id and Workflow ID.
- Duplicate acceptance verifies encrypted digest and immutable route memo.
- Ingestion never waits for Workflow completion; offsets require durable start or DLQ ack.
- Stable publish_id tolerates Activity retries; downstream dedup is (tenant_id,publish_id).
- Context resets; replay is safe; app 8080/Worker SDK 9090 are distinct private listeners.
- Namespace clients/consumer bindings are bounded; Worker limits are process budgets.
- Pinned builds have separate retained Kubernetes Worker Deployments.
- Old encryption keys and compatible Worker versions remain available for retained history.
- No public codec server, new database, runtime workflow interpreter or extra role.

## Final release gate

After F16, run every parent FR/SC and V-001–V-030 release gate with actual unit,
Workflow, real-service, encrypted replay, TLS/tenant/privacy, crash/rebalance,
container/cluster/network/scaling, rollout/rotation and capacity evidence.
Report missing infrastructure as blocked. Production promotion/deployment and
credential changes remain operator actions; this specification package performs none.
