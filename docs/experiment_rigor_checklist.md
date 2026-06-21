# Experiment Rigor Checklist

## Completed In v5-expanded

- [x] Local high-fidelity mass-spring deformable simulator.
- [x] Rope, cloth-strip, elastic-band, and sheet tasks.
- [x] Hidden strain/contact memory and partial observation.
- [x] Eight random seeds.
- [x] Five evaluation splits.
- [x] Learned history, graph, action, and ensemble estimators.
- [x] Strong non-oracle baselines.
- [x] Damage-aware visible MPC baseline.
- [x] Safety-constrained particle filter baseline.
- [x] Robust CEM surrogate baseline.
- [x] Full-latent oracle action-library upper bound.
- [x] Mean and 95 percent confidence intervals.
- [x] Paired comparisons against the strongest non-oracle baseline.
- [x] Ablations for action conditioning, branch memory, safety gate, diagnostic gate, damage penalty, material memory, and uncertainty.
- [x] Stress sweep over combined deformable-memory severity.
- [x] Fixed-risk safety budget sweep.
- [x] Aggregate hard-regime evaluation.
- [x] Negative cases.
- [x] Reproducible CSV outputs and figures.
- [x] 30-page archive manuscript with boxed citation links.
- [x] Validation script for counts, PDF placement, citation boxes, LaTeX log cleanliness, and page threshold.

## Still Missing For ICLR Main

- [ ] Real-robot validation.
- [ ] External public deformable-object benchmark validation.
- [ ] Large neural deformable dynamics checkpoint.
- [ ] Public videos or hardware traces.
- [ ] Manual full-paper related-work synthesis.

Decision: fail ICLR main empirical-rigor gate because the implemented evidence refutes the central downstream claim under the frozen hostile-review protocol.
