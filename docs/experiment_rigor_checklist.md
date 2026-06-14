# Experiment Rigor Checklist

## Completed In v4

- [x] Local high-fidelity mass-spring deformable simulator.
- [x] Rope, cloth-strip, elastic-band, and sheet tasks.
- [x] Hidden strain/contact memory and partial observation.
- [x] Seven random seeds.
- [x] Five evaluation splits.
- [x] Learned history, graph, action, and ensemble estimators.
- [x] Strong non-oracle baselines.
- [x] Full-latent oracle action-library upper bound.
- [x] Mean and 95 percent confidence intervals.
- [x] Paired comparisons against the strongest non-oracle baseline.
- [x] Ablations for action conditioning, branch memory, diagnostic probes, material memory, contact memory, and uncertainty.
- [x] Stress sweep over combined deformable-memory severity.
- [x] Negative cases.
- [x] Reproducible CSV outputs and figures.

## Still Missing For ICLR Main

- [ ] Real-robot validation.
- [ ] External public deformable-object benchmark validation.
- [ ] Large neural deformable dynamics checkpoint.
- [ ] Public videos or hardware traces.
- [ ] Manual full-paper related-work synthesis.

Decision: fail ICLR main empirical-rigor gate because the implemented evidence refutes the central downstream claim.
