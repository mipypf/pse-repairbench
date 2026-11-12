# Reproducibility Requirements

PSE-RepairBench depends on executable process simulation. Reproducibility must
therefore be specified before large-scale data generation.

## DWSIM Environment

Each benchmark release should record:

- DWSIM version
- operating system and version
- execution mode, such as GUI, CLI, automation API, or containerized runner
- installed property packages and thermodynamic models
- solver settings and tolerances
- default unit system
- floating-point and convergence tolerances used by the evaluator

## Instance Metadata

Each instance should record:

- base flowsheet identifier and checksum
- faulty flowsheet identifier and checksum
- fault injector version
- observation extractor version
- executor version
- DWSIM runner version
- evaluator version

## Numerical Stability

Success criteria should use tolerances rather than exact equality. Repaired
flowsheets should be evaluated for:

- fatal simulation errors
- convergence status
- finite stream values
- material balance residual
- energy balance residual
- target purity, recovery, conversion, or duty bounds

If an instance is sensitive to solver initialization or platform differences, it
should be marked as unstable and excluded from the primary benchmark split until
the issue is resolved.

## Release Policy

The main benchmark split should include only instances that pass repeated runs
under the pinned environment. Experimental instances can be released separately
with an instability flag.
