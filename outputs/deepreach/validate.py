"""Independent numerical validation; none of these labels enter PINN training."""
import argparse
import copy
import csv
import json
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from deepreach import dynamics, hamiltonian, load_checkpoint, optimal_control, optimal_disturbance, residual, target, value_grad
from reference import interpolate, save_reference, solve


def predict(model,q):
    with torch.no_grad():
        return np.concatenate([model(torch.tensor(a,dtype=torch.float32)).numpy() for a in np.array_split(q,max(1,math.ceil(len(q)/8192)))])


def error(a,b):
    d=a-b
    return dict(mae=float(np.mean(np.abs(d))),rmse=float(np.sqrt(np.mean(d*d))),max_abs=float(np.max(np.abs(d))))


def classification(a,b):
    unsafe=a<=0; truth=b<=0
    return dict(iou=float(np.sum(unsafe&truth)/max(1,np.sum(unsafe|truth))),
                disagreement_fraction=float(np.mean(unsafe!=truth)),
                false_safe_fraction_of_reference_unsafe=float(np.sum(~unsafe&truth)/max(1,np.sum(truth))),
                false_safe_fraction_of_all=float(np.mean(~unsafe&truth)),
                false_unsafe_fraction_of_reference_safe=float(np.sum(unsafe&~truth)/max(1,np.sum(~truth))),
                reference_unsafe_count=int(truth.sum()),total_count=int(len(a)))


def mechanical_checks(model,c):
    torch.manual_seed(12345)
    q=torch.rand(128,4,dtype=torch.float64)*torch.tensor([c["horizon"],1.2,1.2,2*math.pi],dtype=torch.float64)+torch.tensor([0,-.6,-.6,-math.pi],dtype=torch.float64)
    md=copy.deepcopy(model).double()
    v,dv=value_grad(md,q)
    fd=[]; eps=1e-5
    with torch.no_grad():
        for k in range(4):
            off=torch.zeros_like(q); off[:,k]=eps
            fd.append((md(q+off)-md(q-off))/(2*eps))
    fd=torch.stack(fd,1)
    # Independent explicit normalized-input chain rule.
    z=(q/md.scales).detach().requires_grad_(True)
    raw=md.raw(z)
    dz=torch.autograd.grad(raw.sum(),z)[0]
    chain=c["value_scale"]*dz/md.scales
    s=q[:,1:]; p=torch.randn(128,3,dtype=torch.float64)
    controls=torch.linspace(-c["turn"],c["turn"],33,dtype=torch.float64)
    # Explicit max_u min_d of p.f, with both interval endpoints included.
    flows=dynamics(s[:,None,None,:],controls[None,:,None],controls[None,None,:],c)
    brute=(flows*p[:,None,None,:]).sum(-1).min(dim=2).values.max(dim=1).values
    ham=hamiltonian(s,p,c)
    control=optimal_control(s,p,c); disturbance=optimal_disturbance(p,c)
    selected=(dynamics(s,control,disturbance,c)*p).sum(-1)
    result=dict(autodiff_fd_max_abs=float((fd-dv).abs().max()),chain_rule_max_abs=float((chain-dv).abs().max()),
                hamiltonian_brute_max_abs=float((ham-brute).abs().max()),
                optimal_control_max_abs=float((ham-selected).abs().max()))
    assert result["autodiff_fd_max_abs"]<1e-5
    assert result["chain_rule_max_abs"]<1e-10
    assert result["hamiltonian_brute_max_abs"]<1e-10
    assert result["optimal_control_max_abs"]<1e-10
    return result


def comparison_region(c):
    interior=c["comparison_half_width"]
    # Rotating-frame u terms preserve radius; |r_dot| <= ve+vp = 2v.
    # Every trajectory from this comparison square lies inside the circle of
    # radius sqrt(2)*interior+2*v*T. Fit that circle in the spatial box.
    radius_bound=math.sqrt(2)*interior+2*c["speed"]*c["horizon"]
    if interior <= 0 or radius_bound >= c["domain"]:
        raise ValueError("Enlarge domain for the Air3D comparison region's dependency bound")
    return interior, radius_bound


