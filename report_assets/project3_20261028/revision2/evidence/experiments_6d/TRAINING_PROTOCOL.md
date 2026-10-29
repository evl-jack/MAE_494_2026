# Frozen training plan — Experiment 4

Prepared 28 October 2026, before any Experiment 4 parameter updates. This freezes the training comparison only. Development/reference/control evaluation must be checked separately before model selection or final evaluation; the earlier design draft describes those proposals.

| Run | Output | Terminal-only updates | Physics curriculum | Additional full-horizon updates |
|---|---|---:|---:|---:|
| 4A | Soft terminal | 2,000 | 10,000 | 0 |
| 4B | Exact terminal/obstacle square | 0 | 10,000 | 0 |
| 4C | Continue completed 4B | inherited 0 | inherited 10,000 | 12,000 |

The state order is `(xp, yp, heading_p, xe, ye, heading_e)` with time remaining first in the seven-input network. All runs use three sine hidden layers of width 64 (8,897 parameters), Adam at 0.0001, float32 CPU arithmetic, deterministic Torch operations and two threads. Parameters remain speed 0.75 m/s, turn bound 3 rad/s, collision distance 0.25 m, horizon 0.5 s, position coordinates each within ±2 m and heading sampling within ±1.2π. No numerical-reference labels enter training.

Each update samples 2,048 joint states. Terminal-only updates set all times to zero. Physics batches have 256 trailing zero-time rows. At physics update j the curriculum samples time uniformly from zero to `0.5 * min(j/10000, 1)` seconds. 4C samples the entire horizon from its first added update. The VI loss is mean absolute `max(V_tau - H6, V - l6)` over all rows, including zero-time rows.

4A uses `25*raw + 0.25` and terminal MAE over its zero-time rows. On its first physics batch, **after terminal pretraining**, its terminal weight is fixed to `0.1 * clamp(physics_MAE / max(terminal_MAE, 1e-8), 1e-3, 1e4)`. The total physics-phase loss is VI MAE plus that fixed weight times terminal MAE. 4B and 4C use `l6 - 0.25*(tau/0.5)*raw²`, add 1 to the initialized output bias and use zero terminal penalty. These exact constraints do not guarantee value, gradient or control accuracy.

Initialization seed is 7. Independent terminal and physics sampler seeds are 991745 and 991746. 4A pretraining does not consume the physics stream: its first 10,000 physics batches match 4B's, with equal curriculum times. Initial hidden weights match but the output bias differs. The comparison matches physics updates, not total updates, initialization of the output, runtime or floating-point work. 4C continues 4B's parameters, Adam moments and sampler stream; it is not a fresh run.

Logs record every 100 updates and phase transitions; checkpoints are written every 1,000 updates and on an explicit stop. Resume uses the latest completed saved update, so interrupting between checkpoints can discard up to 999 completed updates. Checkpoint replacement is atomic. No automatic restart or background execution is configured. The checkpoint includes weights, Adam state, terminal weight, both sampler RNG states, Torch RNG, progress, history, elapsed update time, source hashes and parent identity. Update time excludes checkpoint/log I/O and process setup; it is not wall-clock runtime. A future runtime comparison should capture full process time separately.

4A, 4B and 4C write separate main-project folders under `experiments_6d/runs/`. The Homework VS Code entries deliberately use the main project interpreter and output paths, keeping one authoritative training run. Mirrors are saved after runs, not live synchronized. Fresh runs refuse nonempty output folders; resume requires identical configuration and source hashes. 4C requires a completed 4B checkpoint and cannot overwrite it.

`check_training.py` passed 27 disposable optimizer updates using two layers of width 8, batches of 32 and separate fixture seeds. Uninterrupted and resumed weights, Adam state, sampler state and calibrated weight matched bit for bit, including terminal/physics phase boundaries and the 4C extension. The fixtures were deleted. **No Experiment 4 run has started.** The existing 3D checkpoints and consumed final-state bytes are unchanged.

VS Code keeps verification as the first launch entry. Entries containing **START TRAINING** require an intentional start; adding them does not execute them. Before training, inspect current available hardware resources. The `--train` flag is required by the command-line entry point. The trainer does not generate evaluation sets, tune against references or launch later runs automatically.
