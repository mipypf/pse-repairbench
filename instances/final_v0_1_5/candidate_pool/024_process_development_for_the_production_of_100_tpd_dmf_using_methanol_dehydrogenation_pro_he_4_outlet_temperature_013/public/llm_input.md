# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S19`
- Required target: `molar_flow at most 21.7629188519`
- Faulty observed target value: `36.4054931006194`

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
      "thermal_specification/outlet_temperature": 393.15
    },
    "outlet_temperature": 393.15,
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
      "thermal_specification/outlet_temperature": 367.15
    },
    "outlet_temperature": 367.15,
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
S24,MAT-7dd5e878-41a0-4af9-a8c0-b3a2eae84533,298.15,101325,15.2600451773465,1.1064707768754,3.19318471293493e-07,4.87281429789992e-06,0,0,0.013,0.198380587305504,1.18231371034355e-05,0.000180421606336387,0.986273132517854,15.0505725594255
S21,MAT-f0130f75-ad0c-4d27-920d-abe2ee2127c4,383.15,101325,19.9264711785342,1.27554272440902,9.36974737584297e-05,0.00186706001034881,0,0,0.22,4.38382365927752,0.000652487775918993,0.0130017788611957,0.778723689734899,15.5172151595443
S17,MAT-0970798e-03c2-420f-8f63-fa251f5a225f,364.570144042268,200000,56.3342135082599,2.58727944379854,0.0025,0.14083553377065,0,0,0.657780318798892,37.055536920748,0.00587771291998153,0.331116334574497,0.333614526569435,18.7939119692196
S16,MAT-1cd7a802-0929-44f4-bd38-99c0f3e384ea,331.337792038582,100000,183.896306311132,6.30655182547717,0.0215159324549386,3.95670050530302,0,0,0.924072596849734,169.933537324002,0.0204811493255241,3.7664077099706,0.034,6.25247441457848
S15,MAT-2d0e2da0-f064-43a7-b819-23553cbb2cf1,367.15,300000,240.217707069445,8.89339186800012,0.0170564460496943,4.09726036081124,0,0,0.861623553311989,206.977234333633,0.0170564513111254,4.09726162470016,0.104263549327191,25.0459507502999
S18,MAT-7d77af43-0c59-4fac-84c3-d6c81ba829b8,345.423341084171,100000,56.3342135082599,2.58727944379854,0.0025,0.14083553377065,0,0,0.657780318798892,37.055536920748,0.00587771291998153,0.331116334574497,0.333614526569435,18.7939119692196
S12,MAT-32aba7d0-bb43-4062-99a2-eccfd87fee18,393.15,300000,240.217707069445,8.89329969890136,0.121319995376886,29.1432111111111,0,0,0.757360003984798,181.931283583333,0.121320000638317,29.143212375,0,0
S13,MAT-ec0c658c-cd4d-48e9-ae01-1431babdc231,429.358017285242,300000,0,0,0,0,0,0,0,0,0,0,0,0
S14,MAT-8c3fbd41-a2af-4129-b318-790b2595d444,429.358017285242,300000,240.217707069445,8.89339186800012,0.0170564460496943,4.09726036081124,0,0,0.861623553311989,206.977234333633,0.0170564513111254,4.09726162470016,0.104263549327191,25.0459507502999
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
S19,MAT-e38b7663-c341-46d6-bfa7-21fe81dd21b3,338.151450016944,101325,36.4054931006194,1.31165568177993,0.00381700333137212,0.138959888445309,0,0,0.897383665418747,32.6696948400108,0.00873755238191662,0.318094902956167,0.09,3.27649437905575
S20,MAT-6ff3d728-b380-45fe-9ffa-8dc0ea65e854,372.773566865227,101325,19.9264711785342,1.27554272440902,9.36974737584297e-05,0.00186706001034881,0,0,0.22,4.38382365927752,0.000652487775918993,0.0130017788611957,0.778723689734899,15.5172151595443
S22,MAT-9cfd1f92-6d81-454f-9ccd-f459c3301501,339.652567229308,101325,4.66676921654169,0.169084382765274,0.000399060693467968,0.00186232415980809,0,0,0.896926913853718,4.18575091106027,0.00274757539315872,0.0128223002649205,0.1,0.466676921654169
S23,MAT-6d5a8006-7111-410b-beeb-f711a6e9de62,418.920501877898,101325,15.2600451773465,1.1064707768754,3.19318471293493e-07,4.87281429789992e-06,0,0,0.013,0.198380587305504,1.18231371034355e-05,0.000180421606336387,0.986273132517854,15.0505725594255
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S19
Target metric: molar_flow
Observed target value: 36.4054931006194
Required target value: <= 21.762918851866182
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
