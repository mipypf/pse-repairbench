# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `NG-6`
- Required target: `molar_flow at most 591.414858741`
- Faulty observed target value: `643.300943887918`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 10000,
    "guid": "RESF-e00f17c1-1d25-4f6e-8e5e-d668aeb4148e",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 303.15
    },
    "outlet_temperature": 303.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-200",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1477000,
    "guid": "COMP-2c4857ab-c954-4ec2-aa1e-4f77c699cbad",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 2260000
    },
    "outlet_temperature": 360.653905984716,
    "p_out": 2260000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "K-200",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 10000,
    "guid": "RESF-8f776ea7-5d7b-46bf-a9af-fb2700bc38f1",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 303.15
    },
    "outlet_temperature": 303.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-201",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 418000,
    "guid": "COMP-47aebd01-76be-443a-9a22-9a25b63fbccd",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 793000
    },
    "outlet_temperature": 311.383078564362,
    "p_out": 793000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "K-202",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 230000,
    "guid": "COMP-7acb562d-c62a-48a4-a96d-24f5dd45d421",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 375000
    },
    "outlet_temperature": 276.220741472124,
    "p_out": 375000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "K-201",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 25000,
    "guid": "AQ-f45efb9d-5d09-4759-926c-89d211dc63b9",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 232.2956
    },
    "outlet_temperature": 232.2956,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-097",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2005000,
    "guid": "VALV-37a8ebc0-8489-4eb6-8772-6ecf24b44893",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 170000
    },
    "outlet_pressure": 170000,
    "outlet_temperature": 208.576294170564,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-095",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 25000,
    "guid": "RESF-3cf952e3-fe78-43c1-bd74-bf561e7a0473",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 210.16
    },
    "outlet_temperature": 210.16,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-092",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 25000,
    "guid": "AQ-8d82b2ec-4833-4038-9861-54e66d716e08",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 273.341515
    },
    "outlet_temperature": 273.341515,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-088",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1800000,
    "guid": "VALV-d4790127-e770-4a80-beb9-eb086f2909aa",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 400000
    },
    "outlet_pressure": 400000,
    "outlet_temperature": 231.299262149381,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-201",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 25000,
    "guid": "AQ-ff399acf-40b1-46be-9765-ec5f1ad46491",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 299.7396
    },
    "outlet_temperature": 299.7396,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-081",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 25000,
    "guid": "RESF-6c55414c-6338-499d-b12e-45dceb5acdf0",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 233.16
    },
    "outlet_temperature": 233.16,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-080",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 500000,
    "guid": "RESF-b49d1d90-9759-4239-b295-9f03180a5811",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 116.15
    },
    "outlet_temperature": 116.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-008",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1190000,
    "guid": "VALV-32cc2c07-eb8f-468e-a771-60b97413a3b7",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 99000
    },
    "outlet_pressure": 99000,
    "outlet_temperature": 109.40189113462,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-100",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 2785000,
    "guid": "COMP-1785016e-c678-4341-962d-101168f481b8",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 3000000
    },
    "outlet_temperature": 476.774435973259,
    "p_out": 3000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "K-102",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 15000,
    "guid": "RESF-31c024f2-8512-4403-86ce-67b99d5f18e9",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298.15
    },
    "outlet_temperature": 298.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "E-100",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 515000,
    "guid": "COMP-05b5c979-529a-4d1e-900a-590e87f2632d",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 3500000
    },
    "outlet_temperature": 310.743299465252,
    "p_out": 3500000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "K-100",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 15000,
    "guid": "AQ-76318934-5b28-448b-accf-7ad56241f463",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 358.15
    },
    "outlet_temperature": 358.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "E-102",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 480000,
    "guid": "RESF-f02c7ba3-2bbb-4d2f-a54a-7601a54be88d",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 275.11
    },
    "outlet_temperature": 275.11,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-031",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 300000,
    "guid": "RESF-966c8c7f-8f1c-4777-9f72-86ec89e07c9a",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 235.35
    },
    "outlet_temperature": 235.35,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-034",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 305000,
    "guid": "RESF-dc888f3c-74d9-487c-b7a3-078ed06b3e18",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 211.24
    },
    "outlet_temperature": 211.24,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-037",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 500000,
    "guid": "RESF-2bb8bbd8-05e6-4fe4-bfcb-5435bea52155",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 155.95
    },
    "outlet_temperature": 155.95,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-043",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 500000,
    "guid": "RESF-2aa8b799-cf10-42f4-b6a0-4c1a1b5e1d7d",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 108.65
    },
    "outlet_temperature": 108.65,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-046",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1075000,
    "guid": "VALV-ebb60c73-0f61-4563-b639-c67564934d77",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 325000
    },
    "outlet_pressure": 325000,
    "outlet_temperature": 106.010689647287,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-101",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 10000,
    "guid": "AQ-344cc183-7f47-44c1-be9b-4a538fd459e7",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 134.456
    },
    "outlet_temperature": 134.456,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-051",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 500000,
    "guid": "RESF-e3325298-3aec-4d54-9fbb-01e09a6da136",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 148.35
    },
    "outlet_temperature": 148.35,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-055",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1585000,
    "guid": "VALV-2cfa1fa8-1336-4b6d-bc16-8faa38723ff1",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 315000
    },
    "outlet_pressure": 315000,
    "outlet_temperature": 145.058597342429,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-102",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 50000,
    "guid": "AQ-3e52bf68-24ed-4238-918e-eef25aebb490",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 218.3022
    },
    "outlet_temperature": 218.3022,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-062",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 25000,
    "guid": "RESF-dfa1c24c-456d-4768-8711-846f3ac207f1",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 276.265
    },
    "outlet_temperature": 276.265,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-068",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1417000,
    "guid": "VALV-f1fece63-355c-41b6-bcd2-2b04370ee812",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 808000
    },
    "outlet_pressure": 808000,
    "outlet_temperature": 256.694062769504,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-200",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 500000,
    "guid": "RESF-ff7e6811-3892-4fa4-b194-3d8eca5a1295",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 144.05
    },
    "outlet_temperature": 144.05,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-121",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,ethane_mole_fraction,ethane_molar_flow,methane_mole_fraction,methane_molar_flow,n-butane_mole_fraction,n-butane_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow,propane_mole_fraction,propane_molar_flow
