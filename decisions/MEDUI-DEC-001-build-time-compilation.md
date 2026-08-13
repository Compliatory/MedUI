# MEDUI-DEC-001: Build-time-only compilation

Status: Accepted

`.medui` is authored source, never a device runtime asset. Lexing, parsing, semantic validation,
layout, text budgeting, and golden-reference generation happen on a build machine. Device code
consumes immutable compiled data and performs no DSL parsing, layout solving, or text shaping.
