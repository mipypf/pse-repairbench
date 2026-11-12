# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-06`
- Required target: `temperature at most 356.830754008`
- Faulty observed target value: `414.663623640985`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 48263.290776812,
    "guid": "BB-12ca6c07-8d2b-45f7-9ae5-b6b65b388ff4",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 220632.290776812
    },
    "outlet_temperature": 322.050220038022,
    "pout": 220632.290776812,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "P-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-18913ff6-5a98-4a54-b2d4-15354a048183",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 435.372
    },
    "outlet_temperature": 435.372,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-3ca38f36-0bed-44cd-967b-38f2020832cc",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 322.039
    },
    "outlet_temperature": 322.039,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CO-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,benzene_mole_fraction,benzene_molar_flow,hydrogen chloride_mole_fraction,hydrogen chloride_molar_flow,monochlorobenzene_mole_fraction,monochlorobenzene_molar_flow
S-12,MAT-b3b64235-6a95-47d0-82b0-a8649a94c8e2,425.822708732167,172369,15.19672564129,1.71049109381285,9.9999999999545e-06,0.000151967256412209,0,0,0.99999,15.1965736740336
S-13,MAT-4a7f1dd3-00ac-454f-ba4d-7422a3ecfecb,322.039,172369,15.19672564129,1.71049109381285,9.9999999999545e-06,0.000151967256412209,0,0,0.99999,15.1965736740336
S-11,MAT-6a6b1b18-2b69-45cf-b87e-79ae2776b845,371.720037127331,172369,2.9423246985556,0.230264396948611,0.99571773978372,2.9297248985556,0,0,0.0042822602162791,0.0125998
S-10,MAT-f6073d74-d60d-4eec-b241-d11677782cf8,416.88795291553,220632,18.1390503398457,1.94075549076147,0.161523167471224,2.92987686581185,0,0,0.838476832528776,15.2091734740338
S-09,MAT-856c29cb-7bd6-4353-9ad6-3254911adb74,416.887952915458,220632,0.0118796809052803,0.000433144332706569,0,0,1,0.0118796809052803,0,0
S-08,MAT-ba058401-9ebe-4daa-bb79-f9d31133fbc7,416.88795291553,220632,18.150930020751,1.94118863509418,0.16141745147286,2.92987686581185,0.00065449433674742,0.0118796809052803,0.83792805419039,15.2091734740338
S-03,MAT-7b3c4bba-e499-4e03-8b1c-6e50c5678b7c,435.372,255106,0,0,0.176752400819469,0,0.000111570307198789,0,0.823136028873332,0
S-04,MAT-81a0ed49-83d9-4932-84eb-d53aa258ee8c,435.372,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S-02,MAT-8ce56a02-f27b-4bc0-8932-4393715a5a7a,435.372,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S-01,MAT-b0c260c4-775e-4a63-b062-0b72f0b18e30,299.817,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S-05,MAT-5c4e6e7a-8fe5-4555-8ed3-2c4dfdf620eb,322.050233897187,220632.290776812,10.1362160027404,1.14089755957317,9.9999999999545e-06,0.000101362160026943,0,0,0.99999,10.1361146405804
S-06,MAT-8c76857c-a75c-4bbc-81b2-634095601e4e,414.663623640985,220632,6.954407440074,0.615102003510392,0.3034404016748,2.11024818702627,0.17947184281078,1.24812031892708,0.51708775551442,3.59603893412065
S-07,MAT-5c3be040-4c9d-4cc8-b79e-e76bce30d576,416.88795291553,220632,18.150930020751,1.94118863509418,0.16141745147286,2.92987686581185,0.00065449433674742,0.0118796809052803,0.83792805419039,15.2091734740338
S-14,MAT-03854a2e-1594-4d47-b306-a5a859175287,322.039,172369,5.06050963854957,0.569593534239679,9.9999999999545e-06,5.06050963852655e-05,0,0,0.99999,5.06045903345318
S-15,MAT-12006d93-4508-461a-9a1a-fa61541e0623,322.039,172369,10.1362160027404,1.14089755957317,9.9999999999545e-06,0.000101362160026943,0,0,0.99999,10.1361146405804
S- 05,MAT-519f33d8-0f8a-480a-b517-97f93103d0f1,322.050233897187,220632.290776812,10.1362160027404,1.14089755957317,9.9999999999545e-06,0.000101362160026943,0,0,0.99999,10.1361146405804
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-06
Target metric: temperature
Observed target value: 414.663623640985
Required target value: <= 356.8307540083238
```

## Allowed Repair Actions

- `P-01` / GUID `BB-12ca6c07-8d2b-45f7-9ae5-b6b65b388ff4`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HE-01` / GUID `AQ-18913ff6-5a98-4a54-b2d4-15354a048183`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CO-01` / GUID `RESF-3ca38f36-0bed-44cd-967b-38f2020832cc`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