def straight_line_values(states,t,c):
    bx=c["speed"]*(np.cos(states[:,2])-1)
    by=c["speed"]*np.sin(states[:,2])
    denominator=bx*bx+by*by
    closest=np.clip(-(states[:,0]*bx+states[:,1]*by)/np.maximum(denominator,1e-30),0,t)
    return np.hypot(states[:,0]+closest*bx,states[:,1]+closest*by)-c["radius"]


def reference_checks(c,states,times):
    clock=time.perf_counter()
    refs=[]
    for n,nh in [(65,48),(97,72),(129,96)]:
        print(f"Reference: solving {n} x {n} x {nh} through {times[-1]}s",flush=True)
        refs.append(solve(c,n,nh,times))
    refinement={}
    for t in times[1:]:
        vals=[interpolate(r,t,states) for r in refs]
        refinement[str(t)]={"65_to_97":error(vals[0],vals[1]),"97_to_129":error(vals[1],vals[2]),
                            "classification_97_to_129":classification(vals[1],vals[2])}
        assert refinement[str(t)]["97_to_129"]["mae"] < refinement[str(t)]["65_to_97"]["mae"]
    # Same dx and heading, farther spatial boundaries; no neural model involved.
    print("Reference: checking expanded spatial domain at matching dx and dt",flush=True)
    expanded=solve(c,193,96,times,domain=1.5*c["domain"])
    matched=solve(c,129,96,times,dt_limit=expanded["dtmax"])
    boundary={str(t):error(interpolate(matched,t,states),interpolate(expanded,t,states)) for t in times[1:]}
    static=dict(c,speed=0.,turn=0.)
    frozen=solve(static,33,24,times)
    frozen_err=float(np.max(np.abs(frozen["values"][times[-1]]-frozen["values"][0.])))
    assert frozen_err==0.
    # Analytic closest relative separation when neither drone can turn.
    straight=dict(c,turn=0.)
    exact={}
    for t in times[1:]:
        exact[t]=straight_line_values(states,t,c)
    print("Reference: checking no-turn analytic solution",flush=True)
    st_coarse=solve(straight,65,48,times); st_fine=solve(straight,129,96,times)
    straight_errors={str(t):{"coarse":error(interpolate(st_coarse,t,states),exact[t]),"fine":error(interpolate(st_fine,t,states),exact[t])} for t in times[1:]}
    assert all(e["fine"]["mae"]<e["coarse"]["mae"] for e in straight_errors.values())
    # Equal heading has zero relative drift; head-on heading closes at 2v.
    # Check this in the no-turn case, independently of the Air3D game outcome.
    probes=np.array([[.4,0,0],[.4,0,math.pi]])
    probe_values=interpolate(st_fine,times[-1],probes)
    assert probe_values[0] > probe_values[1]+.05
    assert probe_values[1]<.15
    # The value must remain <= the initial target; BRT cannot shrink.
    obstacle=float(np.max(refs[-1]["values"][times[-1]]-refs[-1]["values"][0.]))
    assert obstacle<=1e-12
    assert max(x["max_abs"] for x in boundary.values())<.005
    return refs[-1],dict(refinement=refinement,boundary_sensitivity=boundary,frozen_max_abs=frozen_err,
                        straight_line_analytic=straight_errors,sign_probe_values=probe_values.tolist(),obstacle_violation=obstacle,
                        grids=[[65,65,48],[97,97,72],[129,129,96]],dtmax=refs[-1]["dtmax"],
                        cfl=refs[-1]["cfl"],seconds=time.perf_counter()-clock)


