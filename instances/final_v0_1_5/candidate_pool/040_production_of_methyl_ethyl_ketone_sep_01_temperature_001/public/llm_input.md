# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-08`
- Required target: `temperature at most 292.15`
- Faulty observed target value: `313.15`

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
    "flash_pressure": 354637.5,
    "flash_temperature": 313.15,
    "guid": "SEP-8fb4f430-3460-4b7c-88be-67a243a7a072",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 354637.5,
      "separator_specification/temperature": 313.15
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
S-12,MAT-e3fe516b-2883-4eb9-80c2-d803b78a3584,375.061843314955,111458,0.817201,0.0605673950465552,0.99705556851361,0.814794807644891,3.8737076576279e-22,3.16559777152118e-22,0.0029444314863903,0.00240619235510964
S-13,MAT-324e6e14-76ab-49b2-9291-2293b59316be,349.91404591708,101325,7.5435743329918,0.544010615679273,0.0066337210233265,0.0500419676437939,4.7513239789227e-05,0.000358419656151297,0.99331876573688,7.49317394569182
S-08,MAT-27bed7d7-b5f6-4a15-bc01-1e9665d4d83d,313.15,354637.5,8.60717466700828,0.0573577459826916,0.00327659798580726,0.0282022511774106,0.933778410237821,8.03719387719824,0.0629449917763716,0.54177853863263
S-09,MAT-15f82d59-4faa-471d-89df-d6d06d2cb8af,313.15,354637.5,8.36077533299173,0.604578010725825,0.103439781700153,0.864836775288685,4.28691887864719e-05,0.0003584196561513,0.896517349111061,7.49558013804689
S-07,MAT-0de1443b-b871-4cf9-877f-89d217c7284d,353.15,99268.1025,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-01,MAT-ccb37445-00a7-4024-bbab-29d5b4c29f80,303.15,101325,8.9305,0.6619429488,1,8.9305,0,0,0,0
S-03,MAT-8bf462fa-c66d-4188-babb-d4b6660f0105,673.15,101325,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-04,MAT-2c3f1fbe-aa16-40b5-bb41-fee04e56f5dd,379.75247225114,99268.1025,16.96795,0.6619429488,0.0526315789473685,0.893050000000001,0.473684210526316,8.03745,0.473684210526316,8.03745
S-02,MAT-1081aaac-a858-415f-8800-51c1e68f4cce,373.150000000118,101325,8.9305,0.6619429488,1,8.9305,0,0,0,0
S-05,MAT-fe2ea09f-3042-408e-b4a3-30aaf1f49e1a,673.15,101325,0,0,0,0,0,0,0,0
S-10,MAT-3dbcbe62-72f9-4809-95f3-316a0b60e266,313.249112577418,101325,8.36077533299173,0.604578010725825,0.103439781700153,0.864836775288685,4.28691887864719e-05,0.0003584196561513,0.896517349111061,7.49558013804689
S-11,MAT-f0b73eca-66fb-4240-b8a4-e9161b02cda0,353.15,101325,8.36077533299173,0.604578010725825,0.103439781700153,0.864836775288685,4.28691887864719e-05,0.0003584196561513,0.896517349111061,7.49558013804689
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-08
Target metric: temperature
Observed target value: 313.15
Required target value: <= 292.15
```

## Allowed Repair Actions

- `HEAT-01` / GUID `AQ-b1ad48b4-14bc-4124-9613-8bd2749e8f81`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-01` / GUID `RESF-b0ef157f-5158-44c0-b074-f9c30892db7a`: `thermal_specification/outlet_temperature` (unit: `K`)
- `SEP-01` / GUID `SEP-8fb4f430-3460-4b7c-88be-67a243a7a072`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-8fb4f430-3460-4b7c-88be-67a243a7a072`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
