# Novelty Boundary Map

## Crowded Territory

- Graph dynamics for deformable object manipulation.
- Action-conditioned visual dynamics.
- Dense visual affordance prediction.
- Latent-space planning roadmaps.
- Deformable visual tracking with memory.
- Sim-to-real deformable manipulation.

## Intended Novelty

The intended contribution was to preserve action-conditioned hidden material memory so visually similar deformable states with different latent strain/contact histories lead to different robot actions.

## Actual Boundary After v4 Evidence

The boundary is not strong enough for ICLR main. The method improves memory proxies, but the diagnostic action mechanism damages objects and loses closed-loop success to simpler visible-state and graph baselines.

## Revival Boundary

Revival would require a safer diagnostic policy or planner that converts hidden-memory estimates into better downstream manipulation, validated on real robots or external deformable-object benchmarks.
