# DWSIM Extraction Notes

These notes capture the current assumptions for deriving benchmark observations
from real DWSIM files. They are implementation reference notes for the current
artifact, not a standalone benchmark contract.

## File Formats

DWSIM `.dwxmz` files are ZIP archives, not plain XML files. A typical archive
contains at least one GUID-named `.xml` file and may contain a `.db` file.
Direct `.dwxml` files can be loaded as XML.

The XML root observed in real samples is `DWSIM_Simulation_Data`. Important
top-level sections include:

- `GeneralInfo`
- `SimulationObjects`
- `Settings`
- `GraphicObjects`
- `PropertyPackages`
- `Compounds`
- `ReactionSets`
- `Reactions`
- `Spreadsheet`
- `MessagesLog`

The `.db` entry must be recorded in metadata. Extraction code should preserve
whether it is present even when the current observation path does not read the
database entry directly.

## Topology Extraction

Topology cannot be reconstructed from `SimulationObjects` alone. Connection
data is primarily represented by `GraphicObjects`, especially input and output
connectors. The extractor should join simulation and graphic objects using
stable identifiers where possible and fall back to names only when necessary.

Topology fields:

- object GUID, name, tag, type, object class, and component description
- graphic object name and type
- input connectors and output connectors
- source object, source port, destination object, and destination port
- unresolved connector references

## Parameter Extraction

Unit operation parameters are heterogeneous. The initial schema should preserve
unit-specific data as semi-structured records rather than forcing all units into
one flat table.

Parameter fields:

- object GUID, name, tag, type, object class, and component description
- property package reference
- selected common stream conditions, such as temperature, pressure, flow, and
  composition when available
- unit-specific specification blocks
- unsupported or opaque fields retained as raw paths or summaries

## Audit Metadata

Each extracted instance should record:

- source format: `dwxmz` or `dwxml`
- DWSIM build/version if available
- archive entries
- whether a `.db` entry exists
- XML root element
- discovered top-level sections
- object count
- unsupported sections
- extractor version

This metadata is part of the benchmark contract, not just documentation.