NG-2,MAT-6f4a0ec9-3b98-4ffb-aa27-d474addc89b1,144.05,3000000,10194.4444444445,180.530317555556,0.055,560.694444444446,0.897,9144.41666666669,0.001,10.1944444444445,0.029,295.63888888889,0.018,183.5
P-5,MAT-5280af78-54ae-46ed-b86d-ef251f88bc0c,256.693191962201,808000,14000,519.169,0.5,7000,0,0,0,0,0,0,0.5,7000
P-4,MAT-3c30c904-8425-4e3c-a492-d4a45b6f2c4f,276.265,2225000,10444.4444444445,387.316555555556,0.5,5222.22222222223,0,0,0,0,0,0,0.5,5222.22222222223
P-3,MAT-b0a5006c-b0cf-4831-8ac1-8082369f21dd,276.265,2225000,14000,519.169,0.5,7000,0,0,0,0,0,0,0.5,7000
P-2,MAT-5f59071d-9231-419c-abd5-282373e45779,276.265,2225000,24444.4444444445,906.485555555556,0.5,12222.2222222222,0,0,0,0,0,0,0.5,12222.2222222222
L-10,MAT-f3cc0eb0-d20d-4c19-b27c-86b2bcb6a263,218.3022,265000,16388.888888889,391.262878051412,0.449980508442034,7374.68055502226,0.450015268482719,7375.25023346682,0,0,0.0800054673089039,1311.20071422927,0.0199987557663433,327.757386170628
MSTR-063,MAT-a9a5ac87-559e-4067-b339-a76b08bb6812,218.3022,265000,16388.888888889,391.262878051412,0.449980508442034,7374.68055502226,0.450015268482719,7375.25023346682,0,0,0.0800054673089039,1311.20071422927,0.0199987557663433,327.757386170628
L-9,MAT-1779c771-805c-4c46-b3e7-1904ac074bc0,141.937716612864,315000,16388.888888889,391.262878051412,0.449980508442034,7374.68055502226,0.450015268482719,7375.25023346682,0,0,0.0800054673089039,1311.20071422927,0.0199987557663433,327.757386170628
8,MAT-f903a58d-79c7-49bc-91e1-e989e9885a8e,145.062488653054,315000,9173.21400684211,245.124977598254,0.678565392015381,6224.6255585938,0.270956895855039,2485.5455923079,0,0,0.0158874615719833,145.739085025283,0.0345902505575963,317.30377091512
L-8,MAT-2a56da55-4e34-4504-be03-99e558677e84,148.35,1900000,9173.21400684211,245.124977598254,0.678565392015381,6224.6255585938,0.270956895855039,2485.5455923079,0,0,0.0158874615719833,145.739085025283,0.0345902505575963,317.30377091512
L-7,MAT-ae0851e4-7548-491e-97a0-8c550d210f1e,134.456,315000,7215.67488204687,146.137900453159,0.159382873428774,1150.05499642846,0.677650354414507,4889.70464115892,0,0,0.161518035146475,1165.46162920398,0.0014487370102438,10.4536152555079
L-6,MAT-4ffe339b-0665-4764-b3c7-a22eb25f8082,106.009645622622,325000,7215.67488204687,146.137900453159,0.159382873428774,1150.05499642846,0.677650354414507,4889.70464115892,0,0,0.161518035146475,1165.46162920398,0.0014487370102438,10.4536152555079
L-5,MAT-1ebc807a-a7ec-4f09-b3db-f64ea83df1ba,108.65,1400000,7215.67488204687,146.137900453159,0.159382873428774,1150.05499642846,0.677650354414507,4889.70464115892,0,0,0.161518035146475,1165.46162920398,0.0014487370102438,10.4536152555079
L-4,MAT-480cd763-ce5b-4749-8172-6c5ec985fe78,155.95,1900000,7215.67488204687,146.137900453159,0.159382873428774,1150.05499642846,0.677650354414507,4889.70464115892,0,0,0.161518035146475,1165.46162920398,0.0014487370102438,10.4536152555079
L-3,MAT-18c57284-edd4-45c6-9734-b47030d3270f,211.24,2400000,9173.21400684211,245.124977598254,0.678565392015381,6224.6255585938,0.270956895855039,2485.5455923079,0,0,0.0158874615719833,145.739085025283,0.0345902505575963,317.30377091512
L-2,MAT-580c29d6-1cdd-4215-ae7b-700b2902de7b,211.244316164528,2400000,7215.67488204687,146.137900453159,0.159382873428774,1150.05499642846,0.677650354414507,4889.70464115892,0,0,0.161518035146475,1165.46162920398,0.0014487370102438,10.4536152555079
L-1,MAT-47157eb3-22ce-48e8-a793-7bdb1ac67d42,211.24,2400000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
L-17,MAT-94e47fa3-25f6-4fca-b0e0-8ab225047859,235.35,2705000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
L-16,MAT-127cd7aa-fde0-497c-94c4-22491ad7cc63,275.11,3005000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
L-15,MAT-7d3c0f6e-7744-4e49-9433-4415ba78ac70,358.15,3485000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
L-14,MAT-69ca4547-547e-4ded-a03d-ef998be637bb,310.825441492282,3500000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
L-13,MAT-87adfc03-a6f5-4189-bd1e-970b4209af78,298.15,2985000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
L-12,MAT-0363ceaa-458d-4d0c-946a-5c0abc26b8dd,478.590171325098,3000000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
LNG,MAT-f1f57237-dacf-42cb-b810-7941637294f7,108.387861359872,99000,9551.14350055655,168.054588349983,0.0587006455968834,560.658289671147,0.908912008676785,8681.14902425108,0.00106735420130098,10.1944531425476,0.0121076286388514,115.641698581118,0.0192123628861789,183.500034910662
NG-6,MAT-ed4bbbcc-2dcb-40d6-a24a-073afcc58205,108.389137845595,99000,643.300943887918,12.4757144093375,5.69521252601691e-05,0.0366373559362897,0.72014381480785,463.269195800936,1.32473860126934e-10,8.52205592601329e-08,0.279799041441609,179.994987458322,1.91492807283902e-07,0.000123187503673481
NG-5,MAT-9c41d5dc-6a44-4734-940d-ae0879dcc292,108.388001688756,99000,10194.4444444445,180.530317555556,0.055,560.694444444446,0.897,9144.41666666669,0.001,10.1944444444445,0.029,295.63888888889,0.018,183.5
NG-4,MAT-cb535012-645a-4e58-9141-e143a4816363,116.039300152043,1300000,10194.4444444445,180.530317555556,0.055,560.694444444446,0.897,9144.41666666669,0.001,10.1944444444445,0.029,295.63888888889,0.018,183.5
NG-3,MAT-10bb7977-c030-4798-9a25-b0eed023fea3,116.15,2500000,10194.4444444445,180.530317555556,0.055,560.694444444446,0.897,9144.41666666669,0.001,10.1944444444445,0.029,295.63888888889,0.018,183.5
L-11,MAT-0566623c-9052-4c9b-8c24-b958d32704dc,271.43753,215000,16388.888888889,391.265055426946,0.449991171161223,7374.8553051423,0.45000691600938,7375.11334570932,0,0,0.0800024764186953,1311.15169686196,0.0199994364107021,327.768541175397
NG-1,MAT-4b7a72f4-60c2-44b9-8569-9ff5192fb338,220.374524754599,3500000,10194.4444444445,180.530317555556,0.055,560.694444444446,0.897,9144.41666666669,0.001,10.1944444444445,0.029,295.63888888889,0.018,183.5
Natural gas,MAT-fa45fc4c-9735-4fcb-a417-ebbb97efa8c8,303.15,4000000,10194.4444444445,180.530317555556,0.055,560.694444444446,0.897,9144.41666666669,0.001,10.1944444444445,0.029,295.63888888889,0.018,183.5
P-6,MAT-46c90d2e-74be-4299-ac92-e9e4a11bef7b,233.16,2200000,10444.4444444445,387.316555555556,0.5,5222.22222222223,0,0,0,0,0,0,0.5,5222.22222222223
P-18,MAT-3acec2a2-9864-481c-8cad-991186db7217,299.7396,783000,14000,519.169,0.5,7000,0,0,0,0,0,0,0.5,7000
P-7,MAT-bfe6c0be-e929-418d-80bf-0f7eb8268bdb,233.16,2200000,6666.66666666667,247.223333333333,0.5,3333.33333333333,0,0,0,0,0,0,0.5,3333.33333333334
P-8,MAT-f2e2ce16-0232-4345-b632-e492faa2ef5d,233.16,2200000,3777.77777777778,140.093222222222,0.5,1888.88888888889,0,0,0,0,0,0,0.5,1888.88888888889
P-9,MAT-d9838e4f-0ee2-4eb6-b9bb-0198ffa83dc8,231.298930768796,400000,6666.66666666667,247.223333333333,0.5,3333.33333333334,0,0,0,0,0,0,0.5,3333.33333333334
P-14,MAT-c753df79-dcdf-4736-8c64-201eb5d7230c,273.341515,375000,6666.66666666667,247.223333333333,0.5,3333.33333333334,0,0,0,0,0,0,0.5,3333.33333333334
P-10,MAT-7dee9efc-000a-48c1-894a-f04fc7d62420,210.16,2175000,3777.77777777778,140.093222222222,0.5,1888.88888888889,0,0,0,0,0,0,0.5,1888.88888888889
P-11,MAT-c3b0c418-0a83-4a03-8b87-289aa44f1b80,208.569603414921,170000,3777.77777777778,140.093222222222,0.5,1888.88888888889,0,0,0,0,0,0,0.5,1888.88888888889
P-12,MAT-c691c84d-d19e-4975-afba-7a537f96b2ba,232.2956,145000,3777.77777777778,140.093222222222,0.5,1888.88888888889,0,0,0,0,0,0,0.5,1888.88888888889
P-13,MAT-9928cd75-a616-4dce-9a78-e09eb8d68689,275.314472882195,375000,3777.77777777778,140.093222222222,0.5,1888.88888888889,0,0,0,0,0,0,0.5,1888.88888888889
P-15,MAT-abf8de12-ba44-41a5-8e21-bf150b48fb81,274.05618321331,375000,10444.4444444445,387.316555555556,0.5,5222.22222222223,0,0,0,0,0,0,0.5,5222.22222222223
P-16,MAT-097f1b91-bf2b-4fc6-9c43-5be3c47ce921,310.662490391807,793000,10444.4444444445,387.316555555556,0.5,5222.22222222223,0,0,0,0,0,0,0.5,5222.22222222223
P-17,MAT-46819ac2-be4a-45e5-bbb1-5f4fe3b67c38,303.15,783000,10444.4444444445,387.316555555556,0.5,5222.22222222223,0,0,0,0,0,0,0.5,5222.22222222223
P-19,MAT-8b01f5f3-3a92-43d9-a681-9c676a887ddd,301.199354927736,783000,24444.4444444445,906.485555555556,0.5,12222.2222222222,0,0,0,0,0,0,0.5,12222.2222222222
MSTR-115,MAT-b64f68dc-8547-4190-beb6-617934340ddf,361.579032173711,2260000,24444.4444444445,906.485555555556,0.5,12222.2222222222,0,0,0,0,0,0,0.5,12222.2222222222
P-20,MAT-1132bc4c-dffd-4286-af04-c9ab172477bf,361.579032173711,2260000,24444.4444444445,906.485555555556,0.5,12222.2222222222,0,0,0,0,0,0,0.5,12222.2222222222
P-1,MAT-cd469c78-655e-496b-926f-b2c8fc7407e5,303.15,2250000,24444.4444444445,906.485555555556,0.5,12222.2222222222,0,0,0,0,0,0,0.5,12222.2222222222
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: NG-6
Target metric: molar_flow
Observed target value: 643.300943887918
Required target value: <= 591.4148587405306
```

## Allowed Repair Actions

- `COOL-200` / GUID `RESF-e00f17c1-1d25-4f6e-8e5e-d668aeb4148e`: `thermal_specification/outlet_temperature` (unit: `K`)
- `K-200` / GUID `COMP-2c4857ab-c954-4ec2-aa1e-4f77c699cbad`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-201` / GUID `RESF-8f776ea7-5d7b-46bf-a9af-fb2700bc38f1`: `thermal_specification/outlet_temperature` (unit: `K`)
- `K-202` / GUID `COMP-47aebd01-76be-443a-9a22-9a25b63fbccd`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `K-201` / GUID `COMP-7acb562d-c62a-48a4-a96d-24f5dd45d421`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HEAT-097` / GUID `AQ-f45efb9d-5d09-4759-926c-89d211dc63b9`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-095` / GUID `VALV-37a8ebc0-8489-4eb6-8772-6ecf24b44893`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-092` / GUID `RESF-3cf952e3-fe78-43c1-bd74-bf561e7a0473`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HEAT-088` / GUID `AQ-8d82b2ec-4833-4038-9861-54e66d716e08`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-201` / GUID `VALV-d4790127-e770-4a80-beb9-eb086f2909aa`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HEAT-081` / GUID `AQ-ff399acf-40b1-46be-9765-ec5f1ad46491`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-080` / GUID `RESF-6c55414c-6338-499d-b12e-45dceb5acdf0`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-008` / GUID `RESF-b49d1d90-9759-4239-b295-9f03180a5811`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-100` / GUID `VALV-32cc2c07-eb8f-468e-a771-60b97413a3b7`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `K-102` / GUID `COMP-1785016e-c678-4341-962d-101168f481b8`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `E-100` / GUID `RESF-31c024f2-8512-4403-86ce-67b99d5f18e9`: `thermal_specification/outlet_temperature` (unit: `K`)
- `K-100` / GUID `COMP-05b5c979-529a-4d1e-900a-590e87f2632d`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `E-102` / GUID `AQ-76318934-5b28-448b-accf-7ad56241f463`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-031` / GUID `RESF-f02c7ba3-2bbb-4d2f-a54a-7601a54be88d`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-034` / GUID `RESF-966c8c7f-8f1c-4777-9f72-86ec89e07c9a`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-037` / GUID `RESF-dc888f3c-74d9-487c-b7a3-078ed06b3e18`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-043` / GUID `RESF-2bb8bbd8-05e6-4fe4-bfcb-5435bea52155`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-046` / GUID `RESF-2aa8b799-cf10-42f4-b6a0-4c1a1b5e1d7d`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-101` / GUID `VALV-ebb60c73-0f61-4563-b639-c67564934d77`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HEAT-051` / GUID `AQ-344cc183-7f47-44c1-be9b-4a538fd459e7`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-055` / GUID `RESF-e3325298-3aec-4d54-9fbb-01e09a6da136`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-102` / GUID `VALV-2cfa1fa8-1336-4b6d-bc16-8faa38723ff1`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HEAT-062` / GUID `AQ-3e52bf68-24ed-4238-918e-eef25aebb490`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COOL-068` / GUID `RESF-dfa1c24c-456d-4768-8711-846f3ac207f1`: `thermal_specification/outlet_temperature` (unit: `K`)
- `VALV-200` / GUID `VALV-f1fece63-355c-41b6-bcd2-2b04370ee812`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-121` / GUID `RESF-ff7e6811-3892-4fa4-b194-3d8eca5a1295`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
