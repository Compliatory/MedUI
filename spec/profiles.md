# Optional observation profiles (0.3.0 candidate)

This is the candidate delivery of MEDUI-DEC-007 and MEDUI-DEC-008. Profiles belong to this
implementation-neutral contract; platform adapters, event loops, rendering algorithms and device
actions remain in consumer repositories. Compiler capabilities and diagnostics retain their meanings.
No existing consumer is asserted to support these profiles.

A profile claim names an ID and integer version from `profiles/registry.json`. Version 1 of an ID
is immutable once released; changed outcomes require a new version and a contract minor. Claims
are optional, independent of compiler phases, and require every case for the claimed profile.
`profiles` is an optional, nonempty array in the consumer manifest; duplicate claims are rejected.
An absent array claims nothing. An unknown ID/version or unknown manifest key is rejected.
Presentation and binding claims do not imply interaction or exact-pixel equivalence.

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

`inputs.operation` selects `rendered-check`, `aggregate-evidence`, `normalize`, `hit`, `events`,
`edit`, `boundary`, `bind`, `present`, or `pixels`. Each operates on the supplied public data and
returns the members asserted in `expected`; omitted expected members impose no assertion.
Malformed scenario inputs return `valid:false` (or the specified operation's failure outcome),
without partial publication. The following fixture defaults are part of vector interpretation:

- `hit` points are already normalized; only `normalize` takes device coordinates. Omitted origins
  are zero and omitted scale ratios are 1/1. Omitted clips equal the surface.
- `events` starts unarmed, unfocused, with an empty queue and a zero dropped counter unless an
  initial value is supplied. Omitted capacity accepts the whole batch and the counter limit is
  255. `events` is one batch; `batches` explicitly separates batches and preserves visible state.
  `remove` and `eligibility` are logical scene changes, not platform event types. An absent
  `repeat` is false. `focus-next` follows `focusOrder`, beginning at its first node if unfocused.
- `edit` starts with the explicit text, scalar caret and selection; selection is a half-open
  `[start,end]` scalar range. A successful edit collapses selection at the resulting caret.
  Left/right with a nonempty selection collapse to its start/end without an additional move;
  backspace/delete delete the selected range. Rejected event indices are zero-based.
- `bind` describes one dynamic node. Unless `entries` is explicit, a non-null `value` is shorthand
  for exactly one entry with the supplied screen/node/declaredSource/snapshot and that value;
  `null` supplies no entry. Static components with no entries are valid. Formatting parameters,
  glyph set/length, trace bounds and viewport dimensions are explicit declaration inputs, not
  values inferred from a producer's representation. `format` names the authored Clock format.
- `present` with just a configuration validates the declaration; with a node it additionally
  resolves and observes the indicated variant. `pixels` compares the entire stated surface.
  Fixture SHA strings identify synthetic inputs; they do not attest to real consumer builds.

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

## MEDUI-PROFILE-INTERACTION, version 1

Scenarios supply a surface, a back-to-front ordered list of nodes, eligibility, output mappings,
host queue capacity, dropped-counter limit, editable values and accepted Unicode scalar sets.
Rectangles and pointer coordinates use authored pixels. This describes logical observations,
not a platform input API or device-runtime policy.

- **I01 — coordinates.** Input coordinates and origin are integers; positive integer `scaleNumerator`
  and `scaleDenominator` give device pixels per authored pixel. Normalize each axis exactly once
  with `floor((device-origin)*scaleDenominator/scaleNumerator)`, including negative values. Points
  outside `[0,width) × [0,height)` hit nothing; they are never clamped to an edge control.
- **I02 — hit.** Search reverse paint order using half-open rectangles intersected with the
  surface and explicit ancestor clip. The first containing node occludes every node below it,
  including if it is decorative, disabled or ineligible. Only an eligible Button, CriticalButton
  or TextInput is a target. A disabled foreground node is not transparent to input.
- **I03 — activation.** A primary press replaces any prior arm with the hit eligible Button or
  CriticalButton, or clears it when neither is hit. Release clears the arm and emits an output
  only if the hit is that same still-eligible node. Repeated presses are ordinary presses; a
  release without an arm does nothing. Cancel, focus loss, removal, or loss of eligibility clears
  the arm immediately. Button emits `{kind:"source",node,source}`; CriticalButton emits
  `{kind:"action",node,action,requirement}` even for `NoOp`. Neither output executes an action.
- **I04 — queue.** Capacity and dropped-counter limit are positive integers. Enqueue valid events
  in order until capacity; drop newest on saturation and increment a saturating dropped counter.
  Any saturation clears the existing arm and suppresses all activation for the entire accepted
  batch, including a queued press consumed after the overflow. Suppression resets at the next
  batch boundary; an overflow batch ends unarmed. Invalid events are rejected atomically before
  queue admission and do not increment the dropped counter. The rejection is observable.
- **I05 — boundary.** Consume the accepted batch in order, then update application state from
  emitted outputs, bind exactly one complete snapshot, render, and capture that snapshot's frame.
  Missing or mixed snapshot identities fail binding and yield no successful capture. Injected
  time belongs to the same snapshot; no wall-clock read is an input to replay.
- **I06 — editing.** A primary press focuses an eligible TextInput at its current caret; pressing
  elsewhere or losing focus clears focus. Focus traversal follows explicit eligible TextInput
  order, wraps, and clears the arm. Left/right move one Unicode scalar; home/end select the first/
  last boundary; backspace/delete remove one adjacent scalar if present. Insert and paste replace
  the selection atomically. All inserted values must be valid Unicode scalar strings in the
  declared finite glyph set; resulting scalar length must not exceed `maxLength`. Reject invalid
  UTF-8 (vectors use byte arrays), disallowed glyphs, invalid selection boundaries or oversize
  replacements without changing text/caret/selection. No normalization or grapheme shaping is
  implied. Navigation and deletion at an edge do nothing. Repeats apply only to navigation and
  deletion; repeated insert/paste is rejected. Editing without focus has no effect.

## MEDUI-PROFILE-BINDING, version 1

Each snapshot supplies screen, frame, snapshot ID and an array keyed by node and declared source.
Bindings are already resolved data, independent of any native storage or callback mechanism.
`schemas/binding.schema.json` describes the snapshot envelope and typed values; screen is inherited
by each entry. Declaration-dependent resolution, lengths, dates and ranges are additional semantic
checks. `bind` vectors isolate a single node and may repeat screen in entries to test mismatches.

- **B01 — mapping.** Each dynamic node has exactly one value matching screen, node, declared
  source and snapshot ID. Duplicate, missing, unknown or mistyped entries fail the whole snapshot
  without partial publication. Static Row, Label, Image, Button and CriticalButton need no dynamic
  values; supplying one is an error. TextInput uses a scalar string bounded as in I06. Clock uses
  source `clock` and an injected `[year,month,day,hour,minute,second]` Gregorian civil time (years
  1–9999, seconds 0–59), with no timezone conversion or leap-second inference.
- **B02 — formatting.** NumericDisplay receives a signed decimal integer string without leading
  zeros (except `0`), a nonnegative decimal scale, and explicit prefix/suffix. It inserts a decimal
  point `scale` digits from the right, zero-padding as needed, with ASCII digits, `.` separator,
  no grouping and no rounding. Declarations supply positive `maxDigits` (excluding sign) and
  nonnegative `maxScale`; exceeding either fails. Prefix/suffix are baked template strings, not
  arbitrary application text. Negative zero is invalid. Clock renders `HH:MM:SS` or
  `YYYY-MM-DD HH:MM:SS`, zero-padded. StatusIndicator receives a zero-based integer index into
  authored state order; out-of-range fails. If colours are supplied there is one per state.
- **B03 — trace.** SignalTrace receives integer samples in chronological order (oldest first),
  positive capacity, and explicit integer minimum/maximum. Empty input is allowed. Values outside
  the inclusive range fail; excess samples fail, with no truncation, reordering or clamping.
- **B04 — viewport.** VulkanViewport receives positive width/height matching its declared pixel
  surface and exactly `width*height*4` integers in `[0,255]`. Format is straight RGBA8, rows top to
  bottom and pixels left to right, no padding. Invalid dimensions, lengths, format or channels
  fail atomically; no inferred resizing, wraparound or clamping. Composition over opaque RGB8
  background is per channel `floor((src*alpha + bg*(255-alpha) + 127)/255)` with output alpha 255.
  Transparent source leaves background unchanged. Geometry for traces and all widget appearance
  are supplied by the independently declared presentation configuration.

## MEDUI-PROFILE-PRESENTATION, version 1

This is a presentation-description and observation profile, not a universal widget theme. It
makes each appearance choice explicit; equality is claimed only for the same configuration.
`schemas/presentation.schema.json` defines the declaration shape. Rectangle extent checks and
complete, unique variant resolution are additional semantic checks; schema validity alone does
not establish them.

- **P01 — configuration.** The declaration identifies theme/font/asset digests, backend, surface,
  and a finite set of variants for every component in `spec/component-model.md`. Each variant
  names component, pressed/focused state, face and label rectangles relative to the node (or
  `null` when absent), RGBA8 tint (or `null`), caret rectangle (or `null`), and explicit clipping.
  Every supplied node/state must resolve exactly one variant. Duplicate or missing variants,
  missing component coverage or missing configuration identity fail. Zero-area rectangles are
  allowed; negative extents are not. This descriptor does not prescribe rasterization.
- **P02 — observation.** Resolved face/label/tint/caret/clip observations must equal the selected
  variant, translated by node origin for rectangles, and clipped to node/surface when clipping
  is true. All component kinds, including Row, have observation vectors. State-dependent button
  face and TextInput caret are independently observable.
- **P03 — pixel evidence.** An exact-pixel comparison requires identical presentation declaration
  digest, theme/font/assets, backend, surface, locale, scenario and frame. Any mismatch fails
  identity before pixel comparison, even if byte arrays happen to match. Once identities agree,
  bytes compare exactly. Product-specific captured corpora must carry these declarations;
  synthetic geometry and colour vectors assert no cross-backend pixel parity.

## Adoption

0.2.0 compiler outcomes remain the baseline. New schemas and optional profiles are a 0.3.0
candidate. An implementation first passes all its claimed compiler cases and each new profile's
vectors at an exact candidate SHA, publishes that evidence, then updates its pin/claims. Neither
the 0.2.0 nor 0.3.0 final tag is justified by repository validation. Legacy reports and pinned
corpora remain reproducible. These observations establish neither certification nor clinical
requirements.
