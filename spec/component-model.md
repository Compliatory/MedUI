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

Node IDs are unique after synthetic row-background nodes are included. `position` requires fixed
dimensions and removes the node from flow. Positioned nodes must remain in their containing box and
must not overlap other non-background nodes. Images render at intrinsic dimensions. Text keys must
exist for every approved locale, and every static or bounded-dynamic text value must fit its box in
the worst approved case. Unknown theme tokens, image IDs, templates, charsets, formats, system
events, or CV checks fail compilation.

Compiled output is a flat, locale-free sequence of nodes with absolute rectangles and a finite
draw budget. Implementation-specific output fields beyond these shared semantics are permitted.
