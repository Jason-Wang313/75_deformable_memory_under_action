# Submission Attack Log

## Attack Outcome

The paper does not survive the submission-hardening attack.

## Failed Gate

Required gate: `action_conditioned_memory` must beat the strongest non-oracle baseline on `combined_memory_stress` with a meaningful paired effect while improving latent memory estimates and not increasing damage.

Observed:

- Strongest non-oracle baseline: `visible_state_mpc`.
- Proposed success: 0.440 +/- 0.069.
- Baseline success: 0.607 +/- 0.047.
- Paired success difference: -0.167 +/- 0.094.
- Proposed memory error: 0.217.
- Baseline memory error: 0.585.
- Proposed damage rate: 0.524.
- Baseline damage rate: 0.226.

## Terminal Action

Archive the paper. Do not submit as an ICLR-main paper.
