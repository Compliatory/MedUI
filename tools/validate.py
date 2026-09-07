#!/usr/bin/env python3
"""Dependency-free structural validation for the MedUI contract repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASES = {"syntax", "semantics", "layout", "safety", "support"}
CAPABILITIES = ["syntax", "semantics", "layout", "safety"]
PRECISIONS = ["full", "line-only", "none"]
CASE_ID = re.compile(r"MEDUI-CASE-[A-Z0-9-]+\Z")
CODE = re.compile(r"MEDUI-E[0-9]{3}\Z")
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\Z")
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


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        fail(f"VERSION is not semantic: {version!r}")

    # Decision identifiers are contiguous from 001. The count is free to grow; a gap or a
    # renumber is not (MEDUI-DEC identities are permanent).
    decision_numbers = sorted(
        int(path.name.split("-")[2]) for path in (ROOT / "decisions").glob("MEDUI-DEC-*.md")
    )
    if decision_numbers != list(range(1, len(decision_numbers) + 1)):
        fail(f"decision identifiers are not contiguous from 001: {decision_numbers}")

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
    manifest_schema = json.loads((ROOT / "schemas/consumer-manifest.schema.json").read_text())
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
    case_schema = json.loads((ROOT / "schemas/case.schema.json").read_text())
    case_required = set(case_schema["required"])
    case_top_level = set(case_schema["properties"])
    if case_schema["additionalProperties"] is not False:
        fail("the case schema must reject unknown keys")
    inputs_keys = set(case_schema["properties"]["inputs"]["properties"])
    expected_keys = set(case_schema["properties"]["expected"]["properties"])
    expected_required = set(case_schema["properties"]["expected"]["required"])

    aliases = json.loads((ROOT / "compat/mdx-e-aliases-v0.1.json").read_text())["aliases"]
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
        case = json.loads(path.read_text(encoding="utf-8"))
        if not case_required <= case.keys() or set(case) - case_top_level:
            fail(f"{path.relative_to(ROOT)} has invalid top-level members")
        if not CASE_ID.fullmatch(case["id"]) or case["id"] in seen:
            fail(f"invalid or duplicate case id {case['id']}")
        seen.add(case["id"])
        if case["phase"] not in PHASES or path.parent.parent.name != case["phase"]:
            fail(f"{case['id']} has an invalid or mismatched phase")
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
        if not expected_required <= expected.keys() or set(expected) - expected_keys:
            fail(f"{case['id']} has invalid expected members")
        if not isinstance(expected.get("valid"), bool) or not isinstance(expected.get("diagnostics"), list):
            fail(f"{case['id']} has invalid expected shape")
        for diagnostic in expected["diagnostics"]:
            if set(diagnostic) != {"code", "line", "column"} or not CODE.fullmatch(diagnostic["code"]):
                fail(f"{case['id']} has an invalid diagnostic expectation")
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

    print(f"MedUI validation: OK ({len(cases)} cases, {len(known_codes)} diagnostics)")


if __name__ == "__main__":
    main()
