# Target Metric Contract v0.1.5

## Summary

`final_v0_1_5` targets terminal material stream recovery. The benchmark
objective is not to repair an arbitrary local stream value, but to restore an
outlet material stream condition after a single existing unit-operation scalar
parameter fault.

The promoted v0.1.5 candidate pool uses only `terminal_*` target families.
Existing v0.1 seed artifacts keep their legacy target families for validator
and evaluator compatibility.

## Terminal Material Stream

A terminal material stream is defined mechanically from the DWSIM flowsheet
graph:

- it is a material stream, not an energy stream;
- it has an upstream unit-operation connection;
- it has no downstream unit-operation connection;
- the solved base run reports nonzero molar or mass flow.

When a flowsheet has multiple terminal material streams, all of them are valid
target candidates. Discovery does not infer which one is the semantic main
product.

## Target Families

The current v0.1.5 target metric contract supports these target families:

- `terminal_composition`: `mole_fraction` or `mass_fraction` for a component;
- `terminal_flow`: `molar_flow` or `mass_flow`;
- `terminal_temperature`: stream `temperature`;
- `terminal_pressure`: stream `pressure`.

Legacy `product_purity`, `impurity_max`, `product_flow`, and
`stream_pressure` remain readable by validators and evaluators so existing
seed and archived pilot artifacts continue to work.

## Threshold Rule

Thresholds are generated from base and faulty values with fixed `alpha = 0.7`.

If `base_value > faulty_value`:

```text
direction = min
threshold = faulty_value + 0.7 * (base_value - faulty_value)
```

If `base_value < faulty_value`:

```text
direction = max
threshold = faulty_value - 0.7 * (faulty_value - base_value)
```

A candidate target is accepted only when:

- the faulty run misses the generated threshold;
- the gold-repaired run satisfies the generated threshold;
- the repaired value is closer to the base value than the faulty value is.

## Minimum Sensitivity

Discovery rejects weak terminal metric changes:

- composition: absolute delta at least `0.01`;
- flow: relative delta at least `0.05`;
- pressure: relative delta at least `0.05`;
- temperature: absolute delta at least `1 K` and relative delta at least
  `0.01`.

Component composition candidates also require nonzero base component flow.

## Public Artifact Rule

Generated selection-benchmark public problem statements should describe
terminal stream target recovery without naming the hidden gold parameter family.
`public/llm_input.md` remains a target+parameter pair-selection prompt, and
hidden gold/mock artifacts keep the exact repair action.

Leakage checks still scan hidden repair parameters and direct hidden labels.
For terminal targets, exact-token scanning does not treat the base terminal
target value itself as forbidden, because the same temperature, pressure, flow,
or composition value can legitimately appear as an observed public stream
condition elsewhere in the faulty flowsheet.

For `pressure_specification/outlet_pressure`, exact-token scanning also does
not treat the hidden gold pressure value itself as forbidden. Pressure values
are ordinary observable stream/unit state values in DWSIM artifacts, so leakage
enforcement focuses on oracle fields, hidden paths, direct repair phrasing, and
specialized legacy action names.

The same rule applies to `thermal_specification/outlet_temperature`.
Temperature values are ordinary observable stream/unit state values, so leakage
checks focus on oracle fields and direct repair phrasing rather than raw
floating-point temperature tokens.

The same rule applies to `separator_specification/pressure` and
`separator_specification/temperature`. Flash pressure and flash temperature
values can appear naturally as observable unit or stream state, so leakage
checks focus on hidden paths, oracle fields, direct repair phrasing, and legacy
specialized action names rather than raw pressure/temperature tokens.
