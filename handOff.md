# Project 2 Handoff

## Current state

The report now contains measured results from a successful MATLAB desktop run and a validated Python translation. The user authorized edits in a separate MATLAB copy, requested Python, and asked to save the completed files to GitHub. The original `deblur_test.m` and `Test_Image.jpg` remain unchanged.

Repository: https://github.com/evl-jack/MAE_494_2026, branch `Main`.

## New working files

- `analysis/deblur_report.m`: copy of the original, wrapped as a function. It locates the existing JPG, exports evidence, correctly reports GD stopping status, and combines all RGB CG residuals to match GD.
- `analysis/plot_report_convergence.m`: full-budget and early-iteration plots from saved measurements.
- `analysis/deblur_report.py`: complete standalone translation, plus a shared-input validation mode.
- `analysis/test_deblur_report.py`: five numerical tests.
- `analysis/requirements.txt` and `analysis/README.md`: dependencies, usage, differences, and validation instructions.
- `report_assets/matlab-run/`: MATLAB measurements, log, and selected figures.
- `report_assets/python-shared-input-results.json`, `python-standalone-results.json`, and `translation-validation.json`: cross-language evidence.
- `project 2.md`: measured D3/D4 results, corrected comparison, reconstruction figures, small-case verification, and reproduction instructions.

## Results

The model and all experiment parameters remain unchanged: periodic Gaussian blur; lambda 0.0001; noise standard deviation 0.001; 2048-pixel direct reconstruction; 1080-pixel optimizer analysis; GD limit 20000; CG limit 500; tolerance 0.0001.

MATLAB R2023b Update 9 with Image Processing Toolbox ran successfully through the user's open session. Starting a separate batch process still failed with service error 5202. Computer Use can run the copied function in the existing MATLAB Command Window.

- Hessian condition number: 10001.
- GD: failed the tolerance at 20000; RGB relative gradient 0.0158258416059053.
- CG: 40, 42, 47 iterations; all flags zero; RGB relative residual 0.0000990052086765.
- Clipped relative image errors: blurred 0.17448852; GD 0.12399872; CG 0.13058171; direct full-resolution 0.14457829.
- The final MATLAB direct solve took about 0.894 seconds in one observation. This is not a GD/CG or cross-language timing benchmark.

CG converges to the optimization criterion much earlier, but its image error is slightly higher than GD's. Preserve that distinction. The copied CG curve now aggregates RGB, holding each converged channel's final residual fixed. The original red-channel-only curve is not used for the corrected comparison.

## Validation

Five numerical tests passed: explicit small Hessian versus Fourier spectrum, GD recurrence versus literal iterations, CG versus direct solve, stopping/zero-input cases, and resize checks.

Shared-input Python returned the same CG iteration counts as MATLAB. Maximum pixel differences: GD 8.33e-15, CG 2.26e-14, direct solve 1.12e-14. Independent bicubic resizing matched MATLAB within 1.6e-13. Standalone Python also ran successfully with its own seeded noise. NumPy and MATLAB seeds do not produce identical noise samples.

The 2-by-2 hand-check case uses the existing sigma 0.5 and lambda 0.0001: Hessian eigenvalues 1.0001, 0.5801256584 (twice), and 0.3365297644; condition number 2.9718025145. This validates the formula without replacing the image experiment.

Source protection: original MATLAB raw Git blob remains `59ce9537f49a3f76aac89980985a95ba868bbafa`; image blob remains `44e52b98e03f87c86fa1750ceeb132ce569b5ab8`.

## Local execution artifacts

The checkout is under `work/MAE_494_2026` in this Codex task. Neighboring scratch folders `work/matlab-results-final`, `work/python-reference-results`, and `work/python-standalone-results` contain full run outputs. `work/matlab-results-final/reference.mat` is approximately 303 MB and intentionally excluded from GitHub; rerunning the MATLAB copy regenerates it. The portable commands in `analysis/README.md` use ignored `analysis/results_*` folders instead.

Python dependencies were installed only in the task's `work/python-deps` directory. To use that local installation, set PYTHONPATH to it and run the bundled Python executable. Normal users can install the listed requirements in their preferred environment.

The MATLAB copy restores the caller's RNG state and does not clear the workspace. Its generated figures are exported and closed. MATLAB remains open.

## Next session

1. Review the report and images as a team; no missing numerical evidence remains from the earlier startup failure.
2. Verify final GitHub math/image rendering before submission.
3. Do not replace the original MATLAB file with the working copy unless separately requested.
4. If more cases or different regularization are desired, treat them as new experiments and preserve the current evidence.

The previous 20-minute heartbeat is disabled because the earlier timed report-drafting task ended. No reset credits were consumed by this work. Current progress is communicated in the active task.
