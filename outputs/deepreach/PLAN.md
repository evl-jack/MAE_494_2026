# Air3D build plan — updated 20 October 2026

The user selected Air3D in place of Dubins3D and authorized implementation with an explicit pause before actual training.

1. Implemented: official Air3D relative dynamics, max-min Hamiltonian, evader control and adversarial pursuer turn, checked against upstream commit a8127aa7825d58623e9646211644876c83dd71d0. Both speeds .75 m/s, turn bounds 3 rad/s, collision radius .25 m.
2. Implemented: original soft terminal-loss sine PINN, normalization/chain rules, uniform samples, terminal pretraining and expanding-time curriculum. Explicit Air3D config identity rejects old Dubins checkpoints; modern exact/diff alternatives are documented separately.
3. Implemented: smoke, reduced CPU (.5 s) and full paper-scale (1 s) configs. Widen spatial boxes to [-2,2] and [-3,3] for interior comparisons; document this departure.
4. Implemented: independent NumPy Air3D solver with periodic heading, constant spatial extension, local Lax-Friedrichs viscosity, Air3D speed bounds/CFL and obstacle projection.
5. Current checks: syntax/import, direct pinned-upstream comparison, derivatives, max-min optimization, finite physics-loss parameter gradients without updates, sampling, and small .1 s solver refinement/analytic/boundary tests. Save check results in checks/. Optimizer steps remain zero.
6. Save implementation, documentation and check results in Git, then synchronize the separate repository at the user's separate homework project folder. Preserve upstream source and prior history.
7. PAUSE BEFORE TRAINING: no smoke training, terminal pretraining, curriculum training or optimizer restart test. The launcher requires an explicit --train flag.
8. After the user requests training: run smoke and feasible nontrivial training; save resumable checkpoints, logs and runtime. Validate the reference at the actual horizon, then compare held-out terminal/PDE/value/BRT metrics and plots. Report false-safe fractions, grid sensitivity and limitations honestly. Empirical agreement is not a safety guarantee.

Reference labels do not enter PINN training. No full quadrotor model, paid services, external logging or separate gradient reliability study is included.
