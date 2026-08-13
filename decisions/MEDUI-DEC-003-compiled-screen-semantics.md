# MEDUI-DEC-003: Compiled-screen semantics

Status: Accepted

A compiled screen is locale-free layout data: flat nodes, absolute rectangles, validated text and
theme identifiers, bounded work figures, requirement identifiers, and applicable goldens. Locale
glyph data stays in text packages and is selected by bounded lookup on device.

Rust modules, canonical JSON, C++ modules/headers, committed artifact layouts, and byte-identity
evidence remain implementation decisions. Conformance compares observable meaning, not output
encoding.
