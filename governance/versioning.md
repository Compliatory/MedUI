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
# The MedUI contract repository being pinned - always this one, never the consumer's own.
repository = "https://github.com/Compliatory/MedUI"
version = "0.1.0-candidate"
commit = "<40-character SHA>"
capabilities = ["syntax"]
positions = "full"          # or "line-only", or "none"
```

| Key | Required | Value |
|---|---|---|
| `repository` | yes | the MedUI contract repository this manifest pins. It identifies the contract, not the consumer, and is always this repository. |
| `commit` | yes | the exact 40-character lowercase hexadecimal commit SHA pinned in that repository. |
| `capabilities` | yes | a non-empty array drawn from `syntax`, `semantics`, `layout`, `safety`. |
| `positions` | yes | exactly one of `full`, `line-only`, `none`. |
| `version` | no | a human-readable label for the pinned revision. |

`commit` alone identifies the contract. `version` is informational: it records which release a pin
was taken from and is never consulted, so a `version` that does not match the `VERSION` file at the
pinned commit is not an error — a pre-release label such as `0.1.0-candidate` against a `VERSION`
of `0.1.0` is the ordinary case.

An unknown key is an error rather than something to ignore, so a misspelled `capabilties` fails
instead of silently claiming nothing; TOML already forbids a repeated key in one table. An empty
`capabilities` array is an error too, because a harness reading it would assert nothing while still
reporting success.

`schemas/consumer-manifest.schema.json` states these constraints in machine-readable form. It
describes the manifest's *parsed* structure — the file on disk is TOML — so a harness can validate
against it after parsing rather than reimplementing the rules.

`positions` declares the diagnostic position precision defined by `spec/diagnostics.md`. A phase
claimed at reduced precision is still claimed, and counts for the rule above: a candidate commit
must pass every implementation claiming the affected capability, each at the precision it
declares. Precision is a property of the implementation, not of the phase, so it is declared once
rather than per capability.

Moving TrustSC or MduX into the Compliatory organization is deferred until the 1.0 milestone and
appropriate open-source GitHub Copilot benefits are available. Repository ownership is not part of
the language contract.
