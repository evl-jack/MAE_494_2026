# Experiment 4 — 6D training completed

The three predefined runs completed in VS Code using the main project interpreter and output folders. No numerical-reference evaluation, control evaluation or new evaluation dataset was created in this training phase.

| Run | Completed updates | Cumulative physics updates | Added update time | Last sampled VI MAE |
|---|---:|---:|---:|---:|
| 4A | 12,000 | 10,000 | 363.7 s | 0.079117 |
| 4B | 10,000 | 10,000 | 329.7 s | 0.015381 |
| 4C | 22,000 | 22,000 | 441.9 s | 0.011403 |

4C inherits 4B, so their cumulative update counts must not be added as independent training. Update times exclude checkpoint/log I/O, debugger startup and process setup; they are not full wall-clock timings. Last-batch residuals describe training batches and are not prediction-error or safety metrics. 4A has a soft terminal penalty; 4B/4C enforce terminal and obstacle constraints through their output.

![Training histories](training_history.png)

Checkpoint hashes, parent identity, configurations, execution descriptions and environments are in [training_results.json](training_results.json). Source/configuration hashes were frozen before training. The parent 4B checkpoint and all protected 3D checkpoints/final-state bytes remain unchanged.

Next: check and freeze a grouped development evaluation, then measure value accuracy, coordinate invariance and gradient/control quality against the reduced numerical reference. Training loss alone does not establish transfer quality from the 3D study.
