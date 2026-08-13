# MEDUI-DEC-002: Closed language and bounded layout

Status: Accepted

The language has a closed component dictionary and no loops, conditionals, recursion, embedded
scripting, or data-dependent structure. `Row` is the only nested authoring container and cannot
nest. Fixed and flow dimensions are resolved to absolute rectangles before device execution.

The grammar is token-based and whitespace-insensitive. Comments beginning with `//` are accepted.
One property per line is canonical authoring style, not a syntactic restriction.
