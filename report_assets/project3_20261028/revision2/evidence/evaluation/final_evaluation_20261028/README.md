# Fixed final evaluation — Improvement carries over

Completed 28 October 2026. **The 22,000-step model improves final-time value MAE by 12.61% over Adam +200 on the 24,000 previously unused states.** The paired 95% bootstrap interval is **11.93%–13.25%**. Its overall MAE is lower at every one of the 20 nonzero evaluated horizons.

No training, optimizer updates, tuning or additional model selection occurred. The three checkpoint hashes, evaluation points, solver and metrics were fixed in `protocol.json` before the reserved states were opened. The final set is now consumed and is no longer an untouched test resource. Its original input-file bytes remain unchanged.

## Final-time results

All rows use the same 24,000 final states and the .5-second horizon.

| Metric | Original 3A | Adam +200 | Long22000 |
|---|---:|---:|---:|
| Value MAE [m] | .02628533 | .02297716 | **.02008032** |
| Value RMSE [m] | .04615090 | .04152166 | **.03726135** |
| Relative L2 error | 19.17% | 17.25% | **15.48%** |
| Unsafe-set IoU | .79701 | .81636 | **.84239** |
| False-unsafe / reference-safe | 7.008% | 6.190% | **5.149%** |
| False-unsafe count | 1,319 | 1,165 | **969** |
| False-safe / reference-unsafe | 0 observed | 0 observed | 0 observed |
| 99th-percentile absolute error [m] | .174863 | .163988 | **.146123** |
| Own worst-240 MAE [m] | .203541 | .186868 | **.179124** |
| Maximum absolute error [m] | .290847 | .266150 | **.264548** |

There are 5,179 reference-unsafe and 18,821 reference-safe states at .5 s. Zero false-safe classifications were also observed at each of the 20 nonzero horizons for all three models. These are comparisons against an approximate numerical reference, not a certificate of controller or real-world safety. The same states recur across horizons, so the horizons are not independent trials.

The longer model improves mean and tail metrics, but its largest observed value error remains .26455 m. A small average value error should not be interpreted as a uniform error bound. These are errors in the scalar reachability value, not position-prediction errors.

## Does the development improvement replicate?

| Model | Development MAE at .5 s [m] | Final MAE [m] |
|---|---:|---:|
| Original 3A | .02602121 | .02628533 |
| Adam +200 | .02281836 | .02297716 |
| Long22000 | .01985405 | .02008032 |

The final improvement versus Adam +200 is **12.61%**, close to the development result of 12.99%. Versus original 3A, Long22000 improves final MAE **23.61%**; the paired 95% interval is **23.04%–24.14%**. These results support transfer of the measured improvement to new states drawn from this same evaluation domain and fixed Air3D game.

The primary absolute MAE reduction is **.00289684 m**, with a paired 95% interval of **.00273285–.00307074 m**. The bootstrap resamples the paired states 2,000 times, seed 991743, at the final horizon. It measures sampling variation conditional on the fixed models and approximate reference. It does not account for training-seed variation, numerical-solver bias, different game parameters or real-world uncertainty. A synthetic constant-error fixture independently checks the bootstrap arithmetic.

## Protocol and data independence

The final inputs were reserved earlier using seed 991731 and did not enter the preceding development comparisons, model choices, gradients or training. They are uniform over x,y in [-.6,.6] m and heading in [-pi,pi]. Each is evaluated at 21 horizons, 0 to .5 seconds in .025-second increments.

The frozen models are:

- **3A:** width 64, three sine hidden layers, 10,000 physics steps.
- **Adam200:** the saved 10,200-step width-64 checkpoint.
- **Long22000:** the saved 22,000-step width-64 checkpoint selected as the strongest development candidate before this final evaluation.

Full paths and SHA256 values are in `protocol.json`. The wider model was not added after seeing the final data. No hyperparameters, checkpoint choices, thresholds, numerical grids or horizon points were changed in response to final results.

