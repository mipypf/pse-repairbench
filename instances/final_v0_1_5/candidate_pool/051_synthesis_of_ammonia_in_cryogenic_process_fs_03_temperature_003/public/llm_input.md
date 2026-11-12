# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-10`
- Required target: `mass_flow at most 0.00810233031289`
- Faulty observed target value: `0.0270061941994002`

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
    "flash_temperature": 208.15,
    "guid": "SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 1500000,
      "separator_specification/temperature": 208.15
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
    "flash_temperature": 238.15,
    "guid": "SEP-e526b085-c1b6-4412-953b-befa1a9e4ce4",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/temperature": 238.15
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
S-11,MAT-285cb3bd-fb74-43f3-b643-b1b96cc37228,208.15,1500000,24.088932085413,0.454029016213687,0.0128506459201999,0.309558336825384,0.299805130240999,7.22198542123383,0.311845548871343,7.51202624790013,0.375498673781483,9.04536205088481,1.18597574746744e-09,2.85688892356901e-08
S-22,MAT-8a67c0db-a31b-40e1-89b8-a5122b4bec4e,235.726775502273,200000,637.493379819153,10.8762770392701,0.998166232312377,636.324365058167,0.00135153252870955,0.861593039662577,9.51229825548955e-07,0.000606402716473986,0.000481283929085987,0.306815318605667,1.86747251686179e-15,1.1905013664936e-12
S-21,MAT-6567acd2-cf15-4019-9a28-2fbc9357cf9e,235.726775502273,200000,13.1684890643535,0.321279344947452,0.413214399744278,5.4414093042659,0.338721377075917,4.46044874988696,0.0107276335348904,0.141266724890595,0.237336589615767,3.12536428492618,2.91479112782691e-11,3.83833950916631e-10
S-20,MAT-29553b4f-03da-40cd-b729-7e38f0cb410e,235.726775502273,200000,650.661868883506,11.1975581790514,0.98632740283376,641.765631258829,0.00817955466394593,5.32212432427786,0.000218048357504316,0.141875751800737,0.00527499414419842,3.43223754821369,5.91753721915772e-13,3.85031582620487e-10
S-05,MAT-8a3f4d4f-22bd-439a-adbf-ca848e6346f3,323.154306049684,9000000,1075.10791352421,18.5416156107601,0.964511308914048,1036.95374089709,0.0147174831204864,15.8228825699939,0.00720069799813323,7.74152740069098,0.0135705099401792,14.5897626272456,2.71528832739181e-11,2.91922796827886e-08
S-18,MAT-3c0de8c0-9c4d-42ae-a114-1b67c4e18e1a,323.15,9000000,398.792758347955,6.86301952909602,0.98632740283376,393.34022561025,0.00817955466394593,3.26194716649288,0.000218048357504316,0.0869561059423874,0.00527499414419842,2.1036294650342,5.91753721915772e-13,2.3598709902546e-10
S-17,MAT-9a5fba2f-2b28-4980-b058-c0ea540b8569,323.15,9000000,398.792758347955,6.86301952909602,0.98632740283376,393.34022561025,0.00817955466394593,3.26194716649288,0.000218048357504316,0.0869561059423874,0.00527499414419842,2.1036294650342,5.91753721915772e-13,2.3598709902546e-10
S-16,MAT-11ca46a1-8306-4987-8ee0-fafa9c4c73ee,240.129430890638,9000000,398.792758347955,6.86301952909602,0.98632740283376,393.34022561025,0.00817955466394593,3.26194716649288,0.000218048357504316,0.0869561059423874,0.00527499414419842,2.1036294650342,5.91753721915772e-13,2.3598709902546e-10
S-19,MAT-efd98ad5-11a6-41c8-bbfb-704ce24ef8ea,238.15,1500000,650.661868883506,11.1975581790514,0.98632740283376,641.765631258829,0.00817955466394593,5.32212432427786,0.000218048357504316,0.141875751800737,0.00527499414419842,3.43223754821369,5.91753721915772e-13,3.85031582620487e-10
S-15,MAT-336dec11-4c27-4f38-a775-62a7f5701de4,238.15,1500000,398.792758347955,6.86301952909602,0.98632740283376,393.34022561025,0.00817955466394593,3.26194716649288,0.000218048357504316,0.0869561059423874,0.00527499414419842,2.1036294650342,5.91753721915772e-13,2.3598709902546e-10
S-01,MAT-5b9d6902-e4a5-461e-ba47-db69fd39a412,323.15,9000000,1388.88888888889,12.1873219444445,0,0,0.01,13.8888888888889,0.74,1027.77777777778,0.01,13.8888888888889,0.24,333.333333333334
S-03,MAT-3450e369-7948-4509-b8d3-194eb9db1db0,323.15,9000000,69.4812324119521,0.955881608567944,0.330321402882011,22.9511381642871,0.123149845293677,8.55660302234591,0.396061885329891,27.5188679041221,0.1504668645399,10.4546231853945,1.95452093060402e-09,1.35802523033323e-07
S-04,MAT-06ccd223-a4f1-499f-90d0-0a087e44f3cb,323.15,9000000,676.090356812992,11.6747051374463,0.951637986306553,643.393265718794,0.0185746360520853,12.5581323161258,0.011321816615544,7.65457103537441,0.0184655609829505,12.484387713715,4.28672529047046e-11,2.89821363119345e-08
S-06,MAT-2d628033-a1c1-49cd-9f43-1390f4a5591c,301.529656322851,1500000,1075.10791352421,18.5416156107601,0.964511308914048,1036.95374089709,0.0147174831204864,15.8228825699939,0.00720069799813323,7.74152740069098,0.0135705099401792,14.5897626272456,2.71528832739181e-11,2.91922796827886e-08
S-07,MAT-7767eccd-baaa-42b1-b6c1-fec751c049d3,238.15,1500000,1075.10791352421,18.5416156107601,0.964511308914048,1036.95374089709,0.0147174831204864,15.8228825699939,0.00720069799813323,7.74152740069098,0.0135705099401792,14.5897626272456,2.71528832739181e-11,2.91922796827886e-08
S-09,MAT-f45418a5-4b6a-4703-baf7-7954dae45958,238.15,1500000,25.6532862927483,0.481035236376072,0.0720946575268132,1.84946488971298,0.282160236239711,7.23833732068679,0.292835369036568,7.51218955853767,0.352909736083237,9.05329449524151,1.11367159643566e-09,2.8569336299466e-08
S-08,MAT-da108e3c-6dee-4710-bc72-df8b24132c36,238.15,1500000,1049.45462723146,18.0605777081474,0.98632740283376,1035.10585686908,0.00817955466394593,8.58407149077074,0.000218048357504316,0.228831857743125,0.00527499414419842,5.53586701324789,5.91753721915772e-13,6.21018681645946e-10
S-10,MAT-fd0ef933-59a8-4ad2-a260-1f404c3a37a5,208.15,1500000,1.56435420733524,0.0270061941994002,0.984382222535976,1.53992247145017,0.0104497806721997,0.0163471583602861,0.000101129717816931,0.000158202699553542,0.00506686707373367,0.00792637482480368,2.73362655797702e-13,4.27636020725471e-13
S-12,MAT-9286e475-040c-4236-8942-be10d4a46510,354.695728358338,9000000,24.088932085413,0.454029016213687,0.0128506459201999,0.309558336825384,0.299805130240999,7.22198542123383,0.311845548871343,7.51202624790013,0.375498673781483,9.04536205088481,1.18597574746744e-09,2.85688892356901e-08
S-13,MAT-ebedbc29-9b0c-4301-a194-e7e8fe722681,323.15,9000000,24.088932085413,0.454029016213687,0.0128506459201999,0.309558336825384,0.299805130240999,7.22198542123383,0.311845548871343,7.51202624790013,0.375498673781483,9.04536205088481,1.18597574746744e-09,2.85688892356901e-08
S-14,MAT-a72f8b87-748a-40b8-8241-665f96d8f0f2,323.15,9000000,24.088932085413,0.454029016213687,0.0128506459201999,0.309558336825384,0.299805130240999,7.22198542123383,0.311845548871343,7.51202624790013,0.375498673781483,9.04536205088481,1.18597574746744e-09,2.85688892356901e-08
S-02,MAT-0983118c-fa43-46b3-8c87-82bfc5ae3c89,323.06097909076,9000000,1412.98550457634,12.6416070681386,0.000219156935986535,0.309665573776339,0.0149437156711319,21.1152536278197,0.732695276108516,1035.2878044129,0.0162347366825711,22.9394476030868,0.235907114601795,333.333333358767
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-10
Target metric: mass_flow
Observed target value: 0.0270061941994002
Required target value: <= 0.00810233031289103
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
