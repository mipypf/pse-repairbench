# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Stream 5`
- Required target: `pressure at least 182150`
- Faulty observed target value: `119500`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 812000,
    "guid": "VALV-8482025b-3efb-461d-867f-8ba04f2839e3",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 179000
    },
    "outlet_pressure": 179000,
    "outlet_temperature": 298.447372979067,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-002",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 34000,
    "guid": "AQ-8ab45388-2721-4bff-90dd-9625acb6376c",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 818.15
    },
    "outlet_temperature": 818.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Propylene Heater",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 180000,
    "guid": "AQ-79440953-41de-4c4a-91b4-3d294bf6eec0",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 784.15
    },
    "outlet_temperature": 784.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-009",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,2-chloro prop-1-ene_mole_fraction,2-chloro prop-1-ene_molar_flow,"3,3-dichloro prop-1-ene_mole_fraction","3,3-dichloro prop-1-ene_molar_flow",allyl chloride_mole_fraction,allyl chloride_molar_flow,carbon_mole_fraction,carbon_molar_flow,chlorine_mole_fraction,chlorine_molar_flow,hydrogen chloride_mole_fraction,hydrogen chloride_molar_flow,propylene_mole_fraction,propylene_molar_flow,water_mole_fraction,water_molar_flow
MSTR-014,MAT-db04e9e9-6ebc-4ddd-9166-6a057d0e2650,784.15,187500,,-2.83122722467377e-16,0,,0,,0,,0,,0,,0,,0,,0,
Stream 4,MAT-b2ec8238-4dba-4c2e-95ba-9aecf2798fdd,784.15,187500,27.2080353812715,1.2750713874042,0.0184784033090085,0.502761051020909,0.00469768276602373,0.127814718907963,0.158802516792258,4.32070449551872,0.0144491925599764,0.393134142402642,0,0,0.215574670753267,5.86536326916083,0.587997533819467,15.9982577042605,0,0
Stream 3,MAT-dcd8ed21-203d-4975-bd93-2b74e080995b,784.15,214500,26.5527782,1.2750713874042,0,0,0,0,0,0,0,0,0.206088498867512,5.4722222,0,0,0.793911501132488,21.080556,0,0
MSTR-008,MAT-6e8736d8-9b36-4654-ac57-cfe75f1e89f3,782.735120145387,394500,26.5527782,1.2750713874042,0,0,0,0,0,0,0,0,0.206088498867512,5.4722222,0,0,0.793911501132488,21.080556,0,0
MSTR-005,MAT-71e10823-a6c0-4566-ac87-82d63f48ac06,818.149999999982,145000,21.080556,0.8870634723132,0,0,0,0,0,0,0,0,0,0,0,0,1,21.080556,0,0
MSTR-003,MAT-c44eb5a6-55b9-43bf-a318-52244a4588d6,298.447369050807,179000,21.080556,0.8870634723132,0,0,0,0,0,0,0,0,0,0,0,0,1,21.080556,0,0
Stream 1,MAT-4eddd469-b8e8-4c4f-8f88-f5ab2fc71d35,298.447368930712,1170000,21.080556,0.8870634723132,0,0,0,0,0,0,0,0,0,0,0,0,1,21.080556,0,0
Stream 2,MAT-7cfd555b-06b6-47b2-94a1-8ddbff43466b,298.15,644000,5.4722222,0.388007915091,0,0,0,0,0,0,0,0,1,5.4722222,0,0,0,0,0,0
Boiler Feed Water,MAT-b42ba56e-39a9-40f9-a14f-d22aa01e8870,363.15,600000,18.4845961698585,0.333,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,18.4845961698585
Low Pressure Steam,MAT-de35bb41-2d61-4819-bc66-c5681305bbad,432.049864428986,600000,18.4845961698585,0.333,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,18.4845961698585
MSTR-019,MAT-444d009c-04de-44c3-ba69-fa3421689089,473.15,153500,27.2080353812715,1.2750713874042,0.0184784033090085,0.502761051020909,0.00469768276602373,0.127814718907963,0.158802516792258,4.32070449551872,0.0144491925599764,0.393134142402642,0,0,0.215574670753267,5.86536326916083,0.587997533819467,15.9982577042605,0,0
Cooling Water In,MAT-20b51e4b-c90a-402b-b11f-a359f5d62bcf,303.15,400000,123.024333157831,6.82,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289
Cooling Water Out,MAT-7bf47104-9a44-4f29-ab9f-800dcff4ace6,316.546362269882,400000,123.024333157831,6.82,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289,0.125,15.3780416447289
Stream 5,MAT-6048a708-f08c-4b35-9ff2-cbb57a9e62fc,323.15,119500,27.2080353812715,1.2750713874042,0.0184784033090085,0.502761051020909,0.00469768276602373,0.127814718907963,0.158802516792258,4.32070449551872,0.0144491925599764,0.393134142402642,0,0,0.215574670753267,5.86536326916083,0.587997533819467,15.9982577042605,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Stream 5
Target metric: pressure
Observed target value: 119500.0
Required target value: >= 182150.0
```

## Allowed Repair Actions

- `VALV-002` / GUID `VALV-8482025b-3efb-461d-867f-8ba04f2839e3`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `Propylene Heater` / GUID `AQ-8ab45388-2721-4bff-90dd-9625acb6376c`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HEAT-009` / GUID `AQ-79440953-41de-4c4a-91b4-3d294bf6eec0`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
