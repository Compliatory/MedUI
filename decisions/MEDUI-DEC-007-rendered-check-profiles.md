# MEDUI-DEC-007: Rendered-check profiles and evidence identity

Status: Accepted

Accepted on 2026-09-07 by Ambroise Leclerc, maintainer, by explicit instruction.
Acceptance records the architectural direction below. The profile identifiers, schemas and candidate
conformance corpus are specified in [the 0.3.0 profile contract](../spec/profiles.md); no consumer
support is asserted.

Raised by [MedUI #15](https://github.com/Compliatory/MedUI/issues/15) from a comparison of the
MduX and TrustSC verifiers. This record accepts the direction. The linked candidate delivery allocates optional profile/check
identities with schemas and corpus; it allocates no language diagnostic codes.

## Problem

`MEDUI-DEC-004` keeps golden *selection* in the contract but leaves the rendered check itself to
each implementation. The two consumers diverge in ways a case cannot currently catch: bounds as
measured-extent equality versus expanded-region containment; tint composition with a bounded
per-composite rounding allowance versus an exact `SHA-256` of packed `RGBA8`; a missing baseline
treated as pass versus fail. "Passes the golden check" therefore names different obligations in
each repository.

## Direction

1. Keep golden selection in the language contract. Define **rendered-check profiles** separately,
   each with an immutable ID and version, so a report names which check it ran.
2. Distinguish the check families explicitly — extent equality, ink containment, tint
   composition, exact hash — rather than one fuzzy "colour check". Each profile fixes its pixel
   format, coordinate space, background and chrome resolution, empty-content policy, sampling
   region, and arithmetic and rounding. Exact hashes carry zero tolerance and a named backend.
3. Give an evidence report a derived identity: contract SHA; producer, version and source SHA;
   profile and version; screen artifact and asset digests; screen and node; explicit locale or
   locale-free scope; scenario digest or `static`; capture or frame; check ID and version;
   backend and rendering configuration where relevant. Outcomes are `pass`, `fail`,
   `unsupported`, `not-run` and `missing-baseline` — distinct, and an omitted obligation cannot
   read as success.
4. The required obligation set is derived independently of the report, so a producer that skips
   a check cannot pass by silence.

## Candidate delivery

The profiles belong to MedUI as optional observation contracts, with no renderer implementation.
0.3.0 introduces `MEDUI-PROFILE-RENDERED/1` (four distinct checks) and
`MEDUI-PROFILE-EVIDENCE/1` (identity and independently supplied obligations), optional manifest
claims, evidence and vector schemas, and synthetic conformance cases. The definitions choose
explicit semantics; they do not assert that either consumer already implements them unchanged.
Legacy checks run alongside the candidate checks and retain their original identities/baselines.
See [profiles](../spec/profiles.md) for arithmetic, migration and the remaining consumer proof gate.

## Rollout

`MEDUI-DEC-004` and `MEDUI-DEC-005` remain authoritative for existing compiler and golden-selection
claims. Profile adoption requires a minor release with its own candidate corpus, passed by every implementation claiming
the affected capability before any consumer advertises a profile. Language-diagnostic ambiguities
stay with MedUI #2, #3, #4 and #8, not this record.
