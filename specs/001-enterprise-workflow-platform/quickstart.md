# Implementation quickstart and environment handoff

This repository currently contains specifications. The commands below are the intended
operator experience after implementing the task backlog; they do not claim an application,
Docker image, Helm chart or passing runtime tests already exists.

## Before implementation

Read [ai-handoff.md](ai-handoff.md), follow [roadmap.md](roadmap.md) F01–F16 and implement
each feature's local task list in order. The old global task reference is superseded.
Use Linux CI for the qualified container/test-server baseline; local Windows editing is
supported, while SDK/test-server binary availability is verified in F02/F03. Create generated
application files at repository root; the current checkout directory need not be renamed.

Supply staging infrastructure values before real integration/cluster gates:

| Input | Owner and expected value |
|---|---|
| Temporal endpoint/service capabilities | Platform owner; supported version, namespace permissions and 30d baseline closed-history retention |
| Tenant routes/namespaces | Platform owner; approved opaque IDs, one namespace per tenant and bounded queue inventory |
| TLS profile mounts | Security owner; cert/key/CA paths, verified server identity and rotation window |
| Namespaced encryption keyring | Security owner; SEC-KEYS manifest, active+retained IDs, backup/restore and usage policy |
| Kafka endpoints/topics/groups/ACLs | Streaming owner; trigger/output/DLQ bindings, TLS/SASL profiles and 7d baseline replay window |
| OIDC issuer/audience/JWKS/grant mapping | Identity owner; asymmetric allowlist and tenant/domain scope claims |
| Kubernetes/CNI/KEDA/monitoring | Cluster owner; supported versions, egress/DNS assumptions, private scrape and OTLP endpoints |
| Image registry/resources/quotas | Release owner; immutable digest, CPU/memory limits, external rate/concurrency quotas |

Environment-specific values must pass configuration/preflight checks. Production never
uses fixture keys or disables TLS. No credentials are needed to finish the specification.

## Required generated local experience

The relevant feature checkpoint tasks must document commands to provision synthetic external test services, namespaces,
topics and disposable keys/certificates. Require explicit `APP_ENV=local|test` for insecure
fixtures, isolate them from production defaults, and clean them up using the provided tool.
Then the following role commands should work with complete config and mounted fixtures:

```text
python -m pip install --require-hashes -r requirements.txt
python -m app.main
```

Run the entrypoint once with `APP_ROLE=WORKER` and once with `APP_ROLE=INGESTION`, in separate
processes/containers. A single role process is not both roles. Both roles expose private
app health/metrics8080; WORKER also exposes private SDK metrics9090. Distinct local host
port mappings avoid collisions. `TEMPORAL_NAMESPACE` selects the Worker namespace, and
the route/config/profile files select approved ingestion bindings.

The documented synthetic demonstration must:

1. Start both roles and verify startup/readiness.
2. Obtain a disposable test token with the required tenant/domain scopes.
3. POST a valid body with a pre-generated canonical UUID Idempotency-Key; see OpenAPI example.
4. Repeat the request and observe a verified duplicate200 with the same ID/run identity.
5. GET status with tenant/domain and request the completed receipt only when authorized.
6. Produce the contract event with its matching UUID key; inspect its Workflow and output.
7. Verify the outgoing workflow.processed publish_id and demonstrate downstream dedup.
8. Scrape app and SDK metrics; inspect raw history for encrypted business Payloads.
9. Send SIGTERM; observe drain/commit fences and recover uncommitted work on restart.

## Required generated verification commands

Implementation documentation must expose separate commands for these layers:

```text
python -m pytest tests/unit
python -m pytest tests/workflow
python -m pytest tests/replay
python -m pytest tests/integration
```

V-001–V-030 in [verification.md](verification.md) specify environment and pass conditions.
Real-service tests must report missing infrastructure as blocked, not silently pass with
mocks. Load/cluster tests require a staging environment and produce measurement reports.

## Required generated production experience

Build and scan the one image, render/validate the chart with approved values, then deploy
the two roles using that same digest through the organization's release process. Run
staging TLS/network/lifecycle/scale/qualification gates before production promotion.
The specification does not authorize an AI generator to deploy or rotate live credentials.
Use [operations.md](operations.md) for upgrade/rollback/rotation/recovery conditions.
