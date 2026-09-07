# MEDUI-DEC-008: Optional interaction, data-binding and presentation profiles

Status: Accepted

Accepted on 2026-09-07 by Ambroise Leclerc, maintainer, by explicit instruction.
Acceptance records the architectural direction below. Profile identifiers, schemas and the
candidate conformance corpus remain delivery work; no consumer support is asserted.

Raised by [MedUI #16](https://github.com/Compliatory/MedUI/issues/16) from a comparison of the
MduX and TrustSC runtimes for [MduX #312](https://github.com/ambroise-leclerc/MduX/issues/312).
This record accepts the architectural direction and behavioral defaults below. Detailed
profile definitions and their conformance cases remain prerequisites for consumer claims.

## Problem

The compiled screen is locale-free layout data with no runtime behaviour (`MEDUI-DEC-003`). The
two implementations have each grown an input and update path anyway — hit testing, press/release
activation, focus and text editing, an event loop — and they differ: reverse-paint all-node
traversal versus a target list; caller-bound rendering values versus a bounded event batch and
character-indexed editing. The component dictionary and the closed action names do not pin any of
this, so "the same screen" behaves differently under interaction.

## Direction

Define an **optional, versioned logical interaction profile**, with presentation profiles
declared separately. A consumer that does not claim the profile keeps today's contract unchanged.
Accepted direction for the profile definitions:

1. **Coordinates and hit testing.** Normalize platform coordinates once into authored pixels;
   specify clipping, scaling and integer rounding. Hit testing uses half-open rectangles, reverse
   paint order and all-node occlusion. `Button` source and `CriticalButton` closed action are
   distinct outputs, never executable callbacks.
2. **Press/release.** Press arms one control; release activates only that same eligible control
   under the release coordinate. Focus loss, cancellation, removal and overflow clear armed
   state.
3. **Event batch and update boundary.** One bounded ordered event batch with a host-supplied
   capacity; one normalize-enqueue / consume-in-order / update / bind-one-snapshot / render /
   capture boundary. Saturation and invalid input have observable outcomes; overflow
   policy is drop-newest with a saturating counter and cancellation of any pending activation.
4. **Editing.** Address Unicode scalar boundaries with a bounded accepted glyph set and length;
   reject invalid encoding, disallowed glyphs and oversize edits with no partial mutation.
   Establish repeat, paste, navigation and focus policy before scenario tooling depends on them.
5. **Dynamic inputs.** Normalize by screen and node plus declared source mapping, types, bounds
   and snapshot identity. Clock input is injected for replay. State ordering, number formatting,
   trace ordering and viewport rows are specified independently of any native storage.
6. **Presentation.** Widget appearance — face and label placement, pressed and focused states,
   tint, caret — lives in declared presentation profiles. Equal source does not imply equal
   pixels; an exact-pixel corpus case identifies profile, theme, fonts, assets, surface and
   backend.

## Delivery decisions remaining

- Does an interaction profile belong in MedUI at all, or does the contract stay layout-only and
  point at a separate runtime contract?
- Which of the proposed defaults are actually shared, versus a starting point for negotiation
  between the two implementations?
- What is the smallest first profile — hit testing and press/release only — that both
  implementations could pass without changing observable behaviour?
- How do capability and manifest schemas carry a profile claim, and under which minor?

## Rollout

`MEDUI-DEC-003` remains authoritative. This record feeds, and is fed by,
[MEDUI-DEC-007](MEDUI-DEC-007-rendered-check-profiles.md). Language-diagnostic and safety
ambiguities stay with MedUI #2, #3, #4 and #8. Adoption is a minor release with a candidate
corpus — edge coordinates, overlapping controls and non-controls, press/release cancellation,
overflow during activation, critical versus ordinary actions, Unicode edit limits, a consistent
update/capture order and injected time — passed by every implementation claiming the profile.
Nothing here infers a clinical workflow or hazard classification from an example screen.
