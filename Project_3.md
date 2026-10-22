# MAE 494 — Project 3: DeepReach Air3D Reproduction

## Objective and interview context

Reproduce a minimal DeepReach physics-informed neural network (PINN) for Hamilton–Jacobi (HJ) reachability as an ASU Design Optimization Project 3 experiment.

According to the project interview notes, Professor Yi (Max) Ren explicitly approved reproducing DeepReach as sufficient for the assignment. He suggested HJ safe control and DeepReach and raised a question about whether learned safety value-function gradients provide useful, reliable control directions.

The immediate priority is reproducing the PINN. A separate investigation of gradient reliability is optional future work. DeepReach **does compute gradients**: automatic differentiation supplies the derivatives used in training and in deriving control from the value function. The open question concerns their accuracy and usefulness in an approximation.

## Current status — October 22, 2026

**Experiment 1 — Reduced CPU baseline is complete.** The first trained Air3D PINN and independent numerical comparison are now saved. This reproduces the core training workflow, but its measured accuracy is not satisfactory.

- [Experiment 1: full report, plots and artifacts](outputs/deepreach/experiments/experiment_1/README.md)
- [Experiment index](outputs/deepreach/experiments/README.md)
- [Code and setup instructions](outputs/deepreach/README.md)
- [Measured metrics](outputs/deepreach/experiments/experiment_1/metrics.json)

Public materials include the report, comparison figures, aggregate diagnostics and configuration. Raw model/optimizer checkpoints, source snapshots, training logs and reference arrays remain in the local project copies.

The 60-step smoke run is a setup check and is not counted as another experiment. Full paper-scale training has not run; no Experiment 2 has been executed.

## Experiment 1 — results summary

The reduced model uses three sine hidden layers of width 64, 2,048 samples per iteration, 2,000 terminal-pretraining steps and 10,000 physics-curriculum steps. Training took 206.4 seconds on two CPU threads, with a .5 s horizon.

| Time remaining | Value MAE | Unsafe-region IoU | False-safe among reference-unsafe |
|---|---|---|---|
| 0 s | .01184 m | .930 | 6.28% |
| .25 s | .04230 m | .695 | 23.77% |
| .5 s | .09150 m | .478 | 46.42% |

False-safe here means PINN>0 while the approximate grid reference is <=0, divided by the reference-unsafe sample count. The comparison uses 24,000 held-out interior states. At .5 s, 5,276 are reference-unsafe; false-safe among all states is 10.20%. These are reference-relative classifications, not certified ground truth.

**Interpretation:** the network learned the terminal condition considerably better than the time-dependent reachability solution. Checkpoint reload and optimizer restart checks passed. Reference refinement improved, and the larger-domain test showed negligible interior sensitivity. The reduced PINN nevertheless misses substantial unsafe regions, so successful reproduction of the paper's reported accuracy is not claimed.

![Experiment 1: PINN values with grid reference contours in white and PINN contours in red](outputs/deepreach/experiments/experiment_1/figures/value_and_brt_slices.png)

## The Air3D problem

The evader chooses a turn rate to avoid collision; a worst-case pursuer chooses its turn rate to force collision. The model uses relative position and heading in the evader's rotating coordinate frame. It does not include altitude, thrust or full quadrotor dynamics.

| Parameter | Value |
| --- | --- |
| Both drone speeds | 0.75 m/s |
| Evader and pursuer turn bounds | ±3 rad/s |
| Collision radius | 0.25 m |
| Reduced experiment horizon | 0.5 s |
| Full experiment horizon | 1 s |
| State | Relative x, y, heading psi |
| Network input | Time remaining tau and the three states |

With evader turn u and pursuer turn d:

```text
xdot   = v*(cos(psi)-1) + u*y
ydot   = v*sin(psi) - u*x
psidot = d-u
l(s)   = sqrt(x*x+y*y)-R
```

For p=grad_s(V), the avoid Hamiltonian is max_u min_d p.f:

```text
H  = v*((cos(psi)-1)*p_x + sin(psi)*p_y)
     + omega*abs(y*p_x-x*p_y-p_psi) - omega*abs(p_psi)
u* =  omega*sign(y*p_x-x*p_y-p_psi)
d* = -omega*sign(p_psi)
```

Using time remaining tau=T-t:

```text
max(V_tau-H, V-l) = 0
V(0,s) = l(s)
```

For the ideal solution, V<=0 identifies states from which collision can be forced despite optimal evasion. Controls derived from a learned approximation are candidates and are not certified safe.

## Four parts of the implementation

