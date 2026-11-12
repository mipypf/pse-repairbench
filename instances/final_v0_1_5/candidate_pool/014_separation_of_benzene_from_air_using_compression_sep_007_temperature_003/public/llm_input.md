# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `liquid benzene`
- Required target: `temperature at least 290.149968192`
- Faulty observed target value: `269.149893974011`

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
    "flash_pressure": 14489475,
    "flash_temperature": 269.15,
    "guid": "SEP-443953ab-5634-4b6f-93ae-b110cd98182c",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 14489475,
      "separator_specification/temperature": 269.15
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
valve outlet,MAT-3b61dd0c-4dd9-43e0-89ab-a0298fa4548a,269.15,101325,32.765163292346,0.949090110773195,0.99986899923052,32.7608710307425,0.000131000769480099,0.00429226160343842
liquid benzene,MAT-72b85346-c84f-4f01-b829-9923f33a9dc6,269.149893974011,14489475,0.741542672772474,0.050909885605146,0.192455951523394,0.142714300683627,0.807544048476606,0.598828372088847
purified air,MAT-4aa39093-653c-4e27-a8d2-7b8bde060aa7,269.15,14489475,32.765163292346,0.949090110773195,0.99986899923052,32.7608710307425,0.000131000769480099,0.00429226160343842
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
Target stream: liquid benzene
Target metric: temperature
Observed target value: 269.149893974011
Required target value: >= 290.1499681922033
```

## Allowed Repair Actions

- `COOL-004` / GUID `RESF-866cd520-75ec-45e5-b3ea-a62b8e3958e1`: `thermal_specification/outlet_temperature` (unit: `K`)
- `SEP-007` / GUID `SEP-443953ab-5634-4b6f-93ae-b110cd98182c`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-007` / GUID `SEP-443953ab-5634-4b6f-93ae-b110cd98182c`: `separator_specification/temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
