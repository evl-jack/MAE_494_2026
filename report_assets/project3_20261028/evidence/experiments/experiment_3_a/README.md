# Experiment 3A — Exact terminal and obstacle constraints

[Finite direction/step-size probes](step_direction_probe/README.md): 120 independent temporary parameter overrides, with physics-only selection. The selected probe reduces audit physics loss 10.78% and final-time development MAE 2.90%. No training or replacement checkpoint; 3A stays the baseline.

[Parameter-learning diagnostics](learning_signals/README.md): the outliers have strong gradients, but residual descent and value-error descent need not align locally. Saved Adam directions and fresh batches were inspected without applying updates. Fresh final-evaluation states are reserved and unused.

[Remaining-outlier analysis](outliers/README.md): the largest errors are conservative ahead encounters, with concrete heading-equivalence and reflection mismatches. This diagnostic did not retrain the model.

**Status: training and evaluation completed on 27 October 2026.** See [measured results](RESULTS.md) and [comparison figure](comparison.png). The 10,000-step run took 220.28 seconds through VS Code Run and Debug. At .5 s, MAE is .02602 m versus A's .04477 m; false-safe / reference-unsafe is 0% observed, false-unsafe / reference-safe is 7.10%, and IoU is .799. These are single-seed validation results, not a safety guarantee. The existing Experiment 1/2 models and diagnostic measurements remain unchanged. No optimizer was created or stepped for the earlier implementation checks.

## Hypothesis and construction

The failure analysis found false-safe predictions inside the known collision disk and violations of V<=l. We test whether enforcing those two known conditions helps the same small network learn the remaining value function more effectively.

The candidate predicts

    l(s) = sqrt(x*x+y*y)-R
    V(tau,s) = l(s) - beta*(tau/T)*g_theta(tau,s)^2
    beta = R = .25 m, T = .5 s.

For nonnegative look-ahead, this guarantees V(0,s)=l(s) and V(tau,s)<=l(s). Already-collided states therefore cannot have positive values. The constraints come directly from the physical target/game definition; no numerical-reference values, gradients or learned reference bounds enter training.

This does not enforce heading periodicity, monotonicity in look-ahead, accurate values outside the collision disk, or accurate control gradients. Those remain measurements or later candidates. A zero correction is representable, unlike a strictly positive softplus correction, but squaring has a flat derivative at g=0. The existing random output bias is shifted by +1 to initialize g away from zero; hidden initialization remains unchanged. The fixed .25 m correction scale comes from the physical collision radius, not reference fitting. On the implementation batch, g ranged from .886 to 1.064, and every parameter group had a finite, nonzero physics-loss gradient. These initial values do not establish convergence.

## Comparison design and budget

Experiment 2A is the comparison baseline. Both use three sine layers of width 64, 8,705 parameters, Adam at 1e-4, 2,048 samples per step, the same seed, dynamics, raw-angle inputs, domain and .5 s horizon.

The constrained candidate uses **10,000 physics updates**, with the same expanding-horizon schedule as A's 10,000 physics updates. The 256 zero-time coordinates per batch still participate in the physics loss. Terminal error is logged but has zero weight because it is identically zero against the analytic target.

A's 2,000 terminal-only pretraining steps are omitted: they cannot change this candidate's output at zero time and would waste updates. Thus the comparison matches the physics-phase step budget and schedule, not total optimizer steps: **10,000 candidate updates versus A's 12,000 total updates**. It also starts from a fresh initialization rather than A's pretrained weights, because the output has different semantics. Report actual elapsed time separately; a matched update count does not guarantee matched wall-clock cost.

The legacy value_scale=25 and value_mean=.25 config fields are retained for compatibility but are unused in the constrained output. constraint_scale=.25 controls its output instead. Terminal pretraining and a zero correction-bias shift are rejected by this candidate's config validation. Terminal-weight calibration is bypassed; the logged terminal weight is zero.

No periodic encoding, revised time sampling, optimizer schedule, extra hold steps, or reference supervision is combined with this candidate. It tests the chosen terminal/obstacle output construction and its necessary initialization/training-phase changes; it does not separately isolate terminal enforcement from obstacle enforcement.

## Checks completed without training

See [implementation_checks.json](implementation_checks.json):

- Exact analytic terminal values, obstacle inequalities and nonpositive values inside the collision disk, including origin/boundary value probes.
- Hand-calculated constant-g example and equality with the explicit output formula.
- Physical-input finite-difference derivative check: maximum discrepancy 6.66e-9 in double precision.
- Independent normalized-input chain rule: maximum discrepancy 2.22e-16.
- Hamiltonian/control mechanical checks and finite, nonzero physics-loss parameter gradients without updates.
- In-memory serialization/reload of an untrained fixture, config guards and unchanged weights.
- Bitwise-identical predictions from all four old checkpoints against the archived original network implementation; checkpoint and original-reference hashes unchanged.

The radial target is nonsmooth at x=y=0. Value constraints were checked there; derivative probes exclude that point. No optimizer trajectory, checkpoint restart, trained accuracy or controller performance was tested. Existing numerical-solver checks were reused; the solver was not changed.

## Execution in VS Code

Run **Air3D: Constraint candidate checks - no training** for the checks. After explicit user authorization, **Air3D: Experiment 3A - Train constraints (starts training)** was selected in the Homework workspace and executed through VS Code Run and Debug. The existing CPU interpreter and two threads were used. Before training, 15.99 GiB RAM was available out of 31.45 GiB; CPU load was a 50% snapshot across 14 logical processors. See the run's execution.json for execution/source records. No system power settings were changed.

The completed run directory is outputs/deepreach/runs/experiment_3_a_constraints, including the checkpoint, config, history, environment, execution record, exact source snapshots and three-point validation. The existing trainer refuses to overwrite this completed run. Training remains separate from evaluation; compare_constraints.py evaluates the saved model and writes the 21-point comparison without training.

The command represented by that launch configuration was (a fresh run over the saved checkpoint is now refused):

```powershell
python outputs/deepreach/deepreach.py --train --config outputs/deepreach/configs/experiment3a_constraints.json --out outputs/deepreach/runs/experiment_3_a_constraints
```

## Evaluation completed and remaining limits

The saved model was compared with A and Experiment 1 at all 21 saved look-ahead times using the same validation states/reference values. RESULTS.md reports relative L2, MAE/RMSE, IoU, both false-safe and false-unsafe rates, and conditional metrics for initially separated states. Analytic collision/obstacle/terminal checks are separate from interpolated reference metrics: the approximate reference can disagree slightly with exact target geometry near its boundary.

Equation residuals, temporal monotonicity and heading mismatch were rechecked, and original three-point validation was retained. The output guarantees its terminal/obstacle constraints, but 25.04% of states still have an upward value increment from .475 to .5 s, the equivalent-heading gap is .03151 m on average, and 1.78% of final predictions fall below the separate physical lower bound -R, which this construction does not enforce. No control rollout, optimizer restart test, second seed or 6D transfer was run. These validation states already informed selection; a fresh final test remains future work.

Files: ../../deepreach.py implements the optional output/training branch; ../../validate.py checks its chain rule; ../../configs/experiment3a_constraints.json specifies the candidate; ../../check_constraints.py reproduces the checks. No reference solver changes were made.
