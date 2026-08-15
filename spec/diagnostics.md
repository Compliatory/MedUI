# Diagnostic contract

The canonical finding envelope is defined by `schemas/diagnostic.schema.json`. Positions are
1-based; `0` means unknown. Columns count UTF-8 bytes. Messages and fix hints may be reworded, but a
code's meaning, severity, and phase are stable.

## Positions in conformance cases

A case always pins a full position — both `line` and `column` — and those pinned values are the
same for every consumer. A case is never rewritten, zeroed, or otherwise adjusted to suit an
implementation. What varies is how much of that pinned position an implementation is required to
reproduce, which it declares as `positions` in its manifest.

The table below constrains the **reported** diagnostic, never the fixture:

| `positions` | Implementation reports | Required reported position |
|---|---|---|
| `full` | line and column | `line` equals the pinned line, and `column` equals the pinned column |
| `line-only` | line only | `line` equals the pinned line, and `column` is `0` |
| `none` | neither | `line` is `0`, and `column` is `0` |

Reporting `0` where a case pins a non-zero value satisfies the case only at the declared
precision. Reporting a position the declaration says will not be reported is a failure, so an
implementation cannot quietly gain precision without amending its manifest — and cannot quietly
lose it either. An implementation reporting a *different* non-zero position from the one pinned
fails at every precision.

| Code | Phase | Meaning |
|---|---|---|
| `MEDUI-E000` | support | recipe unreadable |
| `MEDUI-E001` | support | recipe unparsed |
| `MEDUI-E002` | support | recipe member missing |
| `MEDUI-E003` | support | source unreadable |
| `MEDUI-E004` | syntax | source is not UTF-8 |
| `MEDUI-E010` | syntax | unexpected token |
| `MEDUI-E011` | semantics | unknown component |
| `MEDUI-E012` | semantics | missing required field |
| `MEDUI-E013` | semantics | unknown field |
| `MEDUI-E014` | syntax | duplicate node ID |
| `MEDUI-E015` | syntax | nested row |
| `MEDUI-E016` | syntax | forbidden construct |
| `MEDUI-E017` | semantics | hardcoded product string |
| `MEDUI-E030` | semantics | unknown color token |
| `MEDUI-E031` | semantics | unknown text key |
| `MEDUI-E032` | semantics | text key missing for an approved locale |
| `MEDUI-E033` | semantics | field value has the wrong semantic kind |
| `MEDUI-E050` | layout | text budget exceeded |
| `MEDUI-E051` | layout | layout overflow |
| `MEDUI-E052` | layout | surface exceeded |
| `MEDUI-E053` | semantics | dynamic text escapes its charset |
| `MEDUI-E070` | safety | safety-critical node has no requirement |
| `MEDUI-E071` | safety | unknown CV check |
