# MAE 494 — Project 3: Minimal DeepReach Reproduction

## Objective and interview context

Reproduce a minimal DeepReach physics-informed neural network (PINN) for Hamilton–Jacobi (HJ) reachability as an ASU Design Optimization Project 3 experiment.

According to the project interview notes, Professor Yi (Max) Ren explicitly approved reproducing DeepReach as sufficient for the assignment. He suggested HJ safe control and DeepReach and raised a question about whether learned safety value-function gradients provide useful, reliable control directions.

The immediate priority is reproducing the PINN. A separate investigation of gradient reliability is optional future work. DeepReach **does compute gradients**: automatic differentiation supplies the derivatives used in training and in deriving control from the value function. The open question concerns their accuracy and usefulness in an approximation.

## Primary sources

- Bansal and Tomlin, *DeepReach: A Deep Learning Approach to High-Dimensional Reachability*: [paper](https://arxiv.org/abs/2011.02082), [PDF](https://arxiv.org/pdf/2011.02082).
- [Official DeepReach repository](https://github.com/smlbansal/deepreach).
- Relevant upstream files on the inspected `public_release` branch:
  - [Dynamics](https://github.com/smlbansal/deepreach/blob/public_release/dynamics/dynamics.py)
  - [Network](https://github.com/smlbansal/deepreach/blob/public_release/utils/modules.py)
  - [Loss](https://github.com/smlbansal/deepreach/blob/public_release/utils/losses.py)
  - [Sampling](https://github.com/smlbansal/deepreach/blob/public_release/utils/dataio.py)
  - [Experiment launcher](https://github.com/smlbansal/deepreach/blob/public_release/run_experiment.py)

Record the exact upstream commit when implementing. The refactored repository includes options introduced after the original paper; its current defaults are not automatically the original experimental protocol.

## Initial example choice: Dubins3D

Start with the repository's documented avoid-mode Dubins3D example. It has three state variables and one bounded control, making an independent grid-based comparison practical. Air3D remains a possible follow-up for closer comparison to the paper's running example, but adds adversarial dynamics.

The upstream tutorial parameters are:

| Parameter | Value |
| --- | --- |
| Target radius | 0.25 |
| Constant speed | 0.6 |
| Maximum turn rate | 1.1 |
| Heading normalization factor | 1.2 |
| Set mode | avoid |
| Reachability option | minWith=target |

For state `s=(x,y,theta)` and control `|u| <= omega_max`:

```text
dx/dt     = v cos(theta)
dy/dt     = v sin(theta)
dtheta/dt = u
l(s)      = sqrt(x^2 + y^2) - R
H(s,p)    = v[cos(theta) p_x + sin(theta) p_y] + omega_max |p_theta|
u*(s)     = omega_max sign(p_theta)
```

The target is `l(s) <= 0`. The avoid-mode backward reachable tube identifies states from which entering the target cannot be prevented within the horizon.

Use time-to-go `tau = T-t`, with `V(s,0)=l(s)`. The inspected upstream target-constrained residual is:

```text
r = max(dV/dtau - H(s, grad_s V), V - l(s))
```

Minimize its absolute magnitude together with a weighted terminal-condition loss. Verify the sign convention, normalization chain rules, and actual loss weights against the pinned source before training.

## Reproduction requirements

1. **Network:** Sine activations and the upstream SIREN initialization. The inspected module uses `sin(30*z)`. Trace the constructor to establish the actual number of layers.
2. **Physics loss:** Automatic time and state derivatives, matching dynamics and Hamiltonian, and the HJ variational inequality.
3. **Terminal condition:** Use the original soft terminal-loss formulation for the baseline. Current Dubins3D code selects an exact-boundary model; trace launcher overrides and document any use of that later option.
4. **Sampling:** Uniform sampling in normalized state space, terminal samples in training batches, terminal-only pretraining, and gradual expansion of the time interval.
5. **Training:** Seeded runs, explicit optimizer and loss settings, recorded device and package versions, and resumable checkpoints.
6. **Configurations:** A quick CPU smoke configuration and a source-faithful configuration. Clearly label reductions in network size, samples, iterations, or horizon.

The paper's reported Air3D setup describes width 512, a three-layer network, roughly 65k samples, Adam at learning rate 1e-4, 10k pretraining iterations, and 100k curriculum iterations. Check layer-count semantics and distinguish these settings from modern repository defaults. Published Air3D accuracy figures are not Dubins3D results.

## Smallest feasible build plan

- Inspect available Python, PyTorch, CPU/GPU, upstream code, dependency requirements, and licensing.
- Write a compact PyTorch implementation with explicit configuration and a documented mapping to source equations and code.
- Run smoke checks, then a feasible nontrivial training run; save model, optimizer, configuration, random state, and curriculum progress.
- Generate an independent numerical reference for the same Dubins3D problem.
- Compare learned and reference value functions and reachable tubes.
- Save metrics and plots and write a short results report with exact reproduction commands.

Routine setup and implementation choices can be made from the available environment. Request user input only when a genuinely required choice cannot be discovered.

## Validation

An appropriate minimal reference is an independent monotone grid-based HJ solver, such as an upwind/local Lax–Friedrichs scheme with a justified CFL limit. Use periodic heading, explicit spatial boundary handling, matching parameters, and a grid-refinement check. Compare within a region where spatial boundaries do not contaminate the result. Reference values are for evaluation, not PINN supervision.

Required checks and diagnostics:

- Terminal-condition error on held-out states.
- Autodiff versus finite differences away from nonsmooth points.
- Analytic Hamiltonian versus direct bounded-control optimization.
- Time-direction and sign sanity checks.
- Checkpoint reload consistency.
- Numerical-reference refinement.
- Separate PDE and terminal loss curves.
- Held-out value-function errors.
- Reachable-tube overlap and classification errors, including a clearly defined false-safe fraction.
- Value slices and zero-level contours at several times and headings.

Low training loss alone does not establish a correct reachability solution. Numerical agreement is empirical evidence, not a formal safety guarantee.

## Expected deliverables

- Requirements and installation instructions.
- Exact commands for smoke training, longer training, resuming, evaluation, and plotting.
- Source code and reproducible configurations.
- Actual saved checkpoints and recorded run metadata.
- Independent reference results, quantitative diagnostics, and plots.
- A report distinguishing completed results from proposed work, reduced experiments from full training, and reproduction from extensions.

If available compute does not produce good numerical agreement, report the measured errors and provide a longer-training command. Do not claim published-quality reproduction based on a smoke run.

## Current status

As of October 19, 2026, the paper and selected upstream source files have been inspected, and Dubins3D is the initial choice. A fresh Codex coding chat titled **Project 3: Minimal DeepReach PINN reproduction** has been started with the context and build requirements above.

This document records the project scope and implementation plan. It does not claim completed training, saved checkpoints, or validated accuracy; those results must be added after execution.
