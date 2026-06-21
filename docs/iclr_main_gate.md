# ICLR Main Gate

Paper: 75 deformable_memory_under_action

Hardening version: v5-expanded

Gate verdict: KILL_ARCHIVE

Evidence digest: BBAC0390BC96955

## Why It Fails

The v5-expanded rebuild produced stronger local evidence and a full 30-page manuscript, but the central submission claim still fails:

- `action_conditioned_memory_v5` reaches 0.562 +/- 0.062 closed-loop success on `combined_memory_stress`.
- The strongest non-oracle baseline, `damage_aware_visible_mpc`, reaches 0.589 +/- 0.058.
- The main paired success difference is -0.027 +/- 0.052 against the proposed method.
- The aggregate hard-regime paired success difference is -0.103 +/- 0.016.
- The proposed method reduces hidden-memory error by 0.349 and improves mechanism F1 by 0.031 relative to damage-aware visible MPC, but damage is worse by 0.045.
- At maximum stress, v5 reaches 0.583 success, while `damage_aware_visible_mpc` reaches 0.653.
- Multiple ablations match the full v5 method, so the mechanism is not isolated strongly enough for main-track claims.

## Remaining Main-Track Blockers

- No real-robot evaluation.
- No external public deformable-object benchmark validation.
- The proposed planner does not beat damage-aware visible MPC on downstream success.
- The damage and max-stress gates are negative.
- The ablation evidence does not isolate a necessary action-conditioned mechanism.
- The local action library and learned surrogates remain diagnostic, not a polished general deformable manipulation system.
- Prior work on graph dynamics, action-conditional visual dynamics, dense affordances, latent roadmaps, and deformable object manipulation leaves little novelty unless the downstream evidence wins.

The only honest main-conference-safe decision is to archive rather than overclaim.
