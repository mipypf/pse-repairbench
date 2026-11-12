# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-08`
- Required target: `pressure at least 301441.875`
- Faulty observed target value: `177318.75`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-b1ad48b4-14bc-4124-9613-8bd2749e8f81",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 353.15
    },
    "outlet_temperature": 353.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-b0ef157f-5158-44c0-b074-f9c30892db7a",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 353.15
    },
    "outlet_temperature": 353.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "flash_pressure": 177318.75,
    "flash_temperature": 283.15,
    "guid": "SEP-8fb4f430-3460-4b7c-88be-67a243a7a072",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 177318.75,
      "separator_specification/temperature": 283.15
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
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,2-butanol_mole_fraction,2-butanol_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methyl ethyl ketone_mole_fraction,methyl ethyl ketone_molar_flow
S-06,MAT-9c1506eb-0ed1-4074-a298-5bd03d19b74a,673.15,101325,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-12,MAT-e3fe516b-2883-4eb9-80c2-d803b78a3584,375.063895782441,111458,0.817201,0.0605674734587748,0.99710316667558,0.814833704910451,5.285085362263e-21,4.31897704312669e-21,0.0028968333244177,0.00236729508954747
S-13,MAT-324e6e14-76ab-49b2-9291-2293b59316be,351.159061047,101325,7.847946628934,0.566006015755656,0.0088694822209016,0.0696072230959148,2.935355278857e-05,0.000230365115654294,0.99110116422631,7.77810904072243
S-08,MAT-27bed7d7-b5f6-4a15-bc01-1e9665d4d83d,283.15,177318.75,8.30280237106608,0.035368605527785,0.00103673478035381,0.00860780399248825,0.968014343158414,8.03723178360165,0.0309489220612326,0.256962783471941
S-09,MAT-15f82d59-4faa-471d-89df-d6d06d2cb8af,283.15,177318.75,8.66514762893393,0.626573489214426,0.102068766266961,0.884440928006365,2.65852499598599e-05,0.000230365115654296,0.89790464848308,7.78047633581191
S-07,MAT-0de1443b-b871-4cf9-877f-89d217c7284d,353.15,99268.1025,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-01,MAT-ccb37445-00a7-4024-bbab-29d5b4c29f80,303.15,101325,8.9305,0.6619429488,1,8.9305,0,0,0,0
S-03,MAT-8bf462fa-c66d-4188-babb-d4b6660f0105,673.15,101325,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-04,MAT-2c3f1fbe-aa16-40b5-bb41-fee04e56f5dd,379.75247225114,99268.1025,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-02,MAT-1081aaac-a858-415f-8800-51c1e68f4cce,373.150000000118,101325,8.9305,0.6619429488,1,8.9305,0,0,0,0
S-05,MAT-fe2ea09f-3042-408e-b4a3-30aaf1f49e1a,673.15,101325,0,0,0,0,0,0,0,0
S-10,MAT-3dbcbe62-72f9-4809-95f3-316a0b60e266,283.189253413837,101325,8.66514762893393,0.626573489214426,0.102068766266961,0.884440928006365,2.65852499598599e-05,0.000230365115654296,0.89790464848308,7.78047633581191
S-11,MAT-f0b73eca-66fb-4240-b8a4-e9161b02cda0,353.15,101325,8.66514762893393,0.626573489214426,0.102068766266961,0.884440928006365,2.65852499598599e-05,0.000230365115654296,0.89790464848308,7.78047633581191
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-08
Target metric: pressure
Observed target value: 177318.75
Required target value: >= 301441.875
```

## Allowed Repair Actions

- `HEAT-01` / GUID `AQ-b1ad48b4-14bc-4124-9613-8bd2749e8f81`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-01` / GUID `RESF-b0ef157f-5158-44c0-b074-f9c30892db7a`: `thermal_specification/outlet_temperature` (unit: `K`)
- `SEP-01` / GUID `SEP-8fb4f430-3460-4b7c-88be-67a243a7a072`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-8fb4f430-3460-4b7c-88be-67a243a7a072`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
