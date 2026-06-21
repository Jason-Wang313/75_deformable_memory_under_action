# Paper 75 Protocol Freeze - 2026-06-21

Paper: `deformable_memory_under_action`

This document freezes the v5 full protocol before interpreting the results. The experiment is allowed to fail. The terminal decision is whatever the frozen gates imply.

## Frozen Execution Constraints

- CPU only.
- Single-process runner.
- No GPU dependencies.
- No large neural checkpoints.
- No uncontrolled parallel workers.
- Final numbered PDF only in `C:/Users/wangz/Downloads/75.pdf`.
- No PDF copied to `C:/Users/wangz/Desktop`.

## Frozen Scale

- Seeds: 8 (`0` through `7`).
- Splits: 5.
- Training scenarios per split: 48.
- Evaluation scenarios per split: 14.
- Methods in main evaluation: 11.
- Ablation scenarios: 10.
- V5 ablation methods: 8.
- Stress levels: 7 (`0.00` through `1.00`).
- Stress scenarios per level: 9.
- Stress methods: 8.
- Fixed-risk budgets: `0.10`, `0.20`, `0.30`, `0.40`.
- Fixed-risk splits: hidden strain, occluded contact, combined memory stress.
- Fixed-risk scenarios per split: 8.
- Fixed-risk methods: 9.
- Simulation steps per rollout: 60.

## Expected Artifact Counts

- Main rollouts: 6,160.
- Raw seed metrics: 440.
- Main summary metrics: 55.
- Main pairwise rows: 50.
- Aggregate hard-regime seed metrics: 88.
- Aggregate hard-regime summary rows: 11.
- Aggregate hard-regime pairwise rows: 10.
- Ablation rollouts: 640.
- Ablation seed metrics: 64.
- Ablation summary rows: 8.
- Stress raw rows: 4,032.
- Stress summary rows: 56.
- Fixed-risk raw rows: 6,912.
- Fixed-risk seed metrics: 864.
- Fixed-risk summary rows: 108.
- Fixed-risk pairwise rows: 96.
- Training summary rows: 1.

## Frozen Promotion Gates

`STRONG_REVISE` is allowed only if all gates pass:

- `action_conditioned_memory_v5` beats the strongest non-oracle baseline on `combined_memory_stress` by at least 0.04 success.
- The paired lower bound against that baseline is positive on `combined_memory_stress`.
- The paired lower bound is positive on the aggregate hard regime.
- V5 is best or tied-best at fixed predicted-risk budgets 0.10 and 0.20.
- V5 does not increase damage or force clipping relative to the strongest non-oracle baseline.
- V5 improves hidden-memory error or mechanism macro-F1 without sacrificing downstream success.
- No v5 ablation matches or beats full v5 within tolerance.
- V5 does not collapse earlier than the strongest non-oracle baseline at maximum stress.

If any central gate fails, the terminal decision is `KILL_ARCHIVE`.

## Frozen Disclosures

The manuscript must disclose that the artifact has no real-robot validation, no videos, no external deformable-object benchmark, no tactile/RGBD perception stack, and no large neural dynamics model.
