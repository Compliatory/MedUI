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


def fail(message: str) -> None:
    print(f"MedUI validation: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "0.1.0":
        fail("VERSION must be 0.1.0 for the initial contract")

    decision_ids = []
    for path in sorted((ROOT / "decisions").glob("MEDUI-DEC-*.md")):
        decision_id = path.name.split("-", 3)[:3]
        decision_ids.append("-".join(decision_id))
    if decision_ids != [f"MEDUI-DEC-{number:03d}" for number in range(1, 6)]:
        fail(f"decision identifiers are not the expected contiguous set: {decision_ids}")

    known_codes = set(re.findall(r"`(MEDUI-E[0-9]{3})`", (ROOT / "spec/diagnostics.md").read_text()))
    if len(known_codes) != 22:
        fail(f"expected 22 registered diagnostics, found {len(known_codes)}")

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

    aliases = json.loads((ROOT / "compat/mdx-e-aliases-v0.1.json").read_text())["aliases"]
    if set(aliases.values()) != known_codes:
        fail("MDX-E alias values must cover the canonical diagnostic registry exactly")
    for old, new in aliases.items():
        if old.replace("MDX-", "MEDUI-") != new:
            fail(f"alias changes numeric identity: {old} -> {new}")

    seen = set()
    cases = sorted((ROOT / "conformance").glob("**/case.json"))
    if not cases:
        fail("no conformance cases found")
    for path in cases:
        case = json.loads(path.read_text(encoding="utf-8"))
        required = {"id", "phase", "source", "expected"}
        if not required <= case.keys() or set(case) - (required | {"inputs"}):
            fail(f"{path.relative_to(ROOT)} has invalid top-level members")
        if not CASE_ID.fullmatch(case["id"]) or case["id"] in seen:
            fail(f"invalid or duplicate case id {case['id']}")
        seen.add(case["id"])
        if case["phase"] not in PHASES or path.parent.parent.name != case["phase"]:
            fail(f"{case['id']} has an invalid or mismatched phase")
        source = path.parent / case["source"]
        if not source.is_file() or source.suffix != ".medui":
            fail(f"{case['id']} source does not resolve")
        expected = case["expected"]
        if set(expected) - {"valid", "diagnostics", "observations"}:
            fail(f"{case['id']} has invalid expected members")
        if not isinstance(expected.get("valid"), bool) or not isinstance(expected.get("diagnostics"), list):
            fail(f"{case['id']} has invalid expected shape")
        for diagnostic in expected["diagnostics"]:
            if set(diagnostic) != {"code", "line", "column"} or not CODE.fullmatch(diagnostic["code"]):
                fail(f"{case['id']} has an invalid diagnostic expectation")
            if diagnostic["code"] not in known_codes or diagnostic["line"] < 0 or diagnostic["column"] < 0:
                fail(f"{case['id']} references an invalid diagnostic")

    print(f"MedUI validation: OK ({len(cases)} cases, {len(known_codes)} diagnostics)")


if __name__ == "__main__":
    main()
