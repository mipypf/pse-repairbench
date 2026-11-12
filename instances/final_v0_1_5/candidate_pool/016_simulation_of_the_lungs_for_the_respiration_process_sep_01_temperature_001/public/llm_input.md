# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-06 `
- Required target: `temperature at least 301.15`
- Faulty observed target value: `280.15`

## Observed Candidate Unit Parameters

```json
[
  {
    "flash_pressure": 101300,
    "flash_temperature": 280.15,
    "guid": "SEP-10480f7f-3284-43c8-80b3-2d8d426a6f6e",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 101300,
      "separator_specification/temperature": 280.15
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
S-08 ,MAT-abca85bb-c0f3-4b72-9ab2-1b54f4819d94,280.149999999788,101300,9.26703311640905e-06,2.9653393928535e-07,0,0,0,0,1,9.26703311640905e-06,0,0
S-07 ,MAT-f283e04c-f97c-432f-bd47-7610d35c417d,280.15,101300,0.00483652410848584,0.000145060770383649,0.0815527803729782,0.00039443198838796,0.720642463281496,0.00348540464725958,0.189689177174745,0.000917436278524496,0.00811557917078141,3.92511943138098e-05
S-06 ,MAT-4a38bc35-78ad-4611-a6ef-f50474126d09,280.15,101300,0.000258708858397731,4.66103811823021e-06,4.82397787291026e-05,1.24800580843653e-08,3.63386584934166e-08,9.40113285453681e-12,3.0194807528736e-07,7.81166418529851e-11,0.999951421934537,0.000258696290821872
S-05 ,MAT-9a2916f2-e61f-411f-b8fe-ad77187fb97b,280.15,101300,0.00484579114160225,0.000145357304322934,0.0813968198096012,0.00039443198838796,0.719264315239789,0.00348540464725958,0.191238805916528,0.000926703311640905,0.008100059034082,3.92511943138098e-05
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
Target metric: temperature
Observed target value: 280.15
Required target value: >= 301.15
```

## Allowed Repair Actions

- `SEP-01` / GUID `SEP-10480f7f-3284-43c8-80b3-2d8d426a6f6e`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-10480f7f-3284-43c8-80b3-2d8d426a6f6e`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
