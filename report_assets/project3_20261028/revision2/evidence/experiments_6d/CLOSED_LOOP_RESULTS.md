# Closed-loop tests completed

[Full results, policy matrix, trajectories and remaining failure](closed_loop_evaluation/README.md)

The fixed 8-by-8 policy matrix ran at both time steps with no training or final-test queries. On the reference-safe subset against the reference pursuer, 4A had 40 contacts across 17 encounter groups, 4B had 9 across 3 groups, and 4C had 4 across 1 group. There are 576 posed initial states representing 144 groups. The best saved 3D model fails on the same remaining group; reference feedback avoids contact.

The remaining failure survives halving the control interval, and both learned models initially flag that encounter unsafe. It provides a concrete next target for first-action and gradient diagnosis. These finite tests are not an exhaustive adversarial guarantee.
