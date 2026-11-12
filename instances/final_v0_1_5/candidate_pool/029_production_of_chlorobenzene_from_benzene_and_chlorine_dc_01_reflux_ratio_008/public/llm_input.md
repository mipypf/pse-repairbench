# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-10`
- Required target: `P-dichlorobenzene mass_fraction at most 0.523517964664`
- Faulty observed target value: `not available in stream table`

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
    "feed_stage": 3,
    "feed_stage_name": "Stage3",
    "feed_stream_id": "MAT-355e8342-aea3-47dd-91ce-0d5c1af565df",
    "guid": "DC-a97989ca-ac4b-48d2-9654-2323021b0956",
    "kind": "unit_operation",
    "number_of_stages": 12,
    "observed_values": {
      "column_specification/reflux_ratio": 1.807499999915625
    },
    "reboiler_duty": -378.956893973127,
    "reflux_ratio": 1.807499999915625,
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
S-08,MAT-99357e52-6227-4aa9-8014-1b6bf38bbba1,411.073719246864,111325,11.94,1.40576655740524,0.0176042336035579,0.210194549226481,0,0,0,0,0.81443656573418,9.72437259486611,0.0494843217593464,0.590842801806596,0.118474878902916,1.41459005410082
S-07,MAT-0a9925f7-d336-415b-af26-5078e2f83083,354.318941549791,101325,2.06086944519554,0.163849453578035,0.959662553269233,1.9777392337309,0,0,0,0,0.0402286365515512,0.0829059678909685,1.78675180925388e-05,3.68226220983917e-05,9.09426611227645e-05,0.000187420951572678
S-04,MAT-77e65f24-f1bc-491e-ad6e-25874eeece7e,313.15,101325,29.034083359704,2.16941987449744,0.511122352214474,14.839968981203,0.485745621164946,14.1031788565143,0,0,0.00312485582986591,0.0907273246513838,1.98796097783445e-06,5.77186247462841e-05,5.18282973611058e-06,0.000150478710597387
S-05,MAT-eefb8ddc-9268-486f-b44d-3b839b76363a,313.15,101325,14.16436720693,1.57557755613987,0.154466999384178,2.18792730063013,0,0,0.0115428920505837,0.16349776163442,0.692391248186903,9.80728389018388,0.0417159451023506,0.590879964813825,0.0998829152759841,1.41477828966771
S-06,MAT-290d212b-d770-40ce-88fb-2d6249bfb1fc,313.15,101325,14.8696941378845,0.593842318357565,0.0378929621358317,0.563456756938256,0,0,0.937453720072402,13.9396500858986,0.0240383105339994,0.357442325232059,0.000185888078389696,0.00276409886953388,0.000429119179376789,0.00638087094603285
S-03,MAT-f4678183-e7a6-412f-99a6-47d94c5ae20d,302.423367995863,101325,29.034083359704,2.16941987449744,0.511122352214474,14.839968981203,0.485745621164946,14.1031788565143,0,0,0.00312485582986591,0.0907273246513838,1.98796097783445e-06,5.77186247462841e-05,5.18282973611058e-06,0.000150478710597387
S-02,MAT-dd50b5c9-3730-4051-a95f-c905f4a24be5,313.15,101325,14.1031788565143,1,0,0,1,14.1031788565143,0,0,0,0,0,0,0,0
S-01,MAT-a5f5b467-6cb0-47b3-bd09-aec5aed0fbc1,313.15,101325,12.8021564976577,1,1,12.8021564976577,0,0,0,0,0,0,0,0,0,0
S-07,MAT-662800f5-c17e-4aa6-b329-e80fb6d31909,354.318941549791,101325,2.06086944519554,0.163849453578035,0.959662553269233,1.9777392337309,0,0,0,0,0.0402286365515512,0.0829059678909685,1.78675180925388e-05,3.68226220983917e-05,9.09426611227645e-05,0.000187420951572678
S-09,MAT-675ced55-ae0a-4506-9070-21c5e0edb2c3,404.682450609377,101325,10.4637736295198,1.19676654852133,0.0200578027186103,0.209880307153104,0,0,0,0,0.907178340153449,9.49250879296917,0.0153187546111833,0.160291980537584,0.057445102516757,0.601092548859901
S-10,MAT-c5d3a2d6-1af4-4330-8ad7-d4b484a09ef3,441.742730236934,111325,1.47622637038024,0.209,0.000212872865310158,0.000314248537309256,0,0,0,0,0.157065373650944,0.231864046457149,0.291656306769632,0.43055073114104,0.551065446714114,0.813497344244742
S-11,MAT-355e8342-aea3-47dd-91ce-0d5c1af565df,313.15,101325,14.0008694452955,1.56961627406279,0.156270816550275,2.18792730063013,0,0,0,0,0.700476775996168,9.80728389018388,0.0422030908239322,0.590879964813825,0.101049316629625,1.41477828966771
S-12,MAT-48e23d4e-2022-468e-b6ba-c03e21c2914a,313.150000002938,101325,0.16349776163442,0.00596128207708689,0,0,0,0,1,0.16349776163442,0,0,0,0,0,0
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-10
Target metric: P-dichlorobenzene mass_fraction
Observed target value: 0.572180557888352
Required target value: <= 0.5235179646638837
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
