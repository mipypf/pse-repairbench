# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-09`
- Required target: `Monochlorobenzene mole_fraction at least 0.909160496422`
- Faulty observed target value: `0.872291598205371`

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
      "column_specification/reflux_ratio": 1.49992826408384
    },
    "reboiler_duty": -940.523455848378,
    "reflux_ratio": 1.49992826408384,
    "supported_parameters": [
      "column_configuration/feed_stage",
      "column_specification/reflux_ratio"
    ],
    "tag": "DC-026",
    "type": "DWSIM.UnitOperations.UnitOperations.DistillationColumn"
  },
  {
    "condenser_duty": 161.981425787715,
    "feed_stage": 5,
    "feed_stage_name": "Stage5",
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
S-08,MAT-99357e52-6227-4aa9-8014-1b6bf38bbba1,409.557008270087,111325,11.94,1.40592775618822,0.0337996318081614,0.403567603789447,0,0,0,0,0.781653838752059,9.33294683469958,0.0672262582883894,0.802681523963369,0.11732027115139,1.4008040375476
S-07,MAT-0a9925f7-d336-415b-af26-5078e2f83083,353.843163453838,101325,1.81330711413261,0.142972420690128,0.97868388847741,1.77465445746306,0,0,0,0,0.0213117496272571,0.0386447472137183,6.09841399085972e-07,1.10582974745518e-06,3.75205393331927e-06,6.80362608989709e-06
S-04,MAT-77e65f24-f1bc-491e-ad6e-25874eeece7e,313.15,101325,28.7834648651974,2.14821850338123,0.508497870600895,14.6363305924686,0.489975022901661,14.1031788565143,9.64295687921799e-19,2.77557710529585e-17,0.00152679930283311,0.0439465740893048,4.13086632134283e-08,1.18900645623199e-06,2.65885947796474e-07,7.65311883654953e-06
S-05,MAT-eefb8ddc-9268-486f-b44d-3b839b76363a,313.15,101325,13.913720160151,1.55474856391246,0.156552835636793,2.17823234532845,0,0,0.0115291269388748,0.160413045918363,0.673549791040539,9.37158330646622,0.0576899555891801,0.80268189811939,0.100678290794613,1.40080956431855
S-06,MAT-290d212b-d770-40ce-88fb-2d6249bfb1fc,313.15,101325,14.8697267702229,0.593469939468767,0.0382422187482615,0.568651343873744,0,0,0.937659522732796,13.9427409065343,0.0234089149704129,0.34808416959742,0.000257514630268581,0.00382917219142877,0.000431828918260544,0.0064211780260152
S-03,MAT-f4678183-e7a6-412f-99a6-47d94c5ae20d,302.032020021921,101325,28.7834648651974,2.14821850338123,0.508497870600895,14.6363305924686,0.489975022901661,14.1031788565143,9.64295687921799e-19,2.77557710529585e-17,0.00152679930283311,0.0439465740893048,4.13086632134283e-08,1.18900645623199e-06,2.65885947796474e-07,7.65311883654953e-06
S-02,MAT-dd50b5c9-3730-4051-a95f-c905f4a24be5,313.15,101325,14.1031788565143,1,0,0,1,14.1031788565143,0,0,0,0,0,0,0,0
S-01,MAT-a5f5b467-6cb0-47b3-bd09-aec5aed0fbc1,313.15,101325,12.8021564976577,1,1,12.8021564976577,0,0,0,0,0,0,0,0,0,0
S-07,MAT-662800f5-c17e-4aa6-b329-e80fb6d31909,353.843163453838,101325,1.81330711413261,0.142972420690128,0.97868388847741,1.77465445746306,0,0,0,0,0.0213117496272571,0.0386447472137183,6.09841399085972e-07,1.10582974745518e-06,3.75205393331927e-06,6.80362608989709e-06
S-09,MAT-675ced55-ae0a-4506-9070-21c5e0edb2c3,402.938606474632,101325,10.4713914176088,1.19692774744461,0.0384855050239622,0.402996787010258,0,0,0,0,0.872291598205371,9.13410675509997,0.0246894997197287,0.258533415470221,0.0645333970509383,0.675754460028335
S-10,MAT-c5d3a2d6-1af4-4330-8ad7-d4b484a09ef3,443.360364505308,111325,1.46860858229122,0.209,0.000388686712957012,0.00057082864247123,0,0,0,0,0.135393672409241,0.198840309288137,0.370519420369426,0.544148000660106,0.493698220508375,0.725049443700501
S-11,MAT-355e8342-aea3-47dd-91ce-0d5c1af565df,313.15,101325,13.7533071142326,1.54889975347001,0.158378804983879,2.17823234532845,0,0,0,0,0.681405805064008,9.37158330646622,0.0583628280421903,0.80268189811939,0.101852561909922,1.40080956431855
S-12,MAT-48e23d4e-2022-468e-b6ba-c03e21c2914a,313.150000002938,101325,0.160413045918363,0.00584881044244666,0,0,0,0,1,0.160413045918363,0,0,0,0,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-09
Target metric: Monochlorobenzene mole_fraction
Observed target value: 0.872291598205371
Required target value: >= 0.9091604964224044
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
