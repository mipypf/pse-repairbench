# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `M-24`
- Required target: `temperature at least 69.1759999951`
- Faulty observed target value: `48.1759999450952`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-41d4e056-2c7e-4293-8dba-7823598a05f5",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 48.176
    },
    "outlet_temperature": 48.176,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HT-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1830000,
    "guid": "VALV-291ee0e2-16c7-4dfb-ad0c-d31f54a85262",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 250000
    },
    "outlet_pressure": 250000,
    "outlet_temperature": 247.56412910715,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-04",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "flash_pressure": 2080000,
    "flash_temperature": 323.433,
    "guid": "SEP-2290d065-57bb-4e67-a372-abef9abc5615",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 2080000,
      "separator_specification/temperature": 323.433
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-04",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-89fe8705-44dd-42a7-8fa0-88911851ed82",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-07",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1850000,
    "guid": "COMP-62f2a702-7ce6-4f0b-ba85-c393c1a1917a",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 2100000
    },
    "outlet_temperature": 357.954674190619,
    "p_out": 2100000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-04",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-ddf698d8-5033-43d6-8fba-dff42389b26a",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 247.4136
    },
    "outlet_temperature": 247.4136,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HT-04",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-df10ab4d-9db6-4e28-a15f-fecbdb6bb194",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 171.55
    },
    "outlet_temperature": 171.55,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-04",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2466000,
    "guid": "VALV-73649080-e917-4b58-bc21-c1e5387d5b89",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 34000
    },
    "outlet_pressure": 34000,
    "outlet_temperature": 99.8544926765354,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-e4b14b07-263d-421b-9e14-fe94d9d3fd46",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 254.15
    },
    "outlet_temperature": 254.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2466000,
    "guid": "COMP-6fd39550-a2ef-4147-89df-0440eab9398c",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 2500000
    },
    "outlet_temperature": 337.428779512769,
    "p_out": 2500000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-0c61acce-22f2-4d7b-8a6f-b9e1cc683ba6",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 99.994
    },
    "outlet_temperature": 99.994,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HT-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-cccdbb6a-6369-4f7d-97e3-be9c5faac84f",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 78.15
    },
    "outlet_temperature": 78.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2067532,
    "guid": "VALV-d3e33225-3e0a-4649-a292-176264af1f86",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 112468
    },
    "outlet_pressure": 112468,
    "outlet_temperature": 78.2507468846781,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "flash_pressure": 2180000,
    "flash_temperature": 117.121,
    "guid": "SEP-cea80b9b-9448-4c48-ad90-e28a8fd45dc2",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 2180000,
      "separator_specification/temperature": 117.121
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-a7209d99-5d9f-4253-a751-7a9d73774069",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 117.15
    },
    "outlet_temperature": 117.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2087532,
    "guid": "COMP-7e7efd8b-8968-4922-a14f-884e20b366eb",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 2200000
    },
    "outlet_temperature": 211.074802172693,
    "p_out": 2200000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-c4f4aec8-64ed-416d-8895-1b2bd4942fcf",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 167.005
    },
    "outlet_temperature": 167.005,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HT-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2413700,
    "guid": "COMP-5707123b-c624-4b15-9c6b-22c360502088",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 2500000
    },
    "outlet_temperature": 383.925250844404,
    "p_out": 2500000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-77fca4f2-5a82-4dd0-9dad-a7e54ccc4bea",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-05",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-1390c5ca-f9cd-4028-9f9d-9e61e6eb1c8b",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 252.35
    },
    "outlet_temperature": 252.35,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-06",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "flash_pressure": 2480000,
    "flash_temperature": 252.2607,
    "guid": "SEP-c67aef20-df6a-4377-bd92-e48c93e32cf5",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 2480000,
      "separator_specification/temperature": 252.2607
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "SEP-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2393700,
    "guid": "VALV-b5a363fc-a925-4814-9d9d-9b2deb69382c",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 86300
    },
    "outlet_pressure": 86300,
    "outlet_temperature": 166.68528785578,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,ethylene_mole_fraction,ethylene_molar_flow,methane_mole_fraction,methane_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow,propylene_mole_fraction,propylene_molar_flow,water_mole_fraction,water_molar_flow
