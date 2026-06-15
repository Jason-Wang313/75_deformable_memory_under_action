# Paper 75 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15
Paper: 75 - `deformable_memory_under_action`
Target venue posture: ICLR main only if supported by decisive downstream evidence
Current terminal label entering audit: `KILL_ARCHIVE`

## Goal

Rebuild and audit Paper 75 as a real submission candidate rather than a cosmetic manuscript. The audit must decide whether the deformable-physics evidence can honestly support an ICLR-main action-conditioned memory submission, or whether the paper remains a terminal negative result.

## Decision Rule

Upgrade from `KILL_ARCHIVE` only if all of the following are true:

1. `action_conditioned_memory` decisively beats the strongest non-oracle baseline, especially `visible_state_mpc`, on `combined_memory_stress` task success.
2. Hidden-memory or mechanism-F1 gains translate into downstream manipulation success.
3. The method does not increase deformable-object damage relative to the strongest baseline.
4. Ablations show diagnostic probes and action-conditioned memory are necessary rather than harmful.
5. Stress-sweep results remain favorable under the hardest deformation and partial-observation settings.
6. The evidence is reproducible from checked-in code, raw CSVs, and a clean PDF build.

If any of these gates fail, preserve `KILL_ARCHIVE` and document the exact failure mode.

## Evidence Gates

Run these checks before changing the decision:

1. Code integrity: compile the experiment source with `python -m py_compile src/run_experiment.py`.
2. Result integrity: verify all required CSVs exist, are nonempty, finite, and schema-valid.
3. Scale check: confirm the recorded evidence includes 2,940 main rollout rows, 245 seed metric rows, 392 ablation rollout rows, and 1,344 stress rows.
4. Baseline check: verify `visible_state_mpc`, `history_rnn_estimator`, `particle_filter_memory`, `graph_dynamics_baseline`, `ensemble_uncertainty_planner`, and `oracle_latent_state` are present.
5. Stress check: confirm `combined_memory_stress` and stress-sweep outcomes are represented.
6. Ablation check: confirm whether the full action-conditioned memory method beats removed-component variants, especially no-diagnostic-probe variants.
7. Paper build: run LaTeX/BibTeX to produce a clean PDF and copy only the numbered PDF to `C:/Users/wangz/Downloads/75.pdf`.
8. Artifact hygiene: confirm no numbered PDF is copied to the visible Desktop.
9. GitHub hygiene: confirm the matching public GitHub repository exists and the local commit is pushed.
10. Root-report hygiene: update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.

## Expected Risk

The existing evidence summary reports that `action_conditioned_memory` reaches 0.440 combined-memory-stress success while `visible_state_mpc` reaches 0.607, with paired success difference -0.167 +/- 0.094. The proposed method reduces hidden-memory error but increases damage. Unless direct verification contradicts that result, Paper 75 cannot honestly become submission-ready in this pass.

## Execution Order

1. Re-check repository cleanliness and result inventory.
2. Run code and CSV integrity gates.
3. Rebuild the paper PDF and repair recoverable build warnings.
4. Write a terminal audit with exact evidence and rejection rationale.
5. Update child status, local audit docs, and root reports.
6. Commit and push the Paper 75 repository.
7. Verify `Downloads/75.pdf`, no Desktop copy, public GitHub visibility, clean git state, and root report consistency.

