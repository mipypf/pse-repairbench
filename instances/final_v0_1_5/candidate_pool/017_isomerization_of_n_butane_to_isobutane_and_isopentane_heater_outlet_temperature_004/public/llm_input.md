# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Reactor Output 2`
- Required target: `mass_flow at least 0.214401735372`
- Faulty observed target value: `0.187162875096727`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 0,
    "guid": "RESF-0e30f3a3-019c-4936-9359-414547f28fbf",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 329.928
    },
    "outlet_temperature": 329.928,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": 219575.48333333,
    "guid": "BB-93a5650f-6358-4ec5-a663-352683b8b162",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 861845
    },
    "outlet_temperature": 330.108678986212,
    "pout": 861845,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "pump",
    "type": "DWSIM.UnitOperations.UnitOperations.Pump"
  },
  {
    "calc_mode": "OutletTemperature",
    "delta_p": 0,
    "guid": "AQ-6c7ba34b-bb9b-4a44-805a-1db1e6e9b834",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 377.039
    },
    "outlet_temperature": 377.039,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Heater",
    "type": "DWSIM.UnitOperations.UnitOperations.Heater"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,isobutane_mole_fraction,isobutane_molar_flow,isopentane_mole_fraction,isopentane_molar_flow,n-butane_mole_fraction,n-butane_molar_flow,propane_mole_fraction,propane_molar_flow
Reactor Output 2,MAT-8250e372-d697-444b-a620-b1cadd3dc778,342.076718288712,861845,3.20925595744941,0.187162875096727,0.433535938449951,1.39132779323893,0.0140865145456471,0.0452072307253157,0.55237211876253,1.7727035128676,5.42824187199172e-06,1.74206175661658e-05
Reactor Output1,MAT-a302881c-d42f-4cb5-9667-7c91def1dc04,342.076718288712,861845,24.4907440462677,1.42570420057911,0.494991765833552,12.1227166420396,0.00655695187392976,0.160584630068109,0.498439125298724,12.2071450403366,1.21569937933192e-05,0.000297733823364244
R4,MAT-dbb1da71-fd4c-4d82-8ae9-610b5bda2ea9,377.039,861845,27.7,1.61286707567584,0.2392941229449,6.62844720557373,0.0074293096094845,0.205791876182721,0.75326519002947,20.8654457638163,1.1377416141187e-05,0.00031515442711088
R3,MAT-3174a79f-fff4-4d76-bbcb-f785cc13dbb2,308.217473912812,861845,27.7,1.61286707567584,0.2392941229449,6.62844720557373,0.0074293096094845,0.205791876182721,0.75326519002947,20.8654457638163,1.1377416141187e-05,0.00031515442711088
R2,MAT-f77c0a0f-967f-4002-9935-d489e6ba142a,329.928,642269.51666667,27.7,1.61286707567584,0.2392941229449,6.62844720557373,0.0074293096094845,0.205791876182721,0.75326519002947,20.8654457638163,1.1377416141187e-05,0.00031515442711088
B1,MAT-dcb72175-bc2b-4d52-9554-88cc645c2b05,367.31873636037,650865,0.61370377648108,0.0438475704986469,0.00010354650107273,6.35468787497366e-05,0.95,0.583018587657026,0.049896453498924,0.0306216419453023,3.6090312045192e-15,2.21487607965149e-15
D1,MAT-4e90a53a-f0ec-483d-b1b9-cf252f49c04a,321.236129493284,620528,8.7896775919274,0.509109187800306,0.90567423290654,7.96058451056465,1.0777491590438e-10,9.47306763296589e-10,0.08,0.703174207354192,0.014325766985684,0.12591887306124
R1,MAT-976ba279-5a47-4eae-9f29-37b68d7c0871,332.826614901795,642269.51666667,27.7,1.61286707567584,0.2392941229449,6.62844720557373,0.0074293096094845,0.205791876182721,0.75326519002947,20.8654457638163,1.1377416141187e-05,0.00031515442711088
Feed,MAT-8b48a7ff-c28f-4b8f-bac6-050943950ece,298.15,101325,12.5998,0.73939737966736,0.2,2.51996,0.05,0.62999,0.74,9.323852,0.01,0.125998
Recycle,MAT-3ce0ae10-0f11-4e6f-88d1-32b9add72a3d,342.076718288712,861845,24.4907440462677,1.42570420057911,0.494991765833552,12.1227166420396,0.00655695187392976,0.160584630068109,0.498439125298724,12.2071450403366,1.21569937933192e-05,0.000297733823364244
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Reactor Output 2
Target metric: mass_flow
Observed target value: 0.187162875096727
Required target value: >= 0.2144017353717548
```

## Allowed Repair Actions

- `Cooler` / GUID `RESF-0e30f3a3-019c-4936-9359-414547f28fbf`: `thermal_specification/outlet_temperature` (unit: `K`)
- `pump` / GUID `BB-93a5650f-6358-4ec5-a663-352683b8b162`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `Heater` / GUID `AQ-6c7ba34b-bb9b-4a44-805a-1db1e6e9b834`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