M-17,MAT-5a82bdd6-3869-4f86-bae4-3b37c42053bb,166.68528785578,86300,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-16,MAT-9aee8638-d272-461b-9795-79e2c195682f,252.2607,2480000,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-0000,MAT-ee6bec75-b62c-424b-9188-03ba241869a3,252.2607,2480000,0,0,1,0,0,0,0,0,0,0,0,0
M-15,MAT-e6ece93e-b8cb-4fee-89ed-66d66292368d,252.350000054405,2500000,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-14,MAT-6ec2cedd-3cd6-472d-84e5-ce5292d5a72b,323.150000000214,2500000,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-13,MAT-66fdf6d6-b534-4763-8c6d-cba55a8b8bfe,383.925250857881,2500000,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-017,MAT-c6eb0801-be4b-4a2f-99eb-bb74d9c32fa5,166.68528785578,86300,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-12,MAT-1a1f767e-21cd-4a5b-9e72-cd5d334c7ca2,167.005000000831,86300,711.666666666668,19.9644988666667,1,711.666666666668,0,0,0,0,0,0,0,0
M-1,MAT-3dfb8064-8ffc-4a24-b7ff-4575647f052e,78.1499999880346,112468,352.222222222222,9.86694199999999,0,0,0,0,1,352.222222222222,0,0,0,0
M-01,MAT-a7630cf8-e9f1-416f-b4dd-1be1a5c5b8fd,78.1499999880346,112468,352.222222222222,9.86694199999999,0,0,0,0,1,352.222222222222,0,0,0,0
M-2,MAT-fa9ace07-22d7-4418-87c0-3149135454ca,211.074717591144,2200000,352.222222222222,9.86694199999999,0,0,0,0,1,352.222222222222,0,0,0,0
M-3,MAT-12e1b14e-12fc-425b-a95b-9cd53fde447f,117.150000217208,2200000,352.222222222222,9.86694199999999,0,0,0,0,1,352.222222222222,0,0,0,0
M-00,MAT-a93829a1-e752-4f34-9c7a-10b15f6aedb0,117.121,2180000,0,0,0,0,0,0,1,0,0,0,0,0
M-4,MAT-fd745f7d-f6cb-4cde-b921-33fc3d7e2e3c,117.121,2180000,352.222222222222,9.86694199999999,0,0,0,0,1,352.222222222222,0,0,0,0
M-5,MAT-5406681b-f4f4-4ed0-9d36-01e3400b78c3,78.2507468846781,112468,352.222222222222,9.86694199999999,0,0,0,0,1,352.222222222222,0,0,0,0
M-011,MAT-b03f298e-0c84-4b3b-8a5b-c3bc7588dcf2,99.8544926765354,34000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-6,MAT-568aa411-4751-46f0-a728-9af9e8953b14,99.9940000005202,34000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-7,MAT-50781c90-369c-49ec-82eb-7287e581fbf8,337.428780106322,2500000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-8,MAT-1569df09-c597-4488-8cbf-b9db867036ae,254.150000000023,2500000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-000,MAT-dff94b70-e785-4784-8e74-750c99ba6b15,171.549999999349,2500000,0,0,0,0,1,0,0,0,0,0,0,0
M-10,MAT-2c75c81f-0679-42b1-b120-602ae183127c,171.549999999349,2500000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-9,MAT-ffb37c00-580b-4389-9182-e59ee974e36f,171.549999999349,2500000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-11,MAT-a9a04d1f-08e2-4765-9eb1-4f51c5ce40a7,99.8544926765354,34000,589.444444444442,9.45613892222218,0,0,1,589.444444444442,0,0,0,0,0,0
M-022,MAT-2e1b341f-dae5-4f61-a15d-85a97fceb2d0,247.56412910715,250000,962.222222222221,40.4900609333333,0,0,0,0,0,0,1,962.222222222221,0,0
M-18,MAT-261eca02-c2e9-4b27-b4c8-569c653551e8,247.413599943261,250000,962.222222222221,40.4900609333333,0,0,0,0,0,0,1,962.222222222221,0,0
M-19,MAT-854ea3e3-20a1-42da-be29-0a8ebbd42ec1,357.953338725407,2100000,962.222222222221,40.4900609333333,0,0,0,0,0,0,1,962.222222222221,0,0
M-20,MAT-7dfa27c4-c486-44c0-b771-77ad18abdacf,323.149999999811,2100000,962.222222222221,40.4900609333333,0,0,0,0,0,0,1,962.222222222221,0,0
M-00000,MAT-360d7229-b80c-477a-96b6-1aa9321e0035,323.433,2080000,0,0,0,0,0,0,0,0,1,0,0,0
M-21,MAT-1fc5a874-eaa5-407a-a772-f98ac9fb4c82,323.433,2080000,962.222222222221,40.4900609333333,0,0,0,0,0,0,1,962.222222222221,0,0
M-22,MAT-341f9677-d944-4728-8fd6-525de5a7f3fc,247.56412910715,250000,962.222222222221,40.4900609333333,0,0,0,0,0,0,1,962.222222222221,0,0
M-23,MAT-052c8b80-014b-46dd-a801-ad12ffadd996,83.15,192022,176.666666666667,4.94903400000001,0,0,0,0,1,176.666666666667,0,0,0,0
M-24,MAT-fac0c9c9-4dda-4df4-8258-f8434c830dc9,48.1759999450952,192022,176.666666666667,4.94903400000001,0,0,0,0,1,176.666666666667,0,0,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: M-24
Target metric: temperature
Observed target value: 48.1759999450952
Required target value: >= 69.17599999508403
```

## Allowed Repair Actions

- `HT-01` / GUID `AQ-41d4e056-2c7e-4293-8dba-7823598a05f5`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-04` / GUID `VALV-291ee0e2-16c7-4dfb-ad0c-d31f54a85262`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `SEP-04` / GUID `SEP-2290d065-57bb-4e67-a372-abef9abc5615`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-04` / GUID `SEP-2290d065-57bb-4e67-a372-abef9abc5615`: `separator_specification/temperature` (unit: `K`)
- `CL-07` / GUID `RESF-89fe8705-44dd-42a7-8fa0-88911851ed82`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-04` / GUID `COMP-62f2a702-7ce6-4f0b-ba85-c393c1a1917a`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HT-04` / GUID `AQ-ddf698d8-5033-43d6-8fba-dff42389b26a`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-04` / GUID `RESF-df10ab4d-9db6-4e28-a15f-fecbdb6bb194`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-02` / GUID `VALV-73649080-e917-4b58-bc21-c1e5387d5b89`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `CL-03` / GUID `RESF-e4b14b07-263d-421b-9e14-fe94d9d3fd46`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-02` / GUID `COMP-6fd39550-a2ef-4147-89df-0440eab9398c`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HT-02` / GUID `AQ-0c61acce-22f2-4d7b-8a6f-b9e1cc683ba6`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-02` / GUID `RESF-cccdbb6a-6369-4f7d-97e3-be9c5faac84f`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-01` / GUID `VALV-d3e33225-3e0a-4649-a292-176264af1f86`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-cea80b9b-9448-4c48-ad90-e28a8fd45dc2`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-01` / GUID `SEP-cea80b9b-9448-4c48-ad90-e28a8fd45dc2`: `separator_specification/temperature` (unit: `K`)
- `CL-01` / GUID `RESF-a7209d99-5d9f-4253-a751-7a9d73774069`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-01` / GUID `COMP-7e7efd8b-8968-4922-a14f-884e20b366eb`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HT-03` / GUID `AQ-c4f4aec8-64ed-416d-8895-1b2bd4942fcf`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-03` / GUID `COMP-5707123b-c624-4b15-9c6b-22c360502088`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `CL-05` / GUID `RESF-77fca4f2-5a82-4dd0-9dad-a7e54ccc4bea`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-06` / GUID `RESF-1390c5ca-f9cd-4028-9f9d-9e61e6eb1c8b`: `thermal_specification/outlet_temperature` (unit: `K`)
- `SEP-03` / GUID `SEP-c67aef20-df6a-4377-bd92-e48c93e32cf5`: `separator_specification/pressure` (unit: `Pa`)
- `SEP-03` / GUID `SEP-c67aef20-df6a-4377-bd92-e48c93e32cf5`: `separator_specification/temperature` (unit: `K`)
- `VALV-03` / GUID `VALV-b5a363fc-a925-4814-9d9d-9b2deb69382c`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
