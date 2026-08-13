# MEDUI-DEC-004: Safety annotations and golden references

Status: Accepted

An `@safety_critical` node requires an explicit requirement identifier. A positioned node receives
an automatic `Bounds` golden. When both rules apply, the compiler emits one merged entry with
deduplicated checks. Dynamic content pins bounds and applicable color, not its changing value.

These mechanisms provide reviewable engineering evidence; they do not by themselves establish
certification or the adequacy of a device manufacturer's risk controls.
