# MEDUI-DEC-004: Safety annotations and golden references

Status: Accepted

An `@safety_critical` node requires an explicit requirement identifier: the annotation promotes
`requirement` to required regardless of the component's own field list, and its absence is
`MEDUI-E070`. A component that already requires `requirement` and omits it reports the ordinary
`MEDUI-E012` instead, so the two codes never overlap. A positioned node receives an automatic
`Bounds` golden. When both rules apply, the compiler emits one merged entry with
deduplicated checks. Dynamic content pins bounds and applicable color, not its changing value.

These mechanisms provide reviewable engineering evidence; they do not by themselves establish
certification or the adequacy of a device manufacturer's risk controls.
