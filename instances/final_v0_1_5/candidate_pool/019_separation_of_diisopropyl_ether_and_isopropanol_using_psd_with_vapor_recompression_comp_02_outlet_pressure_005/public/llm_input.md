# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `IPA`
- Required target: `temperature at most 324.34103246`
- Faulty observed target value: `359.41371155302`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 172432.5038625,
    "guid": "BB-180aba9d-82e3-470c-9c04-766cf19f9e00",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 415432.5
    },
    "outlet_temperature": 363.181061503183,
    "pout": 415432.5,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "PUMP",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 141674.9961375,
    "guid": "COMP-1e9e4b5c-aa2a-4eb9-a159-7fa0317c82cd",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 242999.9961375
    },
    "outlet_temperature": 1132.02791792041,
    "p_out": 242999.9961375,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-1e0499ee-3c34-4ffa-a609-11f7f9e6794a",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 363.15
    },
    "outlet_temperature": 363.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-017",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 202699.953225,
    "guid": "COMP-ea3c9f7a-cd27-45e9-84f0-2b2283c7f9af",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 303999.9766125
    },
    "outlet_temperature": 1007.96914693503,
    "p_out": 303999.9766125,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 506674.953225,
    "guid": "VALV-2aa477ff-9667-4f89-bcf2-2010f062ba70",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 101325
    },
    "outlet_pressure": 101325,
    "outlet_temperature": 347.474330211215,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALVE",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,diisopropyl ether_mole_fraction,diisopropyl ether_molar_flow,isopropanol_mole_fraction,isopropanol_molar_flow
DIPE,MAT-4c3acf25-b369-420a-8a12-52de68754dd3,394.14276304966,431300,6.9307726930188,0.707858668364505,0.999,6.92384192032578,0.001,0.0069307726930188
S15,MAT-6fa9b5e1-98fb-487f-be54-4aff65bfc11c,395.908463815714,431300,6.9306813610796,0.707849340385112,0.999,6.92375067971852,0.001,0.0069306813610796
IPA,MAT-742dd2e6-e885-47d6-8794-db31699a3227,359.41371155302,119325,20.846340752201,1.25363847386299,0.001,0.020846340752201,0.999,20.8254944114488
S17,MAT-92bd70ab-1817-4f50-a835-99bfee01bb85,347.076601256057,101325,14.171760901541,1.21100708272157,0.60259594769204,8.5398456909291,0.39740405230796,5.6319152106119
S-16,MAT-bf9b4ead-1888-4721-9334-688daab0ab85,347.142307753586,303999.9766125,14.171506026891,1.21098530313548,0.60259594768254,8.53969210436321,0.39740405231746,5.63181392252779
S14,MAT-3738c478-ea05-47ce-b0e3-da56dff05f91,347.142307753586,303999.9766125,14.171506026891,1.21098530313548,0.60259594768254,8.53969210436321,0.39740405231746,5.63181392252779
S-13,MAT-c2ab7242-6d56-4281-8185-8cae4c6ac8e5,981.148132158477,303999.9766125,14.171506026891,1.21098530313548,0.60259594768254,8.53969210436321,0.39740405231746,5.63181392252779
S-11,MAT-a87a4fc4-32c1-4302-9c13-05daa81f5f98,395.908463815714,431300,6.9306813610796,0.707849340385112,0.999,6.92375067971852,0.001,0.0069306813610796
S-10,MAT-fd758071-d919-4145-be11-631453b43640,380.70104666358,405300,14.171506026891,1.21098530313548,0.60259594768254,8.53969210436321,0.39740405231746,5.63181392252779
S-12,MAT-5b758074-788e-4130-8845-07becf91fa5f,992.267536864193,405300,14.171506026891,1.21098530313548,0.60259594768254,8.53969210436321,0.39740405231746,5.63181392252779
S-05,MAT-a67fdd0b-970f-4fbd-a0cf-eb24eb91138f,1132.03269054505,242999.9961375,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
S-07,MAT-5095ae43-1c38-4552-bd58-7bc92713abd4,363.15,242999.9961375,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
S-06,MAT-9bf686f0-1d60-4536-a9e8-e5de996a7d1a,501.959663117557,242999.9961375,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
S-08,MAT-5492f87f-68d8-4f04-9def-642cfe281f7f,363.181719351664,415432.5,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
S-04,MAT-41c8a93c-ef16-4505-9bc4-36f0f9b18eba,1098.45310242685,101325,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
Fresh Feed,MAT-367c78e8-43bc-4f3c-b381-598de311d073,298.15,101325,27.7777777777778,1.96152680555556,0.25,6.94444444444446,0.75,20.8333333333334
S-07,MAT-ebb3ab66-79f2-4c6d-a67e-1bf037f23618,359.677535262918,119325,20.847351291347,1.25369924475645,0.001,0.020847351291347,0.999,20.8265039400557
S-03,MAT-c9178513-2ac1-4043-b6cc-3c42c3711bda,359.677535262918,119325,20.847351291347,1.25369924475645,0.001,0.020847351291347,0.999,20.8265039400557
S-01,MAT-89cc5f92-e45b-43d8-b485-c397fefe4ba7,337,101325,27.7777777777778,1.96152680555556,0.25,6.94444444444446,0.75,20.8333333333334
S-02,MAT-dfaf3762-6316-45e2-8f0a-c6b68c5fe775,345.200371139814,101325,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
S-09,MAT-6f836035-6260-4b69-a989-b40170ff8be3,372,415432.5,21.102187387971,1.9188346435206,0.73278862042976,15.4634427840816,0.26721137957024,5.63874460388945
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: IPA
Target metric: temperature
Observed target value: 359.41371155302
Required target value: <= 324.3410324595218
```

## Allowed Repair Actions

- `PUMP` / GUID `BB-180aba9d-82e3-470c-9c04-766cf19f9e00`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COMP-01` / GUID `COMP-1e9e4b5c-aa2a-4eb9-a159-7fa0317c82cd`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-017` / GUID `RESF-1e0499ee-3c34-4ffa-a609-11f7f9e6794a`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-02` / GUID `COMP-ea3c9f7a-cd27-45e9-84f0-2b2283c7f9af`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `VALVE` / GUID `VALV-2aa477ff-9667-4f89-bcf2-2010f062ba70`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
