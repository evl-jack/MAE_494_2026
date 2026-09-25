# Deblurring report code

The original [`../deblur_test.m`](../deblur_test.m) is unchanged. `deblur_report.m` is its separate working copy; `deblur_report.py` translates the same experiment to Python. Both retain the Gaussian circular blur, image resolutions, regularization, noise level, step-size formula, tolerances, and iteration limits.

## Changes in the MATLAB working copy

- Uses the repository's `Test_Image.jpg` without an image picker.
- Runs as a function, preserving the caller's workspace and restoring its random-number state.
- Exports figures, a log, numerical JSON, and a MATLAB reference file.
- Aggregates CG residuals over all RGB channels to match GD. Channels that have already stopped retain their last residual in the aggregate curve.
- Reports GD convergence separately from its iteration cap. A binary search over the existing Fourier trajectory finds the exact first successful integer iteration, if any; it does not increase the 20,000-iteration budget.
- Handles a zero initial gradient without dividing by zero.
- Labels GD's convergence status and provides a full-budget/early-iteration convergence plot.

No preconditioner, pixel constraint, new regularizer, or replacement optimization model was added.

## MATLAB

MATLAB with Image Processing Toolbox is required. From the repository root:

```matlab
addpath('analysis');
results = deblur_report(fullfile(pwd,'analysis','results_matlab'));
```

The function displays no interactive image picker and saves its output under the supplied folder. `results.json` records stopping status, channel counts, relative residuals, image errors, and conditioning. `plot_report_convergence.m` also creates a zoomed comparison. The original script's display-image error convention (clipping to [0,1]) is retained.

## Python

Use Python 3.10 or newer with the dependencies in `requirements.txt`:

```text
python -m pip install -r analysis/requirements.txt
python analysis/deblur_report.py --output analysis/results_python
```

An optional `--image path/to/image.jpg` selects another input. The script saves PNG figures and `results.json`, with no GUI required.

The Python resize implements separable bicubic interpolation with antialiasing and symmetric boundaries. On the supplied image it agreed with MATLAB's two resized references within 1.6e-13 maximum absolute intensity difference. Standalone noise uses NumPy `default_rng(1)`: the distribution and seed are fixed, but its samples differ from MATLAB `rng(1)`. Do not expect independent runs to be bit-for-bit identical.

### Validate against the exact MATLAB inputs

Run the MATLAB copy first, then:

```text
python analysis/deblur_report.py --reference-mat analysis/results_matlab/reference.mat --output analysis/results_python_shared
python -m unittest discover -s analysis -p "test_*.py" -v
```

The shared-input mode loads MATLAB's resized references and noisy observations, then independently computes the Python blur transfers and solutions. The reference file is approximately 303 MB for this image and is intentionally not tracked; the MATLAB run regenerates it. Generated `results_*` folders and Python caches are ignored.

Five numerical tests check an explicit small Hessian, the Fourier GD trajectory against literal gradient steps, CG against the direct solve, exact stopping behavior, and resize identities. The 2-by-2 case is only a verification case, not a replacement for the full-resolution experiment.

## Verified results

MATLAB R2023b Update 9 ran successfully through the user's already-open session. Shared-input Python returned the same CG counts (40, 42, 47) and differed by less than 3e-14 in reconstructed pixel values. GD failed the 1e-4 relative-gradient tolerance within 20,000 iterations in both implementations. The standalone Python run also completed successfully.

CG convergence does not mean its image error must be lower than GD's. The report records the observed image errors separately from solver residuals. Neither implementation supplies a reliable GD-versus-CG wall-clock benchmark: GD uses an analytical Fourier trajectory, and CG solves three channels separately.

Saved evidence is under [`../report_assets/matlab-run`](../report_assets/matlab-run), with shared-input and standalone Python results alongside it. The environment used Python 3.12, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2, and Pillow 12.3.0. Runtime measurements are single observations, not cross-language benchmarks.
