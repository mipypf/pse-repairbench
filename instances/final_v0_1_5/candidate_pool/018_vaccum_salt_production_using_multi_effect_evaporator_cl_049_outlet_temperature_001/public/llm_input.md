# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `MS-053`
- Required target: `temperature at least 321`
- Faulty observed target value: `300`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "CL-137acbff-a2e7-43aa-8ca9-aec17cc89af5",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 300
    },
    "outlet_temperature": 300,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-049",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "HT-d4a694dc-44da-4897-9d69-ee6a5de1e427",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 350
    },
    "outlet_temperature": 350,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "heater",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  },
  {
    "flash_pressure": 55000,
    "flash_temperature": 380,
    "guid": "V-1ed3d67d-176d-45e5-8957-9a3b8d9a7b51",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 55000,
      "separator_specification/temperature": 380
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "V-005",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "flash_pressure": 40000,
    "flash_temperature": 365,
    "guid": "V-d959b7d1-4c5f-4c4f-9af2-34c2914bf79f",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 40000,
      "separator_specification/temperature": 365
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "V-025",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "flash_pressure": 30000,
    "flash_temperature": 350,
    "guid": "V-998d07d5-3cd1-41e0-9b4f-0bda5622e566",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 30000,
      "separator_specification/temperature": 350
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "V-036",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "CL-49fb4817-9f1c-43dd-b03f-683cd4437c15",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298
    },
    "outlet_temperature": 298,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "CL-055",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,sodium chloride_mole_fraction,sodium chloride_molar_flow,water_mole_fraction,water_molar_flow
