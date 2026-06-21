# Paper 75 Expanded Submission Plan - 2026-06-21

Paper: `deformable_memory_under_action`

Target: rebuild Paper 75 to the expanded v5 standard before making a terminal ICLR-main decision. The goal is not to make the result look better; the goal is to make the evidence hard to dismiss.

## Non-Negotiable Rules

- Do not optimize for pretty results. Optimize for a result that survives hostile review.
- Improve the method during development, then freeze the final protocol and report all predefined results honestly.
- Keep execution CPU-only and RAM-light: single-process full runs, classical regressors, no GPU-only checkpoints, no uncontrolled worker pools, and bounded CSV artifacts.
- Do not pad the paper to reach 25 pages. The page count must come from theory, benchmark definition, frozen protocol, baselines, ablations, fixed-risk evaluation, stress results, negative cases, and reproducibility details.
- Store the final numbered PDF only at `C:/Users/wangz/Downloads/75.pdf`.
- Do not copy any PDF to the visible Desktop.

## Claim Under Test

The strongest defensible version of Paper 75 is:

> Deformable manipulation policies should preserve action-conditioned hidden material memory because the same visible geometry can carry different latent strain, contact, crease, or stored-energy histories, and a safety-gated memory planner can exploit that latent information better than visible-state, graph, particle-filter, uncertainty, and damage-aware baselines.

The v5 paper can only be promoted if the memory method improves downstream closed-loop manipulation. Better hidden-state estimation alone is not enough.

## Development Phase

The v4 result failed because `action_conditioned_memory` estimated hidden memory better but overused diagnostic branch pulls and increased damage. Before freezing, v5 will try the obvious credible rescue moves:

- Add `action_conditioned_memory_v5`, a safety-gated memory planner with branch memory, conservative scoring over memory hypotheses, damage penalties, diagnostic-probe gating, and uncertainty-sensitive route selection.
- Preserve the v4 method as `action_conditioned_memory`, so improvement or failure can be measured directly.
- Add stronger CPU-light baselines:
  - `damage_aware_visible_mpc`
  - `safety_constrained_particle_filter`
  - `robust_cem_surrogate`
- Keep the existing serious baselines:
  - `visible_state_mpc`
  - `history_rnn_estimator`
  - `particle_filter_memory`
  - `graph_dynamics_baseline`
  - `ensemble_uncertainty_planner`
  - `oracle_latent_state`
- Expand the evaluation with more scenarios and an aggregate hard-regime table across hidden strain, occluded contact, material shift, and combined memory stress.
- Add fixed-risk evaluation: success under explicit predicted-risk budgets rather than only unconstrained success.
- Add calibration and safety diagnostics: memory error, uncertainty-error mismatch, mechanism macro-F1, damage rate, force clipping, diagnostic rate, contact rate, stretch, and strain energy.
- Add negative-case mining comparing v5 failures against the strongest successful baseline on the same scenario when available.

## Frozen Full Protocol

After the v5 runner is implemented and smoke-tested, freeze one full protocol:

- Use at least 8 seeds unless a documented CPU failure forces a smaller run.
- Use all five original splits: nominal visible state, hidden strain memory, occluded contact memory, material shift, and combined memory stress.
- Use at least 14 evaluation scenarios per split in the full run.
- Use at least 9 stress scenarios per stress level and at least seven stress levels from 0.00 to 1.00.
- Use at least 10 ablation scenarios for the v5 method.
- Produce raw rollout rows, seed metrics, summary metrics, pairwise statistics, aggregate hard-regime metrics, fixed-risk metrics, ablation metrics, stress sweeps, negative cases, figures, and `training_summary.csv`.
- Report paired statistics against the strongest non-oracle baseline selected by frozen rules.
- Report all v5 ablations:
  - no action conditioning
  - no branch memory
  - no safety gate
  - no diagnostic gate
  - no damage penalty
  - no material memory
  - no uncertainty term

## Submission Gates

`STRONG_REVISE` is allowed only if every gate below is satisfied:

- Main split: `action_conditioned_memory_v5` beats the strongest non-oracle baseline on `combined_memory_stress` by at least 0.04 success.
- Paired evidence: the paired lower bound against the strongest non-oracle baseline is positive on `combined_memory_stress`.
- Aggregate evidence: the paired lower bound is positive on the aggregate hard regime.
- Fixed-risk evidence: v5 is best or tied-best at the 0.10 and 0.20 predicted-risk budgets.
- Safety evidence: v5 does not increase damage, force clipping, or diagnostic probing relative to the strongest non-oracle baseline.
- Mechanism evidence: v5 improves hidden-memory error or mechanism macro-F1 without sacrificing downstream success.
- Ablation necessity: no ablation can match or beat full v5 on the primary combined-memory success metric within the frozen tolerance.
- Stress robustness: v5 must not collapse earlier than the strongest non-oracle baseline at maximum stress.
- Honesty constraints: the paper must explicitly disclose no hardware validation, no videos, no external benchmark, and no large neural dynamics checkpoint unless those artifacts actually exist.

If any central gate fails, the terminal decision remains `KILL_ARCHIVE`, even if the manuscript is 25+ pages and some diagnostics are positive.

## Theory Expansion

The manuscript will add a real conceptual section:

- Define deformable memory as a latent material-state variable that is not identifiable from a single partial observation.
- Distinguish estimation benefit from control benefit: latent estimates only matter if the planner can safely exploit them.
- State a failure theorem-style proposition: if diagnostic actions have non-negligible damage probability and the candidate action library lacks low-risk disambiguation actions, a memory estimator can reduce latent error while reducing task success.
- Tie this theory to the empirical gates: hidden-memory error and mechanism F1 are secondary unless closed-loop success and safety improve.

## Manuscript And Citation Requirements

- Generate an expanded ICLR-style manuscript of at least 25 pages, earned by evidence and appendices.
- Use bright boxed clickable citation links through `hyperref`, with in-text citations routing to the bibliography.
- Use real references and avoid fake bibliographic entries.
- Include method, theory, benchmark, frozen protocol, main results, paired tests, fixed-risk tests, ablations, stress sweeps, negative cases, limitations, hostile-review audit, and reproducibility detail.
- Validate PDF page count, citation/link settings, artifact placement, and root status consistency.

## Deliverables

- Updated runner with frozen v5 experiments.
- Generated result CSVs, figures, summaries, validation script, protocol freeze, development log, and terminal audit.
- `paper/main.tex`, `paper/references.bib`, and `paper/main.pdf`.
- Final `C:/Users/wangz/Downloads/75.pdf` only.
- Public GitHub repo push.
- Updated root `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, `MASTER_SUBMISSION_REPORT.md`, and `SUBMISSION_AUDIT_MATRIX.csv`.
