# Final Audit

Paper: 75 deformable_memory_under_action

Version: v4

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- Local mass-spring deformable manipulation benchmark.
- Seven seeds: 0 through 6.
- Five splits and four deformable object families.
- 2,940 main rollout rows.
- 245 seed-level metric rows.
- 392 ablation rollout rows.
- 1,344 stress-sweep raw rows.
- 12 negative cases.

## Gate Result

The proposed method fails the decisive gate.

- `action_conditioned_memory`: 0.440 +/- 0.069 combined-memory-stress success.
- `visible_state_mpc`: 0.607 +/- 0.047 combined-memory-stress success.
- Paired success difference: -0.167 +/- 0.094.
- Hidden-memory error reduction versus visible-state MPC: +0.369.
- Mechanism-F1 difference versus visible-state MPC: +0.125.
- Damage reduction versus visible-state MPC: -0.298, meaning more damage.

## Audit Conclusion

The repo is now a real negative-result artifact. It should not be submitted to ICLR main.

## Continuation Audit 2026-06-15

Rechecked gates:

- `python -m py_compile src/run_experiment.py` passed.
- CSV integrity passed with expected blank `actual_failures` and `predicted_failures` allowed for no-failure/no-prediction rows.
- Evidence scale matched: 2,940 main rollout rows, 245 raw seed metric rows, 35 aggregate metric rows, 30 pairwise rows, 392 ablation rollout rows, 1,344 stress-sweep raw rows, and 12 negative cases.
- Required baselines were present: `visible_state_mpc`, `history_rnn_estimator`, `particle_filter_memory`, `graph_dynamics_baseline`, `ensemble_uncertainty_planner`, and `oracle_latent_state`.
- LaTeX/BibTeX rebuilt a 4-page PDF; `C:/Users/wangz/Downloads/75.pdf` SHA256 is `B405E5051AAD13FE4FA2A821AD77B83F8F40D6A48C888FC634B4B9464D5D27D9`.
- `C:/Users/wangz/Desktop/75.pdf` does not exist.

The decisive negative result was reproduced. On `combined_memory_stress`, `action_conditioned_memory` scores 0.440 +/- 0.069 success, while `visible_state_mpc` scores 0.607 +/- 0.047. The paired success difference is -0.167 +/- 0.094, with zero better seeds for the reference method. The proposed method reduces hidden-memory error by 0.369 and improves mechanism macro-F1 by 0.125 versus visible-state MPC, but increases damage: paired damage reduction is -0.298.

The ablation gate also fails. `action_conditioned_no_diagnostic_probes` reaches 0.554 +/- 0.050 success and 0.286 damage, while `action_conditioned_full` reaches 0.375 +/- 0.107 success and 0.554 damage. The mechanism claimed as a strength is the most direct source of harm.

Stress-sweep evidence is unfavorable at every non-oracle level. At maximum stress 1.00, `action_conditioned_memory` reaches 0.321 success and 0.625 damage; `ensemble_uncertainty_planner` reaches 0.375 success and 0.571 damage, and the oracle remains far higher at 0.768 success.

Continuation decision: keep `KILL_ARCHIVE`. Revival would require new experiments that beat visible-state MPC and ensemble baselines on success, damage, and stress robustness without relying on harmful diagnostic probing.
