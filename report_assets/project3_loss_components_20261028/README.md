# P2 — loss-component plots

Four figures cover 17 existing run histories: Experiment 1; 2A/B/C; 3A/B/C; 3D Adam/plain/scaled refinements; 3E long/wide models; 4A/B/C; and 5U/R. These charts were produced from saved logs only. No training, network/reference evaluation or final-test query occurred.

## Read the plots

- Blue: unweighted terminal MAE. Orange: native mean-absolute physics VI loss.
- Green: terminal MAE multiplied by the logged terminal weight, during the physics phase. Gray: logged total training objective when it differs from physics alone.
- Early terminal-only training has no physics-loss line; its logged physics value is zero.
- Exact-output models have zero analytic terminal-value loss. It is annotated, not drawn at an invented positive epsilon. For 3D, this follows from the unchanged output construction; its refinement CSVs log only physics losses. Experiment 5 records zero terminal maximum error rather than a separate terminal MAE series.
- The 3D refinement panels distinguish pre-update loss and selected-step loss on the same construction batch. These are not held-out audit curves. Its x-axis is additional updates from 3A, while other full histories use cumulative updates. The Adam +200 endpoint is marked on the +800 trace.
- The Long64, 2C and 4C plots include inherited parent histories. Markers identify continuation. These are not independent fresh runs throughout their displayed range.
- All logged rows are shown, without smoothing. Nonpositive values are omitted from log lines; panel ranges vary. Raw loss magnitudes have different implementation conventions and are not a common physical error bound.
- Experiment 5 changes the collocation distribution. Its training curves do not establish superiority; use the saved common physics and value/control evaluation.

## Data and provenance

histories/ contains byte-identical CSV copies. manifest.json lists original source paths, hashes, row counts and first/last rows. All source hashes were checked again after plotting and were unchanged. The original reference, checkpoints and evaluation records were not loaded or modified.

The existing baseline and early-candidate component plots were already saved. The report's earlier joint-history summary displayed physics loss only; these consolidated figures expose the separate components available in the logs.

The plotting source is reproduce_plots.py. It uses only the bundled histories with NumPy and Matplotlib; run python reproduce_plots.py from any working directory. It writes the four PNGs and manifest alongside the script.
