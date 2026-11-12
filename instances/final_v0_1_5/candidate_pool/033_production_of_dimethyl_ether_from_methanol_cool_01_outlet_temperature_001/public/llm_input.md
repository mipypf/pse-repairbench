# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-08`
- Required target: `Dimethyl ether mole_fraction at least 0.99124860108`
- Faulty observed target value: `0.97141792432898`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1448675,
    "guid": "BB-fa33141d-a21e-4712-869d-a34766997ba2",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 1550000
    },
    "outlet_temperature": 319.702475898492,
    "pout": 1550000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "PUMP-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-78f5fb09-6ab8-4e03-a1cc-7c2af7518cc6",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298.4845
    },
    "outlet_temperature": 298.4845,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 430000,
    "guid": "RESF-78e60d10-b729-4ce5-83a4-0bf1b8459ccf",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 382.15
    },
    "outlet_temperature": 382.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 80000,
    "guid": "AQ-9479413c-f4c3-4e89-944d-f6023910ca8c",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 523.15
    },
    "outlet_temperature": 523.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1450000,
    "guid": "BB-3bea0233-4eea-400d-af82-50af17f25c47",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 1550000
    },
    "outlet_temperature": 298.484457343291,
    "pout": 1550000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "PUMP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,dimethyl ether_mole_fraction,dimethyl ether_molar_flow,methanol_mole_fraction,methanol_molar_flow,water_mole_fraction,water_molar_flow
S-14,MAT-316ae657-4bb4-44f5-8d9c-d94a909207ba,298.4845,1550000,18.941697426959,0.624751882786821,0.10561845361794,2.00059279113432,0.85585199794669,16.2112895873645,0.038529548435375,0.729815048460235
S-01,MAT-98659740-f687-4c43-a743-d5f57bac1ea7,298.15,100000,72.6797633812755,2.31146417833333,0,0,0.983,71.4442074037938,0.017,1.23555597748168
S-02,MAT-2dbad523-ed95-467a-9c32-31633855ce6c,298.484459164318,1550000,72.6797633812755,2.31146417833333,0,0,0.983,71.4442074037938,0.017,1.23555597748168
S-03,MAT-bfb4a7ba-3480-47f9-8a66-2e9a7aa1dd21,298.350549759829,1550000,91.8537336388284,2.94452534250336,0.0225160112810439,2.06817970281787,0.956024229672861,87.8143949446371,0.0214597590460953,1.97115899137348
S-04,MAT-3aaa6264-9653-4bab-af92-8a901c6108ff,523.15,1470000,91.8537336388284,2.94452534250336,0.0225160112810439,2.06817970281787,0.956024229672861,87.8143949446371,0.0214597590460953,1.97115899137348
S-05,MAT-543c45d6-91b6-4257-b897-fbda49b8721e,523.15,1470000,91.8537336388284,2.94452534250336,0.404925703150188,37.1939376806727,0.191204845934572,17.5628789889274,0.40386945091524,37.0969169692283
S-06,MAT-8a5df21a-5fae-43ab-a1bf-f9d0e5ce5463,523.15,1470000,0,0,0,0,0,0,0,0
S-07,MAT-9731fc26-3088-41c9-931f-bf7b54f40e2c,382.15,1040000,91.8537336388284,2.94452534250336,0.404925703150188,37.1939376806727,0.191204845934572,17.5628789889274,0.40386945091524,37.0969169692283
S-09,MAT-6b64b2e3-48e7-490c-aa72-790707cf8c34,336.15567698021,101325,55.624893534582,1.29075533448586,0.03596578611576,2.0005930235767,0.29803421388424,16.5781214169737,0.666,37.0461790940316
S-08,MAT-9272f70f-0f84-4445-8ef7-ea9defc41d8c,319.762046300799,1030000,36.228840104246,1.65377000799002,0.97141792432898,35.1933446549132,0.027181592662838,0.984757574360704,0.0014004830081801,0.0507378749720703
S-10,MAT-4403a138-f007-4da5-97c1-b4856de3c43b,295.135146794488,101325,18.941697426959,0.624751882786821,0.10561845361794,2.00059279113432,0.85585199794669,16.2112895873645,0.038529548435375,0.729815048460235
S-11,MAT-09fefc71-541b-462e-a875-68078143d462,371.343362903842,101325,36.683196107624,0.666003449393117,4.6075510500508e-09,1.69019698744902e-07,0.009999995392449,0.366831792056543,0.99,36.3163641465478
S-12,MAT-f425642f-e5a6-40ab-91a1-3c739c87db7c,295.50475939033,1550000,18.941697426959,0.624751882786821,0.10561845361794,2.00059279113432,0.85585199794669,16.2112895873645,0.038529548435375,0.729815048460235
S-13,MAT-9ba41b26-0ae4-4033-a028-38e65b07f97b,298.4845,1550000,18.941697426959,0.624751882786821,0.10561845361794,2.00059279113432,0.85585199794669,16.2112895873645,0.038529548435375,0.729815048460235
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-08
Target metric: Dimethyl ether mole_fraction
Observed target value: 0.97141792432898
Required target value: >= 0.991248601079697
```

## Allowed Repair Actions

- `PUMP-02` / GUID `BB-fa33141d-a21e-4712-869d-a34766997ba2`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-02` / GUID `RESF-78f5fb09-6ab8-4e03-a1cc-7c2af7518cc6`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-01` / GUID `RESF-78e60d10-b729-4ce5-83a4-0bf1b8459ccf`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HEAT-01` / GUID `AQ-9479413c-f4c3-4e89-944d-f6023910ca8c`: `thermal_specification/outlet_temperature` (unit: `K`)
- `PUMP-01` / GUID `BB-3bea0233-4eea-400d-af82-50af17f25c47`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
