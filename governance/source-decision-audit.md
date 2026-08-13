# Source decision audit

This table is the initial audit prompted by
[TrustSC issue #48](https://github.com/ambroise-leclerc/TrustSC/issues/48). Existing ADR numbers
remain permanent local identities; shared records provide an unambiguous cross-repository name.

| Subject | Shared record | TrustSC source | MduX source | Disposition |
|---|---|---|---|---|
| Build-time-only compilation | MEDUI-DEC-001 | ADR-008 | ADR-011 | Shared |
| Closed language and bounded layout | MEDUI-DEC-002 | ADR-008, ADR-014, ADR-015 | ADR-011 | Shared composite baseline |
| Compiled-screen meaning | MEDUI-DEC-003 | ADR-009 | ADR-012 | Shared semantics; emission remains local |
| Safety annotations and goldens | MEDUI-DEC-004 | ADR-011, ADR-014, ADR-016 | ADR-011, ADR-012 | Shared |
| Diagnostics and conformance | MEDUI-DEC-005 | ADR-022 and current compiler | MduX issue #191 and ADR-011 | Shared composite baseline |
| Trust zones | — | ADR-005 | ADR-004 | Local implementation decision |
| Rust/C++ generated source | — | ADR-009 | ADR-012 | Deliberate implementation difference |
| Evidence directory/file layout | — | ADR-007/009/016 | ADR-007/012 | Deliberate implementation difference |
| MedUI Studio | — | ADR-022 | No equivalent | TrustSC-local tooling |
| Zero-SOUP ML | — | ADR-017 | ADR-008 | Outside MedUI |

The composite baseline uses TrustSC's implemented component semantics, locale/text budgets,
layout, and golden predicate together with MduX's tokenization, UTF-8 byte columns, comments,
multi-error recovery, and stable diagnostic registry.
