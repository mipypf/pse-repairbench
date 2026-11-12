# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `8 (WATER)`
- Required target: `temperature at least 357.483332908`
- Faulty observed target value: `336.483332715538`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-6688b989-4b0c-461d-b035-efd599791c92",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 310.927778
    },
    "outlet_temperature": 310.927778,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "EXCHANGER2_2",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-2938f98f-22f0-4647-ae26-06d0062f7043",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 336.483333
    },
    "outlet_temperature": 336.483333,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "EXCHANGER2",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-3eb7356d-dbe2-4ce6-9345-6bbf816a5b73",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 533.15
    },
    "outlet_temperature": 533.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "EXCHNGER1",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,water_mole_fraction,water_molar_flow
1 (FEED),MAT-10bb1415-2b01-4d78-b8a5-9647df10c6a3,366.483333,92350,54.6161007024331,0.490151,0,0
3,MAT-7c2dcd0d-ef54-4afa-9a5e-be7d2f5b522f,810.927778,92350,155.639114950897,2.11824438025208,0.0770557546735678,11.9928894592675
L,MAT-754a92a6-e617-47f1-93f6-2ee9acb87c14,810.927778,92350,0,0,0,0
4,MAT-426464d6-cda4-4162-a9c6-7effea471605,533.15,92350,155.639114950897,2.11824438025208,0.0770557546735678,11.9928894592675
5,MAT-fde8dfb4-b179-458c-a7f6-0597e542fe45,336.483333,92350,155.639114950897,2.11824438025208,0.0770557546735678,11.9928894592675
6 (PRODUCTS),MAT-8a9ffcc4-d174-4597-b57c-529915ca293b,336.483333,92350,24.2797019323399,0.330446123319324,0.0770557546735678,1.87089075564574
7,MAT-316d233f-e0b8-45f1-ad84-275c4b4c7771,336.483333,92350,131.359413018557,1.78779825693275,0.0770557546735678,10.1219987036218
9,MAT-25b8fd97-d588-4933-bb92-26ddeb3db2ae,336.483333,92350,122.4642870697,1.6275525629641,0.0100182084436323,1.22687275476508
8 (WATER),MAT-f3fd1cd5-52d7-4bca-9689-a87973beab14,336.483332715538,92350,8.89512594885672,0.160245693968654,1,8.89512594885672
10,MAT-62f38a43-1c51-4173-8558-a4b23627c240,310.927778,92350,122.4642870697,1.6275525629641,0.0100182084436323,1.22687275476508
RECYCLE,MAT-8038a2e6-a2d3-4aee-a8da-6997b9a945d1,310.927778,92350,122.4642870697,1.6275525629641,0.0100182084436323,1.22687275476508
2,MAT-7a437f8f-a935-4506-97fa-3ccb22a76897,326.574312282434,92350,177.182000796115,2.11844507372355,0.00697669755110284,1.23614523105376
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: 8 (WATER)
Target metric: temperature
Observed target value: 336.483332715538
Required target value: >= 357.4833329081276
```

## Allowed Repair Actions

- `EXCHANGER2_2` / GUID `AQ-6688b989-4b0c-461d-b035-efd599791c92`: `thermal_specification/outlet_temperature` (unit: `K`)
- `EXCHANGER2` / GUID `RESF-2938f98f-22f0-4647-ae26-06d0062f7043`: `thermal_specification/outlet_temperature` (unit: `K`)
- `EXCHNGER1` / GUID `RESF-3eb7356d-dbe2-4ce6-9345-6bbf816a5b73`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
