# Experiment 3D — Short physics-only refinement of 3A

[Optimizer-history diagnostic](optimizer_history_probe/README.md) is complete: removing momentum or resetting Adam does not restore value descent at Adam +200. All 160 probes there lower audit physics loss while worsening final-time value MAE. The report records the older-checkpoint comparison and limits; no restart training was run.

[Geometry/horizon weighting probes](geometry_horizon_probe/README.md) tested the follow-up hypothesis without training. Weighting helps locally at 3A but all tested directions at Adam +200 worsen final-time value accuracy, including unweighted controls. No new checkpoint is promoted.

[Three follow-up diagnostics](followup_diagnostics/README.md) examine location, horizon and value changes without training. Controlled loss reduction is dominated by the outer region; Adam +200 improves values broadly, beyond changes in safe/unsafe classification.

Completed 28 October 2026. The letter D labels the experiment; the game still has three state dimensions. [Results and interpretation](RESULTS.md).

## Question and fixed protocol

Do the promising finite-step directions transfer to sequential refinement? Can we lower the remaining physics residual and improve reference accuracy with a small additional budget?

The protocol was saved before training and is retained in `protocol.json`, with its hash in `training_manifest.json`. All branches start from 3A checkpoint SHA256 `44d19503406e4339fda5376c1074a20e5bf2c3508085af9f47d159e9858d8b62`, retaining its network, exact terminal/obstacle output, learning rate .0001 and saved Adam moments. No architecture, reference bounds or supervised labels were added.

- Adam: save fixed endpoints after 200 and 800 additional updates on one trajectory.
- Plain gradient with step selection: 200 construction-gradient batches.
- Second-moment-scaled gradient with step selection: 200 construction-gradient batches.

Sampling continues the parent's saved Torch RNG, with 2,048 states per batch: 1,792 full-horizon time samples uniform over 0 to .5 s, and 256 zero-time physics samples. Spatial/heading bounds are unchanged. All branches use the same first 200 batches, verified by byte hashes; this differs from the eight diagnostic batches used in the preceding finite-step study. Adam at 800 sees 600 additional fresh batches.

## Controlled directions and acceptance

Each controlled iteration computes the current mean absolute HJI-VI residual gradient g. Standard Adam advances its saved moments once and produces a temporary proposal. Its actual parameter displacement supplies the norm for equal-size direction comparisons. That temporary proposal is then restored before evaluating alternatives.

Plain direction: -g. Scaled direction: -g/(sqrt(v_hat)+epsilon), using the **updated**, bias-corrected Adam second moment. Both are rescaled to the temporary Adam displacement norm. Candidate multipliers are .1, .3 and 1; unchanged parameters are also an option. The candidate with the lowest physics loss on the same construction batch is accepted. No independent audit or reference error enters acceptance. This is a finite grid search, not a formal trust-region, Armijo, L-BFGS or standard RMSprop implementation.

The moment policy is explicit: moments advance once per construction gradient, even if every proposed parameter move is rejected. In this run all 200 controlled iterations accepted a move. Plain-gradient selections were .1 in 11 cases and .3 in 189; scaled selections were .3 in 186 and 1 in 14. Although first moments do not supply these directions, they affect their Adam-based displacement norm. The plain branch therefore is not ordinary SGD at a fixed learning rate.

No reference-based early stopping was used. All endpoints were fixed before training; nonfinite losses, gradients or parameters would stop the run. The script requires `--train` and refuses an existing experiment folder. It does not implement automatic resume.

## Budget and execution

| Endpoint | Gradient batches | Extra trial-loss batches | Total physics batch assessments | Unique construction samples | Training time [s] |
|---|---:|---:|---:|---:|---:|
| Adam 200 | 200 | 0 | 200 | 409,600 | 4.34 |
| Adam 800 | 800 | 0 | 800 | 1,638,400 | 15.28 |
| Plain 200 | 200 | 600 | 800 | 409,600 | 8.57 |
| Scaled 200 | 200 | 600 | 800 | 409,600 | 7.91 |

Adam 200 matches gradient batches; Adam 800 matches total physics batch assessments. Neither comparison matches FLOPs exactly: gradient batches require parameter differentiation through input derivatives, while trial-loss batches do not. The controlled methods repeatedly assess the same construction states at different proposed weights. Timings exclude evaluation and interpreter startup; short CPU timings are not general speed benchmarks. Adam 200's time is a prefix of Adam 800, not another separate training run. The full training orchestration took 39.00 s including setup/checkpoint overhead.

This **adds training**. The 200-step branches add 2% to 3A's 10,000 gradient batches; controlled branches also add trial losses. This does not establish improvement within the original training budget.

Training launched successfully through **VS Code Run and Debug**, using the Homework window's new Experiment 3D launcher, the main repo interpreter/output and two CPU threads. The Debug Console confirmed all endpoints completed. `execution.json` records the launch. The launch entry intentionally uses absolute paths to the main repo on this laptop; results are also copied into Homework afterward. Evaluation used a separate managed process.

## Evaluation and checks

Only after every endpoint was saved, `compare_refinement.py` evaluated the original 24,000 development states at all 21 saved horizons, using existing approximate numerical-reference values. The original worst-240 cohort remains fixed. New worst-tail error is reported separately. Physics audit uses 8,192 full-training-distribution states, seed 991736, with 1,024 zero-time points; it supplies neither training gradients nor step choices.

The fresh 24,000 reserved final states remain unused, with unchanged SHA256 `f902bb08c7fe93d7a6275048e9cc41ddf2f4819be2f9a600597ae1d5666280c6`. They were hashed only, never loaded or evaluated. Existing checkpoints and development references are unchanged.

Pre-training `--check` verified proposal restoration and moment/displacement agreement with ordinary PyTorch Adam on disposable model copies. Saved checkpoints reload successfully; all endpoints pass terminal/obstacle checks within 9.39e-8 m float32 discrepancy. Evaluation does not accumulate parameter gradients or alter weights. Training/source snapshots and hashes are retained.

Temporal-increase fractions in this comparison use V(next)>V(previous)+.0001 m; they should not be directly compared to older diagnostics using a different tolerance. Heading seam uses the same 24,000 development x/y coordinates at -pi/+pi; older reports used different seam grids. Mean nonzero-horizon MAE averages the 20 nonzero snapshots equally.

## Reproduce and inspect

```powershell
python outputs/deepreach/train_refinement.py --check
python outputs/deepreach/train_refinement.py --train
python outputs/deepreach/compare_refinement.py
```

The training command now refuses to overwrite this completed experiment. Choose a new output in a separately specified protocol for another run. Checkpoint files are under `adam/`, `plain_gradient/` and `second_moment_scaled/`, alongside per-step histories. `checkpoint_200.pt` and `checkpoint_800.pt` are distinct Adam endpoints. They are not automatically substituted for 3A.

`comparison.csv` contains 105 model/time rows; `final_comparison.csv/json` includes final accuracy, constraints, audit loss and costs. `endpoint_values.npz` retains all predictions; `evaluation_physics_queries.npz` retains audit inputs. `equation_checks.json` and both manifests record verification. `interpretation_metrics.json` contains separately derived counts, tail summaries and step-choice counts used in this report.
