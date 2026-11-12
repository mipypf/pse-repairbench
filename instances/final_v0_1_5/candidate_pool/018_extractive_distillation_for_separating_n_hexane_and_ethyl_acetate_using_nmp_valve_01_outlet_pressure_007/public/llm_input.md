# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-12`
- Required target: `pressure at least 85850`
- Faulty observed target value: `50500`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-61908faf-c648-4bd2-8dce-3c5696593b8f",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 402.35
    },
    "outlet_temperature": 402.35,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-f854ee52-fae5-4b12-a1ca-719708f90d71",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 341.87
    },
    "outlet_temperature": 341.87,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-3",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 383000,
    "guid": "VALV-ad472bfd-7532-4aba-bddf-79a3b2fc9802",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 50500
    },
    "outlet_pressure": 50500,
    "outlet_temperature": 341.880586189084,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALVE-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 384000,
    "guid": "COMP-eb287107-d05a-4e2e-affa-8594dd3857a3",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 484000
    },
    "outlet_temperature": 423.831629698616,
    "p_out": 484000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "C-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-8bb36765-ae7f-4cc7-ba15-0afb32731436",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 373.92
    },
    "outlet_temperature": 373.92,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,ethyl acetate_mole_fraction,ethyl acetate_molar_flow,n-hexane_mole_fraction,n-hexane_molar_flow,n-methyl-2-pyrrolidone_mole_fraction,n-methyl-2-pyrrolidone_molar_flow
S-01,MAT-c941a272-baba-421c-acbd-c8eb44cde9a6,298.15,120000,27.7777777777778,2.41466584166667,0.39,10.8333333333333,0.61,16.9444444444445,0,0
S-03,MAT-a534308b-b6d0-4f6d-8d93-5e796ff32bfe,298.15,120000,0.00108055555555556,0.000107116660833334,0,0,0,0,1,0.00108055555555556
S-04,MAT-7cc13cd2-bca1-4591-b4ad-81a2eb79add6,373.91690439491,33000,23.8482805555555,2.36336289922398,0.00282709309993045,0.0674213094038164,7.12223119982319e-11,1.69852967834914e-09,0.997172906828847,23.7808592444532
S-16,MAT-c8207350-c280-46c8-a4a9-f33e6c784436,433.369520380725,33000,23.8472,2.36325854941762,0.0028166983813758,0.067170369640345,7.0707505716458e-11,1.68617603032152e-09,0.99718330154792,23.7800296286736
S-02,MAT-df694c42-5fa5-40b7-a343-3f5ae7f70773,334.452973484832,120000,27.7777777777778,2.41466584166667,0.39,10.8333333333333,0.61,16.9444444444445,0,0
S-18,MAT-882b8eb2-f2be-4b0d-8d08-e93b2a62090f,373.92,33000,23.8472,2.36325578256314,0.0028272212001332,0.0674213094038164,7.1225539197438e-11,1.69852967834914e-09,0.99717277872864,23.7797786888976
S-05,MAT-3a18586a-694a-4425-b831-dce39ae464ae,341.281346277356,100000,17.092758333332,1.47326647441659,0.0086919728883103,0.148569792019762,0.99128469842926,16.9437897897812,2.3328682431256e-05,0.000398751531032507
S-17,MAT-761910aa-1471-4890-8c94-b1386322eaa5,390.63,33000,23.8472,2.36325578256314,0.0028272212001332,0.0674213094038164,7.1225539197438e-11,1.69852967834914e-09,0.99717277872864,23.7797786888976
S-06,MAT-72350054-4edd-4577-bef1-22c1e007ada3,387.9,100000,17.092758333332,1.47326647441659,0.0086919728883103,0.148569792019762,0.99128469842926,16.9437897897812,2.3328682431256e-05,0.000398751531032507
S-07,MAT-53332726-ae99-4d15-acef-faabd6a837ca,423.831628312858,484000,17.092758333332,1.47326647441659,0.0086919728883103,0.148569792019762,0.99128469842926,16.9437897897812,2.3328682431256e-05,0.000398751531032507
S-09,MAT-548bbf54-2760-4f2f-80ef-9a308a64b709,402.35,484000,17.092758333332,1.47326647441659,0.0086919728883103,0.148569792019762,0.99128469842926,16.9437897897812,2.3328682431256e-05,0.000398751531032507
S-10,MAT-7f98a350-4f64-4e1d-9b8b-feebcccde054,352.383395444242,484000,17.092758333332,1.47326647949983,0.0086921279164378,0.14857244187808,0.9912845435383,16.9437871422675,2.3328545260732e-05,0.00039874918640989
S-08,MAT-f4ecf367-0dc5-474d-9f02-e8649eb32a38,402.35,484000,17.092758333332,1.47326647441659,0.0086919728883103,0.148569792019762,0.99128469842926,16.9437897897812,2.3328682431256e-05,0.000398751531032507
S-11,MAT-ae03b75a-f5ca-410d-9803-3a7f92e14a16,321.333141763831,50500,17.092758333332,1.47326647949983,0.0086921279164378,0.14857244187808,0.9912845435383,16.9437871422675,2.3328545260732e-05,0.00039874918640989
S-12,MAT-c3c8477b-7053-46b5-864e-cd65633d0555,341.87,50500,17.092758333332,1.47326647949983,0.0086921279164378,0.14857244187808,0.9912845435383,16.9437871422675,2.3328545260732e-05,0.00039874918640989
S-15,MAT-3faeb52d-6500-4568-b4ed-e89ea265454d,433.369520380725,33000,23.8472,2.36325854941762,0.0028166983813758,0.067170369640345,7.0707505716458e-11,1.68617603032152e-09,0.99718330154792,23.7800296286736
S-13,MAT-d74a7cd0-deec-46a3-a135-511223184088,395.131043267127,120000,34.5333,3.30476226647393,0.31135700470899,10.752184850717,1.8957248828826e-05,0.000654656360980497,0.68862403804218,23.780460492922
S-14,MAT-5e0889e2-2917-4efc-8cd3-c06499a934e2,315.869812131326,28000,10.6861,0.941503717056324,0.99989841767124,10.6850144810766,6.1262263576465e-05,0.000654654674804463,4.0320065180255e-05,0.000430864248522723
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-12
Target metric: pressure
Observed target value: 50500.0
Required target value: >= 85850.0
```

## Allowed Repair Actions

- `CL-02` / GUID `RESF-61908faf-c648-4bd2-8dce-3c5696593b8f`: `thermal_specification/outlet_temperature` (unit: `K`)
- `CL-3` / GUID `RESF-f854ee52-fae5-4b12-a1ca-719708f90d71`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALVE-01` / GUID `VALV-ad472bfd-7532-4aba-bddf-79a3b2fc9802`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `C-01` / GUID `COMP-eb287107-d05a-4e2e-affa-8594dd3857a3`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `CL-01` / GUID `RESF-8bb36765-ae7f-4cc7-ba15-0afb32731436`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
