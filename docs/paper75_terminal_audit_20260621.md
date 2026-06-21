# Paper 75 Terminal Audit 2026-06-21

## Verdict

Terminal decision: KILL_ARCHIVE.

ICLR main readiness: no.

## What Was Expanded

- Eight-seed full run.
- Stronger non-oracle baselines: damage-aware visible MPC, safety-constrained particle filtering, and robust CEM surrogate planning.
- v5 action-conditioned memory planner with safety and damage terms.
- Aggregate hard-regime evaluation.
- Fixed-risk safety budget sweep.
- Mechanism ablations for action conditioning, branch memory, safety, diagnostics, damage penalty, material memory, and uncertainty.
- Stress sweep and negative-case mining.
- 30-page manuscript with bright boxed in-text citation links.

## Decisive Evidence

- `action_conditioned_memory_v5`: 0.562 +/- 0.062 combined-memory-stress success.
- `damage_aware_visible_mpc`: 0.589 +/- 0.058 combined-memory-stress success.
- Main paired success difference: -0.027 +/- 0.052.
- Aggregate hard-regime paired success difference: -0.103 +/- 0.016.
- Main memory-error reduction: +0.349.
- Main damage reduction: -0.045, meaning more damage than the best baseline.
- Max-stress success: v5 0.583, best non-oracle 0.653.

## Artifact Checks

- `results/rollouts.csv`: 6,160 rows.
- `results/raw_seed_metrics.csv`: 440 rows.
- `results/metrics.csv`: 55 rows.
- `results/pairwise_stats.csv`: 50 rows.
- `results/aggregate_seed_metrics.csv`: 88 rows.
- `results/aggregate_metrics.csv`: 11 rows.
- `results/aggregate_pairwise_stats.csv`: 10 rows.
- `results/ablation_rollouts.csv`: 640 rows.
- `results/ablation_seed_metrics.csv`: 64 rows.
- `results/ablation_metrics.csv`: 8 rows.
- `results/stress_sweep_raw.csv`: 4,032 rows.
- `results/stress_sweep.csv`: 56 rows.
- `results/fixed_risk_raw.csv`: 6,912 rows.
- `results/fixed_risk_seed_metrics.csv`: 864 rows.
- `results/fixed_risk_metrics.csv`: 108 rows.
- `results/fixed_risk_pairwise.csv`: 96 rows.
- `results/negative_cases.csv`: 12 rows.
- `results/training_summary.csv`: 1 row.

## PDF Checks

- Canonical PDF: `C:/Users/wangz/Downloads/75.pdf`.
- Page count: 30.
- SHA256: `BBAC0390BC96955695BED0FB23BBADA5AB6EAC5BD9233D439B3E2EB81B7250FE`.
- `C:/Users/wangz/Desktop/75.pdf`: absent.

## Conclusion

This is a real archive-quality negative result. The artifact is stronger, longer, and better validated than the v4 paper, but the method still fails the frozen submission gate. Keep archived unless a new method clears success, damage, aggregate, ablation, max-stress, and external-validation gates.
