# Source review and game identity

28 October 2026. Primary paper inspected: [DeepReach, Section VI-B and equations (15)–(16)](https://arxiv.org/html/2011.02082). That section identifies its joint-coordinate two-vehicle problem as the same game as Air3D. It assigns the evader turn to control and the pursuer turn to disturbance. Our prototype follows those roles and uses a reduced .5 s horizon for continuity with our study.

The mathematical formulas and proposed evaluation design in SPECIFICATION.md include our own coordinate/gradient derivations. Their numerical equivalence checks are in physics_checks.json. The max/min Hamiltonian signs are independently checked against the input search and our existing working Air3D equations.

The project's recorded upstream pin is `a8127aa7825d58623e9646211644876c83dd71d0`. The inspected local file is `work/upstream/dynamics/dynamics.py`, SHA256 `ea4e59347430b32f1b28c230082521ae9270aa08168ea64d2e4a5834570b8758`.

Its Air3D class has three relative states, one control and one disturbance. Its separate MultiVehicleCollision class has nine states, three controls, no disturbance and different motion parameters (.6 m/s and 1.1 rad/s). It is not a drop-in implementation of the intended 6D pursuit–evasion game. We therefore implemented explicit joint mechanics in a separate module rather than relabeling that class.

No assertion about paper-scale accuracy, runtime matching or general high-dimensional scalability follows from this source review. The proposed small models and budgets are our adaptations and have not been trained.
