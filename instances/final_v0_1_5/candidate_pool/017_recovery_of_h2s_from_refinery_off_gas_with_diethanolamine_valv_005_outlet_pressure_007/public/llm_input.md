# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `rich amine to amine regeneration unit`
- Required target: `pressure at least 541825.7`
- Faulty observed target value: `318721`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-05d097ea-80fe-4ce6-9956-6d6f699fd155",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 328
    },
    "outlet_temperature": 328,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "lean amine cooler",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1421958,
    "guid": "VALV-f8577b80-daac-4fb5-95da-75a2d40fcc90",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 318721
    },
    "outlet_pressure": 318721,
    "outlet_temperature": 329.077339570873,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-005",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,diethanolamine_mole_fraction,diethanolamine_molar_flow,ethane_mole_fraction,ethane_molar_flow,hydrogen sulfide_mole_fraction,hydrogen sulfide_molar_flow,methane_mole_fraction,methane_molar_flow,water_mole_fraction,water_molar_flow
rich amine,MAT-f1853649-ea1e-4322-bc08-8b199c0cb823,329.01887107114,2059400,176.72782009632,8.49549848251476,0.34023082570355,60.1282521561594,0.019546469677792,3.454404976735,0.011165872503588,1.97332030703255,0.00010438039390278,0.0184469194752335,0.62895245172094,111.153395736878
treated off gas,MAT-26501171-ba14-4428-8d1d-5f3ce19469b8,339.642788550339,2059400,41.380455002448,1.22672451748698,9.2284495732427e-07,3.8187744230793e-05,0.95738032999723,39.6168336656792,0.0082729318582917,0.342337684500358,0.021938286494985,0.907816277136539,0.01240752880416,0.51342918737212
lean amine,MAT-f04d8527-b255-4753-bad8-f6ad0a59913b,328,2059429,171.795115268205,8.333333,0.35,60.1282903438717,0,0,0,0,0,0,0.65,111.666824924333
off gas from process unit,MAT-5e81d862-d814-465d-85d0-7e9958ada890,323.15,539374,46.313159830563,1.38889,0,0,0.93,43.0712386424236,0.05,2.31565799152815,0.02,0.926263196611259,0,0
rich amine to amine regeneration unit,MAT-800055a1-09e5-4daa-acc5-2ef6cb42f782,335.901111986771,318721,176.72782009632,8.49549848251476,0.34023082570355,60.1282521561594,0.019546469677792,3.454404976735,0.011165872503588,1.97332030703255,0.00010438039390278,0.0184469194752335,0.62895245172094,111.153395736878
lean amine from amine regeneraion unit,MAT-2ad60d99-68d7-4362-b3f8-7ef8bdee1ad6,358,2059429,171.795115268205,8.333333,0.35,60.1282903438717,0,0,0,0,0,0,0.65,111.666824924333
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: rich amine to amine regeneration unit
Target metric: pressure
Observed target value: 318721.0
Required target value: >= 541825.7
```

## Allowed Repair Actions

- `lean amine cooler` / GUID `RESF-05d097ea-80fe-4ce6-9956-6d6f699fd155`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-005` / GUID `VALV-f8577b80-daac-4fb5-95da-75a2d40fcc90`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
