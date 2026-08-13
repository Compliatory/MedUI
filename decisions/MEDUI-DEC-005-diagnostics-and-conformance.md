# MEDUI-DEC-005: Diagnostics and conformance

Status: Accepted

MedUI diagnostics use stable `MEDUI-E###` identities, exact 1-based UTF-8 byte positions where
known, a closed severity vocabulary, free-form messages, and optional fix hints. A code's meaning
never changes and retired numbers are never reused.

Conformance cases assert observable acceptance, diagnostics, normalized semantics, layout, or
goldens. Consumers declare capabilities and must not silently skip a claimed phase.
