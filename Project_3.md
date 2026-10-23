# MAE 494 — Project 3: DeepReach Air3D Reproduction

## Objective and interview context

Reproduce a minimal DeepReach physics-informed neural network (PINN) for Hamilton–Jacobi (HJ) reachability as an ASU Design Optimization Project 3 experiment.

According to the project interview notes, Professor Yi (Max) Ren explicitly approved reproducing DeepReach as sufficient for the assignment. He suggested HJ safe control and DeepReach and raised a question about whether learned safety value-function gradients provide useful, reliable control directions.

The immediate priority is reproducing the PINN. A separate investigation of gradient reliability is optional future work. DeepReach **does compute gradients**: automatic differentiation supplies the derivatives used in training and in deriving control from the value function. The open question concerns their accuracy and usefulness in an approximation.

## Current status — October 23, 2026

**Experiments 1 and 2 are complete.** Experiment 1 established a reduced CPU baseline. Experiment 2 tested three separate changes to reduce its errors, with all three runs launched through VS Code Run and Debug on October 22, 2026. Lower terminal-loss weighting produced the strongest final-horizon results in this single-seed comparison: value MAE fell by 51.1%, from .09150 m to .04477 m, and false-safe among reference-unsafe states fell from 46.42% to 10.82%. This is improved approximation accuracy, not a demonstrated safety guarantee.

- [Experiment 1: full report, plots and artifacts](outputs/deepreach/experiments/experiment_1/README.md)
- [Experiment index](outputs/deepreach/experiments/README.md)
- [Code and setup instructions](outputs/deepreach/README.md)
- [Measured metrics](outputs/deepreach/experiments/experiment_1/metrics.json)

Public materials include the report, comparison figures, aggregate diagnostics and configuration. Raw model/optimizer checkpoints, source snapshots, training logs and reference arrays remain in the local project copies.

The 60-step smoke run is a setup check and is not counted as another experiment. Full paper-scale training has not run. The summary below records all three completed Experiment 2 candidates; hybrid training and closed-loop controller evaluation remain future work.

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

## Experiment 2 — controlled error-reduction comparison

### Why we did it

Experiment 1 learned the known time-zero collision-distance function more accurately than the time-dependent reachability solution. At .5 s it missed 46.42% of reference-unsafe states. We tested whether loss balance, the spatial distribution of physics samples, or insufficient training at the full horizon contributed to this error. The aim was to improve the reduced model before committing to a larger network or paper-scale computation.

### What we did

We ran three separate candidates against the unchanged Experiment 1 baseline:

| Candidate | Change | Reason for testing it |
|---|---|---|
| **A — Lower terminal-loss weight** | Divide the initially calibrated terminal multiplier by 10, from about 106.43 to 10.64; keep it fixed afterward | Give the physics equation more influence relative to matching the zero-time condition |
| **B — Focused physics sampling** | Draw 50% of nonterminal physics samples uniformly by area inside a radius-1 m disk; retain uniform-box sampling for the other 50% | Spend more of the same sample budget near the region where collision can occur within the modeled horizon |
| **C — Additional full-horizon training** | Continue Experiment 1's exact model, Adam optimizer and random state for 10,000 additional updates, with time sampled over the full [0,.5] s interval | Test whether more optimization at the final horizon helps after the original expanding-time curriculum |

A and B each started fresh with the original 2,000 terminal-pretraining + 10,000 physics-curriculum steps. C inherited the original 12,000 steps and finished at 22,000 cumulative steps; it therefore has a larger training budget. The radius in B follows the physical bound R+2*v*T=1 m. Terminal/pretraining coordinate samples remain uniform. B retains the original automatic loss-calibration rule, whose changed first physics batch produces a terminal multiplier of about 125.35.

