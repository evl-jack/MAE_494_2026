"""Independent first-order local Lax-Friedrichs Air3D HJI obstacle solver.

Solves V_tau=H subject to V<=l. Heading periodic, x/y constant ghost cells.
For V_tau=H, numerical viscosity has POSITIVE sign. No neural code imported.
"""
import math
import numpy as np
from scipy.interpolate import RegularGridInterpolator


def differences(v, axis, spacing, periodic):
    if periodic:
        return (v-np.roll(v,1,axis))/spacing, (np.roll(v,-1,axis)-v)/spacing
    pads = [(0,0)]*v.ndim; pads[axis] = (1,1)
    p = np.pad(v,pads,mode="edge")
    return np.diff(p,axis=axis).take(range(v.shape[axis]),axis=axis)/spacing, np.diff(p,axis=axis).take(range(1,v.shape[axis]+1),axis=axis)/spacing


def grid_hamiltonian(xx, yy, psi, p, c):
    """Independent NumPy expression; no PINN implementation imported."""
    px, py, pp = p
    return (c["speed"]*((np.cos(psi)-1)*px+np.sin(psi)*py)
            +c["turn"]*np.abs(yy*px-xx*py-pp)-c["turn"]*np.abs(pp))


def dissipation_bounds(xx, yy, psi, c):
    """Bounds on |dH/dp_i| over all allowed turns, including nonsmooth H."""
    return (np.abs(c["speed"]*(np.cos(psi)-1))+c["turn"]*np.abs(yy),
            np.abs(c["speed"]*np.sin(psi))+c["turn"]*np.abs(xx),
            2*c["turn"])


def solve(c,n=65,ntheta=48,times=None,domain=None,dt_limit=None):
    domain = c["domain"] if domain is None else domain
    times = [0,c["horizon"]/2,c["horizon"]] if times is None else list(times)
    if n < 3 or ntheta < 3 or not times or times[0] < 0 or np.any(np.diff(times) < 0):
        raise ValueError("Need grids >=3 and sorted nonnegative times")
    x=np.linspace(-domain,domain,n); th=np.linspace(-math.pi,math.pi,ntheta,endpoint=False)
    dx=x[1]-x[0]; dh=2*math.pi/ntheta
    xx,yy=np.meshgrid(x,x,indexing="ij")
    ell=np.broadcast_to((np.hypot(xx,yy)-c["radius"])[...,None],(n,n,ntheta)).copy()
    v=ell.copy(); psi=th[None,None,:]
    alphas=dissipation_bounds(xx[...,None],yy[...,None],psi,c)
    # Global dt obeys local sum alpha_i/dx_i <= 1 for monotonic Euler step.
    rate=np.max((alphas[0]+alphas[1])/dx+alphas[2]/dh)
    dtmax=.8/rate if rate else float("inf")
    if dt_limit is not None:
        if dt_limit <= 0: raise ValueError("dt_limit must be positive")
        dtmax=min(dtmax,dt_limit)
    output={}; t=0.; steps=0
    for end in times:
        while t < end-1e-12:
            dt=min(dtmax,end-t)
            derivatives=[differences(v,i,h,i==2) for i,h in enumerate([dx,dx,dh])]
            centered=[(dm+dp)/2 for dm,dp in derivatives]
            visc=sum(alpha*(dp-dm)/2 for alpha,(dm,dp) in zip(alphas,derivatives))
            rhs=grid_hamiltonian(xx[...,None],yy[...,None],psi,centered,c)+visc
            v=np.minimum(v+dt*rhs,ell)
            t+=dt; steps+=1
        output[float(end)]=v.copy()
    return dict(x=x,theta=th,values=output,dtmax=dtmax,cfl=.8,steps=steps,dx=dx,dtheta=dh)


def interpolate(ref,t,states):
    th=np.r_[ref["theta"],math.pi]
    val=ref["values"][float(t)]
    wrapped=states.copy(); wrapped[:,2]=(wrapped[:,2]+math.pi)%(2*math.pi)-math.pi
    return RegularGridInterpolator((ref["x"],ref["x"],th),np.concatenate([val,val[:,:,:1]],axis=2),bounds_error=True)(wrapped)


def save_reference(ref,path):
    times=np.array(list(ref["values"]))
    np.savez_compressed(path,x=ref["x"],theta=ref["theta"],times=times,values=np.stack(list(ref["values"].values())),dtmax=ref["dtmax"],cfl=ref["cfl"])
