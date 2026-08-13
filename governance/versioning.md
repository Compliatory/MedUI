# Versioning and compatibility

MedUI uses Semantic Versioning. Before 1.0, a minor release may change accepted syntax, semantics,
or conformance outcomes; a patch release may clarify prose or add cases that do not change an
already-defined outcome. Tags are immutable. Consumers pin the exact 40-character commit SHA.

A contract change is accepted only after every implementation claiming the affected capability
passes the candidate commit. Capabilities are `syntax`, `semantics`, `layout`, and `safety`.

Moving TrustSC or MduX into the Compliatory organization is deferred until the 1.0 milestone and
appropriate open-source GitHub Copilot benefits are available. Repository ownership is not part of
the language contract.
