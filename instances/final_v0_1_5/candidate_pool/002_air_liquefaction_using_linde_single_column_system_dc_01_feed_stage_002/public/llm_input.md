# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-08`
- Required target: `Oxygen mole_fraction at least 0.992389497889`
- Faulty observed target value: `0.983653160294288`

## Observed Candidate Unit Parameters

```json
[
  {
    "condenser_duty": 8503.25047830703,
    "feed_stage": 5,
    "feed_stage_name": "Stage5",
    "feed_stream_id": "MAT-3b08d703-49be-433a-bf6d-9e8019f65a38",
    "guid": "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75",
    "kind": "unit_operation",
    "number_of_stages": 7,
    "observed_values": {
      "column_specification/reflux_ratio": 7.50199999999571
    },
    "reboiler_duty": -8313.83904787466,
    "reflux_ratio": 7.50199999999571,
    "supported_parameters": [
      "column_configuration/feed_stage",
      "column_specification/reflux_ratio"
    ],
    "tag": "DC-01",
    "type": "DWSIM.UnitOperations.UnitOperations.DistillationColumn"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 20163675,
    "guid": "COMP-e62d776c-5d63-4882-84fa-5df79b0f074d",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 20265000
    },
    "outlet_temperature": 1234.05577031637,
    "p_out": 20265000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-ba73118a-8e11-4e3e-b16d-df1d92bec4d3",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298
    },
    "outlet_temperature": 298,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-30f94a25-21b4-4957-bb18-34243330c90d",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 91
    },
    "outlet_temperature": 91,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 20163675,
    "guid": "VALV-59b34710-ae6d-4e4a-a95a-eed7a8ce9d5f",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 101325
    },
    "outlet_pressure": 101325,
    "outlet_temperature": 79.0011007965414,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,nitrogen_mole_fraction,nitrogen_molar_flow,oxygen_mole_fraction,oxygen_molar_flow
S-05,MAT-a875005a-a2f6-44eb-a1c5-bce058f59d89,148.0421,101325,174.9999999999,4.97172533818946,0.900522136953738,157.591373966814,0.0994778630462618,17.4086260330859
S-09,MAT-9ac7748d-2b1d-457b-a944-dcfcb8c2260b,77.9380499509433,101325,174.9999999999,4.97172533818946,0.900522136953738,157.591373966814,0.0994778630462618,17.4086260330859
S-08,MAT-2519ae05-5427-41dd-9478-ba6dab5f5678,89.6016555867044,101325,25,0.798341282625921,0.016346839705712,0.408670992642801,0.983653160294288,24.5913290073572
S-07,MAT-3b08d703-49be-433a-bf6d-9e8019f65a38,78.9719484687114,101325,200,5.7700668,0.79,158,0.21,42
S-06,MAT-9ec66030-175b-4308-b7ea-6d8024486292,91,20265000,200,5.7700668,0.79,158,0.21,42
S-04,MAT-63e6a9e2-bbab-4a05-812f-0f64b09efb30,153.424939910188,20265000,200,5.7700668,0.79,158,0.21,42
S-03,MAT-5b1626c4-d590-4fdd-81bf-9a9a0fd1c5f9,298,20265000,200,5.7700668,0.79,158,0.21,42
S-02,MAT-1c661434-a1e3-4873-828e-ee60b8261219,1234.05577031637,20265000,200,5.7700668,0.79,158,0.21,42
S-01,MAT-33f1eec1-8320-46fe-a0c5-9380d71675ed,298,101325,200,5.7700668,0.79,158,0.21,42
S-10,MAT-cc0d769a-93cd-49f7-9ae0-8ce964e95f32,77.9380499509433,101325,174.9999999999,4.97172533818946,0.900522136953738,157.591373966814,0.0994778630462618,17.4086260330859
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-08
Target metric: Oxygen mole_fraction
Observed target value: 0.983653160294288
Required target value: >= 0.9923894978894683
```

## Allowed Repair Actions

- `DC-01` / GUID `DC-84eedf9c-acf3-4dfc-8675-2245dc73de75`: `column_specification/reflux_ratio` (unit: `null`)
- `DC-01` / GUID `DC-84eedf9c-acf3-4dfc-8675-2245dc73de75`: `column_configuration/feed_stage` (unit: `null`)
- `COMP-01` / GUID `COMP-e62d776c-5d63-4882-84fa-5df79b0f074d`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-01` / GUID `RESF-ba73118a-8e11-4e3e-b16d-df1d92bec4d3`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-02` / GUID `RESF-30f94a25-21b4-4957-bb18-34243330c90d`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-01` / GUID `VALV-59b34710-ae6d-4e4a-a95a-eed7a8ce9d5f`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
