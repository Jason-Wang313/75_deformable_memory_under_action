# Final Audit

Paper: 75 deformable_memory_under_action

Version: v4

Terminal decision: KILL_ARCHIVE

## Evidence Completed

- Local mass-spring deformable manipulation benchmark.
- Seven seeds: 0 through 6.
- Five splits and four deformable object families.
- 2,940 main rollout rows.
- 245 seed-level metric rows.
- 392 ablation rollout rows.
- 1,344 stress-sweep raw rows.
- 12 negative cases.

## Gate Result

The proposed method fails the decisive gate.

- `action_conditioned_memory`: 0.440 +/- 0.069 combined-memory-stress success.
- `visible_state_mpc`: 0.607 +/- 0.047 combined-memory-stress success.
- Paired success difference: -0.167 +/- 0.094.
- Hidden-memory error reduction versus visible-state MPC: +0.369.
- Mechanism-F1 difference versus visible-state MPC: +0.125.
- Damage reduction versus visible-state MPC: -0.298, meaning more damage.

## Audit Conclusion

The repo is now a real negative-result artifact. It should not be submitted to ICLR main.
