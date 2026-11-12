# Sensitivity Discovery Contract v0.1

## Summary

Sensitivity discovery proposes fixed fault specs from a DWSIM source flowsheet.
It is not the artifact builder itself. The output of discovery is a ranked
report plus candidate specs that can be passed to `build_from_fault_spec.py`.

Initial release support is intentionally narrow, with one v0.1.5 pilot
extension:

- `unit_operation + column_specification/reflux_ratio`
- `unit_operation + column_configuration/feed_stage`
- pilot `unit_operation + pressure_specification/outlet_pressure` for native
  Valve, Pump, and Compressor units when `CalcMode == OutletPressure`
- pilot `unit_operation + thermal_specification/outlet_temperature` for native
  Heater and Cooler units when `CalcMode == OutletTemperature`
- pilot `unit_operation + separator_specification/pressure` for native Vessel
  units when `OverrideP == true`
- pilot `unit_operation + separator_specification/temperature` for native
  Vessel units when `OverrideT == true`
- new pilot target families `terminal_composition`, `terminal_flow`,
  `terminal_temperature`, and `terminal_pressure`

## Candidate Enumeration

For each solved distillation column:

- reflux-ratio candidates are `baseline * [0.1, 0.3, 0.5, 0.7, 0.9, 1.2, 1.5]`;
- feed-stage candidates are `baseline + [-4, -3, -2, -1, +1, +2, +3, +4]`
  plus tray-position candidates `[20%, 35%, 50%, 65%, 80%]`;
- invalid, duplicate, and baseline-identical values are removed;
- base, faulty, and gold-repaired runs must all solve successfully.

Gold repair always restores the original baseline parameter value.

For pressure changers:

- supported native unit types are Valve, Pump, and Compressor;
- the XML field is `OutletPressure` for Valve, `Pout` for Pump, and `POut` for
  Compressor;
- candidates are `baseline * [0.5, 0.7, 0.9, 1.1, 1.3, 1.5]`;
- only positive pressure values are valid;
- units are Pa.

For heater/cooler outlet temperature:

- supported native unit types are Heater and Cooler;
- the XML field is `OutletTemperature`;
- candidates are `baseline + [-30, -20, -10, +10, +20, +30] K`;
- only positive temperature values are valid;
- units are K.

For separator flash pressure and temperature:

- supported native unit type is Vessel;
- `separator_specification/pressure` uses `FlashPressure` when
  `OverrideP == true`;
- `separator_specification/temperature` uses `FlashTemperature` when
  `OverrideT == true`;
- pressure candidates are `baseline * [0.5, 0.7, 0.9, 1.1, 1.3, 1.5]`;
- temperature candidates are `baseline + [-30, -20, -10, +10, +20, +30] K`;
- only positive values are valid.

## Target Metric Scoring

Discovery scores only terminal material streams after each successful
candidate fault. Terminal streams are graph outlets: material streams with an
upstream unit operation, no downstream unit operation, and nonzero solved base
flow.

- `terminal_composition`: component `mole_fraction` or `mass_fraction`;
  score is absolute fraction delta.
- `terminal_flow`: stream `molar_flow` or `mass_flow`; score is relative flow
  delta.
- `terminal_temperature`: stream `temperature`; score is absolute temperature
  delta.
- `terminal_pressure`: stream `pressure`; score is relative pressure delta.

Thresholds are generated between faulty and baseline values:

- `min`: `threshold = faulty + 0.7 * (baseline - faulty)`.
- `max`: `threshold = faulty - 0.7 * (faulty - baseline)`.

A target metric is accepted only when the faulty run misses the threshold, the
gold-repaired run satisfies it, the repaired value is closer to base than the
faulty value, and the family-specific score exceeds the minimum threshold.

The minimum deltas are fixed in `docs/design/target_metric_contract_v0_1_5.md`.

## Report Shape

`sensitivity_report.json` contains:

- source metadata, manifest `source_category`, discovered columns, discovered
  pressure units, thermal units, separator units, and allowed repair action pair
  count;
- every tested candidate with run status and rejection reasons;
- top scored target metric candidates for each fault candidate;
- accepted candidates with embedded fixed fault specs;
- optional generated instance build results.

Rejected candidates remain in the report so dataset-generation decisions are
auditable.

## Boundaries

Discovery does not write tracked `instances/seed` artifacts. It writes to
`.tmp/fault_discovery/...` by default and relies on the fixed-spec builder for
materialization. Existing output directories under `.tmp` may be replaced
automatically; outside `.tmp`, replacement requires an explicit `--overwrite`.

Material streams, reactors, property-package faults, topology faults,
CapeOpenUO mutation, and automatic source curation are outside v0.1.5
discovery.
