# Experiment 3E — Training duration versus network capacity

**Completed 28 October 2026 through VS Code Run and Debug.** [Results](RESULTS.md): Long64 at 22,000 steps reduces final-time MAE 12.99% versus Adam +200; Wide96 at 10,000 reduces it 6.80%. The nominal-work budgets are close but actual runtimes differ. All original models and reserved final states remain unchanged.

The fixed protocol compares a longer width-64 run with a width-96 model. Both retain the Air3D formulation, three sine hidden layers, raw heading, exact terminal/obstacle output and physics-only Adam loss. No numerical-reference labels or bounds enter training.

## Why this comparison

Earlier refinements reduced physics residual without consistently improving reference-value accuracy. At Adam +200, removing or restarting optimizer history did not restore local value descent in the tested directions. That does not establish an accuracy ceiling or show that more training cannot help, but motivates separating additional optimization steps from a larger approximation space.

## Fixed runs and comparisons

| Model | Hidden width | Parameters | Curriculum steps | Full-horizon hold | Total steps |
|---|---:|---:|---:|---:|---:|
| Original 3A | 64 | 8,705 | 10,000 | 0 | 10,000 |
| Saved Adam +200 | 64 | 8,705 | 10,000 | 200 | 10,200 |
| Longer run | 64 | 8,705 | 10,000 | 12,000 | **22,000** |
| Wider run | 96 | 19,201 | 10,000 | 0 | **10,000** |

The longer run branches from original 3A with its optimizer and sampling states. The wider network is initialized from scratch with seed 7. Its parameters are different because the architecture differs. The wider run's sampling RNG is then set to the state immediately after the original width-64 initialization; every physical batch throughout its 10,000-step curriculum matches original 3A. Initializations are not made equivalent by matching the integer seed.

The same-update comparison is **original 3A versus width 96**, both at 10,000 curriculum steps and the same physical samples. The approximate nominal-work comparison is **width 64 at 22,000 versus width 96 at 10,000**. Wider capacity and longer full-horizon exposure are different treatments; this is not a complete width-by-duration factorial experiment.

The longer run saves fixed snapshots at 10,200, 10,800, 12,000, 16,000 and 22,000. The first two are replay checks against the prior 3D Adam run; 12,000 and 16,000 are prespecified secondary accuracy endpoints. The wider run's endpoint is 10,000. No reference-based stopping or early endpoint selection changes either training schedule.

## Budget definition

For width w and this architecture, the linear-layer multiply-accumulate count per forward point is `2*w*w + 5*w`: 8,512 at width 64 and 18,912 at width 96. At 2,048 samples per step:

- Long64 total proxy: 22,000 x 2,048 x 8,512.
- Wide96 total proxy: 10,000 x 2,048 x 18,912.
- Wide/long ratio: approximately **1.0099**, within 1%.

This is a transparent work proxy, **not measured training FLOPs or matched wall time**. It excludes nonlinear activation/derivative costs and does not capture small-matrix CPU efficiency. Actual training times and sample counts must be reported alongside it. The longer run's cumulative time includes the archived original 3A time plus this continuation, rather than a new uninterrupted timing of all 22,000 steps. Reusing a saved checkpoint reduces this task's new compute, but not the model's cumulative training budget.

The longer run processes 45,056,000 cumulative training sample points; the wider run processes 20,480,000. The new continuation adds 24,576,000 points to original 3A. Repeated collocation sampling is physics data generation, not a finite labeled dataset.

## Hardware and preflight checks

The laptop reports an Intel Core Ultra 7 165U, 14 logical processors and 31.45 GiB physical RAM, with 15.56 GiB available at preflight. CPU training uses two threads. No CUDA device is available. Disk free space was about 695.6 GiB. These are preflight observations, not continuous thermal/load monitoring.

Both architectures passed physical derivative/normalization and Hamiltonian checks. Physics parameter gradients were finite. A short gradient-only benchmark measured median batch times .01183 s at width 64 and .01465 s at width 96; these initialization-time microbenchmarks are not total training-time predictions.

The full 10,000-batch sampler replay has identical hashes for the two widths and matches original 3A's final saved Torch RNG. Disposable four-step fixture runs verify that saving snapshots, or splitting and resuming training, preserves final model/optimizer/sampling states. Fixture updates are separate from the experimental runs. All preflight details and the sampling hash are in `preflight.json`.

The trainer changes are narrow: optional CPU sampling-RNG alignment to a reference initialization width, and optional immutable step snapshots. Existing configurations retain their prior behavior. The original 200/800-step Adam trajectory is checked again using the actual longer run's snapshots.

## Training, evaluation and saved files

The prepared VS Code launch is **Air3D: Experiment 3E - Capacity versus duration**. It launches from the Homework window with absolute paths to the main repo and its existing interpreter. **Resume capacity comparison** is separate and explicit. Native checkpoints are saved every 1,000 steps, plus the declared snapshots. An interruption can lose work since the last checkpoint; explicit resume restores the saved state. Completed experiments are not overwritten.

Only after all fixed endpoints complete, `compare_capacity_budget.py` evaluates the original 24,000 development states at all 21 saved horizons. Metrics include value MAE/RMSE/relative L2, both classification errors, unsafe-set IoU, fixed and new worst-tail errors, physical constraints, temporal increases, heading seam and physics residuals. The full-domain physics audit reuses the 8,192 points from Experiment 3D, seed 991736. No numerical reference is recomputed.

Reserved final-evaluation states remain outside training and development evaluation; their file is only hashed for preservation. These comparisons continue to use development references, so final generalization is not established. One seed and one fresh initialization per width cannot isolate capacity from initialization variability or establish a universal width advantage.

```powershell
python outputs/deepreach/capacity_budget.py --check
python outputs/deepreach/capacity_budget.py --train
python outputs/deepreach/compare_capacity_budget.py
```

For an interrupted run, use explicit `--train --resume`. Native run folders are `runs/experiment_3_e_long64` and `runs/experiment_3_e_wide96`. Configurations, protocol, hardware, progress, source snapshots and manifests are retained here. Models and results are copied into the Homework project after completion. The exact launch and completion status are recorded in the execution/training/evaluation files; a prepared launcher alone is not evidence that a run completed.
