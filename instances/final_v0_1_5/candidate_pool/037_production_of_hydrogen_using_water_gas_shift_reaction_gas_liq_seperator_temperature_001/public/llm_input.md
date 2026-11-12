# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `Product Gas`
- Required target: `temperature at least 289.15`
- Faulty observed target value: `268.15`

## Observed Candidate Unit Parameters

```json
[
  {
    "flash_pressure": 101325,
    "flash_temperature": 268.15,
    "guid": "SEP-47cfeb93-74c6-42d1-a9ee-4821b7eb45b4",
    "kind": "unit_operation",
    "observed_values": {
      "separator_specification/temperature": 268.15
    },
    "override_p": "false",
    "override_t": "true",
    "supported_parameters": [
      "separator_specification/temperature"
    ],
    "tag": "Gas-liq Seperator",
    "type": "DWSIM.UnitOperations.UnitOperations.Vessel"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-fba3bd36-c991-44f8-b5cd-77f887acde02",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 333.15
    },
    "outlet_temperature": 333.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler 3",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-fc7510a0-ca1f-43c0-9d8f-f9ccee0b5067",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 471.15
    },
    "outlet_temperature": 471.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler 2",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  },
  {
    "calc_mode": "OutletTemperature",
    "guid": "RESF-9e66f56a-06c1-4d8e-9b10-6efb7e064523",
    "kind": "unit_operation",
    "observed_values": {
      "thermal_specification/outlet_temperature": 589.15
    },
    "outlet_temperature": 589.15,
    "supported_parameters": [
      "thermal_specification/outlet_temperature"
    ],
    "tag": "Cooler 1",
    "type": "DWSIM.UnitOperations.UnitOperations.Cooler"
  }
]
```

## Faulty Stream Table

```csv
stream_tag,stream_id,temperature,pressure,molar_flow,mass_flow,carbon dioxide_mole_fraction,carbon dioxide_molar_flow,carbon monoxide_mole_fraction,carbon monoxide_molar_flow,hydrogen_mole_fraction,hydrogen_molar_flow,methane_mole_fraction,methane_molar_flow,nitrogen_mole_fraction,nitrogen_molar_flow,oxygen_mole_fraction,oxygen_molar_flow,water_mole_fraction,water_molar_flow
Flue Gases from Steam Methane Reforming(SMR),MAT-25e172e1-f550-4d6f-b0f7-4af44021c572,617.15,405300,4.709,0.08495694112,0.0556381397324273,0.262,0.0766617116160544,0.361,0.318326608621788,1.499,0.016139307708643,0.0759999999999999,0.283499681461032,1.335,0.00743257591845403,0.035,0.242301974941601,1.141
High Temperature WGSR Inlet,MAT-10619d53-ce3a-4b09-819d-9ab51c5399aa,589.15,405300,4.709,0.08495694112,0.0556381397324273,0.262,0.0766617116160544,0.361,0.318326608621788,1.499,0.016139307708643,0.0759999999999999,0.283499681461032,1.335,0.00743257591845403,0.035,0.242301974941601,1.141
Overhead,MAT-d56c2931-3f04-46db-b2c9-54d71fafae0e,698.15,405300,4.70899239638847,0.08495694112,0.132299851348482,0.622998994043325,0,0,0.394988320237843,1.85999699666225,0.016139307708643,0.0759998772829737,0.283499681461032,1.33499784437855,0.00743257591845403,0.0349999434855801,0.165640263325547,0.779998740535783
Dummy,MAT-9017d75b-e1aa-490b-9691-05a3f65b1ceb,698.15,405300,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
Low Temperature WGSR Inlet,MAT-35f5024a-e6f6-4cca-8e90-8af7e866484f,471.15,405300,4.70899239638847,0.08495694112,0.132299851348482,0.622998994043325,0,0,0.394988320237843,1.85999699666225,0.016139307708643,0.0759998772829737,0.283499681461032,1.33499784437855,0.00743257591845403,0.0349999434855801,0.165640263325547,0.779998740535783
Vapor,MAT-c90f91bd-0409-47d7-ba4a-5f5bb36890cf,473.15,405300,4.70899239634537,0.08495694112,0.132299851362854,0.622998994105304,0,0,0.394988320247864,1.85999699669242,0.0161393077083757,0.0759998772810193,0.283499681456336,1.33499784434422,0.00743257591833092,0.03499994348468,0.165640263306239,0.779998740437724
Dummy 2,MAT-f5b6aa76-6635-4022-bec8-35d298ecbbf6,473.15,405300,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
Cooled Vapor,MAT-11a34680-07b7-46c8-aca6-808fa8a2098d,333.15,405300,4.70899239634537,0.08495694112,0.132299851362854,0.622998994105304,0,0,0.394988320247864,1.85999699669242,0.0161393077083757,0.0759998772810193,0.283499681456336,1.33499784434422,0.00743257591833092,0.03499994348468,0.165640263306239,0.779998740437724
Product Gas,MAT-9e3e51c1-c601-496d-9f80-b44701525e2a,268.15,405300,3.93201134074547,0.0709513926990497,0.158362252639809,0.622682173325728,0,0,0.473039557793786,1.85999690586639,0.0193284992322009,0.0759998781806039,0.339520340904651,1.33499783085086,0.00890127474270408,0.0349999132354037,0.000848074686848559,0.0033346392864877
Water,MAT-bc051748-71c5-4e69-8dd8-9dba4e54a5b3,268.15,405300,0.776981055599903,0.014005548421861,0.000407768459298838,0.000316828367946357,0,0,1.46144560925532e-07,1.13551555218104e-07,3.73052857436125e-11,2.8985500296528e-11,3.83592749133985e-08,2.98044299142592e-08,3.94821788802802e-08,3.06769050237843e-08,0.999592007517381,0.776664053170081
```

## Faulty Simulator Log

```text
DWSIM headless status: success
Solved after calculation: True
Exception count: 0
Messages log count: 0
Target stream: Product Gas
Target metric: temperature
Observed target value: 268.15
Required target value: >= 289.15
```

## Allowed Repair Actions

- `Gas-liq Seperator` / GUID `SEP-47cfeb93-74c6-42d1-a9ee-4821b7eb45b4`: `separator_specification/temperature` (unit: `K`)
- `Cooler 3` / GUID `RESF-fba3bd36-c991-44f8-b5cd-77f887acde02`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Cooler 2` / GUID `RESF-fc7510a0-ca1f-43c0-9d8f-f9ccee0b5067`: `thermal_specification/outlet_temperature` (unit: `K`)
- `Cooler 1` / GUID `RESF-9e66f56a-06c1-4d8e-9b10-6efb7e064523`: `thermal_specification/outlet_temperature` (unit: `K`)

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
