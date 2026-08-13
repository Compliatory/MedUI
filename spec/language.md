# MedUI language contract v0.1

```medui
Screen NeuroSense500 {
    layout: Vertical { spacing: 8px; padding: 0px; }
    surface: 1920px, 1080px;

    @safety_critical(cv_check: [Bounds, ColorHash])
    NumericDisplay {
        id: sedation-index;
        width: 512px;
        height: 512px;
        position: 1392px, 80px;
        requirement: "REQ-NS-001";
        template: "TPL-SEDATION-INDEX-160";
        source: "SEDATION_INDEX";
        color: Theme.Colors.ScoreDigits;
    }
}
```

Source is UTF-8. Columns are counted in UTF-8 bytes. Whitespace is insignificant between tokens;
`//` comments continue to end of line. Identifiers contain ASCII letters, digits, `_`, or `-`.
Sizes are positive `Npx` or `Fill`; spacing, padding, and coordinates may be `0px`.

A screen declares one `Vertical` or `Horizontal` layout and may pin its surface. Leaf components
are `CriticalButton`, `Button`, `VulkanViewport`, `SignalTrace`, `NumericDisplay`,
`StatusIndicator`, `Label`, `Clock`, `Image`, and `TextInput`. A `Row` is a single-level horizontal
container allowed only in a vertical screen and is flattened during compilation.

Text is referenced with `t("KEY")`, images with `img("ID")`, colors with
`Theme.Colors.<Token>`, and CV checks are `Bounds` or `ColorHash`. Loops, conditionals, recursion,
scripts, hardcoded product strings, nested rows, unknown components, and unknown fields are errors.

The detailed component properties and semantic constraints are defined by
[`component-model.md`](component-model.md).
