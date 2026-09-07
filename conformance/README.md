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
