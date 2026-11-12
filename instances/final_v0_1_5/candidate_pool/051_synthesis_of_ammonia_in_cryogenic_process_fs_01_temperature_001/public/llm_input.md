# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-10`
- Required target: `mass_flow at most 0.0181124316109`
- Faulty observed target value: `0.060373198526189`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-08371460-cc5b-4824-97db-084b0bd09799",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 7500000,
    "guid": "COMP-34fb4dec-e0e4-4049-8db8-b3f2d85d9861",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 9000000
    },
    "outlet_temperature": 398.521739053952,
    "p_out": 9000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "flash_pressure": 1500000,
    "flash_temperature": 238.15,
    "guid": "SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 1500000,
      "separator_specification/temperature": 238.15
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "FS-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1300000,
    "guid": "VALV-3b0e6130-7ccb-4e28-834d-982064cac0ab",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 200000
    },
    "outlet_pressure": 200000,
    "outlet_temperature": 235.724569984375,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "flash_pressure": 101325,
    "flash_temperature": 258.15,
    "guid": "SEP-e526b085-c1b6-4412-953b-befa1a9e4ce4",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/temperature": 258.15
    },
    "override_p": "false",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/temperature"
    ],
    "tag": "FS-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 7500000,
    "guid": "VALV-aee346c3-282e-418d-8f72-9fc2d9e5d592",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 1500000
    },
    "outlet_pressure": 1500000,
    "outlet_temperature": 301.52179111604,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-5099e0d5-1132-46d2-9178-74973f950d06",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 238.15
    },
    "outlet_temperature": 238.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 7500000,
    "guid": "COMP-c09d247d-1b08-4373-8e69-a2cc10175777",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 9000000
    },
    "outlet_temperature": 240.129459890534,
    "p_out": 9000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-b0072ae5-268e-446a-8821-bf05980a683f",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,ammonia_mole_fraction,ammonia_molar_flow,argon_mole_fraction,argon_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methane_mole_fraction,methane_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow
