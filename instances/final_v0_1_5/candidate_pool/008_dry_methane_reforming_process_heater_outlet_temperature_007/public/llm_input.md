# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Cooler_out`
- Required target: `Carbon monoxide mass_fraction at least 0.878114568403`
- Faulty observed target value: `not available in stream table`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-090744d3-7826-4f4a-8dc2-2e7b1ed39f04",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-169baed2-3697-4a5a-b20b-5aa520b605cc",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 1070
    },
    "outlet_temperature": 1070,
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
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,carbon dioxide_mole_fraction,carbon dioxide_molar_flow,carbon monoxide_mole_fraction,carbon monoxide_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methane_mole_fraction,methane_molar_flow,water_mole_fraction,water_molar_flow
Cooler_out,MAT-a54bc1dc-48c0-4f55-8f5f-7c0e4298f63f,323.15,101325,1069.71133036851,16.6810597980152,0.0193509135546709,20.699891482413,0.480649085406627,514.155772590729,0.480649085406627,514.155772590729,0.0193509156320749,20.6998937046355,0,0
Reactor_in,MAT-b4ec0d6f-b345-411a-84b1-845f9dccbb51,1070,101325,555.555557777777,16.6812500356511,0.499999998,277.777777777777,0,0,0,0,0.500000002,277.77778,0,0
Product,MAT-b859355b-17c3-49bd-beed-df044e031bb7,1070,101325,1069.71133036851,16.6810597980152,0.0193509135546709,20.699891482413,0.480649085406627,514.155772590729,0.480649085406627,514.155772590729,0.0193509156320749,20.6998937046355,0,0
Reactor_out,MAT-1598ba22-e692-43f4-a636-7a1bf2034b9a,1070,101325,0,0,0,0,0,0,0,0,0,0,0,0
Mixer_out,MAT-51df4690-c14c-4b85-ba3e-e96a707f7405,323.15,101325,555.555557777777,16.6812500356511,0.499999998,277.777777777777,0,0,0,0,0.500000002,277.77778,0,0
Carbon-di-oxide,MAT-091fbf4b-b85b-4f5a-9382-df75928f4668,323.15,101325,277.777777777777,12.2248611111111,1,277.777777777777,0,0,0,0,0,0,0,0
Methane,MAT-23729c45-2c8e-404b-a68c-9deb65afe758,323.15,101325,277.77778,4.45638892454,0,0,0,0,0,0,1,277.77778,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Cooler_out
Target metric: Carbon monoxide mass_fraction
Observed target value: 0.863344617467282
Required target value: >= 0.8781145684030598
```

## Allowed Repair Actions

- `Cooler` / GUID `RESF-090744d3-7826-4f4a-8dc2-2e7b1ed39f04`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Heater` / GUID `AQ-169baed2-3697-4a5a-b20b-5aa520b605cc`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
