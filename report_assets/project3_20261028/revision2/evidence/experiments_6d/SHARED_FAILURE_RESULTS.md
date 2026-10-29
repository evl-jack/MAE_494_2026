# Shared failure diagnosis completed

[Full report, same-state traces and fixed interventions](shared_failure_diagnostic/README.md)

Finite differences confirm that the trained derivatives are computed correctly. Initially both models choose the opposite evader turn from both reference grids. The reference signs agree at the initial state, but magnitudes are not converged; the coarse coefficient fails the prior .01 stability margin, and early reference signs disagree along the unassisted path.

A 5 ms reference-turn prefix fails both models. Among the fixed tested durations, 3D_Long first avoids contact with 10 ms, and 4C with 50 ms, across all four poses and both control intervals. Shorter corrections can worsen minimum separation. These are reference-assisted interventions on one selected development encounter, not a retrained improvement or a general controller patch. No training or final-test queries occurred.