S-11,MAT-285cb3bd-fb74-43f3-b643-b1b96cc37228,238.15,1500000,27.0332345128763,0.530320015612322,0.0721995090122432,1.95178625884249,0.307215173977849,8.30501984405727,0.273809237686807,7.40194933417933,0.346776077015156,9.37447901340596,2.30794444447121e-09,6.23912034100802e-08
S-22,MAT-8a67c0db-a31b-40e1-89b8-a5122b4bec4e,247.833265181602,200000,617.389841527371,10.522180951624,0.99922919260253,616.913952870398,0.000554742731864801,0.34249252731447,7.33795223915047e-07,0.000453037717006453,0.000215330870378069,0.132943091938667,3.24135761813176e-15,2.0011812661919e-12
S-21,MAT-6567acd2-cf15-4019-9a28-2fbc9357cf9e,247.833265181602,200000,30.3076943662136,0.612022005810213,0.745554845970465,22.5960484049223,0.146440351687206,4.43826942181667,0.00614764945901649,0.18632108087449,0.101857152845839,3.0870554574644,3.74735757336227e-11,1.1357376801438e-09
S-20,MAT-29553b4f-03da-40cd-b729-7e38f0cb410e,247.833265181602,200000,647.697535893584,11.1342043415969,0.98735884326904,639.509889828097,0.00738126328477086,4.78082604132787,0.000288370433384063,0.186776819127422,0.00497152301104844,3.22004320389433,1.75661517957175e-12,1.13775532332189e-09
S-05,MAT-8a3f4d4f-22bd-439a-adbf-ca848e6346f3,323.155020388672,9000000,1075.21132718362,18.5490912267897,0.964342866184375,1036.87237301016,0.0149252084851923,16.0477532238558,0.00716543680858082,7.70435882080453,0.0135664884621105,14.586842064567,5.97411067971196e-11,6.42343147267492e-08
S-18,MAT-3c0de8c0-9c4d-42ae-a114-1b67c4e18e1a,323.15,9000000,396.975909096068,6.82418975775296,0.98735884326904,391.957674410769,0.00738126328477086,2.93018370274934,0.000288370433384063,0.114476114949065,0.00497152301104844,1.97357486690298,1.75661517957175e-12,6.97333907842449e-10
S-17,MAT-9a5fba2f-2b28-4980-b058-c0ea540b8569,323.15,9000000,396.975909096068,6.82418975775296,0.98735884326904,391.957674410769,0.00738126328477086,2.93018370274934,0.000288370433384063,0.114476114949065,0.00497152301104844,1.97357486690298,1.75661517957175e-12,6.97333907842449e-10
S-16,MAT-11ca46a1-8306-4987-8ee0-fafa9c4c73ee,260.427242538793,9000000,396.975909096068,6.82418975775296,0.98735884326904,391.957674410769,0.00738126328477086,2.93018370274934,0.000288370433384063,0.114476114949065,0.00497152301104844,1.97357486690298,1.75661517957175e-12,6.97333907842449e-10
S-19,MAT-efd98ad5-11a6-41c8-bbfb-704ce24ef8ea,258.15,1500000,647.697535893584,11.1342043415969,0.98735884326904,639.509889828097,0.00738126328477086,4.78082604132787,0.000288370433384063,0.186776819127422,0.00497152301104844,3.22004320389433,1.75661517957175e-12,1.13775532332189e-09
S-15,MAT-336dec11-4c27-4f38-a775-62a7f5701de4,258.15,1500000,396.975909096068,6.82418975775296,0.98735884326904,391.957674410769,0.00738126328477086,2.93018370274934,0.000288370433384063,0.114476114949065,0.00497152301104844,1.97357486690298,1.75661517957175e-12,6.97333907842449e-10
S-01,MAT-5b9d6902-e4a5-461e-ba47-db69fd39a412,323.15,9000000,1388.88888888889,12.1873219444445,0,0,0.01,13.8888888888889,0.74,1027.77777777778,0.01,13.8888888888889,0.24,333.333333333334
S-03,MAT-3450e369-7948-4509-b8d3-194eb9db1db0,323.15,9000000,70.4645247967233,0.98379703909017,0.330709294784212,23.303273302829,0.128109626523865,9.02718395488982,0.389985096347756,27.480114491949,0.151195978064942,10.6539527455219,4.27922510007575e-09,3.01533563175048e-07
S-04,MAT-06ccd223-a4f1-499f-90d0-0a087e44f3cb,323.15,9000000,678.003911953311,11.7211602627631,0.950848473898942,644.678984978319,0.0193597691094129,13.1259991906948,0.0111940210258319,7.58959004600164,0.01859773587153,12.6093376743717,9.42829631045751e-11,6.39242178154516e-08
S-06,MAT-2d628033-a1c1-49cd-9f43-1390f4a5591c,301.499142188894,1500000,1075.21132718362,18.5490912267897,0.964342866184375,1036.87237301016,0.0149252084851923,16.0477532238558,0.00716543680858082,7.70435882080453,0.0135664884621105,14.586842064567,5.97411067971196e-11,6.42343147267492e-08
S-07,MAT-7767eccd-baaa-42b1-b6c1-fec751c049d3,238.15,1500000,1075.21132718362,18.5490912267897,0.964342866184375,1036.87237301016,0.0149252084851923,16.0477532238558,0.00716543680858082,7.70435882080453,0.0135664884621105,14.586842064567,5.97411067971196e-11,6.42343147267492e-08
S-09,MAT-f45418a5-4b6a-4703-baf7-7954dae45958,258.15,1500000,30.5378821939651,0.590693108786014,0.177036559624902,5.40632160185014,0.272980541560242,8.33624761941148,0.242408881303841,7.40265386002755,0.307574015467801,9.39265905028052,2.04321353402496e-09,6.23954141991693e-08
S-08,MAT-da108e3c-6dee-4710-bc72-df8b24132c36,258.15,1500000,1044.67344498965,17.9583940993499,0.98735884326904,1031.46756423887,0.00738126328477086,7.71100974407721,0.000288370433384063,0.301252934076488,0.00497152301104844,5.19361807079731,1.75661517957175e-12,1.83508923116434e-09
S-10,MAT-fd0ef933-59a8-4ad2-a260-1f404c3a37a5,238.15,1500000,3.50464768108885,0.060373198526189,0.985689690497719,3.45449508807602,0.00891414015925943,0.0312409206380496,0.000204466440779629,0.000716582837538818,0.00519170290101121,0.0181950895329312,1.23049157827307e-12,4.31243945639407e-12
S-12,MAT-9286e475-040c-4236-8942-be10d4a46510,400.109082920431,9000000,27.0332345128763,0.530320015612322,0.0721995090122432,1.95178625884249,0.307215173977849,8.30501984405727,0.273809237686807,7.40194933417933,0.346776077015156,9.37447901340596,2.30794444447121e-09,6.23912034100802e-08
S-13,MAT-ebedbc29-9b0c-4301-a194-e7e8fe722681,323.15,9000000,27.0332345128763,0.530320015612322,0.0721995090122432,1.95178625884249,0.307215173977849,8.30501984405727,0.273809237686807,7.40194933417933,0.346776077015156,9.37447901340596,2.30794444447121e-09,6.23912034100802e-08
S-14,MAT-a72f8b87-748a-40b8-8241-665f96d8f0f2,323.15,9000000,27.0332345128763,0.530320015612322,0.0721995090122432,1.95178625884249,0.307215173977849,8.30501984405727,0.273809237686807,7.40194933417933,0.346776077015156,9.37447901340596,2.30794444447121e-09,6.23912034100802e-08
S-02,MAT-0983118c-fa43-46b3-8c87-82bfc5ae3c89,322.983612450855,9000000,1415.88411346508,12.7160040008976,0.00137651135292105,1.94898055660525,0.0156465669122186,22.1537255212787,0.731122228113973,1035.18434778777,0.0164305298838838,23.2637262384043,0.235424163737003,333.333333361025
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-10
Target metric: mass_flow
Observed target value: 0.060373198526189
Required target value: <= 0.018112431610927675
```

## Allowed Repair Actions

- `COOL-02` / GUID `RESF-08371460-cc5b-4824-97db-084b0bd09799`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-01` / GUID `COMP-34fb4dec-e0e4-4049-8db8-b3f2d85d9861`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `FS-03` / GUID `SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f`: `separator_specification/pressure` (unit: `Pa`)
- `FS-03` / GUID `SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f`: `separator_specification/temperature` (unit: `K`)
- `VALV-02` / GUID `VALV-3b0e6130-7ccb-4e28-834d-982064cac0ab`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `FS-01` / GUID `SEP-e526b085-c1b6-4412-953b-befa1a9e4ce4`: `separator_specification/temperature` (unit: `K`)
- `VALV-01` / GUID `VALV-aee346c3-282e-418d-8f72-9fc2d9e5d592`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-01` / GUID `RESF-5099e0d5-1132-46d2-9178-74973f950d06`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-02` / GUID `COMP-c09d247d-1b08-4373-8e69-a2cc10175777`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HEAT-01` / GUID `AQ-b0072ae5-268e-446a-8821-bf05980a683f`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
