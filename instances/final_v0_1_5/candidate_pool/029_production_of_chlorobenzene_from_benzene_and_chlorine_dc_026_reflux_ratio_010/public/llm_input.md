# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-10`
- Required target: `Monochlorobenzene mole_fraction at most 0.179742587441`
- Faulty observed target value: `0.213959306134652`

## Observed Candidate Unit Parameters

```json
[
  {
    "condenser_duty": 943.632708542232,
    "feed_stage": 5,
    "feed_stage_name": "Stage5",
    "feed_stream_id": "MAT-99357e52-6227-4aa9-8014-1b6bf38bbba1",
    "guid": "DC-4c54c848-290b-4835-8d3d-f19fe55a2979",
    "kind": "unit_operation",
    "number_of_stages": 7,
    "observed_values": {
      "column_specification/reflux_ratio": 1.0499999999899619
    },
    "reboiler_duty": -940.523455848378,
    "reflux_ratio": 1.0499999999899619,
    "supported_parameters": [
      "column_configuration/feed_stage",
      "column_specification/reflux_ratio"
    ],
    "tag": "DC-026",
    "type": "DWSIM.UnitOperations.UnitOperations.DistillationColumn"
  },
  {
    "condenser_duty": 161.981425787715,
    "feed_stage": 3,
    "feed_stage_name": "Stage3",
    "feed_stream_id": "MAT-355e8342-aea3-47dd-91ce-0d5c1af565df",
    "guid": "DC-a97989ca-ac4b-48d2-9654-2323021b0956",
    "kind": "unit_operation",
    "number_of_stages": 12,
    "observed_values": {
      "column_specification/reflux_ratio": 1.20473065575101
    },
    "reboiler_duty": -378.956893973127,
    "reflux_ratio": 1.20473065575101,
    "supported_parameters": [
      "column_configuration/feed_stage",
      "column_specification/reflux_ratio"
    ],
    "tag": "DC-01",
    "type": "DWSIM.UnitOperations.UnitOperations.DistillationColumn"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-65f74fa1-414f-406e-8488-b97858948dce",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 313.15
    },
    "outlet_temperature": 313.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HE-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,benzene_mole_fraction,benzene_molar_flow,chlorine_mole_fraction,chlorine_molar_flow,hydrogen chloride_mole_fraction,hydrogen chloride_molar_flow,monochlorobenzene_mole_fraction,monochlorobenzene_molar_flow,o-dichlorobenzene_mole_fraction,o-dichlorobenzene_molar_flow,p-dichlorobenzene_mole_fraction,p-dichlorobenzene_molar_flow
S-08,MAT-99357e52-6227-4aa9-8014-1b6bf38bbba1,411.809755809286,111325,11.94,1.40525679076818,0.0100261247472401,0.119711929482047,0,0,0,0,0.830832254955954,9.92013712417409,0.0584560628333107,0.69796539022973,0.100685557463495,1.20218555611413
S-07,MAT-0a9925f7-d336-415b-af26-5078e2f83083,355.202497465552,101325,2.142322321138,0.172906176478956,0.924792115315159,1.9812027910521,0,0,0,0,0.0749955837136495,0.160664712976525,4.82721893878684e-05,0.000103414588815831,0.000164028781803658,0.000351402520567052
S-04,MAT-77e65f24-f1bc-491e-ad6e-25874eeece7e,313.15,101325,29.0965206967767,2.17669198118623,0.509791859615045,14.8331693943374,0.484703274439153,14.1031788565143,0,0,0.00548759172750406,0.159669826274782,4.3105594058732e-06,0.000125422280967675,1.29636588919031e-05,0.000377197369254213
S-05,MAT-eefb8ddc-9268-486f-b44d-3b839b76363a,313.15,101325,14.2465654912703,1.58415123427583,0.147468490160053,2.10091950296393,0,0,0.0115286150990501,0.164243170032265,0.707594956262906,10.080797885692,0.0489990727866669,0.698068499466768,0.0844088656913246,1.20253643311529
S-06,MAT-290d212b-d770-40ce-88fb-2d6249bfb1fc,313.15,101325,14.8499328717479,0.592540746910402,0.0362168416338644,0.537817667089611,0,0,0.938650985644863,13.9389041268262,0.0245499908488777,0.364565716107859,0.00021926716502808,0.00325610268164546,0.000362914707366273,0.00538925904255918
S-03,MAT-f4678183-e7a6-412f-99a6-47d94c5ae20d,302.606301125619,101325,29.0965206967767,2.17669198118623,0.509791859615045,14.8331693943374,0.484703274439153,14.1031788565143,0,0,0.00548759172750406,0.159669826274782,4.3105594058732e-06,0.000125422280967675,1.29636588919031e-05,0.000377197369254213
S-02,MAT-dd50b5c9-3730-4051-a95f-c905f4a24be5,313.15,101325,14.1031788565143,1,0,0,1,14.1031788565143,0,0,0,0,0,0,0,0
S-01,MAT-a5f5b467-6cb0-47b3-bd09-aec5aed0fbc1,313.15,101325,12.8021564976577,1,1,12.8021564976577,0,0,0,0,0,0,0,0,0,0
S-07,MAT-662800f5-c17e-4aa6-b329-e80fb6d31909,355.202497465552,101325,2.142322321138,0.172906176478956,0.924792115315159,1.9812027910521,0,0,0,0,0.0749955837136495,0.160664712976525,4.82721893878684e-05,0.000103414588815831,0.000164028781803658,0.000351402520567052
S-09,MAT-675ced55-ae0a-4506-9070-21c5e0edb2c3,405.647803644903,101325,10.4430863328496,1.1962567836848,0.011439260356981,0.119461183491896,0,0,0,0,0.919254941261741,9.59985871349492,0.0193049323865705,0.201603075562779,0.0500008659947074,0.522163360299972
S-10,MAT-c5d3a2d6-1af4-4330-8ad7-d4b484a09ef3,438.585958301873,111325,1.49691366705043,0.209,0.000167510772600496,0.000250749164883859,0,0,0,0,0.213959306134652,0.320278609545588,0.331590416667616,0.496362226572702,0.454282766425131,0.680022081767257
S-11,MAT-355e8342-aea3-47dd-91ce-0d5c1af565df,313.15,101325,14.082322321238,1.57816277390787,0.149188426101814,2.10091950296393,0,0,0,0,0.715847688735886,10.080797885692,0.0495705526079309,0.698068499466768,0.0853933325543691,1.20253643311529
S-12,MAT-48e23d4e-2022-468e-b6ba-c03e21c2914a,313.150000002938,101325,0.164243170032265,0.00598846036795621,0,0,0,0,1,0.164243170032265,0,0,0,0,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-10
Target metric: Monochlorobenzene mole_fraction
Observed target value: 0.213959306134652
Required target value: <= 0.179742587440851
```

## Allowed Repair Actions

- `DC-026` / GUID `DC-4c54c848-290b-4835-8d3d-f19fe55a2979`: `column_specification/reflux_ratio` (unit: `null`)
- `DC-026` / GUID `DC-4c54c848-290b-4835-8d3d-f19fe55a2979`: `column_configuration/feed_stage` (unit: `null`)
- `DC-01` / GUID `DC-a97989ca-ac4b-48d2-9654-2323021b0956`: `column_specification/reflux_ratio` (unit: `null`)
- `DC-01` / GUID `DC-a97989ca-ac4b-48d2-9654-2323021b0956`: `column_configuration/feed_stage` (unit: `null`)
- `HE-01` / GUID `AQ-65f74fa1-414f-406e-8488-b97858948dce`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
