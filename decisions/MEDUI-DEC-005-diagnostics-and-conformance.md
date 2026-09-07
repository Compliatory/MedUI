# MEDUI-DEC-005: Diagnostics and conformance

Status: Accepted

MedUI diagnostics use stable `MEDUI-E###` identities, exact 1-based UTF-8 byte positions where
known, a closed severity vocabulary, free-form messages, and optional fix hints. A code's meaning
never changes and retired numbers are never reused.

Conformance cases assert observable acceptance, diagnostics, normalized semantics, layout, or
goldens. Consumers declare capabilities and must not silently skip a claimed phase.

Position precision is declared, not assumed. A consumer names the precision it reports, and a
claimed phase is checked at that precision: a case's position is matched as far as the declaration
goes, and a diagnostic carrying more position than declared is a failure. The declaration is
checked rather than tolerated, so gaining precision is a manifest change and never a silent one.
A phase claimed at reduced precision is still claimed.

Semantic cases may provide implementation-neutral `inputs`: `themeTokens` is the complete set of
known colour-token names, `imageIds` and `templates` are the complete sets of baked image and
display-template identifiers, and each `textPackages` entry is the complete key view for one
approved locale. An omitted collection is empty. Tokens, identifiers, locale names, and keys are
non-empty and unique; locale order has no semantic meaning. These logical views deliberately do not
prescribe an implementation's package, file, or runtime representation.
