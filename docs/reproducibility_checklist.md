# Reproducibility Checklist

## Environment

- Python package requirements are listed in `requirements.txt`.
- Core dependencies: `numpy`, `matplotlib`, and `scikit-learn`.
- The experiment runner is `src/run_experiment.py`.

## Reproduce Evidence

```powershell
python src\run_experiment.py
```

Expected full-run artifacts:

- `results/rollouts.csv`
- `results/raw_seed_metrics.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/aggregate_seed_metrics.csv`
- `results/aggregate_metrics.csv`
- `results/aggregate_pairwise_stats.csv`
- `results/ablation_rollouts.csv`
- `results/ablation_seed_metrics.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep_raw.csv`
- `results/stress_sweep.csv`
- `results/fixed_risk_raw.csv`
- `results/fixed_risk_seed_metrics.csv`
- `results/fixed_risk_metrics.csv`
- `results/fixed_risk_pairwise.csv`
- `results/negative_cases.csv`
- `results/training_summary.csv`
- `figures/deformable_memory_final_success.png`
- `figures/deformable_memory_error.png`
- `figures/deformable_memory_damage_rate.png`
- `figures/deformable_memory_ablation_success.png`
- `figures/deformable_memory_stress_sweep.png`
- `figures/deformable_memory_fixed_risk.png`

## Quick Smoke

```powershell
$env:PAPER75_QUICK='1'
python src\run_experiment.py
```

Unset or set `PAPER75_QUICK=0` for the full eight-seed run.

## Manuscript And Validation

```powershell
python scripts\generate_manuscript.py
python scripts\validate_submission_artifacts.py
```

The validator checks expected CSV counts, 30-page PDF length, bright citation boxes, hard LaTeX log warnings, and Downloads-only PDF placement.

## PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical PDF: `C:/Users/wangz/Downloads/75.pdf`.

Validated SHA256: `BBAC0390BC96955695BED0FB23BBADA5AB6EAC5BD9233D439B3E2EB81B7250FE`.
