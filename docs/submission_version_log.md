# Submission Version Log

## v3

Synthetic/template archive. Killed because it lacked real robot or high-fidelity simulator evidence.

## v4

Real local deformable-physics rebuild.

- Added mass-spring deformable object benchmark.
- Added hidden strain/contact memory, partial observation, fixtures, material shifts, and force limits.
- Added learned estimators, baselines, oracle, seven-seed evaluation, CIs, paired statistics, ablations, stress sweeps, negative cases, figures, and archive manuscript.
- Terminal decision remains KILL_ARCHIVE, but now for evidence-based reasons: the proposed method improves memory proxies while losing downstream success and increasing damage.

## v5-expanded

Expanded submission-hardening rebuild.

- Increased the evidence to eight seeds, 6,160 main rollouts, 640 ablation rollouts, 4,032 stress-sweep rollouts, and 6,912 fixed-risk rollouts.
- Added damage-aware visible MPC, safety-constrained particle filtering, robust CEM surrogate planning, aggregate hard-regime reporting, fixed-risk safety budgets, calibration metrics, and v5 mechanism ablations.
- Generated a 30-page ICLR-style archive manuscript with boxed citation links and verified Downloads-only PDF placement.
- Terminal decision remains KILL_ARCHIVE: `action_conditioned_memory_v5` improves hidden-memory error but trails `damage_aware_visible_mpc` on frozen success, damage, aggregate, ablation, and max-stress gates.
