# v0.1 Final Family Feasibility Scan

Date: 2026-06-02

This note records a read-only scan over curated DWSIM headless-success sources
to decide which scalar unit-operation parameter families can realistically
support a larger v0.1 final benchmark.

## Scope

Command:

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\scan_family_feasibility.py --category all --output-dir .tmp\final_family_feasibility --overwrite
```

The scan reads DWSIM XML only. It does not mutate flowsheets and does not run
DWSIM solves.

Output artifacts:

- `.tmp/final_family_feasibility/family_feasibility_report.json`
- `.tmp/final_family_feasibility/family_feasibility_summary.csv`
- `.tmp/final_family_feasibility/family_feasibility_rows.csv`

## Summary

Curated source count: 161

Source read errors: 5 (`File is not a zip file`)

| family | candidate objects | candidate sources | strong objects | strong sources | recommendation |
| --- | ---: | ---: | ---: | ---: | --- |
| `thermal_specification/outlet_temperature` | 273 | 101 | 233 | 87 | `strong_candidate` |
| `thermal_specification/heat_duty` | 273 | 101 | 17 | 9 | `weak_or_edge` |
| `separator_specification/pressure` | 64 | 32 | 28 | 14 | `weak_or_edge` |
| `separator_specification/temperature` | 64 | 32 | 28 | 15 | `weak_or_edge` |
| `column_specification/reboiler_duty` | 9 | 5 | 9 | 5 | `weak_or_edge` |
| `column_specification/condenser_duty` | 9 | 5 | 9 | 5 | `weak_or_edge` |
| `column_specification/distillate_flowrate` | 9 | 5 | 0 | 0 | `reject_for_v0_1_final` |
| `column_specification/vapor_flowrate` | 9 | 5 | 0 | 0 | `reject_for_v0_1_final` |

## Interpretation

`thermal_specification/outlet_temperature` is the strongest next family. Native
Heater/Cooler objects are common, the `OutletTemperature` XML field is direct,
and `CalcMode=OutletTemperature` is widely present.

`separator_specification/pressure` and `separator_specification/temperature`
are feasible but smaller. Native Vessel objects expose `FlashPressure` and
`FlashTemperature`, and `OverrideP=true` / `OverrideT=true` provide clean scalar
specification conditions. These are good provisional edge families, but they
are unlikely to carry the final benchmark alone.

`thermal_specification/heat_duty` is readable only in relatively few active
duty-mode Heater/Cooler objects. It may be useful as a harder edge family after
outlet temperature and separator families are stable.

Native distillation-column duty fields are direct, but native columns remain
sparse in the curated corpus. Column duty/spec families should not be relied on
for the main n=200 material unless additional native-column sources are added.

Distillate and vapor flowrate fields are present but zero in the scanned native
columns, so they should be rejected for v0.1 final unless a more reliable active
specification signal is found.

## Recommendation

Keep the terminal target contract fixed. Expand repair-family support in this
order:

1. `thermal_specification/outlet_temperature`
2. `separator_specification/pressure`
3. `separator_specification/temperature`
4. Optional edge: `thermal_specification/heat_duty`

Do not promote column duty or column flow-spec families until more native
column sources or clearer active-specification signals are available.