packing,MS-51c5260b-276c-4fad-958a-7eb48a90f537,298,30000,0.0497860552475662,0.00170478929832399,0.401413422199111,0.0199847908147196,0.598586577800889,0.0298012644328466
MS-048,MS-1906d181-9171-47e5-97e7-8080c24a479a,342.224710765845,30000,49.7860552475717,1.70478929832417,0.401413422199111,19.9847908147218,0.598586577800889,29.8012644328499
MS-045,MS-eb2d79b3-a507-4287-b834-8f954fc1ba36,313.805046489836,30000,50,1.35720225349342,0.225821355593023,11.2910677796511,0.774178644406977,38.7089322203488
MS-041_CLONE,MS-acfe022c-97a7-4a5f-91ab-ff7735ec9649,349.997844249556,30000,16,0.469845068603255,0.280769706944253,4.49231531110804,0.719230293055747,11.507684688892
MS-042,MS-1f67696e-62ae-46df-8acc-e2292ceb2e10,349.997844249556,30000,24.2109153486443,0.710961198933213,0.280769706944253,6.79769160729098,0.719230293055747,17.4132237413534
MS-041,MS-f5251e7e-fdad-4487-967b-0b5465b4688c,349.997844249556,30000,16,0.469845068603255,0.280769706944253,4.49231531110804,0.719230293055747,11.507684688892
MS-038,MS-e2d9ea54-9c00-41af-bfa3-dce1ca74df8f,349.997844249556,30000,40.2109153486443,1.18080626753647,0.280769706944253,11.290006918399,0.719230293055747,28.9209084302453
MS-037,MS-9b3bdaee-e309-44d9-a6ea-3463d12e6b3f,350,30000,9.78908465135564,0.176395982792504,0.000108363857287776,0.00106078297213747,0.999891636142712,9.7880238683835
MS-035,MS-59ba9c3e-0a5b-449b-8a98-75ed1f94efb8,348.991484911314,40000,18.9294205873134,0.341173339951441,0.000201940010145077,0.00382260738544249,0.999798059989855,18.9255979799279
MS-034,MS-1346323b-1041-4e33-b442-db507d1b55ce,330,30000,50,1.35720225349342,0.225821355593023,11.2910677796511,0.774178644406977,38.7089322203488
MS-031,MS-4f68cdec-6834-4edf-b2bb-63eeebb7aabc,307.668025045732,40000,41,1.15694650630911,0.252393274980108,10.3481242741844,0.747606725019892,30.6518757258156
MS-027_CLONE,MS-3c9c8fe9-ac4e-444f-8f40-d4134997ef54,364.999841089504,40000,8,0.295689688832023,0.468671919162406,3.74937535329925,0.531328080837594,4.25062464670075
MS-028,MS-e8429c22-f711-4365-9d90-759d50e371a4,364.999841089504,40000,14.0705794126866,0.520065656027948,0.468671919162406,6.59448545707089,0.531328080837594,7.47609395561575
MS-027,MS-3ee1f496-6af7-4c69-ad9d-e698eb9e33a0,364.999841089504,40000,8,0.295689688832023,0.468671919162406,3.74937535329925,0.531328080837594,4.25062464670075
MS-025,MS-e856cc5d-29ba-44b8-a9f9-45875ea96a03,364.999841089504,40000,22.0705794126866,0.815755344859971,0.468671919162406,10.3438608103701,0.531328080837594,11.7267186023165
MS-024,MS-063a6ef9-92ba-4894-a881-16ef48bd5769,356.85085527271,55000,21.4954395134496,0.387471410486105,0.000258990359864409,0.00556711161503196,0.999741009640136,21.4898724018346
MS-023,MS-acdfdd9c-9eb6-47f4-a1de-0a707d969c98,350,40000,41,1.15694650630911,0.252393274980108,10.3481242741844,0.747606725019892,30.6518757258156
MS-024,MS-705f899c-edda-47f8-a422-b83ef9f26e1e,365,40000,18.9294205873134,0.341173339951441,0.000201940010145077,0.00382260738544249,0.999798059989855,18.9255979799279
MS-015,MS-2315849c-674a-41e1-aa54-11a118cce878,298.15,101325,33,0.861307392,0.2,6.6,0.8,26.4
MS-013,MS-ecb726f1-07bb-414b-876d-ac17fdc31ca8,298.15,101325,33,0.861307392,0.2,6.6,0.8,26.4
MS-003,MS-5b2380db-51f3-4128-a6f6-bbcea656e61b,350,55000,48.5721999996904,1.50250532035494,0.319560946136137,15.5217781878147,0.680439053863863,33.0504218118756
MS-001,MS-a37aab79-f1a4-4da1-8a30-c9fb4705cf7c,298.15,101325,100,2.6100224,0.2,20,0.8,80
MS-008,MS-b4992008-2187-44f1-9a17-6d9030c79b59,380,55000,21.4954395134496,0.387471410486105,0.000258990359864409,0.00556711161503196,0.999741009640136,21.4898724018346
MS-007,MS-4e019937-061a-410a-bbdb-b0565569aca2,379.997423637237,55000,27.0767604862407,1.11503192335409,0.573043512461391,15.5161619351112,0.426956487538609,11.5605985511295
MS-012,MS-e7ae885d-2d20-4362-a498-660d9db6ae04,379.997423637237,55000,11.5045604862407,0.473762443363013,0.573043512461391,6.59261375035992,0.426956487538609,4.91194673588082
MS-011,MS-facdbc5c-a12c-4af5-a0cf-e3321ea3ca4f,379.997423637237,55000,15.5722,0.641269479991079,0.573043512461391,8.92354818475127,0.426956487538609,6.64865181524873
MS-014,MS-581e03cc-57bd-4a55-adb6-42a1f7419199,315.161123475895,55000,48.5721999996904,1.50250532035494,0.319560946136137,15.5217781878147,0.680439053863863,33.0504218118756
MS-011_CLONE,MS-5308326a-cbe0-4502-b6af-ab2864550cb8,379.99031437066,55000,15.5721999996904,0.641197928354939,0.572929848575803,8.92177818781472,0.427070151424197,6.65042181187564
MS-018,MS-b30865b1-bd76-44b1-8ce9-b6f4129a262a,298.15,101325,34,0.887407616,0.2,6.8,0.8,27.2
MS-050,MS-ad7a58c5-67a4-4598-b514-0cfb02163590,300,30000,49.7860552475717,1.70478929832417,0.401413422199111,19.9847908147218,0.598586577800889,29.8012644328499
MS-053,MS-ff62331c-5cf1-4be2-9243-694f8f27ebd1,300,30000,49.7362691923242,1.70308450902585,0.401413422199111,19.9648060239071,0.598586577800889,29.7714631684171
MS-054,MS-6a90b181-31e9-4de3-8379-cd62e125b200,300,30000,0.0497860552475662,0.00170478929832399,0.401413422199111,0.0199847908147196,0.598586577800889,0.0298012644328466
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: MS-053
Target metric: temperature
Observed target value: 300.0
Required target value: >= 321.0
```

## Allowed Repair Actions

- `CL-049` / GUID `CL-137acbff-a2e7-43aa-8ca9-aec17cc89af5`: `thermal_specification/outlet_temperature` (unit: `K`)
- `heater` / GUID `HT-d4a694dc-44da-4897-9d69-ee6a5de1e427`: `thermal_specification/outlet_temperature` (unit: `K`)
- `V-005` / GUID `V-1ed3d67d-176d-45e5-8957-9a3b8d9a7b51`: `separator_specification/pressure` (unit: `Pa`)
- `V-005` / GUID `V-1ed3d67d-176d-45e5-8957-9a3b8d9a7b51`: `separator_specification/temperature` (unit: `K`)
- `V-025` / GUID `V-d959b7d1-4c5f-4c4f-9af2-34c2914bf79f`: `separator_specification/pressure` (unit: `Pa`)
- `V-025` / GUID `V-d959b7d1-4c5f-4c4f-9af2-34c2914bf79f`: `separator_specification/temperature` (unit: `K`)
- `V-036` / GUID `V-998d07d5-3cd1-41e0-9b4f-0bda5622e566`: `separator_specification/pressure` (unit: `Pa`)
- `V-036` / GUID `V-998d07d5-3cd1-41e0-9b4f-0bda5622e566`: `separator_specification/temperature` (unit: `K`)
- `CL-055` / GUID `CL-49fb4817-9f1c-43dd-b03f-683cd4437c15`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
