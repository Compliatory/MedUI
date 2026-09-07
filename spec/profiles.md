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
Every vector applies to a claimed profile, including empty ink and zero-area hash regions.
Consumers may adapt these synthetic observations to a standalone predicate even when their
integrated compiler or capture path rejects degenerate geometry upstream. Returning `unsupported`
instead of a vector's expected outcome does not satisfy the claim. Implementation-local checks,
including glyph-shape checks, may run alongside the shared checks; they neither replace shared
cases nor change their outcomes.

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
  background after either one or two same-tint composites. A single real effective coverage `a`
  in `[0,1]` is shared by all three channels of a sample: the ideal channel is `b + (t-b)*a`.
  Each observed channel may differ by at most `n` UNORM units (inclusive), one per composite.
  This bounds observed compositing precision, not just ideal round-to-nearest arithmetic. The
  channels' feasible coverage intervals must have a common intersection with `[0,1]`; a channel
  with zero tint/background span must differ from that constant by at most `n`.
  Coverage can differ between samples. Every sample must satisfy this constraint and at least
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

The R03 candidate allowance was amended from `n/2` to `n` after the recorded narrow-span
regression in [MduX's GoldenCheckTests at a3f8b6d](https://github.com/ambroise-leclerc/MduX/blob/a3f8b6daae073472b9a6f6b472ee9818b3faedf8/tests/verify/GoldenCheckTests.cpp).
The shared corpus pins `(215,134,135)` over `(209,214,219)` toward `(219,51,46)`: one composite
fails, two pass, and a foreign green channel still fails. Effective coverage also avoids imposing
equal coverage at each composite. For equal coverage, `1-(1-a)^n` spans the same `[0,1]` interval;
the substantive change is the precision allowance. These are candidate changes, not a
reinterpretation of a released profile.

## MEDUI-PROFILE-EVIDENCE, version 1

- **E01 — identity.** Every obligation and report row carries the full identity defined in
  `schemas/evidence.schema.json`: contract SHA; producer name/version/source SHA; profile ID/version;
  screen artifact SHA-256 and an ordered asset array; screen/node; locale (explicit string or `null` for
  locale-free); scenario SHA-256 or `static`; capture/frame; check ID/version; backend and rendering
  configuration token. `assets` is an array of `{id,digest}` entries: IDs match
  `[a-z0-9][a-z0-9./_-]*`, are unique and strictly ascending in ASCII byte order, and each digest
  is the lowercase SHA-256 of that artifact's bytes. IDs identify the role and logical resource,
  for example `font/main`, `image/ui`, `shader/ui`, `text/fr-fr`. The producer's artifact declaration
  fixes those IDs; an empty array explicitly means no assets. No implicit digest roll-up is used.
  Malformed identities (including duplicate or unsorted asset IDs) fail aggregation.
  Backend/configuration are explicit strings even for synthetic observations. Identity comparison is fieldwise,
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

`configuration` is an opaque producer-scoped token with lowercase SHA-256 shape. Its payload and
encoding belong to the named producer/version/source contract; MedUI defines no cross-producer
configuration object or canonical hash. That producer must bind the token to all relevant rendering
settings and reuse it only for the same configuration. Synthetic vectors use explicit placeholder
tokens; they assert comparison behavior, not configuration hashing. Equal tokens from different
producers never pair because the full producer identity is also compared.

`backend` is likewise an exact, case-sensitive producer-scoped identifier. `synthetic` identifies
this corpus's synthetic backend; product adapters declare and reuse their own exact spelling.
No aliasing or case folding equates `lavapipe`, `llvmpipe`, or `Mesa lavapipe`. A producer changing
its backend naming or driver configuration must preserve old evidence identities during migration.
Cross-consumer conformance compares operation outcomes, not producer-scoped evidence rows.

The evidence envelope is a parsed comparison input. Whitespace, object-key ordering and serialized
report bytes are not conformance outputs; MedUI prescribes no canonical report serialization.
Consumers may retain their own canonical committed reports and emit this envelope as a derived
artifact. The schema's rendered profile/check IDs and versions track the candidate registry and
R01–R04; adding a released version requires updating the schema identity under the minor policy.

## Adoption

0.2.0 compiler outcomes remain the baseline. New schemas and optional profiles are a 0.3.0
candidate. An implementation first passes all its claimed compiler cases and each new profile's
vectors at an exact candidate SHA, publishes that evidence, then updates its pin/claims. Neither
the 0.2.0 nor 0.3.0 final tag is justified by repository validation. Legacy reports and pinned
corpora remain reproducible. These observations establish neither certification nor clinical
requirements.