def resume_check(c,out):
    from deepreach import train  # This optional check DOES train; never called by preflight.
    tiny=dict(c,width=16,samples=64,terminal_samples=8,pretrain_steps=2,curriculum_steps=4,log_every=6,save_every=6)
    # This short test checks actual optimizer+RNG restart, not just predictions.
    a=train(tiny,out/"resume_test_continuous")
    train(tiny,out/"resume_test_split",stop_after=4)
    b=train(tiny,out/"resume_test_split",resume=out/"resume_test_split/checkpoint.pt")
    diff=max(float((x-y).abs().max()) for x,y in zip(a.parameters(),b.parameters()))
    assert diff==0
    return dict(split_resume_parameter_max_abs=diff,split_after=4,total_steps=6)


def evaluate(checkpoint,out,check_training_resume=False):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    model,ck=load_checkpoint(checkpoint); c=ck["config"]
    torch.set_num_threads(c["threads"]); model.eval()
    rng=np.random.default_rng(20261019)
    interior,dependency_radius=comparison_region(c)
    states=rng.uniform([-interior,-interior,-math.pi],[interior,interior,math.pi],size=(24000,3))
    times=[0.,c["horizon"]/2,c["horizon"]]
    ref,reference_metrics=reference_checks(c,states,times)
    save_reference(ref,out/"reference_fine.npz")
    print("Comparison: evaluating held-out values and physics diagnostics",flush=True)
    metrics=dict(checkpoint=str(checkpoint),completed_steps=ck["step"],training_seconds=ck["elapsed_seconds"],
                 terminal_weight=ck["terminal_weight"],interior_half_width=interior,dependency_radius_bound=dependency_radius,heldout_seed=20261019,
                 mechanical=mechanical_checks(model,c),reference=reference_metrics,comparisons={})
    for t in times:
        q=np.column_stack([np.full(len(states),t),states])
        a=predict(model,q); b=interpolate(ref,t,states)
        metrics["comparisons"][str(t)]={**error(a,b),**classification(a,b),
            "outside_reference_margin_0.02":classification(a[np.abs(b)>.02],b[np.abs(b)>.02])}
    # Separate fresh held-out physics and terminal samples over full training box.
    q=rng.uniform([0,-c["domain"],-c["domain"],-math.pi*c["angle_factor"]],
                  [c["horizon"],c["domain"],c["domain"],math.pi*c["angle_factor"]],size=(8192,4))
    r,v,_=residual(model,torch.tensor(q,dtype=torch.float32),c)
    ell=target(torch.tensor(q[:,1:],dtype=torch.float32),c)
    q[:,0]=0
    terminal=predict(model,q)-(np.linalg.norm(q[:,1:3],axis=1)-c["radius"])
    metrics["heldout"]={"pde_vi_mae":float(r.detach().abs().mean()),"pde_vi_p95":float(torch.quantile(r.detach().abs(),.95)),
                        "terminal_mae":float(np.abs(terminal).mean()),"terminal_max_abs":float(np.abs(terminal).max()),
                        "positive_obstacle_violation_mean":float((v-ell).detach().clamp_min(0).mean())}
    # Seam mismatch is diagnostic; baseline has no imposed periodic network feature.
    pairs=rng.uniform([0,-interior,-interior,0],[c["horizon"],interior,interior,0],size=(4096,4))
    pairs[:,3]=-math.pi; left=predict(model,pairs); pairs[:,3]=math.pi
    metrics["heldout"]["heading_seam_mae"]=float(np.abs(left-predict(model,pairs)).mean())
    reloaded,_=load_checkpoint(checkpoint)
    metrics["mechanical"]["reload_prediction_max_abs"]=float(np.abs(predict(model,q[:128])-predict(reloaded,q[:128])).max())
    assert metrics["mechanical"]["reload_prediction_max_abs"]==0
    metrics["resume_check"]=resume_check(c,out) if check_training_resume else {"status":"not run; requires --check-training-resume"}
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2))
    print("Comparison: saving metrics and plots",flush=True)
    plot_slices(model,c,ref,out,interior,times)
    plot_history(Path(checkpoint).parent/"history.csv",out)
    print(json.dumps(metrics,indent=2),flush=True)