1. **Problem:** dynamics, collision target, control/disturbance bounds and max-min Hamiltonian.
2. **Neural solver:** a sine network predicts the scalar value from time and state. Terminal pretraining learns the known zero-time function; physics training then expands the sampled time interval. Autodiff supplies the derivatives in the HJI loss.
3. **Independent grid solver:** NumPy local Lax–Friedrichs differences, periodic heading, explicit CFL and target-obstacle projection provide an approximate reference. Spatial boundaries use constant extension and are checked from an interior region against a larger domain.
4. **Comparison:** after training, measure held-out terminal and physics errors, value errors, unsafe-region overlap, false-safe fractions, and value/zero-contour slices. Reference labels never enter PINN training.

## Reproduction choices

The implementation is grounded in the [paper](https://arxiv.org/abs/2011.02082) and [official source pinned at a8127aa](https://github.com/smlbansal/deepreach/tree/a8127aa7825d58623e9646211644876c83dd71d0).

The baseline uses original **soft terminal loss**, distinct from the modern repository's exact-boundary default. Inputs and output have explicit normalization and autodiff chain rules. Hidden activations use sin(30*z) and SIREN initialization. The terminal/PDE weight is calibrated at curriculum start and then fixed; mean losses and this balancing choice are documented departures from modern adaptive/sum-loss options.

| Configuration | Actual sine hidden layers | Samples/step | Pretrain + curriculum iterations | Horizon |
| --- | --- | --- | --- | --- |
| Smoke | 3 × 32 | 256 | 20 + 40 | 0.5 s |
| Reduced CPU | 3 × 64 | 2048 | 2,000 + 10,000 | 0.5 s |
| Full paper-scale | 3 × 512 | 65,000 | 10,000 + 100,000 | 1 s |

All use Adam at 1e-4 and currently select CPU. The modern repository's num_hl=3 creates four sine hidden layers; actual layer counts are explicit here. Spatial boxes are widened to [-2,2] m for reduced runs and [-3,3] m for full, departing from upstream scaling to permit interior reference comparisons. See the implementation README for the dependency-region bound and numerical limitations. Full is a paper-scale configuration, not a claim of exact paper replication.

## Initial implementation checks — before Experiment 1

The [saved check data](outputs/deepreach/checks/preflight_cpu.json) record **zero optimizer steps**.

| Check | Result |
| --- | --- |
| Dynamics/Hamiltonian against pinned official Air3D | Differences below 1e-15 |
| Candidate controls/disturbance against official source | Exact agreement on sampled cases |
| Hamiltonian against direct bounded max-min search | Maximum difference 1.78e-15 |
| Autodiff against float64 finite differences | Maximum difference 4.13e-7 |
| Explicit normalization chain rule | Maximum difference 1.42e-14 |
| Analytic time-to-go sign check | Zero residual |
| Physics-loss parameter derivatives | Finite; weights unchanged |
| Three configs and interior-domain bounds | Passed |
| Launcher without explicit --train | Refuses training |
| Syntax checks | Passed |

A small **0.1 s** grid test showed refinement differences decreasing from 0.00519 m to 0.00250 m in mean absolute value. In the no-turn analytic case, mean error decreased from 0.00691 m to 0.00265 m; fine-grid maximum error remained 0.0515 m. Matching grid spacing and time steps, expanded-domain values agreed at the sampled interior points for this short test. Frozen dynamics, obstacle projection and periodic heading checks also passed.

These initial results are implementation checks. The later Experiment 1 report records the trained comparison and reference refinement at its actual .5 s horizon. The full 1 s paper-scale experiment remains unexecuted.

## Running checks

From the repository root with Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r outputs/deepreach/requirements.txt
.\.venv\Scripts\python.exe outputs/deepreach/preflight.py --config outputs/deepreach/configs/cpu.json --out outputs/deepreach/checks/preflight_cpu.json
```

Preflight never trains. [The implementation README](outputs/deepreach/README.md) contains training, resuming and comparison commands. Training requires an explicit --train flag, and existing checkpoints are protected against accidental overwriting. The smoke and reduced CPU runs and optimizer/checkpoint restart tests have completed.

## Future experiments — not executed

Experiment 1 is the saved baseline. A paper-scale configuration is available but has not run. Smaller network capacity, fewer samples/iterations, broad uniform sampling and loss balancing are plausible contributors to the error; controlled follow-up experiments are required to isolate them. Scaling up alone is not a demonstrated remedy.

No new training was performed for this publication. Low loss or numerical agreement alone does not establish a safety guarantee. A separate learned-gradient reliability study remains outside the present scope.
