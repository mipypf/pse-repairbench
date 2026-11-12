# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S19`
- Required target: `molar_flow at least 13.1033292129`
- Faulty observed target value: `7.54019430398796`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-69f06dce-b24f-4d3c-818d-dfb2533f82fb",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 573.15
    },
    "outlet_temperature": 573.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-1",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 700000,
    "guid": "COMP-8b1e130f-3a4e-4b19-9f43-fd6234ea6287",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 800000
    },
    "outlet_temperature": 298.343260562868,
    "p_out": 800000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "P-1",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-dfbc9bd4-22eb-4b6d-a8c7-a208ea3265d0",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 293.15
    },
    "outlet_temperature": 293.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-2",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": -150000,
    "guid": "COMP-fa6d0bb1-f8bc-440d-9d23-610deb58b70d",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 300000
    },
    "outlet_temperature": 288.173250309271,
    "p_out": 300000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "P-2",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-0d6217fe-a461-4b46-9a9a-12dd0b45dd7d",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 423.15
    },
    "outlet_temperature": 423.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-3",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-f72d1dac-fd59-4703-9d31-e43d1dbafa33",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 397.15
    },
    "outlet_temperature": 397.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-4",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-f6535491-3a9d-46db-9ede-0487a862df69",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298.15
    },
    "outlet_temperature": 298.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-6",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-4487385b-e641-4236-8c37-a088e46bb48b",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 383.15
    },
    "outlet_temperature": 383.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-5",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,dimethylamine_mole_fraction,dimethylamine_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methanol_mole_fraction,methanol_molar_flow,methyl formate_mole_fraction,methyl formate_molar_flow,"n,n-dimethylformamide_mole_fraction","n,n-dimethylformamide_molar_flow"