All candidates retain the same three sine hidden layers of width 64, 2,048 samples per step, Air3D dynamics, .5 s horizon, spatial domain, Adam learning rate of 1e-4, seed 7 and two CPU threads. Each run saved its own configuration, checkpoint, optimizer state, training history, runtime, metrics and plots in the local project. Experiment 1's checkpoint and numerical-reference arrays were preserved and their hashes checked.

We reproduced the baseline measurements, then reused the checked numerical grid and the same 24,000 held-out interior states at 0, .25 and .5 s for every comparison. Separate full-box samples measured terminal and physics errors. **No numerical-reference values or gradients entered training**: Experiment 2 remains physics-informed training, not hybrid supervised training.

### What it showed

Results at **.5 seconds remaining**:

| Run | Value MAE [m] | Unsafe-region IoU | False-safe / reference-unsafe | False-unsafe / reference-safe | Full-box terminal MAE [m] |
|---|---|---|---|---|---|
| Experiment 1 baseline | .09150 | .478 | 46.42% | 3.43% | .00891 |
| **A — Lower terminal weight** | **.04477** | **.688** | **10.82%** | 8.33% | .01457 |
| B — Focused sampling | .07189 | .626 | 20.00% | 7.86% | .01045 |
| C — Additional full-horizon training | .06048 | .613 | 22.80% | 7.31% | **.00708** |

False-safe means the PINN predicts V>0 while the reference has V<=0, divided by the reference-unsafe count. False-unsafe means the PINN predicts V<=0 while the reference has V>0, divided by the reference-safe count. IoU measures intersection/union of the predicted and reference unsafe regions; higher is better. All classifications are relative to an approximate numerical reference.

- **A produced the strongest final-horizon improvement:** value MAE decreased 51.1%, false-safe decreased 35.60 percentage points, and IoU increased from .478 to .688. However, terminal error increased and more reference-safe states were labeled unsafe. Lower weighting improved the balance for this run, rather than improving every metric.
- **B improved value MAE by 21.4%** and reduced false-safe to 20.00%. It outperformed the baseline on the final-horizon classification metrics, but its full-box physics residual increased from .09033 to .09979. Better regional predictions did not imply better physics residual everywhere.
- **C improved value MAE by 33.9%** and reduced false-safe to 22.80%. It also improved terminal error. Its value MAE was lower than B's, while B had fewer missed reference-unsafe states and higher IoU.

A and B recorded 326.5 s and 341.5 s of training, respectively. C added 230.6 s to the baseline's 206.4 s, for 436.9 s cumulative training. These exclude evaluation/setup time; debugger overhead and machine workload prevent interpreting the runtime differences as optimizer-efficiency results.

**Conclusion:** changing how we train can substantially improve a small PINN without enlarging the network. A achieved the best measured final-horizon tradeoff among the tested candidates, showing that loss weighting is a useful direction for further study. Extra training helped C but was not the strongest result.

### Limits of this conclusion

These are exploratory results for one seed and selected settings. A and B are separate experiments; no combined candidate was run. Because the same held-out results were used to select improvements, they now serve as validation comparisons; a new untouched test set and repeated seeds would strengthen a final performance claim. The study measured values, residuals and unsafe-region classifications. It did **not** establish reference-gradient accuracy, closed-loop collision-avoidance performance, or certified safety. Improving those requires further evaluation, not an inference from lower value error alone.

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

## Next investigations — not executed

Experiment 1 remains the baseline and Experiment 2A is the strongest reduced-model candidate so far. Possible next investigations include repeated seeds and an untouched test set, value-gradient and control comparisons, closed-loop encounter simulations, exact terminal-condition enforcement, periodic heading inputs, and hybrid training with carefully separated reference labels. Alternative optimizers and local predictive safety filters have been discussed but not implemented or tested.

A paper-scale configuration is available but has not run. Experiment 2 supports further work on training choices; scaling up alone is not a demonstrated remedy. This October 23 documentation update reports the completed October 22 runs and launches no new training. Low loss or numerical agreement alone does not establish a safety guarantee.
