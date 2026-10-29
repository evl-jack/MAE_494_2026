# Experiment 4 — Joint-coordinate 6D design

**Status: specification and mathematical checks only. No network initialization, optimizer or training run.**

[Full specification and proposed experiment plan](SPECIFICATION.md) defines the six joint states, pursuit–evasion roles, dynamics, target, HJI equation, reduction, gradient/control checks, new data splits and prospective laptop budgets. [Protocol draft](protocol_draft.json) is not a frozen training configuration.

The intended benchmark is the same two-vehicle game in the [DeepReach paper, Section VI-B](https://arxiv.org/html/2011.02082), represented in joint coordinates. Its exact reduction to our existing 3D game provides a numerical evaluation route and a way to test invariance and gradient consistency. This is a six-state representation test, not a new altitude/acceleration model or a game with additional interacting vehicles.

The new `joint6d.py` module contains mechanics and coordinate/gradient mappings. `check_joint6d.py` verifies them against existing Air3D equations, autodiff, explicit max/min input search and symmetry identities. `physics_checks.json` records errors near floating-point precision and unchanged old checkpoint/final-state hashes. These checks are not neural prediction or controller performance results.

The 3D study's final data remain consumed and unchanged. No new development or reserved final dataset was generated here. Future 6D pose groups must be split by underlying relative configuration, and new data seeds are proposed separately in the draft.

The next implementation task is the seven-input network and paired sampler, followed by a checked, frozen training protocol. No training launcher has been added in this design phase.
