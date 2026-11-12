# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `N-heptane`
- Required target: `mass_flow at least 0.665899418072`
- Faulty observed target value: `0.605408994313477`

## Observed Candidate Unit Parameters

```json
[
  {
    "calc_mode": "OutletPressure",
    "delta_p": 303975,
    "guid": "VALV-42381f53-f1a9-496e-b234-65aa1e9846e2",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 101325
    },
    "outlet_pressure": 101325,
    "outlet_temperature": 376.185885301826,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-010",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": -303975,
    "guid": "VALV-3bf55fc6-fa83-49f8-81b0-71e82f87b6b0",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 607950
    },
    "outlet_pressure": 607950,
    "outlet_temperature": 374.766487414927,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-005",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  },
  {
    "calc_mode": "OutletPressure",
    "delta_p": -1114575,
    "guid": "VALV-41032154-7329-4ed4-91c5-02a2695c7a98",
    "kind": "unit_operation",
    "observed_values": {
      "pressure_specification/outlet_pressure": 1215900
    },
    "outlet_pressure": 1215900,
    "outlet_temperature": 374.766306363664,
    "supported_parameters": [
      "pressure_specification/outlet_pressure"
    ],
    "tag": "VALV-018",
    "type": "DWSIM.UnitOperations.UnitOperations.Valve"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,2-methyl-1-propanol_mole_fraction,2-methyl-1-propanol_molar_flow,n-heptane_mole_fraction,n-heptane_molar_flow
Recycle from HPC,MAT-02e64f2a-1339-4522-a8e9-0597c918fda8,439.79705709113,1215900,14.337546136752,1.26679729620793,0.45430629008007,6.51363739423964,0.54569370991993,7.82390874251236
MSTR-024,MAT-f016d390-e04c-4c7e-81ce-cf05ac17f0f8,439.79705709113,1215900,14.337546136752,1.26679729620793,0.45430629008007,6.51363739423964,0.54569370991993,7.82390874251236
MSTR-022,MAT-8a941a1b-8b3f-4004-9d20-54cb77ca5083,439.79705709113,1215900,14.337546136752,1.26679729620793,0.45430629008007,6.51363739423964,0.54569370991993,7.82390874251236
N-HEPTANE,MAT-3d924e79-a036-4601-94db-0a610718142a,425.34587257004,1215900,5.5480934426546,0.555773454703496,0.0011589552660088,0.00642999211167344,0.99884104473399,5.54166345054292
MSTR-019,MAT-efa95d0c-b0da-4131-b870-dafcdf130eb5,460.019480927645,1215900,19.885639579407,1.82235960076462,0.328285308492,6.52816332388635,0.671714691508,13.3574762555206
MSTR-016,MAT-f46baff6-aeb6-4a31-abaa-66502f272aa9,363.069913419241,101325,19.885639579407,1.82235960076462,0.328285308492,6.52816332388635,0.671714691508,13.3574762555206
ISOBUTANOL,MAT-079b0cb0-78bf-426e-9188-1df25a4174e3,380.714514964401,101325,22.229659460303,1.64830881992442,0.999,22.2074298008427,0.001,0.022229659460303
Feed2,MAT-193819dc-bb22-45ad-b234-717109db823d,313.15,101325,27.7777777777778,2.20386666666667,0.8,22.2222222222223,0.2,5.55555555555556
feed,MAT-6f0f030d-51a9-42d5-bdde-54fba1d7def0,313.15,101325,27.7777777777778,2.20386666666667,0.8,22.2222222222223,0.2,5.55555555555556
MSTR-003,MAT-ef38e397-d8d2-49e2-971d-3190f3694e81,363.353451077044,101325,36.70581686561,3.3518513390021,0.34076048923819,12.5078921130127,0.65923951076181,24.1979247525973
Isobutanol,MAT-839610a3-b7ec-440a-abb0-e6d4fdaef187,380.714514964401,101325,21.643514910983,1.60484674025919,0.999,21.621871396072,0.001,0.021643514910983
MSTR-006,MAT-bfccbeaf-c679-4829-8706-b5e71b7ebd39,427.383535419557,607950,36.70581686561,3.3518513390021,0.34076048923819,12.5078921130127,0.65923951076181,24.1979247525973
Recyle back to first column,MAT-686107bb-8974-4dda-ba2a-ea058103d24f,411.193789852416,405300,30.662479168473,2.68318012040365,0.48683129863295,14.9274545528935,0.51316870136705,15.7350246155795
N-heptane,MAT-0600d28e-d1ae-49c5-9383-a1c13f0ddaa9,426.488641634606,405300,6.0433376971374,0.605408994313477,0.001,0.0060433376971374,0.999,6.03729435944026
MSTR-011,MAT-2e801a04-d8e2-447b-853b-6cee906613c3,403.382696025558,101325,30.662479168473,2.68318012040365,0.48683129863295,14.9274545528935,0.51316870136705,15.7350246155795
Recycle stream,MAT-52f17ee4-757a-451b-bc36-fe11ed3cd4fe,403.382696025558,101325,30.662479168473,2.68318012040365,0.48683129863295,14.9274545528935,0.51316870136705,15.7350246155795
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: N-heptane
Target metric: mass_flow
Observed target value: 0.605408994313477
Required target value: >= 0.6658994180720914
```

## Allowed Repair Actions

- `VALV-010` / GUID `VALV-42381f53-f1a9-496e-b234-65aa1e9846e2`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `VALV-005` / GUID `VALV-3bf55fc6-fa83-49f8-81b0-71e82f87b6b0`: `pressure_specification/outlet_pressure` (unit: `Pa`)
- `VALV-018` / GUID `VALV-41032154-7329-4ed4-91c5-02a2695c7a98`: `pressure_specification/outlet_pressure` (unit: `Pa`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
