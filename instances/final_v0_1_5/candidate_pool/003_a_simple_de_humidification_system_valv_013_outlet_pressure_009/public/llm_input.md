# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `dehumidified air`
- Required target: `pressure at least 85000.0221346`
- Faulty observed target value: `50000.013020329`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 174999.947483059,
    "guid": "VALV-49ce35e1-cadd-4096-b355-b7c6420e2da6",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 50000.013020329
    },
    "outlet_pressure": 50000.013020329,
    "outlet_temperature": 293.15,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-013",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-e74a87cd-e036-442f-bfba-e6c8fd6f22dd",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 293.15
    },
    "outlet_temperature": 293.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "cooler",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 174999.947483059,
    "guid": "COMP-b56262ab-52c8-45e2-8bd6-a98b7d39362c",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 274999.973523717
    },
    "outlet_temperature": 355.154570004591,
    "p_out": 274999.973523717,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "compressor",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,air_mole_fraction,air_molar_flow,water_mole_fraction,water_molar_flow
dehumidified air,MAT-dab6b1b5-b92b-4f29-be0e-d24315e02e67,293.15,50000.013020329,34.4781300402968,0.995282783031731,0.991509867677522,34.1854061540231,0.00849013232247793,0.292723886273721
heavy liquid,MAT-b0b3121f-16a8-481b-af4d-9a6d426994ab,293.15,274999.973523717,0,0,0,0,0,0
removed water,MAT-46d048d4-755a-4fb7-98aa-d4b4c22af3eb,293.15,274999.973523717,0.261408179085806,0.00471723850625351,0.00278568562639213,0.000728201007100668,0.997214314373608,0.260679978078705
gas stream,MAT-59aee98e-86db-4c60-b2c2-5d462ce8958c,293.15,274999.973523717,34.4781300402968,0.995282783031731,0.991509867677522,34.1854061540231,0.00849013232247793,0.292723886273721
compressed humid air,MAT-199b68dd-42bf-40b7-9c4f-068753b12ee2,423.371448613701,274999.973523717,34.7395382193826,1,0.984069856406974,34.1861323871925,0.0159301435930262,0.553405832190187
Feed,MAT-9cce4842-de99-4d92-9cdb-6c37a91f10e0,293.15,100000.026040658,34.7395382193826,1,0.984069856406974,34.1861323871925,0.0159301435930262,0.553405832190187
cooled air,MAT-eaa4b644-d703-4bcd-9871-65999ed88cfd,293.15,274999.973523717,34.7395382193826,1,0.984069856406974,34.1861323871925,0.0159301435930262,0.553405832190187
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: dehumidified air
Target metric: pressure
Observed target value: 50000.013020329
Required target value: >= 85000.0221345593
```

## Allowed Repair Actions

- `VALV-013` / GUID `VALV-49ce35e1-cadd-4096-b355-b7c6420e2da6`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `cooler` / GUID `RESF-e74a87cd-e036-442f-bfba-e6c8fd6f22dd`: `thermal_specification/outlet_temperature` (unit: `K`)
- `compressor` / GUID `COMP-b56262ab-52c8-45e2-8bd6-a98b7d39362c`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
