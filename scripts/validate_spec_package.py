"""Validate specification links, task graphs and contract examples (not runtime code).

Requires PyYAML. This is purpose-built structural/example validation, not a full
OpenAPI or JSON Schema standards validator. Full standards validation remains a
generated-implementation gate. Run: python scripts/validate_spec_package.py
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.parse

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PARENT = ROOT / "specs/001-enterprise-workflow-platform"
FEATURES = [
    "002-role-runtime-health", "003-temporal-mtls-connectivity",
    "004-encrypted-workflow-roundtrip", "005-acknowledged-kafka-publication",
    "006-idempotent-rest-start", "007-authorized-status-results",
    "008-kafka-trigger-start", "009-dlq-disposition", "010-rebalance-recovery",
    "011-tenant-route-isolation", "012-correlated-telemetry",
    "013-kubernetes-release", "014-ingestion-autoscaling",
    "015-worker-autoscaling", "016-pinned-worker-rollout",
    "017-key-certificate-rotation",
]
errors: list[str] = []
docs: dict[pathlib.Path, object] = {}
refs = examples = negative_cases = task_count = 0


def need(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def document(path: pathlib.Path):
    path = path.resolve()
    if path not in docs:
        docs[path] = json.loads(read(path)) if path.suffix == ".json" else yaml.safe_load(read(path))
    return docs[path]


def resolve(ref: str, base: pathlib.Path):
    file_part, _, fragment = ref.partition("#")
    if urllib.parse.urlparse(file_part).scheme:
        raise ValueError(f"External reference not supported by structural validator: {ref}")
    target = (base.parent / file_part).resolve() if file_part else base.resolve()
    value = document(target)
    if fragment:
        if not fragment.startswith("/"):
            raise ValueError(f"Unsupported reference fragment: {ref}")
        for token in fragment.lstrip("/").split("/"):
            value = value[token.replace("~1", "/").replace("~0", "~")]
    return value, target


def fits(value, schema, base: pathlib.Path, depth=0) -> bool:
    if depth > 100:
        return False
    if schema is True:
        return True
    if schema is False:
        return False
    if "$ref" in schema:
        referenced, target = resolve(schema["$ref"], base)
        if not fits(value, referenced, target, depth + 1):
            return False
        schema = {k: v for k, v in schema.items() if k != "$ref"}
    types = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "null": value is None,
    }
    if "type" in schema:
        allowed = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(types.get(t, False) for t in allowed):
            return False
    if "const" in schema and value != schema["const"]:
        return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    if isinstance(value, dict):
        if any(k not in value for k in schema.get("required", [])):
            return False
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and any(k not in properties for k in value):
            return False
        for key, item in value.items():
            child = properties.get(key, schema.get("additionalProperties", True))
            if not fits(item, child, base, depth + 1):
                return False
    if isinstance(value, list):
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", sys.maxsize):
            return False
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            return False
        if "items" in schema and any(not fits(x, schema["items"], base, depth + 1) for x in value):
            return False
    if isinstance(value, str):
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", sys.maxsize):
            return False
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            return False
        if schema.get("format") == "date-time":
            try:
                parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    return False
            except ValueError:
                return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", -float("inf")) or value > schema.get("maximum", float("inf")):
            return False
    return True


def walk(node, base: pathlib.Path):
    global refs, examples
    if isinstance(node, dict):
        if "$ref" in node:
            refs += 1
            try:
                resolve(node["$ref"], base)
            except (KeyError, ValueError, FileNotFoundError) as exc:
                errors.append(f"{base.name}: invalid reference {node['$ref']}: {exc}")
        if "schema" in node:
            sample_values = []
            if "example" in node:
                sample_values.append(node["example"])
            if isinstance(node.get("examples"), dict):
                sample_values.extend(v["value"] for v in node["examples"].values() if "value" in v)
            for sample in sample_values:
                examples += 1
                need(fits(sample, node["schema"], base), f"{base.name}: example violates structural schema")
        for child in node.values():
            walk(child, base)
    elif isinstance(node, list):
        for child in node:
            walk(child, base)


for markdown in [ROOT / "README.md", *ROOT.glob(".specify/**/*.md"), *ROOT.glob("specs/**/*.md")]:
    content = read(markdown)
    for target in re.findall(r"\]\(([^)]+)\)", content):
        target = target.strip("<>")
        if target.startswith(("https://", "http://", "#", "mailto:", "codex://")):
            continue
        local = target.split("#", 1)[0]
        need((markdown.parent / urllib.parse.unquote(local)).exists(), f"Broken link in {markdown.relative_to(ROOT)}: {target}")
    need("[NEEDS CLARIFICATION" not in content, f"Unresolved product clarification in {markdown.relative_to(ROOT)}")

roadmap = read(PARENT / "roadmap.md")
for number, name in enumerate(FEATURES, 1):
    folder = ROOT / "specs" / name
    for filename in ("spec.md", "plan.md", "tasks.md"):
        need((folder / filename).exists(), f"F{number:02d} missing {filename}")
    if not all((folder / f).exists() for f in ("spec.md", "plan.md", "tasks.md")):
        continue
    spec = read(folder / "spec.md")
    need("(spec.md)" in read(folder / "plan.md"), f"F{number:02d} plan missing own spec link")
    need("roadmap.md" in spec and f"F{number:02d}" in spec, f"F{number:02d} missing parent roadmap reference")
    need(f"../{name}/spec.md" in roadmap and f"../{name}/plan.md" in roadmap, f"F{number:02d} absent from roadmap")
    tasks = read(folder / "tasks.md")
    ids = re.findall(r"^- \[ \] (T\d{3})\b", tasks, re.M)
    need(ids == [f"T{x:03d}" for x in range(1, len(ids) + 1)], f"F{number:02d} tasks not contiguous/unique")
    need(1 <= len(ids) <= 8, f"F{number:02d} has {len(ids)} tasks; expected1–8")
    task_count += len(ids)
    for match in re.finditer(r"^- \[ \] (T\d{3})\b([\s\S]*?)(?=^- \[ \]|\Z)", tasks, re.M):
        task, body = match.groups()
        need("Accept:" in body or "Acceptance:" in body, f"F{number:02d}/{task} lacks acceptance")
        for dependency in re.findall(r"Depends:\s*([^\n]+)", body):
            for dep in re.findall(r"\bT\d{3}\b", dependency.split("Accept:")[0]):
                need(dep in ids and dep < task, f"F{number:02d}/{task} invalid dependency {dep}")
        for command in re.findall(r"Run:\s*([^\n]+)", body):
            need(not command.rstrip("`").endswith("."), f"F{number:02d}/{task} command ends with an invalid copied period")

contracts = PARENT / "contracts"
for path in [*contracts.glob("*.json"), contracts / "openapi.yaml"]:
    data = document(path)
    walk(data, path)
    if path.suffix == ".json":
        need(data.get("$schema") == "https://json-schema.org/draft/2020-12/schema", f"{path.name}: wrong schema dialect")
        for sample in data.get("examples", []):
            examples += 1
            need(fits(sample, data, path), f"{path.name}: root example fails")
openapi = document(contracts / "openapi.yaml")
need(openapi["openapi"] == "3.1.0", "OpenAPI version mismatch")
need(len(openapi["paths"]) == 6, "Expected two business and four management paths")
routing = document(contracts / "routing.example.yaml")
need(fits(routing, document(contracts / "routing.schema.json"), contracts / "routing.schema.json"), "Routing example violates schema")
tenants = {x["tenant_id"]: x for x in routing["tenants"]}
need(len({x["namespace"] for x in tenants.values()}) == len(tenants), "Tenant namespaces not isolated")
for route in routing["routes"]:
    need(route["namespace"] == tenants[route["tenant_id"]]["namespace"], "Route/tenant namespace differs")
    need(any(b["tenant_id"] == route["tenant_id"] and b["input_topic"] == route["input_topic"] for b in routing["consumer_bindings"]), "Missing trusted topic binding")
    need(any(w["namespace"] == route["namespace"] and w["task_queue"] == route["task_queue"] and route["workflow_type"] in w["workflow_types"] for w in routing["worker_assignments"]), "Missing Worker assignment")

event_path = contracts / "event-envelope.schema.json"
event_schema = document(event_path)
sample = event_schema["examples"][0]
for mutation in ("schema_version", "message_id", "tenant_id", "workflow_type", "payload", "extra"):
    bad = copy.deepcopy(sample)
    if mutation == "extra":
        bad["unapproved"] = "field"
    elif mutation == "payload":
        bad[mutation] = []
    else:
        bad[mutation] = {"schema_version": "2", "message_id": "not-a-uuid", "tenant_id": "BAD TENANT", "workflow_type": "Unregistered"}[mutation]
    negative_cases += 1
    need(not fits(bad, event_schema, event_path), f"Invalid event accepted: {mutation}")

declared = set(re.findall(r"\*\*(FR-[A-Z]+-\d+)\*\*", read(PARENT / "spec.md")))
need(bool(declared), "No parent FR requirements found")
v_ids = set(re.findall(r"\*\*(V-\d{3})\*\*", read(PARENT / "verification.md")))
need(v_ids == {f"V-{n:03d}" for n in range(1, 31)}, "Verification catalog must contain30 unique gates")
if errors:
    print("SPEC PACKAGE VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)
print(f"PASS: {len(FEATURES)} feature packages, {task_count} local tasks, {len(declared)} parent requirements, {len(v_ids)} verification gates")
print(f"PASS: Markdown links, task dependencies, {refs} contract refs, {examples} examples, {negative_cases} negative cases and routing invariants")
print("Scope: structural/example checks only; full standards validation and application runtime/cluster tests are not performed.")
