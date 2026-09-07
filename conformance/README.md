# Conformance cases

Portable cases grouped by the compiler phase they exercise. Each case is a directory holding a
`case.json` (see `schemas/case.schema.json`) and one `.medui` fixture. `tools/validate.py` checks
their structure; an implementation runs them and compares observable behaviour.

A rejection case pins a full position — `line` and `column`, 1-based, columns in UTF-8 bytes. The
pinned position points at **the token that carries the violation**, and every consumer reproduces
it as far as its declared `positions` precision goes (`spec/diagnostics.md`).

## Registered-code coverage

Every registered `MEDUI-E###` should have at least one case once it is mechanically expressible.
Codes still without one, and why:

| Code | Meaning | Blocked on |
|---|---|---|
| `MEDUI-E000`–`MEDUI-E003` | recipe / source I/O failures | a fixture convention for a broken or missing recipe file alongside the `.medui` source |
| `MEDUI-E016` | forbidden construct | a grammar-level statement of what a "forbidden construct" is versus an unexpected token (`MEDUI-E010`) |
| `MEDUI-E050` | text budget exceeded | a font / text-measurement model; the contract has none yet |
| `MEDUI-E053` | dynamic text escapes its charset | a charset model and charset-package `inputs`, the same gap that leaves `charset` resolution uncoded |

Adding any of these is a contract change (a case defines an outcome), not a drop-in fixture.

## Optional profile and schema cases

`profiles/*.json` uses `schemas/profile-case.schema.json` and defines public observation vectors
for the optional 0.3.0 candidate profiles in [the profile contract](../spec/profiles.md).
Each rule in `profiles/registry.json` must have at least one vector; the validator rejects missing
coverage, unknown claims/rules and duplicate case IDs. Inputs use the operation and defaults
specified in that contract. Expected members are assertions; unlisted output members are not
compared. A claiming consumer must execute every vector for that profile, including rejection
vectors. This repository provides no runtime, renderer or native artifact oracle.

`contracts/*.json` supplies valid and invalid parsed manifest/evidence documents. The repository
validator executes these schema expectations using the dependency-free schema subset checker.
Schema acceptance and profile execution are distinct: a well-formed evidence report can still
fail its completeness or identity obligations.
