# Recommendation memo — draft for review

**To:** Project research collaborator  
**Subject:** What the small-scale DeepReach study supports  
**Date:** 28 October 2026  
**Delivery status:** Prepared locally; not sent

We investigated whether a laptop-scale physics-informed network can approximate the Air3D collision-avoidance value function, what improves its accuracy, and whether those gains improve gradient-derived controls.

The strongest practical result is that formulation deserves attention before increasing scale. Reducing the soft terminal-loss multiplier lowered development value MAE from .09150 to .04477 m. Building the known terminal and obstacle conditions into the network output reduced it further to .02602 m without adding physics updates. That comparison also changed initialization and removed terminal pretraining, so we attribute the gain to the formulation package rather than one isolated equation.

Additional training subsequently helped. Our selected relative-coordinate model achieved .02008 m final-horizon MAE on 24,000 previously unused states, a 12.61% reduction versus the short Adam refinement. This confirms a value-accuracy improvement for the same simplified game and evaluation domain. It does not certify safe control.

The corresponding joint-coordinate network exposed a separate reliability issue. Its six states describe the same intrinsically three-state game, but equivalent poses and headings can produce different predictions. The latest uniform and residual-guided continuations both improved value MAE by about 10% relative to their parent. Residual-guided sampling improved some late-time physics diagnostics, but its .32% primary MAE advantage over uniform sampling was inconclusive and it did not reduce the primary contact count. We recommend retaining uniform sampling as the simpler baseline for further comparison.

We would invest further in neural reachability as an approximation research tool, particularly where many queries or genuinely higher-dimensional problems justify it. We would not yet use this model as a safety assurance mechanism. The numerical reference feedback also failed in one newly identified encounter, so remaining disagreements cannot all be attributed to the neural network. Our fixed low-dimensional benchmark does not establish an accuracy-matched speed advantage over a cached grid solver.

The next useful experiment, if this work continues, is a focused reference/feedback refinement around that encounter, followed by a targeted control-gradient or representation intervention evaluated across multiple seeds. More blind training or broader residual prioritization is not justified by these results alone.

We can conclude the present study now: it demonstrates substantial formulation gains and documents why lower physics loss and better average values do not automatically establish reliable control. The unused 6D final set remains available for a later frozen confirmatory assessment.

[Full technical analysis](REPORT.md) · [Evidence register](evidence.json)
