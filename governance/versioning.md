# Versioning and compatibility

MedUI uses Semantic Versioning. Before 1.0, a minor release may change accepted syntax, semantics,
or conformance outcomes; a patch release may clarify prose or add cases that do not change an
already-defined outcome. Tags are immutable. Consumers pin the exact 40-character commit SHA.

A contract change is accepted only after every implementation claiming the affected capability
passes the candidate commit. Capabilities are `syntax`, `semantics`, `layout`, and `safety`.

## The consumer manifest

A consumer records what it pins and what it claims in a `medui-conformance.toml` at its repository
root:

```toml
repository = "https://github.com/Compliatory/MedUI"
version = "0.1.0-candidate"
commit = "<40-character SHA>"
capabilities = ["syntax"]
positions = "full"          # or "line-only", or "none"
```

`positions` declares the diagnostic position precision defined by `spec/diagnostics.md`. A phase
claimed at reduced precision is still claimed, and counts for the rule above: a candidate commit
must pass every implementation claiming the affected capability, each at the precision it
declares. Precision is a property of the implementation, not of the phase, so it is declared once
rather than per capability.

Moving TrustSC or MduX into the Compliatory organization is deferred until the 1.0 milestone and
appropriate open-source GitHub Copilot benefits are available. Repository ownership is not part of
the language contract.
