# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Reactor Output 2`
- Required target: `temperature at least 337.038143374`
- Faulty observed target value: `325.750562992088`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 0,
    "guid": "RESF-0e30f3a3-019c-4936-9359-414547f28fbf",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 329.928
    },
    "outlet_temperature": 329.928,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 219575.48333333,
    "guid": "BB-93a5650f-6358-4ec5-a663-352683b8b162",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 430922.5
    },
    "outlet_temperature": 330.108678986212,
    "pout": 430922.5,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "pump",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 0,
    "guid": "AQ-6c7ba34b-bb9b-4a44-805a-1db1e6e9b834",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 347.039
    },
    "outlet_temperature": 347.039,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Heater",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,isobutane_mole_fraction,isobutane_molar_flow,isopentane_mole_fraction,isopentane_molar_flow,n-butane_mole_fraction,n-butane_molar_flow,propane_mole_fraction,propane_molar_flow
Reactor Output 2,MAT-8250e372-d697-444b-a620-b1cadd3dc778,325.750562992088,430922.5,0,0,0,0,0,0,0,0,0,0
Reactor Output1,MAT-a302881c-d42f-4cb5-9667-7c91def1dc04,325.750562992088,430922.5,27.7,1.61171519601146,0.386508132645283,10.7062752742743,0.0044532731867657,0.12335566727341,0.609038588701257,16.8703689070248,5.4666945631887e-09,1.51427439400327e-07
R4,MAT-dbb1da71-fd4c-4d82-8ae9-610b5bda2ea9,347.039,430922.5,27.7,1.61171519601146,0.08653390238944,2.39698909618749,0.0044532731867657,0.12335566727341,0.9090128189571,25.1796550851117,5.4666945631887e-09,1.51427439400327e-07
R3,MAT-3174a79f-fff4-4d76-bbcb-f785cc13dbb2,307.867699369549,430922.5,27.7,1.61171519601146,0.08653390238944,2.39698909618749,0.0044532731867657,0.12335566727341,0.9090128189571,25.1796550851117,5.4666945631887e-09,1.51427439400327e-07
R2,MAT-f77c0a0f-967f-4002-9935-d489e6ba142a,329.928,642269.51666667,27.7,1.61171519601146,0.08653390238944,2.39698909618749,0.0044532731867657,0.12335566727341,0.9090128189571,25.1796550851117,5.4666945631887e-09,1.51427439400327e-07
B1,MAT-dcb72175-bc2b-4d52-9554-88cc645c2b05,367.320326816316,650865,0.66606147008107,0.0475883942466052,3.108978439871e-05,2.07077075011083e-05,0.95,0.632758396577016,0.049968910215602,0.0332823657965529,1.4465055011589e-18,9.63461580582252e-19
D1,MAT-4e90a53a-f0ec-483d-b1b9-cf252f49c04a,321.441143860789,620528,11.933738529916,0.691847816168601,0.9094418644973,10.8530414190701,3.3006214355253e-11,3.93887531977949e-10,0.08,0.95469908239328,0.010558135469695,0.125998028058772
R1,MAT-976ba279-5a47-4eae-9f29-37b68d7c0871,334.390082228664,642269.51666667,27.7,1.61171519601146,0.08653390238944,2.39698909618749,0.0044532731867657,0.12335566727341,0.9090128189571,25.1796550851117,5.4666945631887e-09,1.51427439400327e-07
Feed,MAT-8b48a7ff-c28f-4b8f-bac6-050943950ece,298.15,101325,12.5998,0.73939737966736,0.2,2.51996,0.05,0.62999,0.74,9.323852,0.01,0.125998
Recycle,MAT-3ce0ae10-0f11-4e6f-88d1-32b9add72a3d,325.750562992088,430922.5,27.7,1.61171519601146,0.386508132645283,10.7062752742743,0.0044532731867657,0.12335566727341,0.609038588701257,16.8703689070248,5.4666945631887e-09,1.51427439400327e-07
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Reactor Output 2
Target metric: temperature
Observed target value: 325.750562992088
Required target value: >= 337.0381433739567
```

## Allowed Repair Actions

- `Cooler` / GUID `RESF-0e30f3a3-019c-4936-9359-414547f28fbf`: `thermal_specification/outlet_temperature` (unit: `K`)
- `pump` / GUID `BB-93a5650f-6358-4ec5-a663-352683b8b162`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `Heater` / GUID `AQ-6c7ba34b-bb9b-4a44-805a-1db1e6e9b834`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
