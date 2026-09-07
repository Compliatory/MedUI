# Candidate profile arithmetic audit

Review of PR #29 compared B04 against
[MduX `blend()` at a3f8b6d](https://github.com/ambroise-leclerc/MduX/blob/a3f8b6daae073472b9a6f6b472ee9818b3faedf8/src/verify/Verify.cpp).
The source snapshot was inspected without modifications to those files.

B04 supplies an opaque background, a source RGB byte `s`, and source alpha byte `a`. The MduX
helper additionally takes coverage `c`; the equivalent call uses `c = 255`, not `c = a`.
Using alpha twice would incorrectly square the opacity.

Let `b` be the background channel and `d = s-b`. B04 is
`b + floor((d*a + 127)/255)`. MduX uses a denominator `255*255`, numerator `d*a*255`, and rounds
the signed delta to nearest with half away from zero before adding `b`. Dividing numerator and
denominator by 255 gives the same rational `d*a/255`. Since 255 is odd and `d*a` is integral,
there is no exact half-integer tie. Both rules therefore choose the same nearest integer, including
for negative `d`. Both preserve output alpha 255 for an opaque background.

An independent temporary arithmetic program enumerated all `256^3 = 16,777,216` `(s,b,a)` channel
triples and found zero differences between those two expressions. It implemented only the two
arithmetic expressions and did not render a frame or execute either consumer. The corpus pins
both sides of the 127/128 rounding boundary, ascending and descending spans, transparency,
opacity and extreme channel values. Consumer execution of the profile corpus remains required.

I01 deliberately uses mathematical floor. For example, `-1/2` normalizes to `-1`, while C/C++
integer truncation produces `0`; `normalize-negative-floor.json` and
`normalize-negative-nonunit.json` distinguish them.