S24,MAT-7dd5e878-41a0-4af9-a8c0-b3a2eae84533,298.15,101325,14.85024584628,1.07699951274987,1.06667538947741e-06,1.5840391771916e-05,0,0,0.013,0.19305319600164,3.39401018969907e-05,0.000504018857218107,0.986477763513786,14.6494373100682
S21,MAT-f0130f75-ad0c-4d27-920d-abe2ee2127c4,383.15,101325,19.4319189733173,1.24370680532941,0.000311831026579294,0.00605947524185521,0,0,0.22,4.27502217412981,0.00186991785774745,0.0363360922985076,0.7774633397513,15.107604622772
S17,MAT-0970798e-03c2-420f-8f63-fa251f5a225f,377.38365231842,200000,26.9728397322873,1.51784129673924,0.0025,0.0674320993307183,0,0,0.405480217815592,10.9369529297529,0.00647110760304019,0.174544148267189,0.585266054585368,15.7862874910793
S16,MAT-1cd7a802-0929-44f4-bd38-99c0f3e384ea,329.359831058785,100000,213.252490401015,7.37580683734291,0.0283203347712439,6.0393819189582,0,0,0.909897368490209,194.037879839867,0.0278180446744876,5.93226730492116,0.034,7.25058467363449
S15,MAT-2d0e2da0-f064-43a7-b819-23553cbb2cf1,397.15,300000,240.217707069445,8.89338447363713,0.02542109907328,6.1065981305685,0,0,0.853258900288403,204.967896563876,0.0254211043347111,6.10659939445742,0.0958988963036057,23.0366129805426
S18,MAT-7d77af43-0c59-4fac-84c3-d6c81ba829b8,358.085167824335,100000,26.9728397322873,1.51784129673924,0.0025,0.0674320993307183,0,0,0.405480217815592,10.9369529297529,0.00647110760304019,0.174544148267189,0.585266054585368,15.7862874910793
S12,MAT-32aba7d0-bb43-4062-99a2-eccfd87fee18,423.15,300000,240.217707069445,8.89329969890136,0.121319995376886,29.1432111111111,0,0,0.757360003984798,181.931283583333,0.121320000638317,29.143212375,0,0
S13,MAT-ec0c658c-cd4d-48e9-ae01-1431babdc231,455.154307870799,300000,0,0,0,0,0,0,0,0,0,0,0,0
S14,MAT-8c3fbd41-a2af-4129-b318-790b2595d444,455.154307870799,300000,240.217707069445,8.89338447363713,0.02542109907328,6.1065981305685,0,0,0.853258900288403,204.967896563876,0.0254211043347111,6.10659939445742,0.0958988963036057,23.0366129805426
S11,MAT-fc8c4f5c-75c5-448c-99f7-7fa8f04ca870,288.173250359288,300000,240.217707069445,8.89329969890136,0.121319995376886,29.1432111111111,0,0,0.757360003984798,181.931283583333,0.121320000638317,29.143212375,0,0
S10,MAT-800ec42d-80a4-4838-874d-f68122204101,288.219066603079,450000,240.217707069445,8.89329969890136,0.121319995376886,29.1432111111111,0,0,0.757360003984798,181.931283583333,0.121320000638317,29.143212375,0,0
S9,MAT-61c2b477-c29c-4445-816d-632186a72918,279.15,100000,29.1432111111111,1.31377595688889,1,29.1432111111111,0,0,0,0,0,0,0,0
S8,MAT-97a5a03a-450b-4796-80e2-b0679b222144,293.15,800000,211.074495958334,7.57952374201248,0,0,0,0,0.861929257522648,181.931283583333,0.138070742477352,29.143212375,0,0
S7,MAT-5a99c796-a3d8-4e70-8c16-bb2261a20196,293.15,800000,58.3537818194445,0.119423174654197,0,0,0.999095485882856,58.301,0.000779627181408918,0.0454941944444445,0.000124886935735357,0.007287625,0,0
S6,MAT-7bbf8a8d-44cb-412d-80eb-fe4be3a00fa1,293.15,800000,269.428277777778,7.69894691666667,0,0,0.216387828630543,58.301,0.675418257054186,181.976777777778,0.108193914315271,29.1505,0,0
S5,MAT-0e3520ed-a7ee-453b-b10f-e803b7022788,463.215443851149,800000,,8.5475481322502e-16,0,,0,,0,,0,,0,
S4,MAT-c2843c62-d91d-4568-b8ff-78e75cc83da8,463.215443851149,800000,269.428277777778,7.69894691666667,0,0,0.216387828630543,58.301,0.675418257054186,181.976777777778,0.108193914315271,29.1505,0,0
S1,MAT-07df605f-27d2-4243-acdf-3d4fcfbc8bfb,298.15,100000,240.277777777778,7.69894691666667,0,0,0,0,1,240.277777777778,0,0,0,0
S2,MAT-efc0c017-1c52-4764-a2f8-d3d43678528f,298.343260555544,800000,240.277777777778,7.69894691666667,0,0,0,0,1,240.277777777778,0,0,0,0
S3,MAT-41f83f34-6516-4592-9526-f23c942b2ea2,573.150000944486,800000,240.277777777778,7.69894691666667,0,0,0,0,1,240.277777777778,0,0,0,0
S19,MAT-e38b7663-c341-46d6-bfa7-21fe81dd21b3,336.4482479505,101325,7.54019430398796,0.274108082649758,0.00813861145747485,0.061366711754023,0,0,0.883437310715498,6.66128897818744,0.0183277427765411,0.138194741688632,0.09,0.678617487358917
S20,MAT-6ff3d728-b380-45fe-9ffa-8dc0ea65e854,372.392872976851,101325,19.4319189733173,1.24370680532941,0.000311831026579294,0.00605947524185521,0,0,0.22,4.27502217412981,0.00186991785774745,0.0363360922985076,0.7774633397513,15.107604622772
S22,MAT-9cfd1f92-6d81-454f-9ccd-f459c3301501,339.055577453856,101325,4.58201199912328,0.166719622670843,0.0013190890494607,0.00604408185254107,0,0,0.890934133655175,4.08227089083651,0.00782073981442232,0.0358347236717042,0.1,0.458201199912328
S23,MAT-6d5a8006-7111-410b-beeb-f711a6e9de62,418.907712510194,101325,14.85024584628,1.07699951274987,1.06667538947741e-06,1.5840391771916e-05,0,0,0.013,0.19305319600164,3.39401018969907e-05,0.000504018857218107,0.986477763513786,14.6494373100682
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S19
Target metric: molar_flow
Observed target value: 7.54019430398796
Required target value: >= 13.103329212876748
```

## Allowed Repair Actions

- `HE-1` / GUID `AQ-69f06dce-b24f-4d3c-818d-dfb2533f82fb`: `thermal_specification/outlet_temperature` (unit: `K`)
- `P-1` / GUID `COMP-8b1e130f-3a4e-4b19-9f43-fd6234ea6287`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HE-2` / GUID `RESF-dfbc9bd4-22eb-4b6d-a8c7-a208ea3265d0`: `thermal_specification/outlet_temperature` (unit: `K`)
- `P-2` / GUID `COMP-fa6d0bb1-f8bc-440d-9d23-610deb58b70d`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HE-3` / GUID `AQ-0d6217fe-a461-4b46-9a9a-12dd0b45dd7d`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HE-4` / GUID `RESF-f72d1dac-fd59-4703-9d31-e43d1dbafa33`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HE-6` / GUID `RESF-f6535491-3a9d-46db-9ede-0487a862df69`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HE-5` / GUID `RESF-4487385b-e641-4236-8c37-a088e46bb48b`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
