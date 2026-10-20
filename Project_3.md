# MAE 494 — Project 3: DeepReach Air3D Reproduction

## Objective and interview context

Reproduce a minimal DeepReach physics-informed neural network (PINN) for Hamilton–Jacobi (HJ) reachability as an ASU Design Optimization Project 3 experiment.

According to the project interview notes, Professor Yi (Max) Ren explicitly approved reproducing DeepReach as sufficient for the assignment. He suggested HJ safe control and DeepReach and raised a question about whether learned safety value-function gradients provide useful, reliable control directions.

The immediate priority is reproducing the PINN. A separate investigation of gradient reliability is optional future work. DeepReach **does compute gradients**: automatic differentiation supplies the derivatives used in training and in deriving control from the value function. The open question concerns their accuracy and usefulness in an approximation.

## Current status — October 20, 2026

The selected case is now **Air3D: two drones avoiding collision at a fixed altitude**, replacing the initial Dubins3D obstacle example. The Air3D implementation, numerical-reference solver, configurations and implementation checks are saved.

**Training is paused at the user's request. No PINN training, trained checkpoints or trained-accuracy results exist yet.** The checks below use a randomly initialized network without changing its weights. They establish implementation consistency, not learned accuracy or a safety guarantee.

- [Code and setup instructions](outputs/deepreach/README.md)
- [PINN and Air3D equations](outputs/deepreach/deepreach.py)
- [Independent numerical solver](outputs/deepreach/reference.py)
- [Checks without training](outputs/deepreach/preflight.py)
- [Actual implementation-check results](outputs/deepreach/checks/README.md)
- [Future trained-model comparisons](outputs/deepreach/validate.py)
- [Current build plan](outputs/deepreach/PLAN.md)

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

## Completed checks without training

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

These results are solver/implementation checks, not PINN training results. Full-horizon reference validation remains pending.

## Running checks

From the repository root with Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r outputs/deepreach/requirements.txt
.\.venv\Scripts\python.exe outputs/deepreach/preflight.py --config outputs/deepreach/configs/cpu.json --out outputs/deepreach/checks/preflight_cpu.json
```

Preflight never trains. [The implementation README](outputs/deepreach/README.md) contains future training, resuming and comparison commands. Training requires an explicit --train flag; even smoke training has not been executed. Optimizer/checkpoint restart checks are also deferred.

## Next work after training is requested

Run smoke training and a feasible nontrivial experiment; save model/optimizer/configuration/random state and curriculum progress; validate the reference at the actual horizon; then report measured value/PDE/terminal/BRT errors and plots. If agreement is poor, report it candidly and provide a longer-training command.

Low loss or numerical agreement alone does not establish a safety guarantee. A separate study of learned-gradient reliability remains outside the present scope.
