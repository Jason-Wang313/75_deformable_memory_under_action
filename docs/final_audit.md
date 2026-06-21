# Final Audit

Paper: 75 deformable_memory_under_action

Version: v5-expanded

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- Local mass-spring deformable manipulation benchmark.
- Eight seeds: 0 through 7.
- Five splits and four deformable object families.
- 6,160 main rollout rows.
- 440 seed-level metric rows.
- 88 aggregate seed rows.
- 640 ablation rollout rows.
- 4,032 stress-sweep raw rows.
- 6,912 fixed-risk rollout rows.
- 12 negative cases.
- 30-page ICLR-style archive manuscript with boxed citation links.

## Gate Result

The expanded v5 method fails the frozen decisive gates.

- `action_conditioned_memory_v5`: 0.562 +/- 0.062 combined-memory-stress success.
- `damage_aware_visible_mpc`: 0.589 +/- 0.058 combined-memory-stress success.
- Main paired success difference: -0.027 +/- 0.052.
- Hidden-memory error reduction versus damage-aware visible MPC: +0.349.
- Mechanism-F1 difference versus damage-aware visible MPC: +0.031.
- Damage reduction versus damage-aware visible MPC: -0.045, meaning more damage.
- Aggregate hard-regime paired success difference: -0.103 +/- 0.016.
- Max-stress success: v5 reaches 0.583, while `damage_aware_visible_mpc` reaches 0.653.

## Continuation Audit 2026-06-21

Rechecked gates:

- `python -m py_compile src/run_experiment.py scripts/generate_manuscript.py scripts/validate_submission_artifacts.py` passed.
- Full-run CSV integrity passed.
- Expected evidence scale matched: 6,160 main rollouts, 440 raw seed metrics, 55 metrics, 50 pairwise rows, 88 aggregate seed rows, 11 aggregate metrics, 10 aggregate pairwise rows, 640 ablation rollouts, 64 ablation seed metrics, 8 ablation metrics, 4,032 stress raw rows, 56 stress rows, 6,912 fixed-risk rows, 864 fixed-risk seed metrics, 108 fixed-risk metrics, 96 fixed-risk pairwise rows, and 12 negative cases.
- Required baselines were present: `visible_state_mpc`, `damage_aware_visible_mpc`, `history_rnn_estimator`, `particle_filter_memory`, `safety_constrained_particle_filter`, `graph_dynamics_baseline`, `ensemble_uncertainty_planner`, `robust_cem_surrogate`, and `oracle_latent_state`.
- LaTeX/BibTeX rebuilt a 30-page PDF; `C:/Users/wangz/Downloads/75.pdf` SHA256 is `BBAC0390BC96955695BED0FB23BBADA5AB6EAC5BD9233D439B3E2EB81B7250FE`.
- Hard LaTeX log scan found no overfull boxes, undefined references, undefined citations, rerun warnings, or natbib warnings.
- `C:/Users/wangz/Desktop/75.pdf` does not exist.

The v5 run is a stronger negative result than v4, not a submission rescue. The method reduces hidden-memory error and removes the catastrophic diagnostic-probe behavior, but it still trails the strongest non-oracle baseline on main success, aggregate hard-regime success, damage, maximum-stress success, and multiple ablation controls. Several ablations match the full v5 method, including no action conditioning, no damage penalty, no material memory, and no safety gate.

Continuation decision: keep `KILL_ARCHIVE`. Revival would require a new mechanism that beats damage-aware visible MPC on success and damage under the frozen protocol, then repeats that gain under aggregate hard regimes, fixed-risk budgets, and external or real-robot validation.
