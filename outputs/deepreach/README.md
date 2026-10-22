# DeepReach Air3D — Experiment 1 completed

The active code models two fixed-altitude drones in the Air3D collision-avoidance game. **Experiment 1** is the first trained baseline: a 12,000-step reduced CPU run completed on 22 October 2026. The 60-step smoke run is a preceding setup check, not another experiment. The CPU training loop took 206.4 seconds using two threads and saved a resumable checkpoint. The Experiment 1 report, comparison figures, aggregate metrics and configuration are public; raw run artifacts remain local. This is a reduced experiment, not a paper-scale reproduction or a safety certificate.

**Measured outcome:** the reduced model is not yet accurate enough for collision decisions. At .5 s, value MAE is .0915 m and 46.4% of reference-unsafe held-out states are labeled safe by the PINN. Grid refinement and checkpoint restart checks passed. See the [Experiment 1 report](experiments/experiment_1/README.md) for denominators, plots and limitations, or the [experiment index](experiments/README.md).

## The problem

Both drones fly at .75 m/s. The evader chooses turn u to maximize minimum separation while a worst-case pursuer chooses turn d to minimize it. Both rates lie in [-3,3] rad/s. Separation <=.25 m is unsafe. This is a planar relative-motion model, without altitude, thrust or full quadrotor dynamics.

Relative state s=(x,y,psi) is expressed in the evader's rotating frame:

    xdot   = .75*(cos(psi)-1) + u*y
    ydot   = .75*sin(psi) - u*x
    psidot = d-u
    l(s)   = sqrt(x*x+y*y)-.25

For spatial value gradient p, the avoid Hamiltonian and candidate controls are:

    H  = .75*((cos(psi)-1)*p_x+sin(psi)*p_y)
         +3*abs(y*p_x-x*p_y-p_psi)-3*abs(p_psi)
    u* =  3*sign(y*p_x-x*p_y-p_psi)
    d* = -3*sign(p_psi)

Time-to-go tau=T-t gives max(V_tau-H,V-l)=0, with V(0,s)=l(s).
For the ideal solution, V<=0 identifies states from which collision can be forced despite optimal evasion. A neural approximation's sign and control are not certified safe.

## Files

| File | Purpose |
|---|---|
| deepreach.py | Air3D dynamics, sine PINN, derivatives, physics loss, sampling, curriculum, training and checkpoint code |
| reference.py | Independent NumPy HJI grid solver and periodic heading interpolation |
| preflight.py | Implementation checks; never trains |
| validate.py | Future trained-PINN/reference comparisons, diagnostics and plots |
| configs/ | Smoke, reduced CPU and full paper-scale budgets |
| checks/ | Actual implementation-check results; these are not trained PINN results |
| PLAN.md | Air3D plan and explicit pause before training |
| AIR3D_PROPOSED_UPDATES.md | Earlier proposal, with status updated |
| THIRD_PARTY_NOTICES.md | Source attribution and SIREN license |
| requirements.txt | Core dependency pins |
| requirements-lock.txt | Exact installed dependencies |
| Experiment 1 report | Public comparison figures, metrics, configuration and limitations |
| Local runs/ | Raw checkpoints, logs, source snapshots and reference arrays; not uploaded |

## Sources and departures

