# Proposed switch to Air3D — 20 October 2026

Historical proposal: implemented on 20 October 2026, followed by the requested pause. On 22 October the user authorized training. The smoke and reduced CPU runs have now completed. This document preserves the earlier proposal; README.md and the dated run outputs describe current results.

## Selected case

Two drones fly at fixed altitude with equal constant speed .75 m/s. The evader chooses turning rate u to avoid collision; a worst-case pursuer chooses turning rate d. Both rates lie in [-3,3] rad/s. The relative state is (x,y,psi), expressed in the evader's rotating frame. Collision means separation <= .25 m. This is the Air3D benchmark, not a full quadrotor or altitude model.

## Dynamics and value function

```
xdot   = -.75 + .75*cos(psi) + u*y
ydot   = .75*sin(psi) - u*x
psidot = d - u
l      = sqrt(x*x+y*y) - .25
```

For spatial value gradient p, the avoid Hamiltonian (max over u, min over d) is:

```
H = .75*(cos(psi)-1)*p_x + .75*sin(psi)*p_y
    + 3*abs(y*p_x-x*p_y-p_psi) - 3*abs(p_psi)
u* =  3*sign(y*p_x-x*p_y-p_psi)
d* = -3*sign(p_psi)
```

These equations were checked against the pinned official repository's `Air3D` class in `dynamics/dynamics.py`. The PINN will retain inputs (time-to-go,x,y,psi), scalar value output, soft terminal loss, sine initialization, autodiff, and an expanding-time curriculum. Its time-to-go VI remains max(V_tau-H,V-l)=0, V(0)=l.

## Files updated together

- `deepreach.py`: Air3D dynamics, max-min Hamiltonian, evader control and pursuer disturbance.
- `reference.py`: independent Air3D Hamiltonian, state-dependent dissipation bounds and CFL.
- `validate.py`: max-min control checks, Air3D sign probes, relative straight-line analytic limit, interior-domain and boundary checks.
- `configs/`: .75 m/s speed and 3 rad/s turn bounds; reduced .5 s trial and 1 s full horizon. Review the spatial domain for boundary-free comparison before executing.
- `README.md` and `PLAN.md`: replace the active Dubins scope with Air3D and record all reductions and departures from the paper.

Trained Air3D checkpoints are saved locally in the dated runs/ folders; raw artifacts are not uploaded in this publication. Initial implementation checks remain in checks/. Agreement against an approximate reference does not establish a safety guarantee.

Sources: https://arxiv.org/abs/2011.02082 and https://github.com/smlbansal/deepreach/tree/a8127aa7825d58623e9646211644876c83dd71d0
