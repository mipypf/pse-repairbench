# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-11 - Glucose 60%`
- Required target: `temperature at least 344.15`
- Faulty observed target value: `323.15`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-328eb7e3-85a0-470b-85c1-13e5e02cc492",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 373.15
    },
    "outlet_temperature": 373.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "flash_pressure": 41254.2,
    "flash_temperature": 323.15,
    "guid": "SEP-19b6a047-bcbb-4345-96ee-6101b58cd9e4",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 41254.2,
      "separator_specification/temperature": 323.15
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "flash_pressure": 101325,
    "flash_temperature": 374.089,
    "guid": "SEP-973de038-1244-43f7-a4cc-86b0c0af8e8d",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 101325,
      "separator_specification/temperature": 374.089
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "flash_pressure": 66452.3,
    "flash_temperature": 363.15,
    "guid": "SEP-081f084d-831b-46db-af90-0f3cfe7574cf",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 66452.3,
      "separator_specification/temperature": 363.15
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,glucose_mole_fraction,glucose_molar_flow,water_mole_fraction,water_molar_flow
S-11 - Glucose 60%,MAT-895dbee3-da82-4769-b87e-60ae0e7cef94,323.15,41254.2,7.42431495890737,0.183750391207426,0.0415340745489868,0.308362050978416,0.958465925451013,7.11595290792895
S-07,MAT-493b8564-b1c1-4fa3-9030-e8f82a0db498,363.147201525663,66452.3,7.42431495890737,0.183750391207426,0.0415340745489867,0.308362050978416,0.958465925451013,7.11595290792895
S-08,MAT-a3d20636-f0a1-41c9-b0f3-b4913ae395aa,363.150000011922,66452.3,3.48648498908089,0.0628100032940892,3.78372378485884e-24,1.31918961787387e-23,1,3.48648498908089
S-05,MAT-7afff729-e7d0-4c19-bd0f-fa9034b05652,374.088762908588,101325,10.9107999479883,0.246561568359806,0.0282627572698516,0.308369290549902,0.971737242730148,10.6024306574384
S-06,MAT-4857b25b-278d-444d-aa52-32d68ef029f1,374.089000009036,101325,1.73277571405592,0.0312164396659173,3.22817373804757e-23,5.59370105404194e-23,1,1.73277571405592
S-04,MAT-1ad4f044-ff0c-4f2a-8f88-89a9708ba55c,373.15,101325,12.6435756620442,0.277777777777778,0.0243892929324217,0.308367870534833,0.975610707067578,12.3352077915093
S-12,MAT-2fce608e-f39b-4502-a032-54f2ccd55fa9,361.71503812389,66452.3,3.48648498908089,0.0628100032940892,3.78372378485884e-24,1.31918961787387e-23,1,3.48648498908089
S-10,MAT-5e9be05c-4503-4768-ac2b-b411ea9e3a65,349.736028076481,41254.2,0,0,3.08061176282849e-29,0,1,0
S-02 - Saturated Steam,MAT-69859cf1-485e-4869-a772-ae55addc54d7,406.718162848355,300000,3.7005623374528,0.0666666666666667,0,0,1,3.7005623374528
S-14,MAT-e2281832-2984-4874-81bb-87e87ee106c6,406.718162848355,300000,3.7005623374528,0.0666666666666667,0,0,1,3.7005623374528
S-09,MAT-6fbc5156-701a-4822-a094-e6b203214e93,406.718162848355,300000,2.62123165569573,0.0472222222222222,0,0,1,2.62123165569573
S-01 - Saturated Steam,MAT-d8873d3c-f9db-4138-9bf8-344fae01eece,406.718162848355,300000,2.62123165569573,0.0472222222222222,0,0,1,2.62123165569573
S-15,MAT-c7a44e30-b755-448c-b5c8-78f70c0afdaa,347.642419765463,66452.3,11.5410546962853,0.207915331848895,5.98982576015416e-24,6.91289067191581e-23,1,11.5410546962853
S-03 - Glucose 20%,MSTR-69238da2-aad8-46a1-b815-a3f6b98080d7,298.15,101325,12.6435756620442,0.277777777777778,0.0243892929324217,0.308367870534833,0.975610707067578,12.3352077915093
S-13,MAT-38297477-e096-413b-86bc-3897f94d2f4c,99.3440564629649,101325,1.73277571405592,0.0312164396659173,3.22817373804757e-23,5.59370105404194e-23,1,1.73277571405592
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-11 - Glucose 60%
Target metric: temperature
Observed target value: 323.15
Required target value: >= 344.15
```

## Allowed Repair Actions

- `HEAT-01` / GUID `AQ-328eb7e3-85a0-470b-85c1-13e5e02cc492`: `thermal_specification/outlet_temperature` (unit: `K`)
- `SEP-03` / GUID `SEP-19b6a047-bcbb-4345-96ee-6101b58cd9e4`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-03` / GUID `SEP-19b6a047-bcbb-4345-96ee-6101b58cd9e4`: `separator_specification/temperature` (unit: `K`)
- `SEP-01` / GUID `SEP-973de038-1244-43f7-a4cc-86b0c0af8e8d`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-973de038-1244-43f7-a4cc-86b0c0af8e8d`: `separator_specification/temperature` (unit: `K`)
- `SEP-02` / GUID `SEP-081f084d-831b-46db-af90-0f3cfe7574cf`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-02` / GUID `SEP-081f084d-831b-46db-af90-0f3cfe7574cf`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
