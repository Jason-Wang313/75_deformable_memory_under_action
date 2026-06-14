# Paper 75 Rebuild Plan: Deformable Memory Under Action

Date: 2026-06-14

## Goal

Rebuild Paper 75 into a real ICLR-main-target robotics submission candidate, or terminate it honestly as `STRONG_REVISE` / `KILL_ARCHIVE` if the evidence does not justify submission. The central question is whether deformable-object state estimation and planning should preserve action-conditioned hidden material memory instead of relying on current visual appearance alone.

## Core Claim To Test

Deformable objects can look similar while carrying different latent strain, twist, fold, contact, or stored-energy histories. A robot that ignores action-conditioned memory may choose the wrong next manipulation even when the visible geometry is nearly identical. The proposed method should maintain action-conditioned latent alternatives and collapse them only after diagnostic contacts or observations.

## High-Fidelity Benchmark

Build a local deformable manipulation benchmark with a physically integrated mass-spring / finite-segment simulator, contact constraints, damping, friction, pinned/fixed points, gripper actions, self-relaxation, and partial observation. The benchmark should include at least:

- Rope/cable dragging around a peg with hidden twist and tension.
- Cloth strip folding with latent crease memory and partial occlusion.
- Elastic band stretching where identical visible endpoints can imply different stored strain.
- Deformable sheet pushing around fixtures with contact-history dependence.

Each rollout should log:

- Full latent deformable state: node positions, velocities, strain energy, contact flags, pinned points, fold/twist memory, and hidden occluded nodes.
- Partial observation: visible keypoints/noisy masks/occluded points.
- Action trace: gripper pulls, pushes, releases, diagnostic probes, and force-limited actions.
- Task success, shape error, energy overshoot, constraint violation, and failure mechanism labels.

Evaluation splits:

- `nominal_visible_state`: visible state mostly identifies the latent state.
- `hidden_strain_memory`: same visible shape but different latent tension/crease history.
- `occluded_contact_memory`: key nodes or contacts are hidden.
- `material_shift`: stiffness, damping, friction, and mass vary.
- `combined_memory_stress`: hidden strain, occlusion, material shift, fixture contact, and force limits overlap.

## Methods To Implement

- `visible_state_mpc`: plans from current observed keypoints only.
- `history_rnn_estimator`: recurrent state estimator over observations and actions.
- `particle_filter_memory`: maintains multiple latent deformable hypotheses.
- `graph_dynamics_baseline`: graph/message-passing style dynamics over observed nodes.
- `ensemble_uncertainty_planner`: conservative ensemble over learned/estimated latent states.
- `action_conditioned_memory`: proposed method; stores action-conditioned latent material memory and uses diagnostic actions to collapse ambiguous branches.
- `oracle_latent_state`: upper bound with full hidden deformable state.

## Metrics

- Closed-loop task success.
- Final shape error / Chamfer-style keypoint distance.
- Hidden strain / stored-energy estimation error.
- Contact/fold/twist mechanism F1.
- Tail risk on `combined_memory_stress`.
- Safety and damage proxy: force/energy overshoot, excessive stretch, fixture snagging.
- Diagnostic action efficiency: success versus number of probes.
- Calibration of latent uncertainty.

## Experimental Rigor

- Use seven random seeds unless runtime becomes impossible.
- Use multiple tasks and multiple material parameters.
- Evaluate downstream planning, not only prediction.
- Report mean, 95 percent confidence intervals, and paired comparisons against the strongest non-oracle baseline.
- Include ablations: no action conditioning, no branch memory, no diagnostic probes, no material-memory features, no contact/fold memory, no uncertainty term.
- Include stress sweeps over occlusion, stiffness shift, damping shift, friction, hidden strain magnitude, and force limits.
- Save raw rollouts, per-seed metrics, summary metrics, pairwise statistics, ablations, stress sweeps, negative cases, figures, and a training/run summary.

## Submission Gate

The paper can only move above archive if `action_conditioned_memory` beats the strongest non-oracle baseline on `combined_memory_stress` closed-loop success by a meaningful paired effect, improves latent memory estimation and mechanism F1, and does not increase damage/safety violations. If particle filtering, RNN history, graph dynamics, uncertainty ensembles, or visible-state MPC match or beat it, the paper remains `KILL_ARCHIVE` or at best `STRONG_REVISE`.

## Deliverables

- Replace the synthetic scaffold with a reproducible deformable physics benchmark runner.
- Generate raw rollout CSVs, metrics, pairwise statistics, ablations, stress sweeps, negative cases, figures, and `training_summary.csv`.
- Rewrite README, claims, novelty boundary, hostile review, reproducibility checklist, final audit, and ICLR gate around actual evidence.
- Rewrite `paper/main.tex` as either a real negative-result paper or a submission-candidate manuscript.
- Compile `paper/main.pdf`, copy exactly to `C:/Users/wangz/Downloads/75.pdf`, and do not copy any PDF to Desktop.
- Commit and push the final Paper 75 repo, then update shared root reports before moving to Paper 76.

## Terminal Outcome

The v4 full run completed on 2026-06-14 with seven seeds, 2,940 main rollout rows, 392 ablation rollout rows, and 1,344 stress-sweep raw rows. The submission gate failed: `action_conditioned_memory` reached 0.440 +/- 0.069 success on `combined_memory_stress`, while `visible_state_mpc` reached 0.607 +/- 0.047. The terminal decision is `KILL_ARCHIVE`.
