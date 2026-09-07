# Optional observation profiles (0.3.0 candidate)

This is the candidate delivery of MEDUI-DEC-007. Profiles belong to this
implementation-neutral contract; platform adapters, event loops, rendering algorithms and device
actions remain in consumer repositories. Compiler capabilities and diagnostics retain their meanings.
No existing consumer is asserted to support these profiles.

A profile claim names an ID and integer version from `profiles/registry.json`. Version 1 of an ID
is immutable once released; changed outcomes require a new version and a contract minor. Claims
are optional, independent of compiler phases, and require every case for the claimed profile.
`profiles` is an optional, nonempty array in the consumer manifest; duplicate claims are rejected.
An absent array claims nothing. An unknown ID/version or unknown manifest key is rejected.
Interaction, binding and presentation profile delivery remains separate under MEDUI-DEC-008.

Each `conformance/profiles/*.json` file is a portable observation vector. `inputs` describes
public observations or a logical scenario, and `expected` is the required observable result.
These are not native artifacts or private object layouts. Each vector lists the numbered rules
it exercises. Repository validation checks structure and rule coverage; consumer harnesses run
the vectors. Passing repository validation alone is not profile conformance.

### Vector protocol

`inputs.operation` selects `rendered-check` or `aggregate-evidence`. Each operates on the supplied
public data and returns the members asserted in `expected`; omitted expected members impose no
assertion. Fixture SHA strings identify synthetic inputs; they do not attest to real consumer builds.

## MEDUI-PROFILE-RENDERED, version 1

All rectangles are integer authored-pixel `[x,y,width,height]` values, nonnegative in extent,
with half-open edges. Captures are top-to-bottom tightly packed straight-alpha RGBA8. Geometry
observations name an independently measured ink rectangle (`null` for empty ink), rather than
prescribing a segmentation algorithm. Insets/expansions are explicit inputs; no hidden tolerance
or default background exists. Product captures require an identified presentation configuration.

- **R01 — extent-equality/1.** Empty ink fails. Otherwise measured ink must equal the golden
  rectangle in all four coordinates; an inset or an overflow fails.
- **R02 — ink-containment/1.** Empty ink passes. Otherwise all ink must be inside the golden
  rectangle expanded by the supplied nonnegative integer margin on each side. Touching its
  outer edge is allowed; extending beyond it fails.
- **R03 — tint-composition/1.** Samples are opaque RGB8 observations over an explicit RGB8
  background after either one or two identical tint-over-background composites. A single real
  coverage `a` in `[0,1]` is shared by all three channels of a sample. The ideal channel after
  `n` composites is `t + (b-t)*(1-a)^n`. Each observed channel may differ by at most `n/2` UNORM
  units (inclusive), accounting for round-to-nearest error at each composite. Coverage can
  differ between samples. Every sample must satisfy the common-coverage constraint and at least
  one sample must exactly equal the tint. Empty samples, absent tint, or an impossible blend
  fail. This is a conservative bounded envelope, not permission for arbitrary per-channel
  fuzzy matching. Chrome must be resolved into the supplied background before sampling; a
  nonuniform background is represented by a separate background for each sample.
- **R04 — rgba8-sha256/1.** Hash the bytes in the golden rectangle in row-major RGBA order,
  with no padding, header or colour conversion. Comparison is exact lowercase SHA-256. Missing
  baseline yields `missing-baseline`, never pass; a mismatched digest fails. Empty rectangles
  hash the empty byte string. The capture must contain the entire rectangle; otherwise fail.
  Profile/backend/configuration identity must match before comparison.

These check names are immutable only in combination with this profile ID/version. Legacy
`Bounds` and `ColorHash` names are not aliases. A consumer maps legacy obligations explicitly to
one or more identified checks, runs old and candidate obligations together, retains both reports,
and rebakes changed baselines explicitly. No check may be weakened by silently relabelling it.

## MEDUI-PROFILE-EVIDENCE, version 1

- **E01 — identity.** Every obligation and report row carries the full identity defined in
  `schemas/evidence.schema.json`: contract SHA; producer name/version/source SHA; profile ID/version;
  screen artifact and asset SHA-256 digests; screen/node; locale (explicit string or `null` for
  locale-free); scenario SHA-256 or `static`; capture/frame; check ID/version; backend and rendering
  configuration digest. Backend/configuration are explicit strings even for synthetic observations
  (`synthetic` and the digest of the synthetic configuration). Identity comparison is fieldwise,
  independent of object-key order. Different locales, scenarios, frames or configurations never
  satisfy each other's obligations.
- **E02 — completeness.** The required obligation array is derived from the selected screen,
  annotations, locales, scenarios and declared check mapping before report production; it is not
  reconstructed from report rows. Every obligation must have exactly one matching row. Missing,
  duplicate or unexpected rows fail the aggregate, including duplicate obligations. An empty
  obligation set with no rows yields `not-run`, never pass. Rows against an empty obligation set
  are unexpected and fail.
- **E03 — outcomes.** Row outcomes are exactly `pass`, `fail`, `unsupported`, `not-run`, and
  `missing-baseline`. An aggregate passes only when the set is nonempty, exact, and every row
  passes. Otherwise it fails, except for the empty-set/no-rows result above. Each original row outcome
  remains visible; aggregation never converts unsupported or missing evidence into success.

## Adoption

0.2.0 compiler outcomes remain the baseline. New schemas and optional profiles are a 0.3.0
candidate. An implementation first passes all its claimed compiler cases and each new profile's
vectors at an exact candidate SHA, publishes that evidence, then updates its pin/claims. Neither
the 0.2.0 nor 0.3.0 final tag is justified by repository validation. Legacy reports and pinned
corpora remain reproducible. These observations establish neither certification nor clinical
requirements.
