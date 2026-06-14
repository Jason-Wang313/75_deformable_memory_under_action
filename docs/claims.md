# Claims

## Supported Claims

- The repository implements a real local mass-spring deformable manipulation benchmark.
- Hidden strain/contact memory can be estimated better when action/history features are used.
- Action-conditioned memory improves mechanism-label F1 on the decisive split.
- Better hidden-memory estimation does not guarantee better downstream manipulation.
- The proposed diagnostic branch action increases damage and reduces closed-loop success in this benchmark.

## Unsupported Claims

- Do not claim ICLR-main readiness.
- Do not claim state-of-the-art deformable manipulation.
- Do not claim real-robot validation.
- Do not claim action-conditioned memory beats visible-state or graph baselines on closed-loop success.

## Terminal Claim

Paper 75 is a useful negative result: action-conditioned deformable memory improves latent-state proxies but fails to improve closed-loop control under combined memory stress.
