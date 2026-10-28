# Frozen 3A: finite direction and step-size probes

28 October 2026. We evaluated 120 independent hypothetical parameter changes from 3A. No training, sequential optimizer steps or replacement checkpoint was produced. 3A remains the working baseline.

## Why and how

The previous learning-signal study found strong outlier gradients, but infinitesimal alignment alone cannot predict finite steps through the nonsmooth physics objective. This probe checks actual finite changes in physics loss and development-reference error. Reference values and reference gradients never construct the directions or choose step sizes.

Eight 2,048-point construction batches replay the previous diagnostic (seed 991733), including 256 zero-time physics points per batch. Other times are uniform over 0 to .5 s, using the original training spatial/heading ranges. Each supplies the mean absolute HJI-VI residual gradient g.

Three directions start independently from the same checkpoint:

1. **Adam:** the hypothetical next update using g and saved first/second moments, bias corrections and learning rate.
2. **Plain gradient:** -g, rescaled to the Adam direction's Euclidean parameter norm.
3. **Second-moment scaling:** -g/(sqrt(v_hat)+epsilon), using the saved bias-corrected second moment, rescaled to that same norm. It uses the current gradient without Adam's first-moment average. This is not a completed RMSprop or other named-optimizer trial.

Multipliers .01, .1, .3, 1 and 3 compare equal parameter displacements within each batch. The norm differs across batches. Multiplier 1 is the original hypothetical Adam displacement, not the other methods' ordinary learning rate. Candidates use temporary functional parameter overrides; every candidate starts at 3A. Saved parameters, buffers, optimizer state and checkpoints remain unchanged.

Two additional physics batches, each with 8,192 points including 1,024 zero-time points (seed 991735), provide selection and audit losses. Directions use neither batch's gradients. The primary candidate minimizes selection physics loss across all probes and the unchanged baseline. The audit batch measures transfer to other physics samples; it is a shared diagnostic audit set, not a final test.

Reference evaluation uses the original 24,000 development states at .1, .25 and .5 s, plus the fixed cohort of 240 previously identified final-time outliers. The reserved fresh final-evaluation states are only hashed for preservation; they are never loaded or evaluated.

## Physics-selected result

The lowest selection loss is batch index 7 (the eighth batch), second-moment scaling, multiplier 1. Parameter displacement L2 is .00166670.

| Measure | Frozen 3A | Selected probe |
|---|---:|---:|
| Selection physics loss | .00836920 | .00742989 |
| Audit physics loss | .00896378 | .00799754 |
| Value MAE at .1 s [m] | .00911772 | .00891437 |
| Value MAE at .25 s [m] | .01802132 | .01762156 |
| Value MAE at .5 s [m] | .02602121 | .02526663 |
| Fixed worst-240 MAE at .5 s [m] | .20120562 | .19691151 |
| Unsafe-set IoU at .5 s | .798789 | .803656 |
| False-unsafe fraction of reference-safe states at .5 s | 7.0978% | 6.8842% |
| False-safe fraction of reference-unsafe states at .5 s | 0 observed | 0 observed |
| Predictions below -R-.0001 at .5 s | 1.7833% | 1.5958% |

Audit loss falls **10.78%**, final-time MAE **2.90%**, and fixed-outlier MAE **2.13%**. Overall value MAE improves at all three inspected times. The fixed final-time outlier cohort slightly worsens at .1 s (.014806 to .014875 m), so improvement is not universal across locations/times. Zero observed false-safe classifications do not establish a safety certificate.

## Consistency and limits

Selecting a step within each method/batch using selection physics loss gives:

| Direction | Audit loss improves | Final-time MAE improves | Median selected final-time MAE [m] |
|---|---:|---:|---:|
| Adam | 5/8 | 8/8 | .02600540 |
| Plain gradient | 8/8 | 8/8 | .02527175 |
| Second-moment scaling | 8/8 | 8/8 | .02514823 |

Every selected candidate beats baseline selection loss. Eight batches at one checkpoint are not eight independent training runs and do not establish optimizer superiority.

At multiplier 1, all eight frozen Adam directions increase audit physics loss, despite their infinitesimal descent on their construction batches in the previous diagnostic. Smaller steps can help. Finite displacement and cross-batch transfer matter. This does not uniquely attribute the difference to momentum or diagonal scaling.

All multiplier-3 steps increase audit physics loss, although final-time MAE improves substantially. A plain-gradient trial even introduces an observed final-time false-safe state. We therefore do not select by the lowest development-reference MAE. Physics loss and reference accuracy measure different aspects of the solution.

![Finite-step comparison](step_direction_probe.png)

## Next experiment

Keep 3A unchanged. These results support a short, strictly budgeted physics-only refinement comparing a direction with step-size control against continued Adam, from identical copies of 3A. Both plain-gradient and second-moment scaling deserve consideration. Count all extra loss/gradient evaluations needed to choose a step. Select the protocol and stopping rules before using the reserved final states.

No sequential refinement, L-BFGS/trust-region implementation, new training seed, full 21-time reevaluation, control-gradient validation, rollout or 6D experiment was run. Repeated updates can behave differently from these local probes.

## Checks and reproduction

Checks verify replayed gradients/Adam directions against the prior diagnostic, baseline predictions against saved 3A predictions, unchanged protected hashes and model parameters/buffers, no accumulated parameter gradients, finite outputs, and the selected candidate's terminal condition within float32 tolerance. The square-output terminal/obstacle construction is unchanged. Separate lower-value and temporal monotonicity conditions remain unenforced. The saved .25-to-.5 time-increase fraction uses tolerance .0001 m; it differs from the older .475-to-.5 diagnostic.

Cost: eight physics-gradient batches, 360 candidate physics-loss assessments (2,211,840 point assessments) plus baseline losses, and 8,640,000 candidate reference-value point evaluations. This is additional computation, not a free training improvement. A managed process used the existing Python environment and two CPU threads; it was not launched by the VS Code debugger. Measured runtime is in summary.json.

```powershell
python outputs/deepreach/probe_step_directions.py
```

- `physics_probes.csv`: construction, selection and audit losses for all 120 candidates.
- `validation_probes.csv`: value/classification metrics at three times.
- `aggregate_by_scale.csv`: counts and medians by direction/multiplier.
- `physics_selected_by_batch.csv`: physics-selected steps per method/batch.
- `directions.csv`, `physics_directions.npz`: directions and displacement scales, without a new checkpoint.
- `physics_assessment_queries.npz`: exact selection/audit inputs.
- `baseline_validation.csv`, `summary.json`, `interpretation_metrics.json`, `manifest.json`: baseline, selection, checks, cost and hashes.
