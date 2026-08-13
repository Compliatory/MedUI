# Authoring portable MedUI

- Write one property per line and use four-space indentation. This is canonical style, although
  tokenization is whitespace-insensitive.
- Use `t("KEY")` for product text and size for the widest approved locale.
- Use governed theme tokens and baked image/template identifiers rather than literal resources.
- Add `requirement:` before applying `@safety_critical`; annotate a node only when the associated
  device risk analysis calls for rendered-truth evidence.
- Use `position` only for deliberate pixel-exact placement. It creates a `Bounds` golden even
  without a safety annotation.
- Treat an implementation checker as feedback, not as a substitute for its pinned conformance
  revision or the manufacturer's review and verification process.
