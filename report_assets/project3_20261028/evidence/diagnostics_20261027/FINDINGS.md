# Findings from the diagnostic supplement

No neural training was performed. Existing checkpoint hashes are unchanged, all twelve earlier value-error comparisons were reproduced, and a fresh fine-grid solve exactly reproduced the saved reference. The relative-L2, Fourier harmonic and energy-identity checks passed.

## What the measurements show

At .5 seconds, relative L2 error is 48.88% for Experiment 1, 24.24% for A, 41.52% for B and 32.00% for C. A remains the best candidate on the main final-horizon value and unsafe-region metrics. Errors increase with look-ahead in every model. A still has 10.82% false-safe predictions among reference-unsafe states, so the improvement does not establish safe deployment.

The centered/windowed spectra concentrate most error energy at lower frequencies. At .5 seconds, A reduces both spatial centered/tapered RMS (0.08154 to 0.05488 m) and heading-centered RMS (0.06622 to 0.03211 m) relative to Experiment 1. Its heading-error spectrum is lower across the sampled harmonics. These statistics use different centering than held-out RMSE and should not be substituted for that metric.

This does not establish that high-frequency representation is the main bottleneck. A change to sine frequencies remains a hypothesis to test. A heading seam, spatial windowing and the numerical reference can also affect spectra. The current measurements support investigating the value fit and terminal/physics balance before assuming an activation change will fix the errors.

The fresh 129×129×96 reference construction took 136.73 seconds. Historical neural training took 206–437 seconds. For batches of 1,024 prepared states, the cached grid took 0.89 microseconds per state versus 2.31–2.69 for the networks. For this fixed 3D game, these measurements do not demonstrate a batched-query speed advantage for the PINN.

The report's single-query crossover estimates use small differences between noisy timing medians. They are illustrative arithmetic, not reliable predictions of a practical speedup; the baseline and grid medians are especially close. Batched-query results favor the cached grid both in initial construction cost and per-state query time. Higher-dimensional grid storage and construction may change the tradeoff, but this experiment has not measured that.

## What remains before stronger claims

- Only three evaluation times (0, .25, .5 seconds) were available. This is a within-horizon difficulty trend, not a sweep of separately trained maximum horizons or a precise failure threshold.
- The original comparison states now serve as validation data because they informed selection. Reserve a fresh final test set before evaluating a future selected method.
- These are single-seed results. No optimizer, activation, exact terminal condition, periodic encoding, reference-supervised training, gradient/control evaluation or 6D transfer test was added here.

The immediate next experiment can use A as the comparison baseline and change one proposed feature at the same training budget. The new diagnostics provide additional ways to judge that change; no such training has started.

See [the full report](README.md) for methods, data files, plots and reproduction instructions.
