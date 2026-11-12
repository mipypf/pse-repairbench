# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Liquified-N2`
- Required target: `pressure at least 98285.25`
- Faulty observed target value: `91192.5`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2431800,
    "guid": "VALV-66b69073-a1b7-4a35-a1c0-655de7a476f6",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 91192.5
    },
    "outlet_pressure": 91192.5,
    "outlet_temperature": 77.3547221359901,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "Valve",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-cbfcb8b7-ed0a-478c-924c-060f815ed8c3",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 85
    },
    "outlet_temperature": 85,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-9905f77d-baad-43f0-8566-89fd694a4aa0",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 300
    },
    "outlet_temperature": 300,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler-001",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2431800,
    "guid": "COMP-45b1e044-8e2c-4d41-8368-720d4a11aa61",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 2533125
    },
    "outlet_temperature": 1131.98199622228,
    "p_out": 2533125,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "Compressor",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,nitrogen_mole_fraction,nitrogen_molar_flow
Com N2,MAT-000b4dcd-6aca-4190-b3bb-6bb51b6eb027,1145.05494487531,2533125,9.91567708209388,0.277777777777778,1,9.91567708209388
Mixed N2,MAT-c0907dbf-9c7c-44b2-a651-e1568538cd98,300,101325,9.91567708209388,0.277777777777778,1,9.91567708209388
Cooled-N2-S1,MAT-abbf3208-85ab-4c5a-8b61-17f97e2006a9,300.000000000001,2533125,9.91567708209388,0.277777777777778,1,9.91567708209388
N2-Cold,MAT-442ad76e-b5e7-483c-a8a0-3d843d03affe,77.3547226738273,101325,8.03169843649604,0.225,1,8.03169843649604
Cooled-N2-S2,MAT-41e90e45-1b9f-4d90-a28c-5a4d5c276968,185.421880373561,2533125,9.91567708209388,0.277777777777778,1,9.91567708209388
N2-Hot,MAT-38ae9812-c1a9-4673-b02e-77dcf0eed1f6,229.000000000666,101325,8.03169843649604,0.225,1,8.03169843649604
Cooled-N2-S3,MAT-6e1e44b0-7ddc-4d11-9fad-a5526d06267d,84.999999999954,2533125,9.91567708209388,0.277777777777778,1,9.91567708209388
Liquified-N2,MAT-ca61f92a-5afb-4c0c-9849-776ced812743,76.4720963773978,91192.5,9.91567708209388,0.277777777777778,1,9.91567708209388
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Liquified-N2
Target metric: pressure
Observed target value: 91192.5
Required target value: >= 98285.25
```

## Allowed Repair Actions

- `Valve` / GUID `VALV-66b69073-a1b7-4a35-a1c0-655de7a476f6`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `Cooler` / GUID `RESF-cbfcb8b7-ed0a-478c-924c-060f815ed8c3`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Cooler-001` / GUID `RESF-9905f77d-baad-43f0-8566-89fd694a4aa0`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Compressor` / GUID `COMP-45b1e044-8e2c-4d41-8368-720d4a11aa61`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
