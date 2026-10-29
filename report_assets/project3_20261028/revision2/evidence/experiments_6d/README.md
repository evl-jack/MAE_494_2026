# 6D experiments — joint-coordinate Air3D

This subsection lives inside the existing project. Experiments 1–3 and their frozen results remain in their original locations.

- [Completed training results and history](TRAINING_RESULTS.md)
- [Experiment 4: problem, equations and proposed comparisons](design/SPECIFICATION.md)
- [Network and paired sampler](network.py)
- [Pre-training verification](check_network.py)
- [What the implementation checks mean](IMPLEMENTATION.md)
- [Verification results](implementation_checks.json)
- [Frozen training plan and run budgets](TRAINING_PROTOCOL.md)
- [Trainer and resume handling](train.py)
- [Disposable resume-check results](training_checks.json)

The network receives seven inputs: time remaining, pursuer x/y/heading, and evader x/y/heading. It predicts one value. The full joint coordinates enter the network directly.

Status: all three predefined training runs completed in VS Code. 4A completed 2,000 terminal-only and 10,000 physics updates; 4B completed 10,000 physics updates; 4C continued 4B for 12,000 more, reaching 22,000 cumulative physics updates. Checkpoints, logs and source snapshots are saved separately. No numerical-reference accuracy/control evaluation or new evaluation set was generated. Earlier implementation-check records describe their original pre-training stage; the frozen training plan remains unchanged.

The same subsection is mirrored in the Homework project, the local GitHub checkout and the GitHub report staging folder. Remote publication is a separate step.
