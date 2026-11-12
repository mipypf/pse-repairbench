# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `valve outlet`
- Required target: `pressure at most 2274746.25`
- Faulty observed target value: `7346062.5`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-866cd520-75ec-45e5-b3ea-a62b8e3958e1",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 299.15
    },
    "outlet_temperature": 299.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-004",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "flash_pressure": 21734212.5,
    "flash_temperature": 299.15,
    "guid": "SEP-443953ab-5634-4b6f-93ae-b110cd98182c",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 21734212.5,
      "separator_specification/temperature": 299.15
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-007",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,air_mole_fraction,air_molar_flow,benzene_mole_fraction,benzene_molar_flow
valve outlet,MAT-3b61dd0c-4dd9-43e0-89ab-a0298fa4548a,299.15,7346062.5,32.7639673416795,0.94961334554025,0.999522594940018,32.7483256578855,0.000477405059982332,0.0156416837940137
liquid benzene,MAT-72b85346-c84f-4f01-b829-9923f33a9dc6,299.149841876159,21734212.5,0.742738623438922,0.0503865793952031,0.209038714415999,0.155261126990781,0.790961285584001,0.587477496448141
purified air,MAT-4aa39093-653c-4e27-a8d2-7b8bde060aa7,299.15,21734212.5,32.7639673416795,0.94961334554025,0.999522594940018,32.7483256578855,0.000477405059982332,0.0156416837940137
cooler outlet,MAT-0a35e700-5e2a-40bc-8f85-77696635f840,299.15,14489475,33.5067059651184,1,0.982,32.9035852577463,0.018,0.603120707372132
compressed gas,MAT-e70ce5c2-9c7f-4a3f-b3f4-1d093e1914dc,1057.19506495739,14489475,33.5067059651184,1,0.982,32.9035852577463,0.018,0.603120707372132
feed,MAT-c7f25921-1bd6-4d9c-9682-2aab93d6389b,299.15,101325,33.5067059651184,1,0.982,32.9035852577463,0.018,0.603120707372132
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: valve outlet
Target metric: pressure
Observed target value: 7346062.5
Required target value: <= 2274746.25
```

## Allowed Repair Actions

- `COOL-004` / GUID `RESF-866cd520-75ec-45e5-b3ea-a62b8e3958e1`: `thermal_specification/outlet_temperature` (unit: `K`)
- `SEP-007` / GUID `SEP-443953ab-5634-4b6f-93ae-b110cd98182c`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-007` / GUID `SEP-443953ab-5634-4b6f-93ae-b110cd98182c`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
