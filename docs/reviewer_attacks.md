# Reviewer Attacks

## Attack 1: The Main Metric Is Lost

The proposed method loses combined-memory-stress success to visible-state MPC: 0.440 +/- 0.069 versus 0.607 +/- 0.047.

Answer: accept. This is fatal for ICLR main.

## Attack 2: Proxy Gains Do Not Matter Enough

The method improves memory error and mechanism F1, but damages the object more often.

Answer: accept. Proxy gains do not rescue worse manipulation.

## Attack 3: Diagnostic Probes Are Harmful

The no-diagnostic ablation beats the full method.

Answer: accept. The intended mechanism fails.

## Attack 4: The Benchmark Is Local

The evidence is local simulation only and lacks real-robot deformable manipulation.

Answer: accept. Even a positive local result would need more validation.

## Attack 5: Prior Work Is Strong

Graph dynamics, action-conditioned visual dynamics, latent roadmaps, and dense affordances are close.

Answer: accept. The paper needs a downstream win to survive that crowding.
