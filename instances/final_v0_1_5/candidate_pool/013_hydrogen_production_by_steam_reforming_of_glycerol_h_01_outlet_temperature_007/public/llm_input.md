# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-09`
- Required target: `Carbon monoxide mass_fraction at least 0.131707515973`
- Faulty observed target value: `not available in stream table`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-cafc70c6-94a8-40f5-9440-f5c00ace4170",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 843.15
    },
    "outlet_temperature": 843.15,
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
      "thermal_specification/outlet_temperature": 298.15
    },
    "outlet_temperature": 298.15,
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
S-10,MAT-b6201f13-782f-407a-a47d-e3cbcbfbcd44,298.15,101325,1.94472651496052,0.0350416162790664,0,0,0.00013509624908996,0.000262725257676957,7.03892231910171e-09,1.36887788707045e-08,0,0,1.89167543455074e-07,3.67879137527029e-07,1.2788491243144e-10,2.48701180068827e-10,0.999864707416559,1.94446340788623
S-09,MAT-894b5dd9-f5a5-4822-9a02-2785a00a74b8,298.15,101325,2.39997901571989,0.0364631267626601,0,0,0.255945822605967,0.614264603415484,0.0603158404473978,0.144756751389263,0,0,0.626095301160523,1.50261558462608,0.0309133643010174,0.0741914256277461,0.0267296714850956,0.0641506506613155
S-08,MAT-c0ebc1a8-87ab-4143-9b9e-2654514127bf,298.15,101325,4.34470553068041,0.0715047354452011,0,0,0.141442961335504,0.614528016390181,0.0333180065272201,0.144756927230059,0,0,0.345850282620394,1.50261763568821,0.0170763032061619,0.0741915089833873,0.462312446310719,2.00861144238857
S-05,MAT-d96237b7-56a8-4a6c-b4f6-2e6885dfee21,843.15,101325,2.8266442748108,0.0715058086073128,0,0,7.69419849897241e-05,0.000217487621363782,5.61800395064972e-09,1.58800987029685e-08,0.0982712187214895,0.277777777777778,1.1643122215472e-07,3.29109647512864e-07,4.69337356615126e-11,1.32664975203098e-10,0.901651717197361,2.54864866428924
S-07,MAT-82d75533-10cc-41ea-baea-19f95ccb5f69,843.15,101325,,-1.58772407321986e-17,0,,0,,0,,0,,0,,0,,0,
S-06,MAT-bbdffa7b-d3ad-4e1c-8769-23d0da09fc41,843.15,101325,4.34470553068041,0.0715047354452011,0,0,0.141442961335504,0.614528016390181,0.0333180065272201,0.144756927230059,0,0,0.345850282620394,1.50261763568821,0.0170763032061619,0.0741915089833873,0.462312446310719,2.00861144238857
S-04,MAT-5879b00b-79ec-4439-aed7-4682246e5a69,295.198957303018,101325,2.8266442748108,0.0715058086073128,0,0,7.69419849897241e-05,0.000217487621363782,5.61800395064972e-09,1.58800987029685e-08,0.0982712187214895,0.277777777777778,1.1643122215472e-07,3.29109647512864e-07,4.69337356615126e-11,1.32664975203098e-10,0.901651717197361,2.54864866428924
S-03,MAT-3da5339c-bc0e-45b9-b4b3-64bbba7daacc,298.15,101325,0.833333333333333,0.0150127333333333,0,0,0,0,0,0,0,0,0,0,0,0,1,0.833333333333333
S-01,MAT-cb9c1196-6c79-4789-b210-2d1ed9a6ce10,298.15,101325,0.277777777777778,0.0255816166666667,0,0,0,0,0,0,1,0.277777777777778,0,0,0,0,0,0
S-02,MAT-6896f5ae-bd8c-4ad9-84b1-4e93e83201db,298.15,101325,1.94472651496052,0.0350416162790664,0,0,0.00013509624908996,0.000262725257676957,7.03892231910171e-09,1.36887788707045e-08,0,0,1.89167543455074e-07,3.67879137527029e-07,1.2788491243144e-10,2.48701180068827e-10,0.999864707416559,1.94446340788623
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-09
Target metric: Carbon monoxide mass_fraction
Observed target value: 0.111198666764929
Required target value: >= 0.13170751597274938
```

## Allowed Repair Actions

- `H-01` / GUID `AQ-cafc70c6-94a8-40f5-9440-f5c00ace4170`: `thermal_specification/outlet_temperature` (unit: `K`)
- `C-01` / GUID `RESF-c246df5a-2e3c-4719-b208-61f141d21d91`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
