"""Air3D soft-terminal DeepReach reproduction. Units: m, s, rad.

Sine initialization follows Vincent Sitzmann's MIT-licensed SIREN implementation;
see THIRD_PARTY_NOTICES.md. DeepReach sources and differences: README.md.
"""
import argparse
import csv
import json
import math
import os
import platform
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

UPSTREAM = "a8127aa7825d58623e9646211644876c83dd71d0"


def target(s, c):
    """Collision signed distance in the evader's relative coordinate frame."""
    return torch.linalg.vector_norm(s[..., :2], dim=-1) - c["radius"]


def dynamics(s, control, disturbance, c):
    """u=evader turn, d=pursuer turn; both lie in [-turn, turn]."""
    x, y, psi, control, disturbance = torch.broadcast_tensors(*s.unbind(-1), control, disturbance)
    return torch.stack((c["speed"]*(psi.cos()-1)+control*y,
                        c["speed"]*psi.sin()-control*x,
                        disturbance-control), dim=-1)


def hamiltonian(s, p, c):
    """H=max_u min_d p.f: avoidance control against a worst-case pursuer."""
    evader_coefficient = s[..., 1]*p[..., 0]-s[..., 0]*p[..., 1]-p[..., 2]
    drift = c["speed"]*((s[..., 2].cos()-1)*p[..., 0]+s[..., 2].sin()*p[..., 1])
    return drift+c["turn"]*evader_coefficient.abs()-c["turn"]*p[..., 2].abs()


def optimal_control(s, p, c):
    """Autodiff value gradients give a candidate avoid control, not a certificate."""
    return c["turn"]*(s[..., 1]*p[..., 0]-s[..., 0]*p[..., 1]-p[..., 2]).sign()


def optimal_disturbance(p, c):
    return -c["turn"]*p[..., 2].sign()


def validate_config(c):
    if c.get("problem") != "Air3D" or c.get("formulation") != "soft_terminal":
        raise ValueError("Expected an Air3D soft_terminal config; old Dubins checkpoints are incompatible.")
    for key in ["horizon", "domain", "radius", "value_scale", "lr"]:
        if c[key] <= 0: raise ValueError(f"{key} must be positive")
    if c["speed"] < 0 or c["turn"] < 0 or c["angle_factor"] < 1:
        raise ValueError("Speed/turn must be nonnegative and angle_factor >= 1")
    for key in ["width", "sine_layers", "samples", "terminal_samples", "curriculum_steps", "threads", "log_every", "save_every"]:
        if not isinstance(c[key], int) or c[key] <= 0: raise ValueError(f"{key} must be a positive integer")
    if c["pretrain_steps"] < 0 or not 0 < c["terminal_samples"] < c["samples"]:
        raise ValueError("Require nonnegative pretraining and 0 < terminal_samples < samples")


class Siren(nn.Module):
    def __init__(self, c):
        super().__init__()
        validate_config(c)
        self.c = c
        self.layers = nn.ModuleList()
        dims = [4] + [c["width"]]*c["sine_layers"] + [1]
        for i, (ni, no) in enumerate(zip(dims[:-1], dims[1:])):
            layer = nn.Linear(ni, no)
            # Upstream reinitializes weights only; keep nn.Linear bias init.
            bound = 1/ni if i == 0 else math.sqrt(6/ni)/30
            nn.init.uniform_(layer.weight, -bound, bound)
            self.layers.append(layer)
        self.register_buffer("scales", torch.tensor([c["horizon"], c["domain"], c["domain"], c["angle_factor"]*math.pi]))

    def raw(self, z):
        for layer in self.layers[:-1]:
            z = torch.sin(30*layer(z))
        return self.layers[-1](z).squeeze(-1)

    def forward(self, physical):
        # z_t=tau/T; physical derivative from autodiff includes 1/T.
        # V = value_scale*raw + value_mean; upstream scale .5/.02=25.
        return self.c["value_scale"]*self.raw(physical/self.scales) + self.c["value_mean"]


def value_grad(model, q, create_graph=False):
    q = q.detach().requires_grad_(True)
    v = model(q)
    dv = torch.autograd.grad(v.sum(), q, create_graph=create_graph)[0]
    return v, dv


def residual(model, q, c, create_graph=False):
    v, dv = value_grad(model, q, create_graph)
    # tau=T-t reverses physical-time min(V_t+H,l-V)=0.
    r = torch.maximum(dv[:, 0]-hamiltonian(q[:, 1:], dv[:, 1:], c), v-target(q[:, 1:], c))
    return r, v, dv


def sample(c, n, tmax, nterminal, device):
    z = 2*torch.rand(n, 4, device=device)-1
    q = z*torch.tensor([1, c["domain"], c["domain"], c["angle_factor"]*math.pi], device=device)
    q[:, 0] = torch.rand(n, device=device)*tmax
    q[-nterminal:, 0] = 0
    return q


def load_checkpoint(path, device="cpu"):
    # Only load locally generated/trusted checkpoints: optimizer/RNG require pickle.
    ck = torch.load(path, map_location=device, weights_only=False)
    model = Siren(ck["config"]).to(device)
    model.load_state_dict(ck["model"])
    return model, ck


