"""Air3D implementation checks. No optimizer, training calls or weight updates.

Runs network inference/autodiff and small numerical-reference computations.
These checks do not establish trained PINN accuracy or a safety guarantee.
"""
import argparse
import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import torch

from deepreach import Siren, dynamics, environment, hamiltonian, optimal_control, optimal_disturbance, residual, sample, target
from reference import differences, grid_hamiltonian, interpolate, solve
from validate import comparison_region, error, mechanical_checks, straight_line_values


def check_upstream(c,path):
    """Optional direct comparison against the pinned local official source."""
    sys.path.insert(0,str(Path(path).resolve()))
    upstream=importlib.import_module("dynamics.dynamics")
    official=upstream.Air3D(c["radius"],c["speed"],c["turn"],c["angle_factor"])
    torch.manual_seed(8)
    s=torch.randn(64,3,dtype=torch.float64); p=torch.randn_like(s)
    u=optimal_control(s,p,c); d=optimal_disturbance(p,c)
    errors=dict(hamiltonian=float((official.hamiltonian(s,p)-hamiltonian(s,p,c)).abs().max()),
                flow=float((official.dsdt(s,u[:,None],d[:,None])-dynamics(s,u,d,c)).abs().max()),
                target=float((official.boundary_fn(s)-target(s,c)).abs().max()),
                control=float((official.optimal_control(s,p).squeeze(-1)-u).abs().max()),
                disturbance=float((official.optimal_disturbance(s,p).squeeze(-1)-d).abs().max()))
    assert max(errors.values()) < 1e-12, errors
    return errors


def checks(c,upstream=None):
    torch.set_num_threads(c["threads"]); torch.manual_seed(c["seed"])
    model=Siren(c).eval()
    before={k:v.clone() for k,v in model.state_dict().items()}
    result={"status":"implementation checks only; no training", "optimizer_steps":0,
            "environment":environment("cpu"),"mechanical":mechanical_checks(model,c)}
    interior,rad=comparison_region(c)
    result["comparison_region"]={"half_width":interior,"dependency_radius_bound":rad,"domain":c["domain"]}
    q=sample(c,128,c["horizon"],16,"cpu")
    assert torch.all(q[-16:,0]==0) and torch.all((q[:,0]>=0)&(q[:,0]<=c["horizon"]))
    assert torch.all(q[:,1:3].abs()<=c["domain"])
    assert torch.all(q[:,3].abs()<=c["angle_factor"]*math.pi)
    r,v,dv=residual(model,q,c,True)
    # Verify physics loss can backpropagate, without creating an optimizer.
    loss=r.abs().mean()+(v[-16:]-target(q[-16:,1:],c)).abs().mean()
    gradients=torch.autograd.grad(loss,tuple(model.parameters()))
    assert all(torch.isfinite(g).all() for g in gradients)
    assert all(torch.equal(value,model.state_dict()[key]) for key,value in before.items())
    result["physics_graph"]={"finite_parameter_gradients":True,"weights_unchanged":True,"sample_shape":list(q.shape)}
    # Explicit time-to-go sign check: head-on no-turn value before collision,
    # at y=0 and x>0, V=x-2*v*tau-R. H=-2*v and V_tau=-2*v.
    class StraightValue(torch.nn.Module):
        def forward(self,q): return q[:,1]-2*c["speed"]*q[:,0]-c["radius"]
    qt=torch.tensor([[.01,.5,0,math.pi],[.02,.6,0,math.pi]],dtype=torch.float64)
    no_turn=dict(c,turn=0.)
    sign_error=float(residual(StraightValue(),qt,no_turn)[0].abs().max())
    assert sign_error<1e-12
    result["time_to_go_sign_max_abs"]=sign_error
    rng=np.random.default_rng(20261020)
    states=rng.uniform([-.6,-.6,-math.pi],[.6,.6,math.pi],size=(4096,3))
    ps=rng.normal(size=(4096,3))
    numpy_h=grid_hamiltonian(states[:,0],states[:,1],states[:,2],ps.T,c)
    torch_h=hamiltonian(torch.tensor(states),torch.tensor(ps),c).numpy()
    result["numpy_torch_hamiltonian_max_abs"]=float(np.max(np.abs(numpy_h-torch_h)))
    assert result["numpy_torch_hamiltonian_max_abs"]<1e-12
    # Keep preflight modest: .1 s, 33/49/65 spatial nodes, 24/36/48 headings.
    short=dict(c,horizon=.1)
    times=[0.,.05,.1]
    refs=[solve(short,n,nh,times) for n,nh in [(33,24),(49,36),(65,48)]]
    vals=[interpolate(ref,.1,states) for ref in refs]
    refinement={"33_to_49":error(vals[0],vals[1]),"49_to_65":error(vals[1],vals[2])}
    assert refinement["49_to_65"]["mae"]<refinement["33_to_49"]["mae"]
    result["short_reference_refinement"]=refinement
    expanded=solve(short,97,48,times,domain=1.5*c["domain"])
    matched=solve(short,65,48,times,dt_limit=expanded["dtmax"])
    boundary=error(interpolate(matched,.1,states),interpolate(expanded,.1,states))
    assert boundary["max_abs"]<.005
    result["short_boundary_sensitivity"]=boundary
    result["boundary_test_matched_dx_and_dt"]=True
    frozen=solve(dict(short,speed=0.,turn=0.),17,12,times)
    assert np.array_equal(frozen["values"][0.],frozen["values"][.1])
    result["frozen_dynamics_max_abs"]=0.
    straight=dict(short,turn=0.)
    analytic=straight_line_values(states,.1,straight)
    coarse=solve(straight,33,24,times); fine=solve(straight,65,48,times)
    straight_errors={"coarse":error(interpolate(coarse,.1,states),analytic),"fine":error(interpolate(fine,.1,states),analytic)}
    assert straight_errors["fine"]["mae"]<straight_errors["coarse"]["mae"]
    result["straight_line_analytic"]=straight_errors
    probes=np.array([[.3,0,0],[.3,0,math.pi]])
    values=interpolate(refs[-1],.05,probes)
    assert values[0]>values[1]
    result["short_game_probe_values_same_heading_head_on"]=values.tolist()
    assert np.all(refs[-1]["values"][.1]<=refs[-1]["values"][0.]+1e-12)
    # Both representations of the heading seam must interpolate identically.
    seam=states[:32].copy(); seam[:,2]=-math.pi
    left=interpolate(refs[-1],.1,seam); seam[:,2]=math.pi
    assert np.array_equal(left,interpolate(refs[-1],.1,seam))
    periodic=np.sin(np.linspace(-math.pi,math.pi,48,endpoint=False))[None,None,:]
    dm,dp=differences(periodic,2,2*math.pi/48,True)
    assert np.isfinite(dm).all() and np.isfinite(dp).all()
    if upstream: result["pinned_upstream_max_abs"]=check_upstream(c,upstream)
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config",default=str(Path(__file__).parent/"configs/cpu.json"))
    ap.add_argument("--out",required=True); ap.add_argument("--upstream")
    a=ap.parse_args()
    result=checks(json.loads(Path(a.config).read_text()),a.upstream)
    path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
