# DeepReach Air3D experiments

| Experiment | Date | Scope | Outcome |
|---|---|---|---|
| [Experiment 1 — Reduced CPU baseline](experiment_1/README.md) | 22 October 2026 | Three sine hidden layers of width 64, 2,048 samples/step, 2,000 terminal + 10,000 physics steps, .5 s horizon | Executed and compared with independent grids; .0915 m final-horizon value MAE, 46.42% false-safe among reference-unsafe samples |

Experiment 1 reproduces the core PINN workflow but does not reproduce the paper's reported accuracy. The smoke run is a setup check and is not counted as another experiment. The full paper-scale configuration is available but has not run. No Experiment 2 has been executed.

Run artifacts retain their original dated directory names for reproducibility. Each experiment record maps its label to the original run, configuration, checkpoint, metrics and plots. Numerical-reference agreement is empirical evidence, not a safety guarantee.
