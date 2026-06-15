# Hostile Reviewer Response

## Reviewer Claim

Better latent memory estimation is not enough; the manipulation policy must improve.

## Evidence-Based Response

Correct. `action_conditioned_memory` reduces hidden-memory error relative to `visible_state_mpc`, but closed-loop success is lower: 0.440 +/- 0.069 versus 0.607 +/- 0.047.

## Reviewer Claim

Diagnostic probing might damage deformable objects.

## Evidence-Based Response

Correct. The proposed method has damage rate 0.524 on `combined_memory_stress`, while visible-state MPC has 0.226. Negative cases are dominated by diagnostic branch pulls causing excessive stretch or fixture snags.

## Reviewer Claim

The ablation should show that diagnostic probes matter positively.

## Evidence-Based Response

It shows the opposite. `action_conditioned_no_diagnostic_probes` reaches 0.554 +/- 0.050 success, above the full ablated action-conditioned variant at 0.375 +/- 0.107.

## Terminal Response

We accept the rejection. The correct action is archive, not rhetorical strengthening.

## Continuation Response 2026-06-15

The hostile-reviewer position became stronger after re-audit, not weaker.

- The central paired comparison remains negative: `action_conditioned_memory` minus `visible_state_mpc` is -0.167 +/- 0.094 success, with 0/7 better seeds.
- The diagnostic-probe concern is validated by ablations: removing diagnostic probes raises success to 0.554 +/- 0.050 and lowers damage to 0.286, while the full ablated variant has 0.375 +/- 0.107 success and 0.554 damage.
- The stress-sweep objection is also valid: the proposed method is below `ensemble_uncertainty_planner` at every stress level, including 0.321 versus 0.375 success at stress 1.00.

No submission-ready framing can honestly rescue this paper without new evidence.
