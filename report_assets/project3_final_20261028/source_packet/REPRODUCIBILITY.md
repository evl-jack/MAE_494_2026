# Reproducibility and reporting guide

## Read the finished analysis

Start with [REPORT.md](REPORT.md). It separates original development comparisons, the completed 3D final evaluation, grouped 6D development results and controller diagnostics. [evidence.json](evidence.json) identifies the source paths, file hashes and machine-readable headline metrics. Paths in that register are relative to the project root, not this report directory.

The figures in this packet are byte-identical copies of existing saved figures. They are not a new experiment or an independent test set. The report's numerical tables retain their original evaluation cohorts; values from different cohorts must not be pooled into one ranking.

## Environment

The measured runs used Windows, Python 3.12, CPU-only PyTorch 2.5.1, NumPy 1.26 and two Torch threads on an Intel Core Ultra 7 165U laptop. Dependency specifications are `outputs/deepreach/requirements.txt` and `outputs/deepreach/requirements-lock.txt`. The working environment is `work/venv`; that environment directory is not a portable artifact. VS Code launch configurations are in `.vscode/launch.json`.

Install dependencies in a separate environment when reproducing on another machine. Preserve archived source bytes and line endings: source/checkpoint guards compare SHA-256 hashes, so automatic Git newline conversion can invalidate a frozen-source check even when a text editor displays equivalent code. A source-hash mismatch should be investigated rather than bypassed.

## Inspect the saved results

From the main project root, the existing environment can verify Experiment 5 without training:

```powershell
$env:MPLCONFIGDIR="$PWD\work\matplotlib"
$env:OMP_NUM_THREADS='2'
& work/venv/Scripts/python.exe outputs/deepreach/experiments_6d/experiment_5_sampling/verify_training.py
& work/venv/Scripts/python.exe outputs/deepreach/experiments_6d/experiment_5_sampling/verify_evaluation.py
```

These scripts recompute verification records from saved artifacts; they do not optimize weights. They require the complete local checkpoint/array archive. Their verification JSON is reproducible output, so preserve the original archive when running further checks. The saved Experiment 5 evaluation verification covers 63 value metric rows, 6 gradient rows, 72 switching rows, 6 common physics rows, the bootstrap intervals, 294 rollout metric rows and 5.88 million replayed control updates.

The final-report packet itself can be checked without loading model checkpoints:

```powershell
& work/venv/Scripts/python.exe outputs/deepreach/final_report/verify_report.py
```

The checker validates evidence hashes, copied figures, local Markdown targets and headline values. It does not create a new evaluation or infer scientific validity from formatting checks.

## Experiment entry points

| Phase | Entry points and saved records |
|---|---|
| Baseline and initial candidates | `deepreach.py`, `experiment2.py`; `experiments/experiment_1`, `experiments/experiment_2` |
| Horizon, field, spectrum and cost diagnostics | `diagnostics.py`, `lookahead_sweep.py`; `diagnostics_20261027`, `lookahead_21points_20261027` |
| Constrained/periodic/time/optimizer/budget studies | `experiments/experiment_3_*` and their saved protocols/manifests |
| Completed 3D final evaluation | `final_evaluate.py`; `evaluation/final_evaluation_20261028` |
| Joint-state mechanics and training | `joint6d.py`, `experiments_6d/network.py`, `experiments_6d/train.py` |
| 6D development and failure diagnostics | `experiments_6d/evaluate.py`, `rollouts.py`, diagnostic scripts and phase folders |
| Experiment 5 | `experiment_5_sampling/runner.py`, `sampler.py`, `evaluate_comparison.py`; `runs/5U`, `runs/5R`, `evaluation` |

All table paths after the first column are under `outputs/deepreach`. The evidence register links the claims to precise records rather than suggesting every archived script is an independent experiment.

Training entry points are explicitly gated. Completed training/evaluation directories are protected against overwriting. A full rerun should use a separately configured working copy and fresh output locations, with protocol changes documented before generating new states or labels. Do not rerun the consumed 3D final set as if it were untouched, silently replace existing results, or open the reserved 6D final set while tuning.

## Submission status

This is the final technical analysis packet, ready for content review. It does not claim that GitHub publication, course submission, researcher approval or memo delivery has occurred.

The course asks for a single Markdown report/notebook, runnable code, outreach/interview context and a researcher-facing recommendation. [REPORT.md](REPORT.md) supplies the technical analysis and [the memo](RECOMMENDATION_MEMO.md) supplies a draft recommendation. Before submission, merge the actual outreach/interview log and confirmed researcher context from the user's records, check permissions for any identifying or unpublished content, and record memo delivery if performed. These details cannot be reconstructed from experimental metrics. No message was sent while preparing this packet.

The historical root `Project_3.md` copies are not automatically replaced by this technical packet. Their old status paragraphs should not be used as the current experimental summary. The report can be integrated into the preferred GitHub format after content review; existing experiment records remain preserved.