Paper: [Bansal and Tomlin, DeepReach](https://arxiv.org/abs/2011.02082).
Official source: [smlbansal/deepreach](https://github.com/smlbansal/deepreach/tree/a8127aa7825d58623e9646211644876c83dd71d0), public_release commit a8127aa7825d58623e9646211644876c83dd71d0, dated 13 November 2024. The homework copy includes this source in references/upstream-a8127aa.

The full physical parameters and 1 s horizon follow the paper. Full uses three actual sine hidden layers of width 512. The modern repository's num_hl=3 creates four sine hidden layers; its constructor and the paper's architecture wording are not treated as equivalent.

This implementation uses original soft terminal loss (vanilla value semantics). The modern Air3D constructor and launcher default to exact, enforcing V=l+25*tau*network. The diff option adds l without the tau multiplier. Neither alternative is implemented here.

Inputs normalize time by T, x/y by domain half-width, and psi by 1.2*pi. Output is 25*network+.25. Autodiff includes physical-unit chain rules. Hidden activations are sin(30*z), with SIREN weight initialization. Losses use mean absolute errors. The terminal loss weight is calibrated once at curriculum start to balance initial terms, then fixed: a documented interpretation of the paper's initial balancing, distinct from the modern repository's optional adaptive parameter-gradient weighting and sum losses. Terminal samples also enter the physics loss, as upstream does.

| Config | Sine hidden layers | Samples/step | Pretrain + curriculum | Horizon | x/y domain |
|---|---|---|---|---|---|
| smoke | 3 x 32 | 256 | 20 + 40 | .5 s | [-2,2] m |
| cpu | 3 x 64 | 2048 | 2000 + 10000 | .5 s | [-2,2] m |
| full | 3 x 512 | 65000 | 10000 + 100000 | 1 s | [-3,3] m |

All select CPU and Adam at 1e-4. Full is paper-scale, rather than an exact recreation of every paper setting. The widened domains depart from the repository's [-1,1] scaling and support an interior comparison on [-.6,.6]^2. Since evader-frame rotation preserves radius and radial speed is bounded by 2v, all dependency trajectories from that square have radius <=sqrt(2)*.6+2*v*T: <2 for the reduced horizon and <3 for full. Numerical boundary sensitivity must still be checked at the actual horizon. This interior region does not necessarily contain the entire BRT.

## Independent numerical reference

The NumPy solver implements Air3D independently of the PINN. It uses positive local Lax-Friedrichs viscosity for V_tau=H, explicit Euler steps, and obstacle projection V=min(V,l). Heading is periodic; spatial ghost cells use constant extension.

    alpha_x   = abs(v*(cos(psi)-1)) + omega*abs(y)
    alpha_y   = abs(v*sin(psi))    + omega*abs(x)
    alpha_psi = 2*omega
    dt <= .8 / max(alpha_x/dx + alpha_y/dy + alpha_psi/dpsi)

These speed bounds and CFL give a monotone update. Spatial extension is artificial; compare only in the interior and test against an expanded domain at matching spacing and time-step schedule. Future full validation uses 65/97/129 spatial nodes and 48/72/96 headings. These approximate references have diffusion, especially on the larger full domain; refinement does not provide a rigorous error bound. Reference labels never enter PINN training.

## Setup and checks: no training

From the project root with Python 3.12:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r outputs/deepreach/requirements.txt
    .\.venv\Scripts\python.exe outputs/deepreach/preflight.py --config outputs/deepreach/configs/cpu.json --out outputs/deepreach/checks/preflight_cpu.json

Add --upstream references/upstream-a8127aa to compare against the bundled official source. In the original Codex workspace the source is work/upstream and the existing interpreter is work/venv/Scripts/python.exe.

Preflight checks autodiff versus finite differences, explicit max-min optimization, NumPy/PyTorch Hamiltonians, physical-time signs, finite physics-loss parameter derivatives without applying them, sampling, a .1 s grid refinement, larger-domain sensitivity, frozen dynamics, no-turn analytic agreement and the periodic heading seam. The randomly initialized network has not learned a value function. Saved checks include software versions and optimizer_steps=0.

## Training commands

The launcher refuses to train without --train and refuses to overwrite an existing checkpoint without --resume. The dated smoke and CPU runs below have completed. For a new experiment, choose a fresh output folder.

    .\.venv\Scripts\python.exe outputs/deepreach/deepreach.py --train --config outputs/deepreach/configs/smoke.json --out outputs/deepreach/runs/air3d_smoke_20261022
    .\.venv\Scripts\python.exe outputs/deepreach/deepreach.py --train --config outputs/deepreach/configs/cpu.json --out outputs/deepreach/runs/air3d_cpu_20261022
    .\.venv\Scripts\python.exe outputs/deepreach/validate.py --checkpoint outputs/deepreach/runs/air3d_cpu_20261022/checkpoint.pt --out outputs/deepreach/runs/air3d_cpu_20261022/validation

Resume by adding --resume outputs/deepreach/runs/air3d_cpu_20261022/checkpoint.pt to the identical training command. Configs must match exactly; old Dubins checkpoints are rejected. Full training substitutes configs/full.json and a separate output directory and requires substantial compute; it has not run. CUDA requires suitable hardware, installation and a device config change. This laptop has integrated Intel graphics and uses CPU PyTorch.

Normal validation does not train. Its optional --check-training-resume runs a six-step optimizer sequence both continuously and with a split restart. The reduced-run comparison command on 22 October includes that check. Comparison outputs include held-out terminal/VI errors, value errors, BRT overlap, false-safe fractions and slices at multiple times/headings. See the Experiment 1 report and aggregate metrics for measured agreement and limitations. Loss alone does not establish correctness. Empirical agreement is not a safety guarantee; a gradient reliability study remains outside scope.
