# MedUI

MedUI is a deterministic, build-time UI description language for medical-device-oriented user
interfaces. This repository owns the implementation-neutral language contract, shared decisions,
diagnostic identities, authoring guidance, and conformance cases used by the independent
[TrustSC](https://github.com/ambroise-leclerc/TrustSC) and
[MduX](https://github.com/ambroise-leclerc/MduX) implementations.

Parsers, compilers, generated-language bindings, renderers, runtimes, and interactive tooling stay
in their implementation repositories. Passing this repository's tests is engineering evidence; it
does not establish certification, regulatory compliance, or suitability for a particular device.

## Repository map

- `decisions/` — stable shared decisions (`MEDUI-DEC-*`).
- `spec/` — grammar, semantic model, and diagnostic contract.
- `schemas/` — machine-readable conformance and diagnostic schemas.
- `conformance/` — portable cases grouped by compiler phase.
- `authoring/` — implementation-neutral author guidance.
- `governance/` — versioning and the source-decision audit.
- `compat/` — historical identifier migration maps.
- `tools/validate.py` — dependency-free repository validator.

## Validate

```bash
python3 tools/validate.py
```

Consumers pin an exact commit in `medui-conformance.toml`; tags describe releases, while the SHA
is the reproducible input.

**Licence:** [EUPL-1.2](LICENSE.md), or separate commercial terms. See [LICENSING.md](LICENSING.md).
