# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-06 `
- Required target: `mass_flow at most 9.045955676e-07`
- Faulty observed target value: `2.09921654719462e-06`

## Observed Candidate Unit Parameters

```json
[
  {
    "flash_pressure": 151950,
    "flash_temperature": 310.15,
    "guid": "SEP-10480f7f-3284-43c8-80b3-2d8d426a6f6e",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 151950,
      "separator_specification/temperature": 310.15
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,carbon dioxide_mole_fraction,carbon dioxide_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow,oxygen_mole_fraction,oxygen_molar_flow,water_mole_fraction,water_molar_flow
S-08 ,MAT-abca85bb-c0f3-4b72-9ab2-1b54f4819d94,310.149999989058,151950,9.26704953340617e-06,2.96534464609557e-07,0,0,0,0,1,9.26704953340617e-06,0,0
S-07 ,MAT-f283e04c-f97c-432f-bd47-7610d35c417d,310.15,151950,0.00497871868247815,0.000147622696311677,0.0792248714394105,0.000394438347552323,0.700061834010823,0.0034854109318796,0.18427189048379,0.000917437903807211,0.0364414040659773,0.000181431499239017
S-06 ,MAT-4a38bc35-78ad-4611-a6ef-f50474126d09,310.15,151950,0.000116514267988426,2.09921654719462e-06,5.86451590775396e-05,6.8329977809843e-09,1.88019262434653e-07,2.19069267302973e-11,9.50059424377421e-07,1.1069547837684e-10,0.999940216762236,0.00011650730238824
S-05 ,MAT-9a2916f2-e61f-411f-b8fe-ad77187fb97b,310.15,151950,0.00498798573201156,0.000147919230776286,0.0790776816021993,0.000394438347552323,0.698761207256702,0.0034854109318796,0.185787410616128,0.000926704953340617,0.036373700524971,0.000181431499239017
S-04 ,MAT-6fc6f508-96ab-4808-b2f5-913814d0db1b,310.15,101300,0.000246166666666667,4.43476142666667e-06,0,0,0,0,0,0,1,0.000246166666666667
S-02 ,MAT-6d44f213-685d-4292-8f7a-dc131705a2bd,310.15,101300,0.000394444444444445,1.73593027777778e-05,1,0.000394444444444445,0,0,0,0,0,0
S-03 ,MAT-ae9a0214-fb60-4d2b-a89e-290e39cc7769,310.15,101300,0.00446388888888887,0.000128224274702044,0,0,0.7808,0.00348540444444443,0.2076,0.000926703333333329,0.0116,5.17811111111109e-05
S-01,MAT-15563d68-2b37-452e-b2a4-349df35eda7e,293.15,101300,0.00446388888888887,0.000128224274702044,0,0,0.7808,0.00348540444444443,0.2076,0.000926703333333329,0.0116,5.17811111111109e-05
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-06 
Target metric: mass_flow
Observed target value: 2.09921654719462e-06
Required target value: <= 9.045955676003961e-07
```

## Allowed Repair Actions

- `SEP-01` / GUID `SEP-10480f7f-3284-43c8-80b3-2d8d426a6f6e`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-10480f7f-3284-43c8-80b3-2d8d426a6f6e`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
