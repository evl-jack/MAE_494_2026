# Local physics-loss audit completed

[Full report, residual maps and loss-gradient diagnostics](local_physics_audit/README.md)

The physics loss exposes the selected failure region. For 4C, mean absolute native VI residual is 0.13324 on reference-stable wrong-turn points, versus 0.01099 on the fresh global audit and 0.02085 on its late-time subset. Local parameter-gradient signals remain strong.

Residual magnitude does not distinguish wrong from right turning signs well within the 6D map (AUC 0.482), while 3D_Long shows stronger ranking (0.881). Global and local-wrong physics gradients are nearly orthogonal; local objectives can also conflict. This supports a controlled fixed-budget sampling/priority test, not a claim that a loss rewrite or sampling alone is a proven fix. No optimizer, parameter step, new solver run, rollout or final-test query occurred.
