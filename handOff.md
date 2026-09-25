# Project 2 Handoff

Updated: September 24, 2026, approximately 3:20 p.m. America/Phoenix.

## User's Request and Boundaries

Develop `project 2.md` from the existing outline using the MATLAB implementation, supplied image, and assignment at https://designinformaticslab.github.io/DesignOptimization2025/project2.html. Make the explanation easy to follow and tied to the assignment. The user explicitly confirmed:

- Report only; document code issues and missing evidence instead of changing MATLAB.
- Use `Test_Image.jpg`. There is no separate PNG to wait for.
- Do not introduce new model variables or simplifications.
- Provide progress updates every 20 minutes while active.
- Save a handoff before exhausting account usage. If quota runs out, pause until 7:50 p.m. America/Phoenix on September 24 and check availability before resuming. Do not consume reset credits.

No new push was requested for this report revision.

## Repository and Files

Repository: https://github.com/evl-jack/MAE_494_2026

Branch: `Main`.

Local checkout: `C:/Users/jackf/Documents/Codex/2026-09-21/github-plugin-github-openai-curated-remote/work/MAE_494_2026`.

Local HEAD at review start: `2515e4e447409ff4ede39a25b53aa85d54a9db08` (original outline).

The GitHub source and local `deblur_test.m` match when line endings are ignored. GitHub blob: `b3bcfd6a33fee29a49357b0dde1618f2c9d2fc69`; local raw hash: `59ce9537f49a3f76aac89980985a95ba868bbafa`. Do not treat that newline-only discrepancy as a model difference.

## Work Completed

- Read the complete MATLAB script and inspected the supplied stadium photo.
- Verified the GitHub repository contents and reread the assignment requirements.
- Replaced the outline with a developed report explaining the existing regularized least-squares formulation, decision variables, constraints, classification, blur mechanism, D1-D4 implementation, assumptions, reproduction steps, and evidence gaps.
- Added `report_assets/d1-spectrum.svg`, `report_assets/d2-conditioning.svg`, and `report_assets/conditioning-check.json` from independent checks of the existing formulas. They are explicitly labeled as NumPy checks, not MATLAB execution results.
- Left MATLAB and input image unchanged.

## Key Findings

The code minimizes `0.5*||A*x-b||^2 + lambda/2*||x||^2` with known periodic Gaussian blur and `lambda = 1e-4`. It is continuous, unconstrained, strongly convex quadratic optimization. `clampImage` is postprocessing, not a constraint.

The supplied JPG is 1920 by 1281 RGB. The code resizes it to 2048 by 1366 for direct Fourier reconstruction, then 1080 by 720 for optimizer diagnostics. The main analysis sigma is 3.1640625 pixels. It generates separate noisy observations at the two resolutions.

Independent spectral checks give minimum eigenvalue approximately 0.0001, maximum approximately 1.0001, condition number approximately 10001, and GD step approximately 1.99960008. The D2 condition number increases from 1.31 to about 10001 across the existing sigma list; Jacobi scaling leaves it unchanged. Regularization explains saturation of the condition number.

The GD trajectory is evaluated using Fourier formulas from a zero initial image, not a full timed iterative loop. Its stopping index is the first successful logarithmic sample, or 20000 on failure. Do not report the iteration cap as successful convergence.

`pcg` has no preconditioner supplied. It solves each RGB channel separately. GD's plotted relative gradient combines RGB, but CG's stored history contains only the first (red) channel. Do not claim a directly comparable whole-image speedup from these curves.

The full 2K result is a direct Fourier solve, not the CG result. Reconstruction-error values compare clipped displays to their corresponding resized references. These are not optimization residuals.

## Verification and Blockers

MATLAB R2023b exists at `C:/Program Files/MATLAB/R2023b/bin/matlab.exe`. A batch startup failed initially due to preferences setup; setting `MATLAB_PREFDIR` to the workspace fixed that issue. Startup then failed with MathWorks service error 5202, including after network permission was granted. No MATLAB solver run completed. Do not invent iteration counts, flags, timings, image errors, or restored images.

The existing script asks for `stadium.png`; since it is absent, a normal interactive run opens an image picker. Select `Test_Image.jpg`.

Scratch verification files, outside the repository:

- `../check_conditioning.py`: exact D1/D2 formulas evaluated using NumPy 2.3.5; assertions check eigenvalue bounds and unchanged Jacobi condition number.
- `../plot_conditioning.py`: generates the two report SVG charts.
- `../conditioning-check.json`: numeric check output.
- `../review-source/deblur_test.m`: fetched GitHub source for comparison.
- `../matlab-check.log`: startup failure record.

Bundled Python: `C:/Users/jackf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

Final review passed: both charts were rasterized and visually inspected; a legend overlap was corrected. Local Markdown links resolve, six display-math blocks and four code blocks are balanced, SVG XML parses, and all D2 table entries match the independently calculated values to their printed precision. Dimensions and model settings were checked against the source. `git diff --check` passed. MATLAB and image hashes remain unchanged. Scratch `../verify_report.py` records these checks. These checks do not establish successful MATLAB execution or full assignment completion.

## Next Steps

The requested report draft and handoff are complete. Repository changes are local and uncommitted. Reviewable copies are provided under `../../outputs/project-2-review/`, with the report, handoff, unchanged reference script/image, and report assets. A ZIP of that folder is also provided. Source files are copied only so the exported report's relative links work.

For the next work session:

1. Review the developed draft with the team.
2. Run the existing script in an authenticated MATLAB session, selecting `Test_Image.jpg` when prompted.
3. Supply D3/D4 evidence, image comparisons, output logs, flags, and error values. The assignment's small-case hand verification remains pending.
4. Resolve the RGB/red-channel comparison only if the user authorizes a code change. Until then, keep the caveat explicit.
5. Check final GitHub math rendering and publish only when requested. The requested draft is complete; the full experimental submission is not.

## Progress Automation and Usage

Heartbeat ID: `project-2-report-progress`. It was scheduled every 20 minutes and is now disabled (PAUSED) because the requested draft work is complete. No quota pause or reset-time restart was needed. Only one heartbeat can attach to a task; no separate reset automation was created.

The last checked account limits were 46% used in the five-hour window and 7% used in the weekly window; recheck rather than relying on these old values. No reset credits were used. The tool does not expose a separate daily token counter.
