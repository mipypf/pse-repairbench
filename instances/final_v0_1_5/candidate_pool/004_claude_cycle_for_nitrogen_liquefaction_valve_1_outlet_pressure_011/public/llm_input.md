# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-11`
- Required target: `molar_flow at least 17.4916290061`
- Faulty observed target value: `0`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2900000,
    "guid": "VALV-7af8423d-387f-4378-bba3-8950218c85d2",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 90000
    },
    "outlet_pressure": 90000,
    "outlet_temperature": 77.2434997306958,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALVE-1",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-fb8b924a-4b3e-49f7-a2a2-e79abd663936",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 123.61
    },
    "outlet_temperature": 123.61,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "COOL-fc807de0-456b-4dfd-81ba-d32ee92695d3",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 168.15
    },
    "outlet_temperature": 168.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-a73f020b-5f48-41a2-90bc-722cff02e0f0",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 303.15
    },
    "outlet_temperature": 303.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2900000,
    "guid": "COMP-ad69457f-65f9-4aa6-9986-f7a6ffae4404",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 3000000
    },
    "outlet_temperature": 735.48964913147,
    "p_out": 3000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "C-1",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-f16232ec-f5c3-4f6a-8169-20fba64277fb",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 114.91
    },
    "outlet_temperature": 114.91,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-04",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-cd726418-8787-4d61-ac36-6ad94da6de0a",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 280.04
    },
    "outlet_temperature": 280.04,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-05",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,nitrogen_mole_fraction,nitrogen_molar_flow
S-14,MAT-180a11e7-a4ec-487c-9433-de8fe15be6a9,114.910000585025,90000,71.3944041066061,2,1,71.3944041066061
S-15,MAT-1e0007ff-6ae8-4b92-b98f-ec171430fb29,280.039999999992,90000,71.3944041066061,2,1,71.3944041066061
S-13,MAT-c5613347-cba3-4be2-ba6e-34d9b27de9d7,76.363416299504,90000,71.3944041066061,2,1,71.3944041066061
S-01,MAT-6c044f9e-9583-4efa-be10-eda64c3d0a0b,300,100000,9.94095682780384,0.27848,1,9.94095682780384
S-02,MAT-e67beb25-1e6d-4120-b245-4936f39a347a,282.819192190158,100000,71.3944041066061,2,1,71.3944041066061
S-03,MAT-6b0dd617-1585-4b4c-9612-f4dac14f3aa5,735.48965164092,3000000,71.3944041066061,2,1,71.3944041066061
S-04,MAT-1003a040-2697-424a-903a-8983c410b841,303.150000000002,3000000,71.3944041066061,2,1,71.3944041066061
S-05,MAT-e89c0387-4699-4ad4-85f7-9fe4f67377c5,168.150000000111,3000000,71.3944041066061,2,1,71.3944041066061
S-06,MAT-aae80a4d-c6f3-4482-b772-b387387c22d1,168.150000000222,3000000,46.406362669294,1.3,1,46.406362669294
S-07,MAT-622b173e-4408-4cc8-bac8-98162df4145d,168.150000000222,3000000,24.9880414373121,0.7,1,24.9880414373121
S-08,MAT-94ddcecf-0314-418a-b6d3-30047485fd8c,77.2434997306959,100000,46.406362669294,1.3,1,46.406362669294
S-09,MAT-4041e650-9e13-4877-904b-470b84d96c01,123.616205716517,3000000,24.9880414373121,0.7,1,24.9880414373121
S-10,MAT-9b72ffb4-ed8f-4e9a-810c-8d6f64bf1977,76.363416299504,90000,24.9880414373121,0.7,1,24.9880414373121
S-12,MAT-ce13c181-6c99-4fc6-b38f-46ebd661e309,76.363416299504,90000,24.9880414373121,0.7,1,24.9880414373121
S-11,MAT-4df43a66-f1e6-4d1e-b506-f7a79dccaedb,76.363416299504,90000,0,0,1,0
S-16,MSTR-ec4fb0b1-1d0a-4b13-a9b3-8524c61933c0,280.040000003635,100000,61.4534472788023,1.72152,1,61.4534472788023
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-11
Target metric: molar_flow
Observed target value: 0.0
Required target value: >= 17.49162900611847
```

## Allowed Repair Actions

- `VALVE-1` / GUID `VALV-7af8423d-387f-4378-bba3-8950218c85d2`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `CL-03` / GUID `RESF-fb8b924a-4b3e-49f7-a2a2-e79abd663936`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-02` / GUID `COOL-fc807de0-456b-4dfd-81ba-d32ee92695d3`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-01` / GUID `RESF-a73f020b-5f48-41a2-90bc-722cff02e0f0`: `thermal_specification/outlet_temperature` (unit: `K`)
- `C-1` / GUID `COMP-ad69457f-65f9-4aa6-9986-f7a6ffae4404`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `CL-04` / GUID `RESF-f16232ec-f5c3-4f6a-8169-20fba64277fb`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-05` / GUID `RESF-cd726418-8787-4d61-ac36-6ad94da6de0a`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
