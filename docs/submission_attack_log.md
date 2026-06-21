# Submission Attack Log

## Attack Outcome

The paper does not survive the submission-hardening attack.

## Failed Gate

Required gate: `action_conditioned_memory` must beat the strongest non-oracle baseline on `combined_memory_stress` with a meaningful paired effect while improving latent memory estimates and not increasing damage.

Observed:

- Strongest non-oracle baseline: `visible_state_mpc`.
- Proposed success: 0.440 +/- 0.069.
- Baseline success: 0.607 +/- 0.047.
- Paired success difference: -0.167 +/- 0.094.
- Proposed memory error: 0.217.
- Baseline memory error: 0.585.
- Proposed damage rate: 0.524.
- Baseline damage rate: 0.226.

## Terminal Action

Archive the paper. Do not submit as an ICLR-main paper.

## Continuation Attack 2026-06-15

The submission-hardening attack was rerun against the stored v4 artifacts.

- CSV/code/PDF gates passed, so the failure is scientific rather than an artifact issue.
- `action_conditioned_memory` loses to every relevant non-oracle success target on the central split: `visible_state_mpc` 0.607, `graph_dynamics_baseline` 0.548, `history_rnn_estimator` 0.464, `particle_filter_memory` 0.464, `ensemble_uncertainty_planner` 0.452, proposed 0.440.
- The proposed method has zero better seeds versus `visible_state_mpc`.
- The memory proxy win does not matter enough: memory error improves from 0.585 to 0.217, while success falls and damage rises from 0.226 to 0.524.
- The hardest stress level repeats the pattern: proposed 0.321 success and 0.625 damage versus ensemble 0.375 success and 0.571 damage.

Updated terminal action: keep the archive and do not submit.

## Expanded Attack 2026-06-21

The submission-hardening attack was rerun after the v5-expanded protocol was frozen.

- CSV/code/PDF gates passed, so the failure is again scientific rather than an artifact issue.
- `action_conditioned_memory_v5` reaches 0.562 +/- 0.062 on the central split, below `damage_aware_visible_mpc` at 0.589 +/- 0.058.
- The aggregate hard-regime paired gap is -0.103 +/- 0.016, which is too large to explain away as formatting or randomness.
- Memory proxy gains persist: v5 memory error is 0.229 versus 0.578 for the damage-aware visible baseline, but downstream success and damage do not clear the gate.
- Fixed-risk budgets do not rescue the claim; they show v5 can be competitive in constrained variants, not that it dominates the best non-oracle baseline.
- The hardest stress level repeats the failure: v5 0.583 success versus damage-aware visible MPC 0.653.

Updated terminal action: keep the archive and do not submit.