The exact terminal/obstacle construction is the same for all models. Its analytic conditions pass within float32 tolerance. Other defects remain: final predictions below -R-.0001 occur at 1.771%, 1.088% and 1.417% of states for 3A, Adam200 and Long22000 respectively. Long22000 therefore does not improve every physical diagnostic. Value increases from .475 to .5 seconds, using tolerance .0001 m, occur at 20.22%, 20.86% and 19.70% respectively. No control-gradient reliability or closed-loop rollout evaluation was performed.

## Numerical reference

The unchanged NumPy local Lax-Friedrichs obstacle solver uses a 129 x 129 x 96 grid, spatial domain [-2,2], periodic heading, CFL .8 and direct snapshots at all 21 times. Physical parameters and comparison domain match development. Labels use spatial/heading interpolation only; there is no temporal interpolation.

The solve took **105.01 seconds** and 340 time steps. Grid spacing is .03125 m and .06544985 rad; maximum time step is .00149921 s. Recomputed reference values at the first 64 original development states match the earlier dense reference exactly at all times. Shared snapshots differ from the older three-time fine-grid solve by at most 1.38e-5 m, as expected because extra output times shorten some Euler steps. Both consistency checks were fixed before final data use and passed without changing the solver.

The reference is approximate. Its interpolation can produce a small discrepancy from the exact analytic terminal target at zero horizon; the separate terminal-output check assesses that analytic condition directly. Full grids are not duplicated here: the queried final reference values and deterministic solver/configuration are retained.

## Integrity and reservation status

All 63 model/horizon rows are exported with raw prediction arrays. Saved MAE, RMSE and classification counts were independently recomputed from those arrays. Checkpoint bytes, reference/development inputs and the reserved `states.npz` retain their hashes. Evaluation leaves all model parameters unchanged and accumulates no parameter gradients.

The original reservation metadata and README are archived as `reservation_before_use.json` and `reservation_readme_before_use.md`. The current reservation manifest now says **consumed; fixed final evaluation completed**, and links its final protocol/manifest hashes. This prevents the same inputs from later being presented as a new untouched test. Further development must not use this record as fresh final evidence for a subsequently tuned model.

Execution used a managed process with the existing project interpreter, CPU/two threads; it was not a VS Code debugger run. Total evaluation execution was about **116 seconds**, including reference construction. Software versions and interpreter path are saved in `environment.json`.

![Final comparison across horizons](final_comparison.png)

## Files and reproduction

- `protocol.json` and `sources/`: protocol and code frozen before opening final inputs.
- `reference_values.npz`, `reference_check.json`: final labels and numerical consistency checks.
- `model_predictions.npz`: predictions for the three fixed models at every horizon.
- `metrics.csv/json`, `final_metrics.csv/json`: all 63 rows and final-time results.
- `worst_240_each_model.csv`: each model's own worst 1% at the final horizon, with final-state IDs and values. These are descriptive rankings, not training data.
- `paired_confidence_intervals.json`, `bootstrap_verification.json`: predeclared uncertainty calculation and synthetic check.
- `development_vs_final.csv`: development/final comparison without changing either dataset.
- `equation_checks.json`, `verification.json`, `manifest.json`, `status.json`, `environment.json`: constraints, exported-metric checks, hashes, completion and environment.

The original final states remain in `evaluation/reserved_final_states/states.npz` with SHA256 `f902bb08c7fe93d7a6275048e9cc41ddf2f4819be2f9a600597ae1d5666280c6`.

The executed sequence was:

```powershell
python outputs/deepreach/final_evaluate.py --prepare
python outputs/deepreach/final_evaluate.py --evaluate
```

The completed folder is protected from overwrite. Explicit `--evaluate --resume` supports recovery of an interrupted evaluation under the identical frozen protocol; it does not permit replacing a completed final record or adding models. Reviewing the saved files requires no rerun. No further training or evaluation was scheduled by this report.