def environment(device):
    return dict(python=platform.python_version(), torch=torch.__version__, numpy=np.__version__,
                platform=platform.platform(), processor=platform.processor(), cpu_count=os.cpu_count(),
                device=str(device), cuda_available=torch.cuda.is_available(), threads=torch.get_num_threads(), upstream=UPSTREAM)


def train(c, out, resume=None, stop_after=None):
    out = Path(out)
    if (out/"checkpoint.pt").exists() and not resume:
        raise FileExistsError("This run already has a checkpoint. Use --resume or a new output folder.")
    out.mkdir(parents=True, exist_ok=True)
    device = torch.device(c["device"])
    torch.set_num_threads(c["threads"])
    torch.use_deterministic_algorithms(True)
    random.seed(c["seed"]); np.random.seed(c["seed"]); torch.manual_seed(c["seed"])
    model = Siren(c).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=c["lr"])
    start, weight, elapsed = 0, None, 0.
    if resume:
        model, ck = load_checkpoint(resume, device)
        if ck["config"] != c:
            raise ValueError("Resume requires identical config; use stop-after to split a run.")
        optimizer = torch.optim.Adam(model.parameters(), lr=c["lr"])
        optimizer.load_state_dict(ck["optimizer"])
        start, weight, elapsed = ck["step"], ck["terminal_weight"], ck["elapsed_seconds"]
        torch.set_rng_state(ck["torch_rng"].cpu()); np.random.set_state(ck["numpy_rng"]); random.setstate(ck["python_rng"])
        if device.type == "cuda": torch.cuda.set_rng_state_all(ck["cuda_rng"])
    total = c["pretrain_steps"]+c["curriculum_steps"]
    print(f"Air3D | device={device} | threads={c['threads']} | "
          f"sine layers={c['sine_layers']} x {c['width']} | samples={c['samples']} | "
          f"steps={start}..{total} | horizon={c['horizon']}s | output={out}",flush=True)
    end = min(total, stop_after) if stop_after else total
    (out/"config.json").write_text(json.dumps(c, indent=2))
    (out/"environment.json").write_text(json.dumps(environment(device), indent=2))
    clock = time.perf_counter()
    log = open(out/"history.csv", "a" if resume else "w", newline="")
    writer = csv.writer(log)
    if not resume: writer.writerow(["step", "phase", "tmax", "terminal_mae", "pde_mae", "terminal_weight", "loss", "elapsed_seconds"])
    def save(step):
        ck = dict(model=model.state_dict(), optimizer=optimizer.state_dict(), config=c, step=step,
                  curriculum_step=max(0,step-c["pretrain_steps"]), terminal_weight=weight,
                  elapsed_seconds=elapsed+time.perf_counter()-clock, torch_rng=torch.get_rng_state(),
                  numpy_rng=np.random.get_state(), python_rng=random.getstate(),
                  cuda_rng=torch.cuda.get_rng_state_all() if device.type == "cuda" else None,
                  environment=environment(device), upstream=UPSTREAM)
        torch.save(ck, out/"checkpoint.tmp")
        os.replace(out/"checkpoint.tmp", out/"checkpoint.pt")
    for step in range(start, end):
        pre = step < c["pretrain_steps"]
        j = step-c["pretrain_steps"]+1
        tmax = 0 if pre else c["horizon"]*min(j/c["curriculum_steps"],1)
        nt = c["samples"] if pre else c["terminal_samples"]
        q = sample(c, c["samples"], tmax, nt, device)
        if pre:
            b = (model(q)-target(q[:, 1:],c)).abs().mean()
            p = torch.zeros((),device=device)
            loss = b
        else:
            r, v, _ = residual(model,q,c,True)
            p = r.abs().mean()  # Upstream includes terminal points in PDE sum.
            b = (v[-nt:]-target(q[-nt:,1:],c)).abs().mean()
            if weight is None:
                # Paper: balance initial loss terms. Fixed thereafter; no modern
                # repo adaptive parameter-gradient balancing in this baseline.
                weight = float((p.detach()/b.detach().clamp_min(1e-8)).clamp(1e-3,1e4))
            loss = p+weight*b
        optimizer.zero_grad(set_to_none=True)
        if not torch.isfinite(loss): raise FloatingPointError("Nonfinite training loss")
        loss.backward(); optimizer.step()
        if (step+1)%c["log_every"] == 0 or step in [0,c["pretrain_steps"]] or step+1 == end:
            row = [step+1,"pretrain" if pre else "curriculum",tmax,float(b.detach()),float(p.detach()),weight,float(loss.detach()),elapsed+time.perf_counter()-clock]
            writer.writerow(row); log.flush()
            print(f"[{step+1}/{total}] {row[1]} | horizon sampled=0..{tmax:.4f}s | "
                  f"terminal MAE={row[3]:.6f} | VI MAE={row[4]:.6f} | "
                  f"elapsed={row[7]:.1f}s",flush=True)
        if (step+1)%c["save_every"] == 0 or step+1 == end: save(step+1)
    log.close()
    return model


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--resume"); ap.add_argument("--stop-after",type=int)
    ap.add_argument("--train", action="store_true", help="Explicitly start training; preflight.py never trains.")
    a = ap.parse_args()
    if not a.train: ap.error("Training is paused by default. Supply --train only when ready to train.")
    train(json.loads(Path(a.config).read_text()),a.out,a.resume,a.stop_after)
