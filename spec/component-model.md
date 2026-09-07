# Component and semantic model

| Construct | Required fields | Optional fields |
|---|---|---|
| `Row` | `id`, `height` | `spacing`, `background` |
| `CriticalButton` | `id`, `requirement`, `width`, `height`, `label`, `color`, `on_press` | `position` |
| `Button` | `id`, `width`, `height`, `label`, `color`, `source` | `position`, `requirement` |
| `VulkanViewport` | `id`, `width`, `height`, `stream_source` | `position` |
| `SignalTrace` | `id`, `width`, `height`, `stream_source`, `color` | `position` |
| `NumericDisplay` | `id`, `width`, `height`, `requirement`, `template`, `source`, `color` | `position` |
| `StatusIndicator` | `id`, `width`, `height`, `requirement`, `source`, `states` | `position`, `colors` |
| `Label` | `id`, `width`, `height`, `text`, `color` | `position` |
| `Clock` | `id`, `width`, `height`, `format` | `position` |
| `Image` | `id`, `width`, `height`, `source` | `position` |
| `TextInput` | `id`, `width`, `height`, `source`, `max_length`, `color` | `position`, `charset`, `requirement` |

## Field value domains

Field presence and field value shape are separate semantic checks. A known field whose value has
the wrong domain reports `MEDUI-E033`; it is not a syntax error merely because the field cannot use
that syntactically valid value.

| Field | Accepted value domain |
|---|---|
| `id` | identifier |
| `width`, `height`, `spacing` | pixel size or `Fill` |
| `position` | pixel coordinate pair |
| `requirement`, `template`, `stream_source` | quoted string |
| `source` | `img("ID")` for `Image`; quoted string for every other component |
| `label`, `text` | `t("KEY")` |
| `states` | non-empty list of `t("KEY")` values |
| `color`, `background` | `Theme.Colors.<Token>` |
| `colors` | non-empty list of `Theme.Colors.<Token>` values |
| `on_press`, `format` | member of the field's closed set (below) |
| `charset` | named value, resolved against the implementation's baked charsets |
| `max_length` | positive integer |

### Closed named values

`format` and `on_press` accept only the members below. A syntactically valid identifier that is not
a member reports `MEDUI-E034`; a value of the wrong *kind* still reports `MEDUI-E033`.

| Field | Component | Members | Rendering |
|---|---|---|---|
| `format` | `Clock` | `TimeSeconds` | `HH:MM:SS` |
| | | `DateTimeSeconds` | `YYYY-MM-DD HH:MM:SS` |
| `on_press` | `CriticalButton` | `NoOp` | no effect |
| | | `TriggerHalt` | requests the host's halt path |

Every member above is pinned by a positive conformance case as well as a negative one: a closed set
whose members are all rejected would otherwise satisfy the rejection cases while implementing an
empty vocabulary. The compiler corpus has no text-budget case or font model, so
`clock-format-members` carries the renderings as an `observations` entry. The optional candidate
[binding profile](profiles.md) separately asserts formatted text from injected civil time; those
string observations do not establish font measurement or pixel output.

Closing `format` is what makes a clock measurable. Because the rendering of each member is fixed
here, a text-budget pass knows a `TimeSeconds` clock draws eight glyphs and can check them against
the node's bounds. An open name can only be looked up in a table the product supplies, which moves a
compile-time guarantee into configuration.

Closing `on_press` is what keeps a critical control honest: a screen that can name any system event
can name one the host does not implement, and the press of a critical button is the worst place to
discover it.

## Resource identifiers

`img("ID")` names a baked image and `template` names a baked display template. Neither is a member
of a closed set — the identifiers a screen may use are whichever ones the product baked — so an
identifier that does not resolve reports `MEDUI-E035` (unknown resource identifier), with the kind
named in the message. A semantic case declares the resolvable identifiers with the `imageIds` and
`templates` `inputs` collections, the same way `themeTokens` declares the known colour tokens.

`charset` also names an implementation resource rather than a member of a fixed vocabulary, but it
stays **outside** `MEDUI-E035`: an unresolved `charset` fails compilation with no code assigned,
because a case cannot yet declare which character sets exist. An unknown screen `layout` kind is
likewise fatal and unassigned; whether it is a closed named value (`Vertical`, `Horizontal`) or a
grammar production is still open.

Node IDs are unique after synthetic row-background nodes are included. `position` requires fixed
dimensions and removes the node from flow; a positioned node whose `width` or `height` is `Fill`
reports `MEDUI-E054`, which is distinct from layout overflow (`MEDUI-E051`) because nothing has
overflowed — the node's geometry simply cannot be resolved. Positioned nodes must remain in their
containing box and must not overlap other non-background nodes. Images render at intrinsic
dimensions. Text keys must
exist for every approved locale, and every static or bounded-dynamic text value must fit its box in
the worst approved case. Unknown theme tokens (`MEDUI-E030`), text keys (`MEDUI-E031`), CV
checks (`MEDUI-E071`), members outside a closed set (`MEDUI-E034`), and unknown image or template
identifiers (`MEDUI-E035`) fail compilation. An unknown `charset` or screen `layout` kind is also
fatal and has no code assigned yet.

## Safety annotations

`@safety_critical(cv_check: [...])` marks a node for rendered-truth evidence (MEDUI-DEC-004). The
annotation **promotes `requirement` to required** on the node it annotates, whatever that
component's own row says: a `Button` or `TextInput`, where `requirement` is otherwise optional,
must carry one once annotated, and its absence reports `MEDUI-E070`.

`MEDUI-E070` is only ever the promotion failure. A component whose own row already requires
`requirement` — `CriticalButton`, `NumericDisplay`, `StatusIndicator` — that omits it reports the
ordinary `MEDUI-E012` (missing required field), annotated or not; the annotation adds no obligation
it did not already have. So the two codes never both apply to the same node: `MEDUI-E070` is reachable
only where the schema made `requirement` optional and the annotation made it required.

Compiled output is a flat, locale-free sequence of nodes with absolute rectangles and a finite
draw budget. Implementation-specific output fields beyond these shared semantics are permitted.
