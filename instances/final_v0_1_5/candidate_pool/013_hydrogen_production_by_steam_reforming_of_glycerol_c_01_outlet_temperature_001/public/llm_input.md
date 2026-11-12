# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-09`
- Required target: `temperature at least 289.15`
- Faulty observed target value: `268.15`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-cafc70c6-94a8-40f5-9440-f5c00ace4170",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 873.15
    },
    "outlet_temperature": 873.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "H-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-c246df5a-2e3c-4719-b208-61f141d21d91",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 268.15
    },
    "outlet_temperature": 268.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "C-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,carbon_mole_fraction,carbon_molar_flow,carbon dioxide_mole_fraction,carbon dioxide_molar_flow,carbon monoxide_mole_fraction,carbon monoxide_molar_flow,glycerol_mole_fraction,glycerol_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methane_mole_fraction,methane_molar_flow,water_mole_fraction,water_molar_flow
S-10,MAT-b6201f13-782f-407a-a47d-e3cbcbfbcd44,268.15,101325,2.19965412641104,0.0396370349420938,0,0,0.00016497557266931,0.000362889199179071,2.10713981882793e-09,4.63497879740987e-09,1.34200905970595e-06,2.9519557658632e-06,5.09448160277445e-08,1.12060974794679e-07,6.04465500773622e-12,1.32961503304981e-11,0.999833629360271,2.19928816854684
S-09,MAT-894b5dd9-f5a5-4822-9a02-2785a00a74b8,268.15,101325,2.48602311908668,0.0364556514756357,0,0,0.252034277489671,0.626563040641629,0.0706678047829398,0.175681796465493,9.17447557154403e-21,2.28079583763544e-20,0.661536120799608,1.64459409041874,0.0124698060662633,0.031000226171258,0.00329199086151833,0.00818396538955665
S-08,MAT-c0ebc1a8-87ab-4143-9b9e-2654514127bf,268.15,101325,4.68567724549772,0.0760926230118767,0,0,0.133797241348655,0.626930689297761,0.0374936486813832,0.175683136477043,6.29990127762026e-07,2.95193040654273e-06,0.350985912399136,1.64460670321888,0.00661600451684154,0.0310004618206745,0.471106563063857,2.20745330275295
S-05,MAT-d96237b7-56a8-4a6c-b4f6-2e6885dfee21,873.15,101325,3.08112178191188,0.0760929855940248,0,0,0.000104172346158835,0.000320967684822852,1.44873015994029e-09,4.46371405190472e-09,0.09015475448212,0.277777777777778,3.23075417802066e-08,9.95434706990227e-08,4.83750525557315e-12,1.49049428130596e-11,0.909741039410612,2.80302293242719
S-07,MAT-82d75533-10cc-41ea-baea-19f95ccb5f69,873.15,101325,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
S-06,MAT-bbdffa7b-d3ad-4e1c-8769-23d0da09fc41,873.15,101325,4.68567724549772,0.0760926230118767,0,0,0.133797241348655,0.626930689297761,0.0374936486813832,0.175683136477043,6.29990127762026e-07,2.95193040654273e-06,0.350985912399136,1.64460670321888,0.00661600451684154,0.0310004618206745,0.471106563063857,2.20745330275295
S-04,MAT-5879b00b-79ec-4439-aed7-4682246e5a69,279.863509821492,101325,3.08112178191188,0.0760929855940248,0,0,0.000104172346158835,0.000320967684822852,1.44873015994029e-09,4.46371405190472e-09,0.09015475448212,0.277777777777778,3.23075417802066e-08,9.95434706990227e-08,4.83750525557315e-12,1.49049428130596e-11,0.909741039410612,2.80302293242719
S-03,MAT-3da5339c-bc0e-45b9-b4b3-64bbba7daacc,298.15,101325,0.833333333333333,0.0150127333333333,0,0,0,0,0,0,0,0,0,0,0,0,1,0.833333333333333
S-01,MAT-cb9c1196-6c79-4789-b210-2d1ed9a6ce10,298.15,101325,0.277777777777778,0.0255816166666667,0,0,0,0,0,0,1,0.277777777777778,0,0,0,0,0,0
S-02,MAT-6896f5ae-bd8c-4ad9-84b1-4e93e83201db,268.15,101325,2.19965412641104,0.0396370349420938,0,0,0.00016497557266931,0.000362889199179071,2.10713981882793e-09,4.63497879740987e-09,1.34200905970595e-06,2.9519557658632e-06,5.09448160277445e-08,1.12060974794679e-07,6.04465500773622e-12,1.32961503304981e-11,0.999833629360271,2.19928816854684
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-09
Target metric: temperature
Observed target value: 268.15
Required target value: >= 289.15
```

## Allowed Repair Actions

- `H-01` / GUID `AQ-cafc70c6-94a8-40f5-9440-f5c00ace4170`: `thermal_specification/outlet_temperature` (unit: `K`)
- `C-01` / GUID `RESF-c246df5a-2e3c-4719-b208-61f141d21d91`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
