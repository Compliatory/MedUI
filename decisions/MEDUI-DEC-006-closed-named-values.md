# MEDUI-DEC-006: Closed named values

Status: Accepted

`format` and `on_press` are closed sets, enumerated in `spec/component-model.md`. `charset` stays an
open name resolved against the implementation's baked character sets. A syntactically valid
identifier outside a closed set reports `MEDUI-E034`; a value of the wrong kind still reports
`MEDUI-E033`.

The contract previously required unknown formats and system events to fail compilation without ever
saying what a known one is. That is not conformable: two implementations rejecting different sets
both satisfied the text, and neither could be shown wrong by a case. Enumerating the members is what
turns the existing requirement into one a conformance case can pin.

Closing `format` also moves a clock from lookup to measurement. Because each member's rendering is
fixed here, a text-budget pass can measure a `TimeSeconds` clock's eight glyphs against the node's
bounds; an open name can only be resolved through a table the product supplies, which relocates a
compile-time guarantee into configuration.

Closing `on_press` bounds what a critical control can request. A screen able to name any system
event can name one the host does not implement, and a critical button's press is the worst place to
discover that.

These mechanisms constrain what a screen can express; they do not by themselves establish the
adequacy of a manufacturer's risk controls.
