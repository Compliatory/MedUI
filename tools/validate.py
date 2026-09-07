#!/usr/bin/env python3
"""Dependency-free structural validation for the MedUI contract repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from schema_check import check_schema, validate

ROOT = Path(__file__).resolve().parents[1]
PHASES = {"syntax", "semantics", "layout", "safety", "support"}
CAPABILITIES = ["syntax", "semantics", "layout", "safety"]
PRECISIONS = ["full", "line-only", "none"]
CASE_ID = re.compile(r"MEDUI-CASE-[A-Z0-9-]+\Z")
CODE = re.compile(r"MEDUI-E[0-9]{3}\Z")
# VERSION is MAJOR.MINOR.PATCH only. Release-candidate and "-candidate" labels live in git tags and
# the consumer manifest's `version` field, never in this file, so a pre-release suffix here is an
# error rather than an accepted shape.
VERSION_SHAPE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\Z")
REGISTRY_ROW = re.compile(r"\|\s*`(MEDUI-E[0-9]{3})`\s*\|\s*([a-z]+)\s*\|")

# Diagnostics registered as of the 0.1 baseline. MEDUI-DEC-005 fixes a code's meaning and forbids
# reuse; this set is the concrete "nothing was dropped" tripwire. New codes are added to
# spec/diagnostics.md and need no entry here.
BASELINE_CODES = {
    "MEDUI-E000", "MEDUI-E001", "MEDUI-E002", "MEDUI-E003", "MEDUI-E004",
    "MEDUI-E010", "MEDUI-E011", "MEDUI-E012", "MEDUI-E013", "MEDUI-E014",
    "MEDUI-E015", "MEDUI-E016", "MEDUI-E017",
    "MEDUI-E030", "MEDUI-E031", "MEDUI-E032", "MEDUI-E033", "MEDUI-E034",
    "MEDUI-E050", "MEDUI-E051", "MEDUI-E052", "MEDUI-E053",
    "MEDUI-E070", "MEDUI-E071",
}


def fail(message: str) -> None:
    print(f"MedUI validation: {message}", file=sys.stderr)
    raise SystemExit(1)


def note(message: str) -> None:
    print(f"MedUI validation: note: {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {error}")


def is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not VERSION_SHAPE.fullmatch(version):
        fail(f"VERSION must be MAJOR.MINOR.PATCH, got {version!r}")

    # Decision identifiers are contiguous from 001. The count is free to grow; a gap or a
    # renumber is not (MEDUI-DEC identities are permanent).
    decision_numbers = sorted(
        int(path.name.split("-")[2]) for path in (ROOT / "decisions").glob("MEDUI-DEC-*.md")
    )
    if decision_numbers != list(range(1, len(decision_numbers) + 1)):
        fail(f"decision identifiers are not contiguous from 001: {decision_numbers}")

    # Every schema's $id names the contract minor it belongs to (governance/versioning.md).
    minor = ".".join(version.split(".")[:2])
    schemas = {}
    for schema_path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = load_json(schema_path)
        check_schema(schema)
        schemas[schema_path.name.removesuffix(".schema.json")] = schema
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str):
            fail(f"{schema_path.name} has no string $id")
        if not schema_id.endswith(f"/schemas/{minor}/{schema_path.name}"):
            fail(f"{schema_path.name} $id does not carry the {minor} contract minor: {schema_id}")

    registry_text = (ROOT / "spec/diagnostics.md").read_text(encoding="utf-8")
    code_phase = {code: phase for code, phase in REGISTRY_ROW.findall(registry_text)}
    code_list = re.findall(r"^\|\s*`(MEDUI-E[0-9]{3})`\s*\|", registry_text, flags=re.MULTILINE)
    known_codes = set(code_list)
    if len(code_list) != len(known_codes):
        fail("spec/diagnostics.md registers a code more than once")
    if not BASELINE_CODES <= known_codes:
        fail(f"baseline diagnostics dropped from the registry: {sorted(BASELINE_CODES - known_codes)}")
    for phase in code_phase.values():
        if phase not in PHASES:
            fail(f"spec/diagnostics.md registers a code under an unknown phase: {phase}")

    # The consumer-manifest schema and governance/versioning.md state the same constraints; a
    # harness reads one and a maintainer reads the other, so they are checked against each other
    # rather than trusted to stay in step.
    manifest_schema = load_json(ROOT / "schemas/consumer-manifest.schema.json")
    if set(manifest_schema["required"]) != {"repository", "commit", "capabilities", "positions"}:
        fail(f"consumer manifest required keys changed: {manifest_schema['required']}")
    if manifest_schema["additionalProperties"] is not False:
        fail("the consumer manifest must reject unknown keys")
    properties = manifest_schema["properties"]
    if properties["positions"]["enum"] != PRECISIONS:
        fail(f"declared precisions changed: {properties['positions']['enum']}")
    if properties["capabilities"]["items"]["enum"] != CAPABILITIES:
        fail(f"capabilities changed: {properties['capabilities']['items']['enum']}")

    # The case schema is the source of truth for member names; the checks below read it rather
    # than restating it, so a schema edit does not silently diverge from the validator.
    case_schema = load_json(ROOT / "schemas/case.schema.json")
    case_required = set(case_schema["required"])
    case_top_level = set(case_schema["properties"])
    if case_schema["additionalProperties"] is not False:
        fail("the case schema must reject unknown keys")
    inputs_keys = set(case_schema["properties"]["inputs"]["properties"])
    expected_keys = set(case_schema["properties"]["expected"]["properties"])
    expected_required = set(case_schema["properties"]["expected"]["required"])

    aliases = load_json(ROOT / "compat/mdx-e-aliases-v0.1.json")["aliases"]
    if not set(aliases.values()) <= known_codes:
        fail("an MDX-E alias points outside the canonical diagnostic registry")
    for old, new in aliases.items():
        if old.replace("MDX-", "MEDUI-") != new:
            fail(f"alias changes numeric identity: {old} -> {new}")

    seen = set()
    asserted_codes = set()
    cases = sorted((ROOT / "conformance").glob("**/case.json"))
    if not cases:
        fail("no conformance cases found")
    for path in cases:
        rel = path.relative_to(ROOT)
        case = load_json(path)
        if not isinstance(case, dict):
            fail(f"{rel} is not a JSON object")
        if not case_required <= case.keys() or set(case) - case_top_level:
            fail(f"{rel} has invalid top-level members")
        if not isinstance(case["id"], str) or not CASE_ID.fullmatch(case["id"]) or case["id"] in seen:
            fail(f"invalid or duplicate case id {case['id']!r} in {rel}")
        seen.add(case["id"])
        if case["phase"] not in PHASES or path.parent.parent.name != case["phase"]:
            fail(f"{case['id']} has an invalid or mismatched phase")
        if not isinstance(case["source"], str) or "/" in case["source"]:
            fail(f"{case['id']} has an invalid source member")
        source = path.parent / case["source"]
        if not source.is_file() or source.suffix != ".medui":
            fail(f"{case['id']} source does not resolve")
        inputs = case.get("inputs", {})
        if not isinstance(inputs, dict) or set(inputs) - inputs_keys:
            fail(f"{case['id']} has invalid semantic inputs")
        for collection in ("themeTokens", "imageIds", "templates"):
            if collection not in inputs_keys:
                continue
            values = inputs.get(collection, [])
            if (not isinstance(values, list)
                    or any(not isinstance(value, str) or not value for value in values)
                    or len(values) != len(set(values))):
                fail(f"{case['id']} has invalid or duplicate {collection}")
        text_packages = inputs.get("textPackages", [])
        if not isinstance(text_packages, list):
            fail(f"{case['id']} has invalid text packages")
        locales = set()
        for package in text_packages:
            if not isinstance(package, dict) or set(package) != {"locale", "keys"}:
                fail(f"{case['id']} has an invalid text package")
            locale = package["locale"]
            keys = package["keys"]
            if (not isinstance(locale, str) or not locale or locale in locales
                    or not isinstance(keys, list)
                    or any(not isinstance(key, str) or not key for key in keys)
                    or len(keys) != len(set(keys))):
                fail(f"{case['id']} has an invalid or duplicate locale/key")
            locales.add(locale)
        expected = case["expected"]
        if not isinstance(expected, dict):
            fail(f"{case['id']} expected is not a JSON object")
        if not expected_required <= expected.keys() or set(expected) - expected_keys:
            fail(f"{case['id']} has invalid expected members")
        if not isinstance(expected.get("valid"), bool) or not isinstance(expected.get("diagnostics"), list):
            fail(f"{case['id']} has invalid expected shape")
        for diagnostic in expected["diagnostics"]:
            if (not isinstance(diagnostic, dict)
                    or set(diagnostic) != {"code", "line", "column"}
                    or not isinstance(diagnostic["code"], str)
                    or not CODE.fullmatch(diagnostic["code"])):
                fail(f"{case['id']} has an invalid diagnostic expectation")
            if not is_int(diagnostic["line"]) or not is_int(diagnostic["column"]):
                fail(f"{case['id']} has a non-integer diagnostic position")
            if diagnostic["code"] not in known_codes or diagnostic["line"] < 0 or diagnostic["column"] < 0:
                fail(f"{case['id']} references an invalid diagnostic")
            registered_phase = code_phase.get(diagnostic["code"])
            if registered_phase and registered_phase != case["phase"]:
                fail(
                    f"{case['id']} is a {case['phase']} case but {diagnostic['code']} "
                    f"is registered under {registered_phase}"
                )
            asserted_codes.add(diagnostic["code"])

    uncovered = sorted(known_codes - asserted_codes)
    if uncovered:
        note(f"{len(uncovered)} registered codes have no conformance case: {', '.join(uncovered)}")

    # Optional profiles carry observations, never .medui parsers or runtime implementations.
    registry = load_json(ROOT / "profiles/registry.json")
    declared = {}
    profile_text = (ROOT / "spec/profiles.md").read_text(encoding="utf-8")
    documented_rules = set(re.findall(r"\*\*([REIBP][0-9]{2}) —", profile_text))
    for profile in registry["profiles"]:
        key = (profile["id"], profile["version"])
        if key in declared or not profile["rules"] or len(set(profile["rules"])) != len(profile["rules"]):
            fail(f"invalid or duplicate profile registration: {key}")
        declared[key] = set(profile["rules"])
    if set().union(*declared.values()) != documented_rules:
        fail("profile registry rules differ from spec/profiles.md")
    evidence_identity = schemas["evidence"]["$defs"]["identity"]["properties"]
    evidence_profile = evidence_identity["profile"]["properties"]
    evidence_key = (evidence_profile["id"]["const"], evidence_profile["version"]["const"])
    evidence_check = evidence_identity["check"]["properties"]
    documented_checks = set(re.findall(r"\*\*R[0-9]{2} — ([a-z0-9-]+)/([0-9]+)\.", profile_text))
    schema_checks = {(check, str(evidence_check["version"]["const"]))
                     for check in evidence_check["id"]["enum"]}
    if evidence_key not in declared or schema_checks != documented_checks:
        fail("evidence profile/check identities differ from the registry or specification")
    claim_schema = properties["profiles"]["items"]
    schema_claims = {
        (identifier, claim_schema["properties"]["version"]["const"])
        for identifier in claim_schema["properties"]["id"]["enum"]
    }
    if schema_claims != declared.keys():
        fail("manifest profile claims differ from the profile registry")
    coverage = {key: set() for key in declared}
    profile_cases = sorted((ROOT / "conformance/profiles").glob("*.json"))
    contract_cases = sorted((ROOT / "conformance/contracts").glob("*.json"))
    for path in profile_cases + contract_cases:
        case = load_json(path)
        schema_name = "profile-case" if path.parent.name == "profiles" else "contract-case"
        problems = validate(case, schemas[schema_name])
        if problems:
            fail(f"{path.relative_to(ROOT)}: {'; '.join(problems)}")
        if case["id"] in seen:
            fail(f"duplicate case ID: {case['id']}")
        seen.add(case["id"])
        if schema_name == "profile-case":
            key = (case["profile"]["id"], case["profile"]["version"])
            if key not in declared or not set(case["rules"]) <= declared[key]:
                fail(f"{case['id']} references unknown profile rules")
            coverage[key].update(case["rules"])
            inputs = case["inputs"]
            if inputs["operation"] == "rendered-check":
                for field in ("captureIdentity", "baselineIdentity"):
                    if field in inputs and inputs[field].get("check") != {
                        "id": inputs.get("check"), "version": key[1]
                    }:
                        fail(f"{case['id']} {field}: identity check differs from the rendered operation")
        else:
            problems = validate(case["document"], schemas[case["schema"]])
            if (not problems) != case["valid"]:
                fail(f"{case['id']} schema outcome differs: {problems}")
    for key, rules in declared.items():
        if rules - coverage[key]:
            fail(f"{key} has uncovered rules: {sorted(rules - coverage[key])}")
    if not contract_cases:
        fail("no contract schema cases found")

    print(f"MedUI validation: OK ({len(cases)} compiler cases, {len(profile_cases)} profile cases, "
          f"{len(contract_cases)} schema cases, {len(known_codes)} diagnostics)")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        fail(str(error))
