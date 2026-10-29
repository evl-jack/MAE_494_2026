# Experiment 5 — training completed

Both fixed continuations completed on October 28, 2026 (America/Phoenix), launched separately through VS Code Run and Debug. Each began from the same completed 4C weights, Adam moments and base sampling state at 22,000 physics updates. Hardware preflight passed on the Intel Core Ultra 7 165U with about 16 GB available memory, CPU-only PyTorch 2.5.1 and two training threads.

## What ran and why

5U keeps uniform sampling as the control. 5R replaces 448 of 1,792 nonterminal rows with residual-bank points to test whether allocating the same number of updates toward physics errors improves the learned solution. The two arms keep 1,600 rows paired per batch, including all 256 terminal rows. There were no reference labels, bounds, known-failure injections, architecture changes or optimizer resets. The [frozen protocol](PROTOCOL.md) remains unchanged.

| Recorded quantity | 5U uniform | 5R mixed |
|---|---:|---:|
| Additional optimizer updates | 2,000 | 2,000 |
| Cumulative physics updates | 24,000 | 24,000 |
| Training point evaluations | 4,096,000 | 4,096,000 |
| Additional candidate points scored | 0 | 327,680 |
| Bank refreshes | 0 | 40 |
| Training-update time (s) | 41.797 | 40.366 |
| Total sampler time (s) | 0.744 | 2.854 |
| Candidate scoring, within sampler time (s) | 0.000 | 1.613 |
| Selection, within sampler time (s) | 0.000 | 0.458 |
| Recorded run wall time (s) | 49.138 | 49.090 |

Run wall time spans `run()` entry through the final checkpoint/history save. It excludes Python imports, debugger startup, UI interaction and the later verification/reporting work. Scoring and selection are included in sampler time; do not add them again. Similar observed wall times do not establish equal compute cost or a speed advantage: these are single sequential runs subject to timing variation. The protocol matches optimizer updates, and 5R performs extra scoring work.

## What the checks showed

The [completed-run verification](training_verification.json) passed. Both endpoints contain finite model weights and Adam state; every parameter's Adam step increased by exactly 2,000 relative to the parent. The endpoint model weights differ, while the base sampler RNG end states match exactly. All 21 logged terminal checks per arm have zero error, as expected from the exact terminal output. Candidate and refresh counts match the fixed plan. Frozen preparation files, protocol snapshots, algorithm sources and the original parent checkpoint retain their recorded hashes.

The endpoint checkpoints are [5U](runs/5U/checkpoint.pt) and [5R](runs/5R/checkpoint.pt), with their histories and completion records stored alongside them. [Hardware preflight](training_preflight.json) and the read-only [verification script](verify_training.py) are saved here too. No automatic training extension or hyperparameter search ran.

## What remains unresolved

Training completion does not show whether residual-guided sampling improved accuracy, gradients or safe control. The final sampled losses are 0.010383 for 5U and 0.014361 for 5R, but they average over different distributions, so they cannot rank the methods. No new development dataset, reference solve, rollout comparison or final evaluation was performed during this training phase.

Next, evaluate the parent, 5U and 5R on the same fresh development groups and common uniform physics audit defined in the frozen protocol. The primary comparison is final-horizon value MAE for 5R versus 5U, followed by gradient, classification, pose consistency and closed-loop checks. Keep the known failure as a secondary diagnostic and report regressions as well as gains. The reserved future final set remains unused.
