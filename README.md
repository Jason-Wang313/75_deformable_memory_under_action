# 75 Deformable Memory Under Action

Submission-hardening version: v4

Terminal decision: KILL_ARCHIVE for ICLR main conference.

This repository now contains a real Paper 75 rebuild: a local mass-spring deformable manipulation benchmark with rope, cloth-strip, elastic-band, and sheet tasks; hidden strain/contact memory; partial observation; learned history/graph/action estimators; visible-state MPC, recurrent-history, particle-filter, graph-dynamics, ensemble, action-conditioned-memory, and oracle-latent-state planners; seven-seed evaluation; paired statistics; ablations; stress sweeps; negative cases; figures; and a rewritten archive manuscript.

The evidence does not support ICLR-main submission. On the decisive `combined_memory_stress` split, `action_conditioned_memory` reaches 0.440 +/- 0.069 closed-loop success, while the strongest non-oracle baseline, `visible_state_mpc`, reaches 0.607 +/- 0.047. The paired success difference is -0.167 +/- 0.094. Action-conditioned memory improves hidden-memory error and mechanism F1, but it overuses diagnostic branch pulls and increases damage.

## Main Result

Full run:

- Main rollout rows: 2,940.
- Seed-level metric rows: 245.
- Ablation rollout rows: 392.
- Stress-sweep raw rows: 1,344.
- Seeds: 0 through 6.
- Training scenarios per split: 38.
- Evaluation scenarios per split: 12.
- Simulator steps per rollout: 58.
- Runtime: 908.45 seconds.

Combined-memory-stress summary:

- `oracle_latent_state`: 0.798 +/- 0.060 success, memory error 0.000, mechanism F1 1.000, damage 0.071.
- `visible_state_mpc`: 0.607 +/- 0.047 success, memory error 0.585, mechanism F1 0.411, damage 0.226.
- `graph_dynamics_baseline`: 0.548 +/- 0.060 success, memory error 0.539, mechanism F1 0.411, damage 0.274.
- `history_rnn_estimator`: 0.464 +/- 0.079 success, memory error 0.202, mechanism F1 0.446, damage 0.464.
- `particle_filter_memory`: 0.464 +/- 0.060 success, memory error 0.202, mechanism F1 0.518, damage 0.488.
- `ensemble_uncertainty_planner`: 0.452 +/- 0.060 success, memory error 0.200, mechanism F1 0.482, damage 0.500.
- `action_conditioned_memory`: 0.440 +/- 0.069 success, memory error 0.217, mechanism F1 0.536, damage 0.524.

The paper is retained as a reproducible negative-result archive.

## Reproduce

```powershell
python src\run_experiment.py
```

Outputs are written under `results/` and `figures/`.

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/75.pdf`

No PDF is copied to the visible Desktop.
