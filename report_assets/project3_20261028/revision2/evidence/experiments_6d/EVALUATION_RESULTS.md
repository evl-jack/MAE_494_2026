# 6D development evaluation completed

[Full results, gradient diagnostics and limitations](development_evaluation/README.md)

The training-stage README and its manifest retain their original bytes. This later evaluation used 6,000 fresh relative groups with four joint poses each, at 21 horizons. No training updates or final-test queries occurred.

At 0.5 s, value MAE is 0.08695 m (4A), 0.02631 m (4B), and 0.02573 m (4C), versus 0.01943 m for fixed 3D_Long. Exact-output 4B improves on 4A by 69.75%; extending to 4C adds 2.19%. Equivalent-pose inconsistency and heading aliases remain. Control-relevant gradient signs are promising on reference-stable subsets, but closed-loop rollouts have not run.
