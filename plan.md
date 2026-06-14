# Plan

Rebuild paper 75 `deformable_memory_under_action` as a real ICLR-main-gated robotics artifact, not a polished template.

## Executed v4 Scope

- Built a local deformable manipulation benchmark with mass-spring rope, cloth-strip, elastic-band, and sheet objects.
- Added hidden strain/contact memory, partial observation, material shift, fixtures, force limits, and damage/failure labels.
- Implemented visible-state MPC, history estimator, particle-filter memory, graph-dynamics baseline, ensemble planner, proposed action-conditioned memory, and full-latent oracle.
- Evaluated seven seeds, five splits, learned estimators, uncertainty intervals, paired statistics, ablations, stress sweeps, negative cases, and figures.
- Compiled a terminal archive manuscript and canonical PDF to Downloads only.

## Terminal Result

The central submission claim failed. `action_conditioned_memory` improves hidden-state proxies but loses downstream closed-loop success and increases damage on `combined_memory_stress`. The repository is a reproducible negative-result archive, not an ICLR-main submission.
