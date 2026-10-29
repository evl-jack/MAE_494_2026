# Experiment 5 â€” sampling comparison

**Status: both training arms completed; common accuracy/control evaluation pending.**

[Training results, timings and verification](TRAINING_RESULTS.md). Each arm completed 2,000 additional updates through VS Code and reached 24,000 cumulative physics updates. The frozen protocol is retained as the original preparation record.

[Full protocol and budgets](PROTOCOL.md) defines the two continuations from the same completed 4C state. [Machine-readable frozen plan](protocol.json) records the parent, algorithm hashes and future evaluation seeds.

| Arm | Additional updates | Sampling |
|---|---:|---|
| 5U | 2,000 | Uniform control |
| 5R | 2,000 | Uniform coverage plus 25% residual-bank points among nonterminal rows |

Both arms add 2,000 updates to 4C and reach 24,000 total. Compare 5R with 5U to separate sampling effects from the benefit of running longer.

The [sampler](sampler.py) preserves paired uniform/terminal rows and independent candidate/selection streams. The [trainer](runner.py) preserves the parent's Adam moments, guards against overwriting runs, and restores the bank and RNG states on resume. It requires the explicit `--train` flag.

[Verification](checks.json) passed analytic selection checks and bitwise resume tests with tiny disposable models. The native-size dry check only scored candidates using 4C: it did not update that model. [Preparation manifest](preparation_manifest.json) records the checked source version.

VS Code provides a check entry and separately labeled start/resume entries. The Homework launch entries use the main project interpreter and output folders. Both experimental run folders now contain their completed checkpoints and logs. No new development set or final dataset has been generated in this training phase. Rerunning the check entry uses tiny disposable optimizer fixtures and preserves experimental checkpoints.

This matches optimizer-update budgets, not wall time. The extra scoring work is recorded explicitly. No numerical reference labels or bounds enter training, and no known failure state is injected into the candidate pool.