def plot_slices(model,c,ref,out,interior,times):
    grid=np.linspace(-interior,interior,161)
    xx,yy=np.meshgrid(grid,grid,indexing="ij")
    headings=[0,math.pi/2,math.pi]
    fig,axs=plt.subplots(3,3,figsize=(11,10),layout="constrained")
    fig2,axs2=plt.subplots(3,3,figsize=(11,10),layout="constrained")
    fig3,axs3=plt.subplots(3,3,figsize=(11,10),layout="constrained")
    error_limit=1e-6
    for i,t in enumerate(times):
        for j,th in enumerate(headings):
            states=np.column_stack([xx.ravel(),yy.ravel(),np.full(xx.size,th)])
            a=predict(model,np.column_stack([np.full(xx.size,t),states])).reshape(xx.shape)
            b=interpolate(ref,t,states).reshape(xx.shape)
            ax=axs[i,j]; im=ax.pcolormesh(xx,yy,a,vmin=-.25,vmax=.6,cmap="viridis",shading="auto")
            ax.contour(xx,yy,b,levels=[0],colors=["white"],linewidths=2)
            ax.contour(xx,yy,a,levels=[0],colors=["red"],linestyles="--",linewidths=1.5)
            ax.set_title(f"tau={t:.2f}s, heading={th/math.pi:.1f} pi")
            im2=axs2[i,j].pcolormesh(xx,yy,a-b,vmin=-.15,vmax=.15,cmap="coolwarm",shading="auto")
            error_limit=max(error_limit,float(np.max(np.abs(a-b))))
            axs2[i,j].set_title(f"tau={t:.2f}s, heading={th/math.pi:.1f} pi")
            im3=axs3[i,j].pcolormesh(xx,yy,b,vmin=-.25,vmax=.6,cmap="viridis",shading="auto")
            axs3[i,j].contour(xx,yy,b,levels=[0],colors="white")
            axs3[i,j].set_title(f"tau={t:.2f}s, heading={th/math.pi:.1f} pi")
            for axis in [ax,axs2[i,j],axs3[i,j]]:
                axis.set_aspect("equal"); axis.set_xlabel("x [m]"); axis.set_ylabel("y [m]")
    fig.suptitle("PINN value [m]; grid zero contour white, PINN zero contour red dashed")
    fig.colorbar(im,ax=axs.ravel().tolist(),shrink=.6); fig.savefig(out/"value_and_brt_slices.png",dpi=160)
    fig2.suptitle("PINN minus numerical reference [m]")
    for axis in axs2.ravel():
        for collection in axis.collections: collection.set_clim(-error_limit,error_limit)
    fig2.colorbar(im2,ax=axs2.ravel().tolist(),shrink=.6); fig2.savefig(out/"error_slices.png",dpi=160)
    fig3.suptitle("Independent grid reference value [m]")
    fig3.colorbar(im3,ax=axs3.ravel().tolist(),shrink=.6); fig3.savefig(out/"reference_slices.png",dpi=160)
    plt.close("all")


def plot_history(path,out):
    with open(path) as f: rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(8,4),layout="constrained")
    for field in ["terminal_mae","pde_mae"]:
        selected=[r for r in rows if field!="pde_mae" or r["phase"]=="curriculum"]
        label="Terminal MAE [m]" if field=="terminal_mae" else "VI residual MAE (physics phase)"
        ax.semilogy([int(r["step"]) for r in selected],[max(1e-8,float(r[field])) for r in selected],label=label)
    starts=[int(r["step"]) for r in rows if r["phase"]=="curriculum"]
    if starts: ax.axvline(min(starts)-1,color="gray",linestyle="--",alpha=.6,label="Physics training begins")
    ax.set_xlabel("Training iteration"); ax.set_ylabel("Mean absolute batch diagnostic"); ax.legend(); ax.grid(alpha=.25)
    fig.savefig(out/"training_history.png",dpi=160); plt.close(fig)


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--checkpoint",required=True); p.add_argument("--out",required=True)
    p.add_argument("--check-training-resume",action="store_true",help="Also run a tiny optimizer restart test; DOES train")
    a=p.parse_args(); evaluate(a.checkpoint,a.out,a.check_training_resume)
