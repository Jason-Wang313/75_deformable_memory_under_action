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
