# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `M-20`
- Required target: `pressure at least 86126.25`
- Faulty observed target value: `50662.5`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": -71325,
    "guid": "VALV-d7046982-4e5b-45bb-8242-d7d141d955df",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 50662.5
    },
    "outlet_pressure": 50662.5,
    "outlet_temperature": 298.132692008692,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-1",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "CL-137acbff-a2e7-43aa-8ca9-aec17cc89af5",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 330
    },
    "outlet_temperature": 330,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COL-1",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "HT-d4a694dc-44da-4897-9d69-ee6a5de1e427",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 380
    },
    "outlet_temperature": 380,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HTR-1",
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
    "tag": "GLS-1",
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
    "tag": "GLS-2",
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
    "tag": "GLS-3",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-20155d70-4292-4da4-9c48-87dd23717c99",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 298.15
    },
    "outlet_temperature": 298.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,sodium chloride_mole_fraction,sodium chloride_molar_flow,water_mole_fraction,water_molar_flow
M-19,MAT-21717e6c-3558-4d0a-9267-438a3c7860ae,298.15,30000,50.2012736475641,0.904812333753767,0.000208109970284114,0.0104473855670192,0.999791890029716,50.190826261997
M-18,MAT-77851db4-732e-491a-8f7f-9d2878f87e10,342.224710765845,30000,50.2012736475641,0.904812333753767,0.000208109970284114,0.0104473855670192,0.999791890029716,50.190826261997
M-12,MS-1906d181-9171-47e5-97e7-8080c24a479a,353.89036778234,30000,49.7987263524359,1.70520942858773,0.401406588172321,19.9895368404584,0.598593411827679,29.8091895119776
M-11,MS-e2d9ea54-9c00-41af-bfa3-dce1ca74df8f,349.997847127314,30000,24.2153593850146,0.711091709324808,0.280769717012468,6.79893960188574,0.719230282987532,17.4164197831288
M-10,MS-9b3bdaee-e309-44d9-a6ea-3463d12e6b3f,350,30000,9.78464061498544,0.176315902767651,0.000108363862689989,0.00106030145207317,0.99989163613731,9.78358031353337
M-08,MS-59ba9c3e-0a5b-449b-8a98-75ed1f94efb8,348.991484911314,40000,18.9244295445564,0.341083355059549,0.000201901951517236,0.00382087925639638,0.999798098048483,18.9206086653
M-09,MS-1346323b-1041-4e33-b442-db507d1b55ce,350,101325,34,0.887407616,0.2,6.8,0.8,27.2
M-17,MS-e856cc5d-29ba-44b8-a9f9-45875ea96a03,364.9976063479,40000,14.0755704554436,0.520223419311967,0.468624974251573,6.59616384225846,0.531375025748427,7.47940661318515
M-05,MS-063a6ef9-92ba-4894-a881-16ef48bd5769,356.85085527271,55000,21.4922034880222,0.387413075926567,0.000258987165352857,0.00556620485854965,0.999741012834647,21.4866372831637
M-06,MS-acdfdd9c-9eb6-47f4-a1de-0a707d969c98,365,101325,33,0.861307392,0.2,6.6,0.8,26.4
M-07,MS-705f899c-edda-47f8-a422-b83ef9f26e1e,365,40000,18.9244295445564,0.341083355059549,0.000201901951517236,0.00382087925639638,0.999798098048483,18.9206086653
M-14,MS-2315849c-674a-41e1-aa54-11a118cce878,298.15,101325,33,0.861307392,0.2,6.6,0.8,26.4
M-02,MS-ecb726f1-07bb-414b-876d-ac17fdc31ca8,298.15,101325,33,0.861307392,0.2,6.6,0.8,26.4
M-03,MS-5b2380db-51f3-4128-a6f6-bbcea656e61b,380,101325,33,0.861307392,0.2,6.6,0.8,26.4
M-01,MS-a37aab79-f1a4-4da1-8a30-c9fb4705cf7c,298.15,101325,100,2.6100224,0.2,20,0.8,80
M-04,MS-b4992008-2187-44f1-9a17-6d9030c79b59,380,55000,21.4922034880222,0.387413075926567,0.000258987165352857,0.00556620485854965,0.999741012834647,21.4866372831637
M-16,MS-4e019937-061a-410a-bbdb-b0565569aca2,379.9972190533,55000,11.5077965119778,0.473894299950952,0.573040493846968,6.59443339631415,0.426959506153032,4.91336311566362
M-15,MS-b30865b1-bd76-44b1-8ce9-b6f4129a262a,298.15,101325,34,0.887407616,0.2,6.8,0.8,27.2
M-13,MS-ad7a58c5-67a4-4598-b514-0cfb02163590,330,30000,49.7987263524359,1.70520942858773,0.401406588172321,19.9895368404584,0.598593411827679,29.8091895119776
M-20,MAT-7daf21d6-325a-477b-aa20-72e7da2abe85,298.14498598698,50662.5,50.2012736475641,0.904812333753767,0.000208109970284114,0.0104473855670192,0.999791890029716,50.190826261997
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: M-20
Target metric: pressure
Observed target value: 50662.5
Required target value: >= 86126.25
```

## Allowed Repair Actions

- `VALV-1` / GUID `VALV-d7046982-4e5b-45bb-8242-d7d141d955df`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COL-1` / GUID `CL-137acbff-a2e7-43aa-8ca9-aec17cc89af5`: `thermal_specification/outlet_temperature` (unit: `K`)
- `HTR-1` / GUID `HT-d4a694dc-44da-4897-9d69-ee6a5de1e427`: `thermal_specification/outlet_temperature` (unit: `K`)
- `GLS-1` / GUID `V-1ed3d67d-176d-45e5-8957-9a3b8d9a7b51`: `separator_specification/pressure` (unit: `Pa`)
- `GLS-1` / GUID `V-1ed3d67d-176d-45e5-8957-9a3b8d9a7b51`: `separator_specification/temperature` (unit: `K`)
- `GLS-2` / GUID `V-d959b7d1-4c5f-4c4f-9af2-34c2914bf79f`: `separator_specification/pressure` (unit: `Pa`)
- `GLS-2` / GUID `V-d959b7d1-4c5f-4c4f-9af2-34c2914bf79f`: `separator_specification/temperature` (unit: `K`)
- `GLS-3` / GUID `V-998d07d5-3cd1-41e0-9b4f-0bda5622e566`: `separator_specification/pressure` (unit: `Pa`)
- `GLS-3` / GUID `V-998d07d5-3cd1-41e0-9b4f-0bda5622e566`: `separator_specification/temperature` (unit: `K`)
- `COOL-02` / GUID `RESF-20155d70-4292-4da4-9c48-87dd23717c99`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
