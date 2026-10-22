# Air3D build plan — updated 20 October 2026

The user selected Air3D in place of Dubins3D and initially requested a pause before training. That pause was honored. On 22 October 2026 the user authorized training and requested VS Code setup and hardware checks. Smoke training, reduced CPU training and independent numerical comparison have now completed. The baseline's measured accuracy is not satisfactory; see experiments/experiment_1/README.md.

1. Implemented: official Air3D relative dynamics, max-min Hamiltonian, evader control and adversarial pursuer turn, checked against upstream commit a8127aa7825d58623e9646211644876c83dd71d0. Both speeds .75 m/s, turn bounds 3 rad/s, collision radius .25 m.
2. Implemented: original soft terminal-loss sine PINN, normalization/chain rules, uniform samples, terminal pretraining and expanding-time curriculum. Explicit Air3D config identity rejects old Dubins checkpoints; modern exact/diff alternatives are documented separately.
3. Implemented: smoke, reduced CPU (.5 s) and full paper-scale (1 s) configs. Widen spatial boxes to [-2,2] and [-3,3] for interior comparisons; document this departure.
4. Implemented: independent NumPy Air3D solver with periodic heading, constant spatial extension, local Lax-Friedrichs viscosity, Air3D speed bounds/CFL and obstacle projection.
5. Current checks: syntax/import, direct pinned-upstream comparison, derivatives, max-min optimization, finite physics-loss parameter gradients without updates, sampling, and small .1 s solver refinement/analytic/boundary tests. Save check results in checks/. Optimizer steps remain zero.
6. Save implementation, documentation and check results in Git, then synchronize the separate repository at the user's separate homework project folder. Preserve upstream source and prior history.
7. Completed 22 October: hardware check, VS Code launch configurations, 60-step smoke training, 12,000-step reduced CPU training, checkpoints and logs. The full paper-scale run is not selected automatically.
8. Completed: comparison at .5 s, grid refinement/boundary checks, reload/restart verification, plots, metrics and experiments/experiment_1/README.md. The reduced model's final value MAE is .0915 m and false-safe fraction among reference-unsafe states is 46.4%; accuracy is not satisfactory. Further physics training/architecture work remains future experimentation. Empirical agreement is not a safety guarantee.

Reference labels do not enter PINN training. No full quadrotor model, paid services, external logging or separate gradient reliability study is included.
