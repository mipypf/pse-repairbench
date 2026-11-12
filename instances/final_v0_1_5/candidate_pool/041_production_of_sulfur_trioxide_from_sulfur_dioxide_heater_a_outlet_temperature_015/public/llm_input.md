# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-7`
- Required target: `Sulfur trioxide mass_fraction at most 0.0793425701186`
- Faulty observed target value: `not available in stream table`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-727d72ba-7acc-4616-aaee-ca7f542c06f9",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 348.15
    },
    "outlet_temperature": 348.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler-A",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-c9c04177-3117-45f9-aaa2-5ea5bb43091b",
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
    "guid": "AQ-d4e49370-0c0b-4353-bccd-09e4dfc751c5",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298.15
    },
    "outlet_temperature": 298.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Heater-B",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-bda0664c-46b4-4fdd-a319-72ad4dfdb941",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 803.15
    },
    "outlet_temperature": 803.15,
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
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,oxygen_mole_fraction,oxygen_molar_flow,sulfur dioxide_mole_fraction,sulfur dioxide_molar_flow,sulfur trioxide_mole_fraction,sulfur trioxide_molar_flow
S-6,MAT-9b4d3ef7-a185-45bf-8d3c-03a6ad2ccbe6,315.78875133615,101325,1.4912108803292,0.119152530160385,3.5931388880254e-16,5.35812780435744e-16,0.0099999999999996,0.0149121088032914,0.99,1.47629877152591
S-5,MAT-779cb403-535e-4d24-b008-5b47987eb68e,289.286075659185,101325,0.34137712704942,0.0197362058645705,0.2714299062143,0.0926599615787312,0.57524911338361,0.196376889664623,0.15332098040209,0.0523402758060659
S-2,MAT-fe0b0356-f266-4a55-91ad-16fb2926a288,803.15,101325,2.59690753104514,0.138888888888889,0.33,0.856979485244896,0.67,1.73992804580024,0,0
S-1,MAT-4c428553-3d20-466f-9f12-c3767ca0f883,298.15,101325,2.59690753104514,0.138888888888889,0.33,0.856979485244896,0.67,1.73992804580024,0,0
S-3V,MAT-b8de84f0-68ec-4586-9ffd-ae017a17327c,803.15,101325,1.83258800737898,0.138888736024984,0.0505623529160039,0.0926599615787321,0.115295416982515,0.211288998467916,0.834142230101481,1.52863904733233
S-3L,MAT-54f84017-88a9-4d50-8890-420e817d6739,803.15,101325,0,0,0,0,0,0,0,0
S-7,MAT-10abdf54-a18b-4248-a76e-ed355555e14f,298.15,101325,0.34137712704942,0.0197362058645705,0.2714299062143,0.0926599615787312,0.57524911338361,0.196376889664623,0.15332098040209,0.0523402758060659
S-8,MAT-ebf20289-cf37-4e7a-91b2-5018ba53c4eb,298.15,101325,1.4912108803292,0.119152530160385,3.5931388880254e-16,5.35812780435744e-16,0.0099999999999996,0.0149121088032914,0.99,1.47629877152591
S-4,MAT-561de80f-c361-4c44-831b-3ecbbd3ab627,348.15,101325,1.83258800737898,0.138888736024984,0.0505623529160039,0.0926599615787321,0.115295416982515,0.211288998467916,0.834142230101481,1.52863904733233
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-7
Target metric: Sulfur trioxide mass_fraction
Observed target value: 0.212327029757977
Required target value: <= 0.07934257011862891
```

## Allowed Repair Actions

- `Cooler-A` / GUID `RESF-727d72ba-7acc-4616-aaee-ca7f542c06f9`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Cooler-B` / GUID `RESF-c9c04177-3117-45f9-aaa2-5ea5bb43091b`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Heater-B` / GUID `AQ-d4e49370-0c0b-4353-bccd-09e4dfc751c5`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Heater-A` / GUID `AQ-bda0664c-46b4-4fdd-a319-72ad4dfdb941`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
