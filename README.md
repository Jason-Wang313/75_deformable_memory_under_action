# 75 Deformable Memory Under Action

Submission-hardening version: v5-expanded

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository contains the expanded Paper 75 rebuild: a local mass-spring deformable manipulation benchmark with rope, cloth-strip, elastic-band, and sheet tasks; hidden strain/contact memory; partial observation; learned history/graph/action estimators; visible-state MPC, damage-aware visible MPC, safety-constrained particle filtering, robust CEM surrogate planning, action-conditioned memory variants, and an oracle-latent upper bound; eight-seed evaluation; paired statistics; ablations; stress sweeps; fixed-risk safety budgets; negative-case mining; figures; validation scripts; and a 30-page archive manuscript.

The evidence still does not support ICLR-main submission. The expanded method improves over the earlier v4 diagnostic-probe planner, but it does not survive frozen hostile-review gates. On `combined_memory_stress`, `action_conditioned_memory_v5` reaches 0.562 +/- 0.062 success, while the strongest non-oracle baseline, `damage_aware_visible_mpc`, reaches 0.589 +/- 0.058. The paired success difference is -0.027 +/- 0.052. Across the aggregate hard regimes, the gap is larger: -0.103 +/- 0.016 against `damage_aware_visible_mpc`.

## Main Result

Full v5 run:

- Main rollout rows: 6,160.
- Seed-level metric rows: 440.
- Aggregate seed rows: 88.
- Ablation rollout rows: 640.
- Stress-sweep raw rows: 4,032.
- Fixed-risk rollout rows: 6,912.
- Seeds: 0 through 7.
- Training scenarios per split: 48.
- Evaluation scenarios per split: 14.
- Fixed-risk budgets: 0.10, 0.20, 0.30, and 0.40.
- Runtime: 1785.35 seconds.

Combined-memory-stress summary:

- `oracle_latent_state`: 0.821 +/- 0.084 success, memory error 0.000, mechanism F1 1.000, damage 0.063.
- `damage_aware_visible_mpc`: 0.589 +/- 0.058 success, memory error 0.578, mechanism F1 0.406, damage 0.205.
- `visible_state_mpc`: 0.589 +/- 0.058 success, memory error 0.578, mechanism F1 0.406, damage 0.205.
- `action_conditioned_memory_v5`: 0.562 +/- 0.062 success, memory error 0.229, mechanism F1 0.438, damage 0.250.
- `graph_dynamics_baseline`: 0.536 +/- 0.092 success, memory error 0.525, mechanism F1 0.427, damage 0.259.
- `safety_constrained_particle_filter`: 0.518 +/- 0.063 success, memory error 0.256, mechanism F1 0.391, damage 0.330.
- `robust_cem_surrogate`: 0.482 +/- 0.058 success, memory error 0.255, mechanism F1 0.406, damage 0.420.

The paper is retained as a reproducible negative-result archive. The correct claim is not "action-conditioned memory is submission-ready"; it is "under this benchmark, latent-memory improvement alone still fails to yield reliable deformable manipulation success under hostile stress tests."

## Reproduce

```powershell
python src\run_experiment.py
python scripts\generate_manuscript.py
python scripts\validate_submission_artifacts.py
```

Outputs are written under `results/`, `figures/`, and `paper/`.

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/75.pdf`

Validated PDF: 30 pages, SHA256 `BBAC0390BC96955695BED0FB23BBADA5AB6EAC5BD9233D439B3E2EB81B7250FE`.

No PDF is copied to the visible Desktop.
