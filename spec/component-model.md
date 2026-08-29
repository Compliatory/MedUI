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

Closing `format` is what makes a clock measurable. Because the rendering of each member is fixed
here, a text-budget pass knows a `TimeSeconds` clock draws eight glyphs and can check them against
the node's bounds. An open name can only be looked up in a table the product supplies, which moves a
compile-time guarantee into configuration.

Closing `on_press` is what keeps a critical control honest: a screen that can name any system event
can name one the host does not implement, and the press of a critical button is the worst place to
discover it.

`charset` stays open. It names a baked character set rather than a member of a fixed vocabulary, so
it is resolved against the implementation's own packages; an unresolved one reports `MEDUI-E034` in
the same way, since the failure is the same shape.

Node IDs are unique after synthetic row-background nodes are included. `position` requires fixed
dimensions and removes the node from flow. Positioned nodes must remain in their containing box and
must not overlap other non-background nodes. Images render at intrinsic dimensions. Text keys must
exist for every approved locale, and every static or bounded-dynamic text value must fit its box in
the worst approved case. Unknown theme tokens (`MEDUI-E030`), text keys (`MEDUI-E031`), CV
checks (`MEDUI-E071`), and named values outside their set (`MEDUI-E034`) fail compilation. Unknown
image IDs and templates fail compilation and have no code assigned yet.

Compiled output is a flat, locale-free sequence of nodes with absolute rectangles and a finite
draw budget. Implementation-specific output fields beyond these shared semantics are permitted.
