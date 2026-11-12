# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-06`
- Required target: `temperature at most 356.835810126`
- Faulty observed target value: `414.664904558178`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 48263,
    "guid": "BB-5d9726c0-39d2-4ff4-a195-e84958cf94ff",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 220632
    },
    "outlet_temperature": 322.050219970425,
    "pout": 220632,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "P-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-7c3e3af4-c21f-4332-aca7-3c97838930e7",
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
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-c0357c67-b5aa-4a19-8f38-afe1e8a08d95",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 435.372
    },
    "outlet_temperature": 435.372,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "H-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,benzene_mole_fraction,benzene_molar_flow,hydrogen chloride_mole_fraction,hydrogen chloride_molar_flow,monochlorobenzene_mole_fraction,monochlorobenzene_molar_flow
S-02,MAT-c1415544-cf34-402a-bed6-16b2d7f64564,435.372,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S- 01,MAT-53bda5a0-6d9d-4ced-bcfc-3672d5e6bf45,375.75,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S - 12,MAT-82ef0cf3-e8ad-46de-b6dc-14feed5e043d,376.277023223974,172369,18.74396685039,2.10975634601203,9.9999999999545e-06,0.000187439668503047,0,0,0.99999,18.7437794107215
S-01,MSTR-6b2995b9-f43e-4e76-aff7-17251f7fcd08,299.817,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S-07,MAT-5c3be040-4c9d-4cc8-b79e-e76bce30d576,416.88765482665,220632,18.146200043368,1.94068041567223,0.16142122769984,2.92918188908735,0.00065449572660955,0.0118766103825864,0.83792427657355,15.2051415438981
S-06,MAT-8c76857c-a75c-4bbc-81b2-634095601e4e,414.664904558178,220632,6.9560258458416,0.615259995148586,0.30346970805249,2.11094313264313,0.17943052787783,1.24812338945119,0.51709976406968,3.59695932374729
S- 12,MSTR-cb16fa65-470d-4eaa-a3bd-45e3dd7d9036,425.822708732167,172369,15.192693670835,1.71003726910636,9.9999999999545e-06,0.000151926936707659,0,0,0.99999,15.1925417438983
S-13,MAT-2eef94c2-f3c4-4af4-8aff-52cae40e0156,322.039,172369,18.74396685039,2.10975634601203,9.9999999999545e-06,0.000187439668503047,0,0,0.99999,18.7437794107215
S-04,MAT-81a0ed49-83d9-4932-84eb-d53aa258ee8c,435.372,255106,12.6,1.148732928,0.4,5.04,0.1,1.26,0.5,6.3
S-03,MAT-7b3c4bba-e499-4e03-8b1c-6e50c5678b7c,435.372,255106,0,0,0.176752400819469,0,0.000111570307198789,0,0.823136028873332,0
S-08,MAT-ba058401-9ebe-4daa-bb79-f9d31133fbc7,416.88765482665,220632,18.146200043368,1.94068041567223,0.16142122769984,2.92918188908735,0.00065449572660955,0.0118766103825864,0.83792427657355,15.2051415438981
S-09,MAT-856c29cb-7bd6-4353-9ad6-3254911adb74,416.887654826578,220632,0.0118766103825864,0.000433032378562859,0,0,1,0.0118766103825864,0,0
S-10,MAT-f6073d74-d60d-4eec-b241-d11677782cf8,416.88765482665,220632,18.1343234329854,1.94024738329367,0.161526946395989,2.92918188908735,0,0,0.838473053604011,15.205141543898
S-11,MAT-4ba2b47f-09b7-493b-96a6-ce39e081c71c,371.720063920628,172369,2.9416297621503,0.230210114187311,0.99571672813414,2.92902996215031,0,0,0.0042832718658618,0.0125998000000001
S-12,MAT-bc3f0c59-28fa-4e5d-8950-a0f66a24888e,425.822708732167,172369,15.192693670835,1.71003726910636,9.9999999999545e-06,0.000151926936707659,0,0,0.99999,15.1925417438983
S-15,MAT-66d5fec2-cb90-4d5a-bd3f-0d785a002df4,322.039,172369,12.5022258892101,1.40720748279002,9.9999999999545e-06,0.000125022258891532,0,0,0.99999,12.5021008669512
S-14,MAT-b6d46a0e-1d9a-4bd8-9859-eb6bf2a56dd8,322.039,172369,6.24174096117986,0.702548863222006,9.9999999999545e-06,6.24174096115146e-05,0,0,0.99999,6.24167854377025
S-05,MAT-3e0fe20f-41d0-4612-8113-32b5745c654a,322.050233829497,220632,12.5022258892101,1.40720748279002,9.9999999999545e-06,0.000125022258891532,0,0,0.99999,12.5021008669512
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-06
Target metric: temperature
Observed target value: 414.664904558178
Required target value: <= 356.8358101259514
```

## Allowed Repair Actions

- `P-01` / GUID `BB-5d9726c0-39d2-4ff4-a195-e84958cf94ff`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `CO-01` / GUID `RESF-7c3e3af4-c21f-4332-aca7-3c97838930e7`: `thermal_specification/outlet_temperature` (unit: `K`)
- `H-01` / GUID `AQ-c0357c67-b5aa-4a19-8f38-afe1e8a08d95`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
