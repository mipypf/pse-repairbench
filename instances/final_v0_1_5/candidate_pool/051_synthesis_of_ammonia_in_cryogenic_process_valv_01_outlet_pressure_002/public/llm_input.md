# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `S-10`
- Required target: `mass_flow at most 0.0120975022782`
- Faulty observed target value: `0.0403234340838281`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-08371460-cc5b-4824-97db-084b0bd09799",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 7500000,
    "guid": "COMP-34fb4dec-e0e4-4049-8db8-b3f2d85d9861",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 9000000
    },
    "outlet_temperature": 398.521739053952,
    "p_out": 9000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "flash_pressure": 1500000,
    "flash_temperature": 238.15,
    "guid": "SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/pressure": 1500000,
      "separator_specification/temperature": 238.15
    },
    "override_p": "true",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/pressure",
      "separator_specification/temperature"
    ],
    "tag": "FS-03",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 1300000,
    "guid": "VALV-3b0e6130-7ccb-4e28-834d-982064cac0ab",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 200000
    },
    "outlet_pressure": 200000,
    "outlet_temperature": 235.724569984375,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "flash_pressure": 101325,
    "flash_temperature": 238.15,
    "guid": "SEP-e526b085-c1b6-4412-953b-befa1a9e4ce4",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/temperature": 238.15
    },
    "override_p": "false",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/temperature"
    ],
    "tag": "FS-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 7500000,
    "guid": "VALV-aee346c3-282e-418d-8f72-9fc2d9e5d592",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 750000
    },
    "outlet_pressure": 750000,
    "outlet_temperature": 301.52179111604,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-5099e0d5-1132-46d2-9178-74973f950d06",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 238.15
    },
    "outlet_temperature": 238.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "COOL-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 7500000,
    "guid": "COMP-c09d247d-1b08-4373-8e69-a2cc10175777",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 9000000
    },
    "outlet_temperature": 240.129459890534,
    "p_out": 9000000,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "COMP-02",
    "type": "DWSIM.UnitOperations.UnitOperations.Compressor"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "AQ-b0072ae5-268e-446a-8821-bf05980a683f",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 323.15
    },
    "outlet_temperature": 323.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "HEAT-01",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,ammonia_mole_fraction,ammonia_molar_flow,argon_mole_fraction,argon_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methane_mole_fraction,methane_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow
