# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-05`
- Required target: `temperature at least 282.485432882`
- Faulty observed target value: `261.483333333333`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-1743a2d1-6118-44f2-b51c-ef8a36c22860",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 261.483333333333
    },
    "outlet_temperature": 261.483333333333,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOLER",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-7ac810bb-40a5-466d-9aec-2c16cbabbec0",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 699.816666666667
    },
    "outlet_temperature": 699.816666666667,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEATER",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,hydrogen_mole_fraction,hydrogen_molar_flow,n-heptane_mole_fraction,n-heptane_molar_flow,toluene_mole_fraction,toluene_molar_flow
FEED,MAT-b9faab21-9fb0-45e1-9fba-26879fb447c0,291.483333333333,101325,9.97984072174208,1,0,0,1,9.97984072174208,0,0
S-01,MAT-3301e46b-07f5-4209-8a43-0333a5338b94,699.816666666662,101325,9.97984072174208,1,0,0,1,9.97984072174208,0,0
S-02,MAT-2a06a64d-9fac-40ff-a6c1-52923ea900de,699.816666666662,101325,15.9677463499541,1,0.375,5.98790488123278,0.53125,8.4828652484131,0.09375,1.49697622030819
S-04,MAT-149d37b0-42e9-43f9-8d0c-43dd6a915442,699.816666666662,101325,0,0,0,0,0,0,0,0
S-03,MAT-4eb142dd-0038-4c61-9f6b-500ad917bd7d,261.483333333333,101325,15.9677463499541,1,0.375,5.98790488123278,0.53125,8.4828652484131,0.09375,1.49697622030819
S-05,MAT-b484fea2-6c14-4381-98ba-245529808c66,261.483333333333,101325,6.02238943853877,0.0165473624824273,0.992472875598001,5.97705816403761,0.00662201476597308,0.0398803517884441,0.000905109636025774,0.00545092271272129
S-06,MAT-a8471ce3-aea2-4751-9a7c-2c663ce4d824,261.483392781191,101325,9.9453569114153,0.983452615756233,0.00109065382936361,0.0108469415998229,0.848937326348863,8.4429847059621,0.149972019821773,1.49152526385338
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-05
Target metric: temperature
Observed target value: 261.483333333333
Required target value: >= 282.485432881567
```

## Allowed Repair Actions

- `COOLER` / GUID `RESF-1743a2d1-6118-44f2-b51c-ef8a36c22860`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HEATER` / GUID `AQ-7ac810bb-40a5-466d-9aec-2c16cbabbec0`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
