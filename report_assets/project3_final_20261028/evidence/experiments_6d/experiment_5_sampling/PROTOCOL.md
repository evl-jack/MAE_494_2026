# Experiment 5 — uniform versus residual-guided continuation

Prepared before Experiment 5 training. The sampler and trainer are implemented and checked. Training remains paused.

## Question and fixed runs

Can redistributing collocation points improve the existing 6D model at the same number of optimizer updates, without reference labels or bounds in training?

| Arm | Starting state | Additional updates | Batch | Nonterminal sampling |
|---|---|---:|---:|---|
| 5U | Completed 4C, including Adam moments and sampler state | 2,000 | 2,048 | All 1,792 fresh uniform |
| 5R | Identical completed 4C state | 2,000 | 2,048 | 1,344 fresh uniform + 448 residual-bank points |

Both arms add 2,000 updates to the existing 22,000-update parent and reach 24,000 cumulative physics updates. This spends additional training in each arm; it tests sampling under equal added update budgets, rather than a zero-extra-training improvement. The 5R versus 5U difference is the sampling comparison; improvements over the parent also include the added updates. They use the same seven-input, 8,897-parameter network, exact terminal/obstacle output, physical domain, Adam learning rate 0.0001, full 0.5-second horizon, float32 CPU arithmetic and two threads. The 256 trailing zero-time rows remain uniform and paired. There is no terminal-only pretraining, altered loss term, architecture change or optimizer reset.

This is a continuation experiment from an already studied model, not a new from-scratch replication or an untouched validation of a previously unknown hypothesis. The parent checkpoint is preserved; each arm writes its own run folder.

## Residual-bank rule

Before additional updates 1, 51, 101, …, 1951, draw 8,192 fresh candidate points uniformly from the full joint training box and full time horizon. No rows are deliberately set to zero time in this pool. Score candidates with the current network's native absolute VI residual, requiring input derivatives but no optimizer step or accumulated parameter gradients.

Keep the 1,024 largest scores. Ties retain candidate order. For each of the next 50 updates, select 448 distinct rows uniformly from that bank. Points may be reused across updates; their scores stay fixed until the next refresh. This can overemphasize stale or repeated points, which is a limitation of this one fixed rule. No refresh-rate, fraction or bank-size search is performed during the runs.

The bank replaces the first 448 nonterminal rows of an otherwise identical fresh uniform batch. Each arm advances the common base sampler by a full batch every update. Candidate generation and bank selection have separate random generators, so the remaining 1,600 rows—including all terminal rows—match exactly across the two arms. Initial weights and Adam state match; subsequent weights can diverge because samples differ.

The bank has no known-failure injection, reference values, reference gradients, safety labels, geometric reference bounds or stored development states. Selection intentionally changes the collocation distribution. No importance correction is applied, so this is not an unbiased estimator of the uniform expected loss. Sampled training losses from the two arms are therefore not directly comparable as performance scores.

## Budget and accounting

Each arm has exactly 2,000 optimizer updates and 4,096,000 training point evaluations. 5R additionally scores 327,680 candidates in 40 refreshes. That is 8% of the training point count, not 8% of training FLOPs or wall time: scoring and training perform different derivative work. There are 21.875% bank points in the entire training batch, equivalent to 25% of its nonterminal rows.

Record training-update time, candidate-scoring time, total sampler time, selection time, candidate counts, refresh counts and run wall time. Scoring/selection times are components of sampler time and must not be added to it again. Run wall time includes initialization and checkpoint/log work inside `run()`, but excludes Python imports and VS Code/debugger startup. This comparison matches optimizer updates, not total compute or wall time. Extra candidate-scoring overhead must be shown alongside accuracy results.

A native-size scoring dry check used 8,192 points from the unchanged parent; it is preparation overhead outside both future run budgets. Resume verification used 27 disposable optimizer updates on two-layer width-8 models with batches of 32; those fixtures were deleted. Neither activity started an Experiment 5 run.

## Reproducibility and resume

Both arms inherit the parent's base sampler states. Candidate seed is 991763 and selection seed 991764. The paired base stream is independent of both. Source and parent hashes are frozen in `protocol.json`; checkpoints carry the current bank, stale scores, last refresh, candidate/base/selection RNG states, model weights, Adam moments, completed updates, cost counters and history.

Checkpoints are saved every 250 completed updates and at an explicit stop. Resume starts from the last saved completed update; an interruption can discard up to 249 completed updates. No automatic restart or arm chaining is configured. Fresh runs refuse nonempty output folders; resume requires the same mode, protocol and source version. Existing 4C and all earlier results remain unchanged.

Verification checked top-score selection, deterministic ties, domain/terminal constraints, paired rows, RNG independence, bank replay across refreshes and bitwise network/Adam/sampler resume for both modes. The actual parent dry check created no optimizer and made no parameter updates. `checks.json` is a rerunnable check record; the preparation manifest embeds its original result summary.

## Prospective evaluation

Report both fixed endpoints and the parent on the same fresh development set: 6,000 relative groups, four poses each, 21 horizons. Relative seed 991765 and pose seed 991766 are reserved for this comparison; no such dataset has been generated during preparation. All equivalent poses stay in a group for analysis and bootstrap uncertainty. Seed 991768 is reserved for a paired group bootstrap.

Primary metric: final-time value MAE of 5R versus 5U. Secondary metrics include the parent comparison, all horizons, both classification errors, value tails, pose/heading consistency, gradient and reference-stable switching signs, and physical/temporal checks. Use the unchanged 129×129×96 numerical solver with the 97×97×72 comparison level as in the broad development benchmark; report its approximation limits. The already saved finer local maps remain an additional evaluation-only diagnostic for the known failure.

Plan the same exact-arc, within-step-contact rollout method on 200 randomly selected fresh groups and four poses (subset seed 991767), at dt=.01 and .005. Include parent/5U/5R/reference/straight/left/right policies in both roles, with the existing reference-safe subset definition. Do not treat a known-case repair alone as success or omit degraded regions. No intermediate-checkpoint accuracy selection is allowed. A separate common uniform physics audit uses seed 991769 and 8,192 points after training; it does not enter updates.

Report all outcomes even if the mixed sampler loses. This is one training seed with paired continuation, and group sampling intervals do not measure training-seed variability or solver error. The old consumed 3D final data and future final seed 991748 remain unused. Final evaluation is a later step after the approach is fixed; it is not part of preparing or training these arms.
