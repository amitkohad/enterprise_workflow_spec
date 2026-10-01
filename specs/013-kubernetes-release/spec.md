# F12 — Deploy the cumulative application with Kubernetes boundaries

**Status:** specified; no implementation, build, deployment or smoke has been executed by this document.

**Roadmap entry:** [F12 in the parent feature index](../001-enterprise-workflow-platform/roadmap.md#feature-index-and-corresponding-plans).

**Predecessor:** F11: correlated telemetry (012). **Program boundary:** the same temporal-enterprise-framework repository/image with APP_ROLE=INGESTION or WORKER. Feature IDs denote deployable increments, not independent microservices.

## Outcome and scope

Package all completed capabilities as one immutable image and a production-shaped Helm deployment with INGESTION and namespace-scoped WORKER roles, mounted secrets, probes, resource bounds and least-privilege network access. This increment proves actual Kubernetes operation, rather than only providing unexecuted YAML.

Infrastructure remains external: Temporal/Kafka/OIDC/KMS secret provisioning/Prometheus/ingress/CNI/KEDA. No application database, UI, third role or new control-plane service. The chart supports distinct immutable Worker Deployments per build, but F15 owns PINNED routing/promotion qualification. Production release remains blocked by F15/F16 and all mandatory V gates.

## Functional contract

- **F12-R01:** Render separate INGESTION and WORKER Deployments from the same built artifact for a candidate version, with APP_ROLE and explicit namespace/queues/profile selection. Worker versions receive unique immutable Kubernetes names/image digests so old pinned builds can coexist; overwriting their image is forbidden.
- **F12-R02:** Run one Uvicorn process/pod without reload; expose API through TLS ingress on 8080 only. Worker8080 has operational endpoints only. Application metrics8080 and Worker SDK 9090 are distinct private scrape targets.
- **F12-R03:** Non-root UID/GID, no privilege escalation, read-only root, RuntimeDefault seccomp, dropped capabilities, read-only mounted cert/key/keyring and finite writable temp volume. No service-account token/RBAC by default.
- **F12-R04:** Set finite requests/limits and documented process task budgets:32 Workflow slots/64 Activity slots/1000 cache allocated across 1-4 queues; shared producer waits64. Production floor2 per active deployment, PDB/topology policies and grace120s. Normal drain90/hard exit110.
- **F12-R05:** Startup/readiness/liveness paths/statuses match the API contract and cached health logic; remote outage removes readiness without liveness storms. Probes/metrics never become public ingress paths.
- **F12-R06:** Default-deny NetworkPolicy explicitly allows approved DNS, Temporal TLS, all Kafka advertised brokers, OIDC/JWKS, optional OTLP, monitoring and tested kubelet probe paths. CNI/FQDN/egress-gateway assumptions require actual cluster proof.
- **F12-R07:** Secret references/credential profiles contain paths only; no private keys/password values in chart/example/image. Validate values, namespace/queue registrations and role mounts before admission.

## Acceptance and evidence

Build image, render/chart-schema/admission validate, then launch both roles on a policy-enforcing restricted staging cluster with real mounted TLS dependencies. Prove one REST and Kafka encrypted flow, both scrape targets, startup/outage/SIGTERM behavior, allowed DNS/broker/OIDC paths and blocked public telemetry/unrelated egress. Render two Worker build identities side-by-side and reject old Deployment image replacement.

Each task supplies its local scoped evidence; referenced umbrella V IDs are traceability to final release gates. A passing local case does not mark unrelated future cases complete. Real service/cluster checks cannot be satisfied by mocks. Tests use synthetic data and injected secrets, never production histories or committed keys.

## Deployable checkpoint

Deliver immutable digest, Helm chart/qualification values, exact install/render commands and cluster smoke evidence. Candidate INGESTION and WORKER use the same artifact; retained historical Worker builds may have their prior digests. No automatic production promotion follows this checkpoint.

This checkpoint may be marked development/staging deployable only after its real smoke and rollback evidence pass. Production approval requires F15 qualified PINNED multi-Deployment rollout/retention, F16 key/certificate rotation and every applicable umbrella V/FR/SC release gate; earlier checkpoints do not waive them.

## Rollback contract

Drain ingestion before compatible image/config rollback and preserve source offsets/routes/keys. Retain all named Worker build Deployments needed for pinned runs; never replace old image to mimic rollback. F15 supplies qualified routing rollback; here validate chart resource preservation and document the outstanding release block.

## Shared normative references

[Platform specification](../001-enterprise-workflow-platform/spec.md), [roadmap](../001-enterprise-workflow-platform/roadmap.md), [data model/contracts](../001-enterprise-workflow-platform/data-model.md), [security](../001-enterprise-workflow-platform/security.md), [operations](../001-enterprise-workflow-platform/operations.md), [verification](../001-enterprise-workflow-platform/verification.md). Resolve disagreement before implementation; this feature refines incremental scope without weakening final production requirements.

