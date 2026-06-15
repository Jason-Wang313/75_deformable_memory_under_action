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

## 2026-06-15 Continuation Plan

- Re-run code integrity and result-schema gates without rerunning expensive experiments.
- Verify the full evidence scale: 2,940 rollout rows, 245 seed metric rows, 392 ablation rollout rows, and 1,344 stress-sweep raw rows.
- Re-evaluate the decisive `combined_memory_stress` comparison against `visible_state_mpc` and all other non-oracle baselines.
- Re-check whether ablations support diagnostic probes and action-conditioned memory.
- Rebuild the LaTeX/BibTeX PDF, copy only `75.pdf` to Downloads, and confirm no Desktop PDF exists.
- Update child and root status artifacts, then commit and push the public GitHub repository.

## 2026-06-15 Continuation Result

The continuation audit preserved `KILL_ARCHIVE`. The proposed method reaches 0.440 +/- 0.069 success versus 0.607 +/- 0.047 for `visible_state_mpc`; the paired success difference is -0.167 +/- 0.094 over seven seeds. The method reduces memory error by 0.369 and raises mechanism-F1 by 0.125 versus visible-state MPC, but damage reduction is -0.298, meaning it causes more damage. The no-diagnostic-probes ablation reaches 0.554 +/- 0.050 success versus 0.375 +/- 0.107 for the full ablated action-conditioned variant, so the diagnostic mechanism is harmful rather than necessary.
