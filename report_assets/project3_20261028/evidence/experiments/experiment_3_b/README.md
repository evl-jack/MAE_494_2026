# Experiment 3B — Periodic heading inputs

**Status: training and evaluation completed.** See [measured results](RESULTS.md): periodic heading gaps are reduced to numerical noise, and the fixed 3A outlier cohort improves 26.02%, but overall MAE worsens 35.14% and false-unsafe rate rises. Keep 3A as the stronger overall baseline. This separate 10,000-step VS Code run took 339.46 s. Experiment 3A and all earlier checkpoints are preserved.

## Hypothesis

The 3A outlier analysis showed large prediction differences for physically equivalent headings, including inputs within the original training interval. Test whether a periodic representation removes that inconsistency and improves the same ahead/opposing-heading outliers, without changing the physics-training budget or adding reference labels.

The physical input remains (tau,x,y,psi). Internally the first layer receives

    (tau/T, x/domain, y/domain, sin(psi), cos(psi)).

The Air3D game still has three state dimensions. Five input features do not introduce another physical state or a 6D game.

The output remains the exact terminal/obstacle construction from 3A:

    V(tau,s) = l(s) - .25*(tau/T)*g_theta(tau,s)^2.

Hidden architecture is unchanged: three sine layers, width 64. The additional first-layer input adds 64 weights: 8,769 parameters versus 3A's 8,705 (about .74% more). First-layer initialization follows the existing fan-in rule for five inputs, so the initial weights/function differ. The test is not a claim of identical parameter count or initialization.

## Controls and training budget

- Same 10,000 physics updates, linear horizon curriculum to .5 s, Adam at 1e-4, seed 7, sample count, spatial/heading sampling ranges, physical dynamics and correction scale as 3A.
- No terminal-only pretraining, revised time sampling, additional hold steps, reflection constraint, lower-bound constraint, optimizer change or reference supervision.
- The existing extended heading range [-1.2*pi,1.2*pi] is retained; periodic features identify equivalent headings within that range.
- Adding an input normally consumes different initialization random numbers and changes subsequent sample draws. The new candidate restores the CPU RNG state obtained immediately after the original raw-input initialization. A sampler-only replay of all 10,000 batches reproduced the saved 3A final RNG state. After training, compare the two final RNG states again. This matches 3A's physics sampling sequence while leaving the new model's own initialization intact.
- Match optimizer-update and sampling budgets, then report actual elapsed time separately. No equal wall-clock-cost claim is made.

## Implementation checks before training

See [implementation_checks.json](implementation_checks.json). No optimizer was created for these checks.

- Equivalent-heading value agreement in double precision: maximum 1.67e-16 m; derivative agreement 1.33e-15.
- Independent sin/cos feature chain rule: maximum discrepancy 3.33e-16.
- Physical-input finite differences: maximum discrepancy 4.32e-9; Hamiltonian/control mechanical checks passed.
- Terminal/obstacle conditions and finite, nonzero physics parameter gradients verified.
- Existing five checkpoint predictions remain bitwise identical to their archived implementations.
- Sampler-only replay matches 3A's final RNG state without training.

Floating-point trigonometry can leave tiny numerical discrepancies between equivalent angles; encoding enforces mathematical periodicity, not bitwise equality for every floating-point representation.

## Execution and evaluation

Training is launched via **Air3D: Experiment 3B - Train periodic heading** in VS Code Run and Debug, in the user's Homework project. The existing interpreter uses CPU and two threads. Before this run, free RAM was 16.19 GiB of 31.45 GiB, with CPU load a 44% snapshot on 14 logical processors. Source snapshots and execution details are saved with the run; no system power settings are changed.

Run path: outputs/deepreach/runs/experiment_3_b_periodic. The trainer refuses a fresh run over an existing checkpoint. An interrupted run requires an explicit resume instruction.

compare_periodic.py evaluates the completed checkpoint without training or solving a new reference grid. Use the same 24,000 validation states and 21 reference times, retain the old three-point validation, and report value error, both sign-error rates, IoU, analytic constraints, time monotonicity and equation residuals. Evaluate the fixed 240-state outlier cohort identified before this test and also locate the new model's own worst 1%; do not redefine the old cohort to make the result look better.

Reference values are approximate; validation data have already informed design choices. No untouched final test, second seed, controller rollout or 6D transfer is included. Inspect both improvements and regressions before selecting a method.

To reproduce checks:

```powershell
python outputs/deepreach/check_periodic.py
```

To evaluate a completed run:

```powershell
python outputs/deepreach/compare_periodic.py
```

The evaluation script regenerates data/plots. This interpretation document is maintained separately.
