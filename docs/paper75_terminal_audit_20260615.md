# Paper 75 Terminal Audit

Date: 2026-06-15 07:06:20 +0100
Paper: 75 - `deformable_memory_under_action`
Decision: `KILL_ARCHIVE`

## Verification Performed

- Compiled `src/run_experiment.py`.
- Verified required CSV artifacts and schemas.
- Confirmed evidence scale: 2,940 main rollout rows, 245 raw seed metric rows, 35 aggregate metric rows, 30 pairwise rows, 392 ablation rollout rows, 1,344 stress-sweep raw rows, and 12 negative cases.
- Confirmed seven seeds: 0 through 6.
- Confirmed central baselines: `visible_state_mpc`, `history_rnn_estimator`, `particle_filter_memory`, `graph_dynamics_baseline`, `ensemble_uncertainty_planner`, and `oracle_latent_state`.
- Rebuilt the LaTeX/BibTeX PDF and copied only `75.pdf` to Downloads.
- Confirmed no `C:/Users/wangz/Desktop/75.pdf` exists.

## Decisive Evidence

On `combined_memory_stress`:

- `action_conditioned_memory`: 0.440 +/- 0.069 success, 0.217 memory error, 0.536 mechanism macro-F1, 0.524 damage.
- `visible_state_mpc`: 0.607 +/- 0.047 success, 0.585 memory error, 0.411 mechanism macro-F1, 0.226 damage.
- Paired proposed-minus-visible success difference: -0.167 +/- 0.094.
- Memory-error reduction versus visible-state MPC: +0.369.
- Mechanism-F1 difference versus visible-state MPC: +0.125.
- Damage reduction versus visible-state MPC: -0.298.
- Better seeds versus visible-state MPC: 0/7.

The proposed method learns a better latent proxy but does not turn that proxy into better manipulation. It trades lower memory error for lower task success and much higher damage.

## Ablation Gate

The ablation evidence rejects the mechanism claim:

- `action_conditioned_full`: 0.375 +/- 0.107 success, 0.554 damage.
- `action_conditioned_no_diagnostic_probes`: 0.554 +/- 0.050 success, 0.286 damage.

Removing diagnostic probes improves success and safety, so the proposed diagnostic mechanism is harmful in this benchmark.

## Stress Gate

At maximum stress level 1.00:

- `action_conditioned_memory`: 0.321 success, 0.625 damage.
- `ensemble_uncertainty_planner`: 0.375 success, 0.571 damage.
- `oracle_latent_state`: 0.768 success, 0.089 damage.

The proposed method is below the strongest non-oracle stress baseline at every stress level.

## Artifact Result

- PDF: `C:/Users/wangz/Downloads/75.pdf`
- SHA256: `B405E5051AAD13FE4FA2A821AD77B83F8F40D6A48C888FC634B4B9464D5D27D9`
- Public GitHub: `https://github.com/Jason-Wang313/75_deformable_memory_under_action`

## Final Recommendation

Keep `KILL_ARCHIVE`. A future revival would need new experiments showing decisive success and safety gains over visible-state MPC and ensemble planning, plus ablations proving diagnostic actions help rather than harm.