S-11,MAT-285cb3bd-fb74-43f3-b643-b1b96cc37228,238.15,1500000,32.9354110123735,0.702644471307151,0.0725418861240084,2.38919683510701,0.346703574882709,11.4188247382212,0.218746080190811,7.20449205842999,0.362008457744591,11.9228973457736,1.05788093743811e-09,3.48417434766792e-08
S-22,MAT-8a67c0db-a31b-40e1-89b8-a5122b4bec4e,236.851178472937,200000,637.274147571226,10.872613230592,0.998209994426691,636.133423295348,0.00135458029401829,0.863239002187284,6.68499854843874e-07,0.000426017675147118,0.000434756779433707,0.277059256014427,1.6846175504692e-15,1.07356321345879e-12
S-21,MAT-6567acd2-cf15-4019-9a28-2fbc9357cf9e,236.851178472937,200000,6.44487926559009,0.158103700697383,0.437793382439609,2.82152549309759,0.341318371598555,2.1997556960805,0.0073252678354765,0.0472104667877565,0.213562978100817,1.37638760945962,2.55424425901123e-11,1.6461795864154e-10
S-20,MAT-29553b4f-03da-40cd-b729-7e38f0cb410e,236.851178472937,200000,643.719026836816,11.0307215213651,0.992598599416406,638.954604455915,0.00475860344643699,3.06320357964274,7.40089742182207e-05,0.047640984860944,0.00256878816268156,1.65357781623131,2.57421651001311e-13,1.6570721466929e-10
S-05,MAT-8a3f4d4f-22bd-439a-adbf-ca848e6346f3,323.157309114577,9000000,1073.52896488971,18.5344623338594,0.964351940017087,1035.25973995593,0.0152615511772807,16.3837172379575,0.00678336423898889,7.28213798995164,0.0136031445339361,14.6033696707616,3.27074339811305e-11,3.51123777459616e-08
S-18,MAT-3c0de8c0-9c4d-42ae-a114-1b67c4e18e1a,323.15,9000000,394.537468061274,6.76076480341732,0.992598599416406,391.617338214916,0.00475860344643699,1.8774473552649,7.40089742182207e-05,0.0291993133018689,0.00256878816268156,1.01348317769016,2.57421651001311e-13,1.0156248641021e-10
S-17,MAT-9a5fba2f-2b28-4980-b058-c0ea540b8569,323.15,9000000,394.537468061274,6.76076480341732,0.992598599416406,391.617338214916,0.00475860344643699,1.8774473552649,7.40089742182207e-05,0.0291993133018689,0.00256878816268156,1.01348317769016,2.57421651001311e-13,1.0156248641021e-10
S-16,MAT-11ca46a1-8306-4987-8ee0-fafa9c4c73ee,240.312701738268,9000000,394.537468061274,6.76076480341732,0.992598599416406,391.617338214916,0.00475860344643699,1.8774473552649,7.40089742182207e-05,0.0291993133018689,0.00256878816268156,1.01348317769016,2.57421651001311e-13,1.0156248641021e-10
S-19,MAT-efd98ad5-11a6-41c8-bbfb-704ce24ef8ea,238.15,750000,643.719026836816,11.0307215213651,0.992598599416406,638.954604455915,0.00475860344643699,3.06320357964274,7.40089742182207e-05,0.047640984860944,0.00256878816268156,1.65357781623131,2.57421651001311e-13,1.6570721466929e-10
S-15,MAT-336dec11-4c27-4f38-a775-62a7f5701de4,238.15,750000,394.537468061274,6.76076480341732,0.992598599416406,391.617338214916,0.00475860344643699,1.8774473552649,7.40089742182207e-05,0.0291993133018689,0.00256878816268156,1.01348317769016,2.57421651001311e-13,1.0156248641021e-10
S-01,MAT-5b9d6902-e4a5-461e-ba47-db69fd39a412,323.15,9000000,1388.88888888889,12.1873219444445,0,0,0.01,13.8888888888889,0.74,1027.77777777778,0.01,13.8888888888889,0.24,333.333333333334
S-03,MAT-3450e369-7948-4509-b8d3-194eb9db1db0,323.15,9000000,75.5381955795868,1.10255725838266,0.332461068572138,25.1135092204006,0.140439452367465,10.6085428200236,0.365891700933353,27.6387988660513,0.161207775829653,12.1773444995705,2.29739153194269e-09,1.73540810862773e-07
S-04,MAT-06ccd223-a4f1-499f-90d0-0a087e44f3cb,323.15,9000000,678.653396295944,11.7682989753069,0.947895808495719,643.29270977031,0.0213976745584625,14.5216045119359,0.0106867939898489,7.25262903672607,0.0200197229043759,13.5864529419584,5.15936599494075e-11,3.50142125520034e-08
S-06,MAT-2d628033-a1c1-49cd-9f43-1390f4a5591c,283.181117450624,750000,1073.52896488971,18.5344623338594,0.964351940017087,1035.25973995593,0.0152615511772807,16.3837172379575,0.00678336423898889,7.28213798995164,0.0136031445339361,14.6033696707616,3.27074339811305e-11,3.51123777459616e-08
S-07,MAT-7767eccd-baaa-42b1-b6c1-fec751c049d3,238.15,750000,1073.52896488971,18.5344623338594,0.964351940017087,1035.25973995593,0.0152615511772807,16.3837172379575,0.00678336423898889,7.28213798995164,0.0136031445339361,14.6033696707616,3.27074339811305e-11,3.51123777459616e-08
S-09,MAT-f45418a5-4b6a-4703-baf7-7954dae45958,238.15,750000,35.2724699916232,0.742967494755769,0.1329552699392,4.6896607691586,0.324399550329,11.4423734042757,0.204262844790745,7.20485506328512,0.338382333953232,11.9355807200608,9.87823287288237e-10,3.48429672579009e-08
S-08,MAT-da108e3c-6dee-4710-bc72-df8b24132c36,238.15,750000,1038.25649489809,17.7914863247824,0.992598599416406,1030.57194267083,0.00475860344643699,4.94065093490765,7.40089742182207e-05,0.0768402981628129,0.00256878816268156,2.66706099392146,2.57421651001311e-13,2.672697010795e-10
S-10,MAT-fd0ef933-59a8-4ad2-a260-1f404c3a37a5,238.15,1500000,2.33705897924966,0.0403234340838281,0.984302147094663,2.3003721711623,0.0100906927108632,0.023582544006772,0.000164738538772266,0.000385003681266192,0.00544242165513191,0.0127192603979888,5.69173888485718e-13,1.33019294683999e-12
S-12,MAT-9286e475-040c-4236-8942-be10d4a46510,401.652527775285,9000000,32.9354110123735,0.702644471307151,0.0725418861240084,2.38919683510701,0.346703574882709,11.4188247382212,0.218746080190811,7.20449205842999,0.362008457744591,11.9228973457736,1.05788093743811e-09,3.48417434766792e-08
S-13,MAT-ebedbc29-9b0c-4301-a194-e7e8fe722681,323.15,9000000,32.9354110123735,0.702644471307151,0.0725418861240084,2.38919683510701,0.346703574882709,11.4188247382212,0.218746080190811,7.20449205842999,0.362008457744591,11.9228973457736,1.05788093743811e-09,3.48417434766792e-08
S-14,MAT-a72f8b87-748a-40b8-8241-665f96d8f0f2,323.15,9000000,32.9354110123735,0.702644471307151,0.0725418861240084,2.38919683510701,0.346703574882709,11.4188247382212,0.218746080190811,7.20449205842999,0.362008457744591,11.9228973457736,1.05788093743811e-09,3.48417434766792e-08
S-02,MAT-0983118c-fa43-46b3-8c87-82bfc5ae3c89,322.919459904616,9000000,1421.60719342708,12.881910874509,0.0016693088986948,2.37310153843636,0.0176777462681078,25.1308112583208,0.728053179785038,1035.00563757987,0.0181233675538588,25.7643096836886,0.2344763974943,333.333333366766
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: S-10
Target metric: mass_flow
Observed target value: 0.0403234340838281
Required target value: <= 0.012097502278219402
```

## Allowed Repair Actions

- `COOL-02` / GUID `RESF-08371460-cc5b-4824-97db-084b0bd09799`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-01` / GUID `COMP-34fb4dec-e0e4-4049-8db8-b3f2d85d9861`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `FS-03` / GUID `SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f`: `separator_specification/pressure` (unit: `Pa`)
- `FS-03` / GUID `SEP-113c45da-a2c8-48a9-9265-85fe92a65d7f`: `separator_specification/temperature` (unit: `K`)
- `VALV-02` / GUID `VALV-3b0e6130-7ccb-4e28-834d-982064cac0ab`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `FS-01` / GUID `SEP-e526b085-c1b6-4412-953b-befa1a9e4ce4`: `separator_specification/temperature` (unit: `K`)
- `VALV-01` / GUID `VALV-aee346c3-282e-418d-8f72-9fc2d9e5d592`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `COOL-01` / GUID `RESF-5099e0d5-1132-46d2-9178-74973f950d06`: `thermal_specification/outlet_temperature` (unit: `K`)
- `COMP-02` / GUID `COMP-c09d247d-1b08-4373-8e69-a2cc10175777`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `HEAT-01` / GUID `AQ-b0072ae5-268e-446a-8821-bf05980a683f`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
