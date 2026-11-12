# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-9B`
- Required target: `temperature at least 289.15`
- Faulty observed target value: `268.15`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-8898227d-b358-4832-97ab-ac7ddfb06c08",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 268.15
    },
    "outlet_temperature": 268.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler-C",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-e3174afb-cb57-44e9-901e-820cfaca0faf",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298.15
    },
    "outlet_temperature": 298.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler-B",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-0d073d2d-d35a-4edb-b080-889416021e2c",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 338.15
    },
    "outlet_temperature": 338.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Heater-C",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-e1efb515-bb7b-4a2f-9155-730e3363d364",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 338.15
    },
    "outlet_temperature": 338.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Heater-A",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,acetaldehyde_mole_fraction,acetaldehyde_molar_flow,acetic acid_mole_fraction,acetic acid_molar_flow,oxygen_mole_fraction,oxygen_molar_flow
S-2A,MAT-11fc5d0d-67ad-4714-9122-6ed0262657dc,338.15,101325,16.0709600090231,0.611111111111111,0.5,8.03548000451156,0,0,0.5,8.03548000451156
S-4A,MAT-89ea71ad-2499-48b5-b031-9153337154f5,338.149892756423,101325,13.0575436525001,0.611111111111111,0.153846282608769,2.00885455093886,0.461537826423434,6.02655031580398,0.384615890967797,5.02213878575721
S-6A,MAT-ee6375c9-74df-4707-bd31-163d68dc284c,387.155818457822,101325,5.820457913931,0.348604662550223,0.0099999999000193,0.0582045785573765,0.99,5.76225333479169,9.9980728623411e-11,5.8193362315672e-10
S-5A,MAT-c3368eac-2ab0-4e52-addb-4fecb7323b4e,311.882299632942,101325,7.237085738569,0.262506453317199,0.26953528055355,1.95064993493529,0.036519833561472,0.264297166642643,0.69394488588498,5.02213863699108
S-1B,MAT-37ddf4a0-2d31-4c85-96c8-d4c90273aa2e,298.15,101325,16.0709600090231,0.611111111111111,0.5,8.03548000451156,0,0,0.5,8.03548000451156
S-2B,MAT-0619002a-17b5-40fb-b5af-79100b84e099,338.15,101325,16.0709600090231,0.611111111111111,0.5,8.03548000451156,0,0,0.5,8.03548000451156
S-3A-L,MAT-95af8995-bec1-499d-b597-dc2ec09e63ad,338.15,101325,5.23080590769301,0.309433855203275,0.0560427329402947,0.293148658547355,0.94394884309331,4.93761318501247,8.42396639496037e-06,4.40641331849661e-05
S-3A-V,MAT-aa941a6d-de1a-4aaf-9f91-6263e7ffdaa7,338.15,101325,7.82673774480705,0.301677255907836,0.219210857490384,1.71570589239151,0.139130397145862,1.08893713079151,0.641658745363754,5.02209472162403
S-1A,MAT-0823637e-968b-4419-85f7-9a783dd6ee12,298.15,101325,16.0709600090231,0.611111111111111,0.5,8.03548000451156,0,0,0.5,8.03548000451156
S-7A,MAT-4b975724-04b8-4428-9117-4c6f8a4507eb,311.882380619368,101325,7.237085738569,0.262506453317199,0.26953528055355,1.95064993493529,0.036519833561472,0.264297166642643,0.69394488588498,5.02213863699108
S-8A,MAT-3bd0a3fe-94c1-4a3a-a9b4-683613c03ed9,298.15,101325,5.820457913931,0.348604662550223,0.0099999999000193,0.0582045785573765,0.99,5.76225333479169,9.9980728623411e-11,5.8193362315672e-10
S-3B-V,MAT-6329a625-225e-4aac-a441-267c24812f70,338.15,101325,7.82673774480705,0.301677255907836,0.219210857490384,1.71570589239151,0.139130397145862,1.08893713079151,0.641658745363754,5.02209472162403
S-3B-L,MAT-af5ea9c1-e8dc-4b22-b810-ec4ce6f491a6,338.15,101325,5.23080590769301,0.309433855203275,0.0560427329402947,0.293148658547355,0.94394884309331,4.93761318501247,8.42396639496037e-06,4.40641331849661e-05
S-4B,MAT-a585aa39-713f-4c2f-82c5-9245d07b2a92,338.149892756423,101325,13.0575436525001,0.611111111111111,0.153846282608769,2.00885455093886,0.461537826423434,6.02655031580398,0.384615890967797,5.02213878575721
S-5B,MAT-2d25b3c5-b8e9-442f-9a5a-ce2b34bb8ebd,311.882299632942,101325,7.237085738569,0.262506453317199,0.26953528055355,1.95064993493529,0.036519833561472,0.264297166642643,0.69394488588498,5.02213863699108
S-6B,MAT-1dfa98d3-67d7-4a8b-8e9f-69e43dbe57a5,387.155818457822,101325,5.820457913931,0.348604662550223,0.0099999999000193,0.0582045785573765,0.99,5.76225333479169,9.9980728623411e-11,5.8193362315672e-10
S-7B,MAT-24cc16b6-1985-4ce0-a960-bbf84a738fe2,311.882380619368,101325,7.237085738569,0.262506453317199,0.26953528055355,1.95064993493529,0.036519833561472,0.264297166642643,0.69394488588498,5.02213863699108
S-8B,MAT-8f8366c9-3229-4112-9bb9-cb74921acf26,314.797641684622,101325,5.820457913931,0.348604662550223,0.0099999999000193,0.0582045785573765,0.99,5.76225333479169,9.9980728623411e-11,5.8193362315672e-10
S-9B,MAT-50e67f5e-5b02-4593-bfb0-ebbbece8541d,268.15,101325,5.820457913931,0.348604662550223,0.0099999999000193,0.0582045785573765,0.99,5.76225333479169,9.9980728623411e-11,5.8193362315672e-10
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-9B
Target metric: temperature
Observed target value: 268.15
Required target value: >= 289.15
```

## Allowed Repair Actions

- `Cooler-C` / GUID `AQ-8898227d-b358-4832-97ab-ac7ddfb06c08`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Cooler-B` / GUID `RESF-e3174afb-cb57-44e9-901e-820cfaca0faf`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Heater-C` / GUID `AQ-0d073d2d-d35a-4edb-b080-889416021e2c`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Heater-A` / GUID `AQ-e1efb515-bb7b-4a2f-9155-730e3363d364`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
