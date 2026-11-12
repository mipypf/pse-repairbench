# LLM Input Packet: Distillation Feed-Stage Repair

## Task

### Repair Task: Distillation Column Feed Stage

The DWSIM air-liquefaction flowsheet runs headlessly, but the selected product stream misses its purity target.

Adjust only the feed stage for column `DC-01` / GUID `DC-84eedf9c-acf3-4dfc-8675-2245dc73de75`. Propose a structured repair action so that `Oxygen` mole fraction in material stream `S-08` is at least `0.99` after rerunning the flowsheet.

Expected repair action type: `set_unit_parameter`.

## Target

- Target stream: `S-08`
- Target component: `Oxygen`
- Required mole fraction: `0.99` or higher
- Faulty observed mole fraction: `0.983653160294288`

## Faulty Column Parameters

```json
{
  "condenser_duty": 8507.87973435722,
  "feed_stage": 5,
  "feed_stage_name": "Stage5",
  "feed_stream_id": "MAT-3b08d703-49be-433a-bf6d-9e8019f65a38",
  "guid": "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75",
  "number_of_stages": 7,
  "reboiler_duty": -8340.64877164773,
  "reflux_ratio": 7.50199999999571,
  "specs": [
    {
      "calculated_value": 7.502,
      "component_id": "",
      "spec_unit": "",
      "spec_value": 7.502,
      "stage_number": 0,
      "stype": "Stream_Ratio"
    },
    {
      "calculated_value": 25,
      "component_id": "Oxygen",
      "spec_unit": "kmol/h",
      "spec_value": 90,
      "stage_number": -1,
      "stype": "Product_Molar_Flow_Rate"
    }
  ],
  "tag": "DC-01",
  "type": "DWSIM.UnitOperations.UnitOperations.DistillationColumn"
}
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,oxygen_mole_fraction,oxygen_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow
S-05,MAT-a875005a-a2f6-44eb-a1c5-bce058f59d89,148.0421,101325,174.9999999999,4.97172533818946,0.0994778630462618,17.4086260330859,0.900522136953738,157.591373966814
S-09,MAT-9ac7748d-2b1d-457b-a944-dcfcb8c2260b,77.9380499509433,101325,174.9999999999,4.97172533818946,0.0994778630462618,17.4086260330859,0.900522136953738,157.591373966814
S-08,MAT-2519ae05-5427-41dd-9478-ba6dab5f5678,89.6016555867044,101325,25,0.798341282625921,0.983653160294288,24.5913290073572,0.016346839705712,0.408670992642801
S-07,MAT-3b08d703-49be-433a-bf6d-9e8019f65a38,78.9719484687114,101325,200,5.7700668,0.21,42,0.79,158
S-06,MAT-9ec66030-175b-4308-b7ea-6d8024486292,91,20265000,200,5.7700668,0.21,42,0.79,158
S-04,MAT-63e6a9e2-bbab-4a05-812f-0f64b09efb30,153.424939910188,20265000,200,5.7700668,0.21,42,0.79,158
S-03,MAT-5b1626c4-d590-4fdd-81bf-9a9a0fd1c5f9,298,20265000,200,5.7700668,0.21,42,0.79,158
S-02,MAT-1c661434-a1e3-4873-828e-ee60b8261219,1234.05577031637,20265000,200,5.7700668,0.21,42,0.79,158
S-01,MAT-33f1eec1-8320-46fe-a0c5-9380d71675ed,298,101325,200,5.7700668,0.21,42,0.79,158
S-10,MAT-cc0d769a-93cd-49f7-9ae0-8ce964e95f32,77.9380499509433,101325,174.9999999999,4.97172533818946,0.0994778630462618,17.4086260330859,0.900522136953738,157.591373966814
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-08
Target component: Oxygen
Observed target mole fraction: 0.983653160294288
Required target mole fraction: 0.99
```

## Required Output

Return one JSON object. The `repair_actions` array must contain a canonical `set_unit_parameter` action targeting the column GUID below. Choose the integer feed-stage value you recommend.

```json
{
  "diagnosis": "short diagnosis",
  "repair_actions": [
    {
      "type": "set_unit_parameter",
      "target": {
        "kind": "unit_operation",
        "guid": "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75"
      },
      "parameter": {
        "namespace": "column_configuration",
        "name": "feed_stage"
      },
      "value": 1,
      "unit": null,
      "rationale": "why this feed stage should restore the target"
    }
  ],
  "rationale": "brief overall reasoning"
}
```
