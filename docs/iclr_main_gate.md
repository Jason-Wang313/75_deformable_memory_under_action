# ICLR Main Gate

Paper: 75 deformable_memory_under_action

Hardening version: v4

Gate verdict: KILL_ARCHIVE

Evidence digest: 9a37ae871897e9da

## Why It Fails

The v4 rebuild produced real local evidence, but the central claim fails:

- `action_conditioned_memory` reaches 0.440 +/- 0.069 closed-loop success on `combined_memory_stress`.
- The strongest non-oracle baseline, `visible_state_mpc`, reaches 0.607 +/- 0.047.
- The paired success difference is -0.167 +/- 0.094 against the proposed method.
- The proposed method reduces hidden-memory error by 0.369 and improves mechanism F1 by 0.125 relative to visible-state MPC, but damage is worse by 0.298.
- The no-diagnostic-probes ablation reaches 0.554 +/- 0.050 success, above the full action-conditioned variant, showing that diagnostic branch pulls are the failure mode rather than the rescue mechanism.

## Remaining Main-Track Blockers

- No real-robot evaluation.
- No external deformable-object benchmark validation.
- The proposed planner does not beat a simple visible-state MPC baseline on downstream success.
- The local action library and learned surrogates are diagnostic, not a polished general deformable manipulation system.
- Prior work on graph dynamics, action-conditional visual dynamics, dense affordances, latent roadmaps, and deformable object manipulation leaves little novelty unless the downstream evidence wins.

The only honest main-conference-safe decision is to archive rather than overclaim.
