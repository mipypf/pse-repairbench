# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Coolent out2`
- Required target: `temperature at least 168.178856157`
- Faulty observed target value: `151.96473339204`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1800000,
    "guid": "COMP-b362cfc2-bfe6-4cab-a2f0-dd163ad5a0e6",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 1000000
    },
    "outlet_temperature": 549.783873425893,
    "p_out": 1000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "Compressor 1",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 20684.2,
    "guid": "RESF-672e856b-ca14-453d-89a3-94f89d3d75f4",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 225.15
    },
    "outlet_temperature": 225.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler 1",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 4898675,
    "guid": "COMP-fc67a970-15ae-4d67-b3e5-db55fafcc287",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 5000000
    },
    "outlet_temperature": 1060.33024437352,
    "p_out": 5000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "Compressor2",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 20684.2,
    "guid": "RESF-995c7dfb-cd32-45ce-b974-806ee098a74a",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 143.15
    },
    "outlet_temperature": 143.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "cooler 2",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 34473.7,
    "guid": "RESF-350e26f4-01a4-4be1-85dd-25edca995f65",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 143.15
    },
    "outlet_temperature": 143.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "cooler 3",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,carbon dioxide_mole_fraction,carbon dioxide_molar_flow,methane_mole_fraction,methane_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow
coolent 3,MAT-b5cc062d-5567-4693-a1a4-63dddb99e99e,143.150000500774,4894842.1,74.3691709443813,2.08333333333333,0,0,0,0,1,74.3691709443813
Cold Biogas2,MAT-3b00487e-dd6f-46f9-94a6-741740f2910e,153.15,879315.8,32.7073035304279,0.890596195045795,0.4,13.0829214121712,0.6,19.6243821182567,0,0
coolent2,MAT-45c08a7c-6b4e-4f33-8fb8-b5092fbc0392,143.150000319494,4979315.8,74.3691709443813,2.08333333333333,0,0,0,0,1,74.3691709443813
coolent1,MAT-94174c2d-be53-468b-b28d-0736b0aa7694,1060.3752888147,5000000,74.3691709443813,2.08333333333333,0,0,0,0,1,74.3691709443813
Coolent out,MAT-aee28644-dbcb-417f-9ad9-6657d0e02a38,224.150000031693,4929315.8,74.3691709443813,2.08333333333333,0,0,0,0,1,74.3691709443813
Coolent(N2)In,MAT-860d25a8-27a9-4444-93e2-b3f01c143ac9,298.15,101325,74.3691709443813,2.08333333333333,0,0,0,0,1,74.3691709443813
Cold biogas,MAT-98e6b16c-e867-489c-a4a9-0c5a3273a589,171.732376718663,929315.8,32.7073035304279,0.890596195045795,0.4,13.0829214121712,0.6,19.6243821182567,0,0
cool biogas,MAT-871acf59-b459-4c99-a20c-84a62465dfd5,225.15,979315.8,32.7073035304279,0.890596195045795,0.4,13.0829214121712,0.6,19.6243821182567,0,0
Biogas Compressed ,MAT-2f258861-a506-435e-b852-4d622c2d374e,471.799752411206,1000000,32.7073035304279,0.890596195045795,0.4,13.0829214121712,0.6,19.6243821182567,0,0
Bio Gas feed,MAT-80f0616a-240e-426e-ade2-5fefbfd0b968,308.15,200000,32.7073035304279,0.890596195045795,0.4,13.0829214121712,0.6,19.6243821182567,0,0
Coolent out2,MAT-9e03367b-74e4-44ae-b131-20c0bcf59d98,151.96473339204,4844842.1,74.3691709443813,2.08333333333333,0,0,0,0,1,74.3691709443813
Biogas to cryogenic column,MAT-8b570fe7-4846-4331-8cbb-6f01bfa9a950,155.061642001289,1009315.8,32.7073035304279,0.890596195045795,0.4,13.0829214121712,0.6,19.6243821182567,0,0
Liquid CO2,MAT-2deec42d-c598-41af-be16-f36dff3f102b,227.234952760629,800000,13.082921412171,0.575702371058504,0.99980743196725,13.080402059732,0.00019256803274503,0.0025193524388996,0,0
Liquid BioMethane,MAT-eb499dc5-a8b3-43ee-b9fa-0b318e4ddcfd,111.396176501239,100000,19.624382118257,0.314904019731167,0.00014695572447095,0.00288391529148321,0.99985304427553,19.6214982029655,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Coolent out2
Target metric: temperature
Observed target value: 151.96473339204
Required target value: >= 168.1788561568457
```

## Allowed Repair Actions

- `Compressor 1` / GUID `COMP-b362cfc2-bfe6-4cab-a2f0-dd163ad5a0e6`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `Cooler 1` / GUID `RESF-672e856b-ca14-453d-89a3-94f89d3d75f4`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Compressor2` / GUID `COMP-fc67a970-15ae-4d67-b3e5-db55fafcc287`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `cooler 2` / GUID `RESF-995c7dfb-cd32-45ce-b974-806ee098a74a`: `thermal_specification/outlet_temperature` (unit: `K`)
- `cooler 3` / GUID `RESF-350e26f4-01a4-4be1-85dd-25edca995f65`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
