# Air3D implementation checks — 20 October 2026

**Passed without training. Optimizer steps: 0.** The network was randomly initialized for inference and differentiation, and its weights were verified unchanged. No trained checkpoint or training results exist.

| Check | Observed result |
|---|---|
| Dynamics and Hamiltonian against pinned official Air3D | Maximum differences below 1e-15 |
| Evader control and pursuer disturbance against official code | Exact agreement on sampled cases |
| Hamiltonian against explicit max-min turn search | Maximum absolute difference 1.78e-15 |
| Autodiff against finite differences, float64 | Maximum absolute difference 4.13e-7 |
| Explicit normalization chain rule | Maximum absolute difference 1.42e-14 |
| Time-to-go sign, analytic no-turn head-on case | Zero residual |
| Physics-loss parameter derivatives | Finite; no update applied |
| All three configs | Network construction and interior dependency-domain checks passed |
| Launcher without --train | Refused to start; no run directory created |
| Syntax and whitespace checks | Passed |

Small numerical-reference checks used a .1 s horizon, independent of PINN training. At 4096 held-out states, the mean difference between consecutive grids decreased from .00519 m (33 to 49 spatial nodes) to .00250 m (49 to 65 nodes). In the no-turn analytic case, mean error decreased from .00691 m to .00265 m; fine-grid maximum error was .0515 m. These first-order grids retain appreciable errors near nonsmooth regions.

Expanding the domain while matching spatial and heading spacing and the time-step schedule produced no detectable change at the sampled interior points for this short test. Frozen dynamics preserved the terminal function exactly. Equal-heading and head-on probes, obstacle projection and periodic heading interpolation passed.

Full details and versions are in preflight_cpu.json. Reproduce from the project root using the preflight command in the main README, with the optional --upstream argument to check the bundled official code. The preflight script never calls training. Checkpoint restart and full-horizon reference/PINN validation remain pending until training is requested. These checks establish implementation consistency, not trained accuracy or a safety guarantee.
