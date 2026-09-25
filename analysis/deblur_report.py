"""Python translation of deblur_test.m, with report-only diagnostic improvements.

Same Gaussian periodic blur, resolutions, noise level, regularization and limits.
Use --reference-mat to validate on the exact inputs exported by deblur_report.m.
Standalone NumPy noise is reproducible but differs from MATLAB rng(1).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.io import loadmat
from scipy.sparse.linalg import LinearOperator, cg


def make_gaussian_transfer(n_rows, n_cols, sigma):
    y = np.arange(-(n_rows // 2), (n_rows + 1) // 2)
    x = np.arange(-(n_cols // 2), (n_cols + 1) // 2)
    X, Y = np.meshgrid(x, y)
    psf = np.exp(-(X**2 + Y**2) / (2 * sigma**2))
    psf /= psf.sum()
    return psf, np.fft.fft2(np.fft.ifftshift(psf))


def apply_blur_rgb(x, Hf):
    return np.fft.ifft2(Hf[:, :, None] * np.fft.fft2(x, axes=(0, 1)), axes=(0, 1)).real


def spectral_deblur_rgb(b, Hf, regularization):
    # regularization is MATLAB's lambda (lambda is a Python keyword).
    Xf = Hf.conj()[:, :, None] * np.fft.fft2(b, axes=(0, 1))
    Xf /= (np.abs(Hf)**2 + regularization)[:, :, None]
    return np.fft.ifft2(Xf, axes=(0, 1)).real


def clamp_image(x):
    return np.clip(x, 0, 1)


def cubic(x):
    """Keys cubic kernel used by MATLAB bicubic resizing."""
    x = np.abs(x)
    return np.where(x <= 1, 1.5*x**3 - 2.5*x**2 + 1,
                    np.where(x <= 2, -.5*x**3 + 2.5*x**2 - 4*x + 2, 0))


def resize_bicubic(image, shape):
    """Separable bicubic resize with antialiasing and symmetric boundaries.

    Pixel-center alignment and downsampling kernel scaling follow imresize.
    This is preprocessing, not a change to the reconstruction model.
    """
    out = image
    for axis, length in enumerate(shape):
        old = out.shape[axis]
        scale = length / old
        width = 4 / min(scale, 1)
        centers = (np.arange(length) + .5) / scale - .5
        left = np.floor(centers - width/2).astype(int)
        indices = left[:, None] + np.arange(int(np.ceil(width)) + 2)
        distances = centers[:, None] - indices
        weights = (scale*cubic(scale*distances) if scale < 1 else cubic(distances))
        weights /= weights.sum(axis=1, keepdims=True)
        # Symmetric extension includes the edge pixel, as MATLAB does.
        folded = indices % (2*old)
        folded = np.where(folded < old, folded, 2*old-1-folded)
        target_shape = list(out.shape)
        target_shape[axis] = length
        resized = np.zeros(target_shape, dtype=np.float64)
        broadcast = [1] * out.ndim
        broadcast[axis] = length
        for column in range(weights.shape[1]):
            resized += np.take(out, folded[:, column], axis=axis) * weights[:, column].reshape(broadcast)
        out = resized
    return out


def relative_gradient(rhs_energy, abs_rho, k):
    initial = rhs_energy.sum()
    return float(np.sqrt(np.sum(rhs_energy * abs_rho**(2*k))/initial)) if initial else 0.


def exact_gd_stop(rhs_energy, abs_rho, tolerance, maximum):
    if relative_gradient(rhs_energy, abs_rho, 0) <= tolerance:
        return 0, True
    if relative_gradient(rhs_energy, abs_rho, maximum) > tolerance:
        return maximum, False
    lo, hi = 0, maximum
    while hi-lo > 1:
        mid = (lo+hi)//2
        if relative_gradient(rhs_energy, abs_rho, mid) <= tolerance:
            hi = mid
        else:
            lo = mid
    return hi, True


def cg_channel(h_eig, rhs, tolerance, maximum):
    h = h_eig.ravel(order='F')
    rhs = rhs.ravel(order='F')
    operator = LinearOperator((h.size, h.size), matvec=lambda z: h*z, dtype=rhs.dtype)
    history = [float(np.linalg.norm(rhs))]
    def record(z):
        history.append(float(np.linalg.norm(rhs-h*z)))
    solution, info = cg(operator, rhs, x0=np.zeros_like(rhs), rtol=tolerance,
                        atol=0., maxiter=maximum, callback=record)
    residual = float(np.linalg.norm(rhs-h*solution))
    if len(history) > 1:
        history[-1] = residual
    initial = history[0]
    relres = residual/initial if initial else 0.
    return solution.reshape(h_eig.shape, order='F'), info, relres, np.array(history)


def save_figure(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def image_panel(images, titles, path, columns=3):
    rows = int(np.ceil(len(images)/columns))
    fig, axes = plt.subplots(rows, columns, figsize=(14, 4.5*rows), squeeze=False)
    for axis in axes.flat:
        axis.axis('off')
    for axis, image, title in zip(axes.flat, images, titles):
        axis.imshow(clamp_image(image))
        axis.set_title(title)
    save_figure(fig, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=Path(__file__).resolve().parents[1]/'Test_Image.jpg')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent/'results_python')
    parser.add_argument('--reference-mat', type=Path, help='Use MATLAB-exported observations for direct validation')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    target_width, analysis_width = 2048, 1080
    sigma2K, regularization, noise_std = 6., 1e-4, .001
    sigma = sigma2K*analysis_width/target_width
    gd_tolerance, max_gd_iterations = 1e-4, 20000
    cg_tolerance, max_cg_iterations = 1e-4, 500
    sigma_list = np.array([.35, .50, .70, 1., 1.3, 1.6, 2.])
    reference = None
    if args.reference_mat:
        reference = loadmat(args.reference_mat)
        xTrue2K, b2K = reference['xTrue2K'], reference['b2K']
        xTrue, b = reference['xTrue'], reference['b']
        provenance = 'MATLAB-exported inputs; shared-data solver validation'
    else:
        image = np.asarray(Image.open(args.image).convert('RGB'), dtype=np.float64)/255
        target_height = int(np.floor(image.shape[0]*target_width/image.shape[1]+.5))
        xTrue2K = resize_bicubic(image, (target_height, target_width))
        analysis_height = int(np.floor(target_height*analysis_width/target_width+.5))
        xTrue = resize_bicubic(xTrue2K, (analysis_height, analysis_width))
        rng = np.random.default_rng(1)
        _, Hf2K = make_gaussian_transfer(*xTrue2K.shape[:2], sigma2K)
        b2K = apply_blur_rgb(xTrue2K, Hf2K) + noise_std*rng.standard_normal(xTrue2K.shape)
        _, Hf = make_gaussian_transfer(*xTrue.shape[:2], sigma)
        b = apply_blur_rgb(xTrue, Hf) + noise_std*rng.standard_normal(xTrue.shape)
        provenance = 'Standalone Python; NumPy default_rng(1), not MATLAB noise'
    if xTrue.ndim != 3 or xTrue.shape[2] != 3 or xTrue2K.shape[2] != 3:
        raise ValueError('The experiment requires three RGB channels.')
    _, Hf2K = make_gaussian_transfer(*xTrue2K.shape[:2], sigma2K)
    _, Hf = make_gaussian_transfer(*xTrue.shape[:2], sigma)
    started = perf_counter()
    xDeblur2K = spectral_deblur_rgb(b2K, Hf2K, regularization)
    direct_time = perf_counter()-started
    eigH = np.abs(Hf)**2 + regularization
    lambda_min, lambda_max = float(eigH.min()), float(eigH.max())
    kappa = lambda_max/lambda_min
    alpha = 2/(lambda_max+lambda_min)
    eig_sorted = np.sort(eigH.ravel())
    indices = np.floor(np.linspace(1,eig_sorted.size,min(10000,eig_sorted.size))+.5).astype(int)-1
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(indices+1, eig_sorted[indices], '.')
    ax.set(xlabel='Eigenvalue index (one channel)', ylabel='Eigenvalue', title=f'D1: Hessian spectrum; kappa = {kappa:.1f}')
    ax.grid(True)
    save_figure(fig,args.output/'d1-spectrum.png')
    kappas, scaled = [], []
    for sigma_i in sigma_list:
        psf_i, Hf_i = make_gaussian_transfer(*xTrue.shape[:2], sigma_i)
        eigHi = np.abs(Hf_i)**2+regularization
        eig_scaled = eigHi/(np.sum(psf_i**2)+regularization)
        kappas.append(float(eigHi.max()/eigHi.min()))
        scaled.append(float(eig_scaled.max()/eig_scaled.min()))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(sigma_list,kappas,'o-',label='Original')
    ax.semilogy(sigma_list,scaled,'s--',label='Jacobi scaled')
    ax.set(xlabel='Gaussian sigma (pixels)',ylabel='Condition number',title='D2: Intrinsic conditioning')
    ax.legend(); ax.grid(True)
    save_figure(fig,args.output/'d2-conditioning.png')
    rho = 1-alpha*eigH
    rhsF = Hf.conj()[:, :, None]*np.fft.fft2(b, axes=(0,1))
    rhs_energy = np.sum(np.abs(rhsF)**2, axis=2)
    samples = np.unique(np.r_[0,np.floor(np.logspace(0,np.log10(max_gd_iterations),300)+.5),max_gd_iterations]).astype(int)
    relative_gd = np.array([relative_gradient(rhs_energy,np.abs(rho),int(k)) for k in samples])
    gd_iterations, gd_converged = exact_gd_stop(rhs_energy,np.abs(rho),gd_tolerance,max_gd_iterations)
    XgdF = rhsF/eigH[:, :, None]*(1-rho**gd_iterations)[:, :, None]
    xGD = np.fft.ifft2(XgdF,axes=(0,1)).real
    xCG = np.zeros_like(xTrue)
    histories, flags, relres, iterations = [], [], [], []
    for c in range(3):
        XcgF, info, residual, history = cg_channel(eigH,rhsF[:, :, c],cg_tolerance,max_cg_iterations)
        xCG[:, :, c] = np.fft.ifft2(XcgF).real
        histories.append(history); flags.append(int(info)); relres.append(residual)
        iterations.append(len(history)-1)
        print(f'Channel {c+1}: iterations={iterations[-1]}, scipy_info={info}, relres={residual:.8e}',flush=True)
    padded = np.stack([np.pad(h,(0,max(map(len,histories))-len(h)),mode='edge') for h in histories])
    cg_rgb = np.sqrt(np.sum(padded**2,axis=0))
    cg_rgb = cg_rgb/cg_rgb[0] if cg_rgb[0] else np.zeros_like(cg_rgb)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogy(samples,relative_gd,label='GD, all RGB')
    ax.semilogy(np.arange(cg_rgb.size),cg_rgb,label='CG, all RGB (stopped channels held fixed)')
    ax.axhline(gd_tolerance,color='gray',linestyle=':',label='Tolerance')
    ax.set(xlabel='Iteration',ylabel='Relative RGB gradient / residual',title='D3 / D4: Same-channel comparison')
    ax.legend(); ax.grid(True)
    fig.tight_layout()
    fig.savefig(args.output/'convergence-rgb.png',dpi=150)
    ax.set_xlim(0,100)
    ax.set_title('D3 / D4: First 100 iterations (same RGB metric)')
    save_figure(fig,args.output/'convergence-early.png')
    image_panel([xTrue2K,b2K,xDeblur2K],['Reference (resized)','Blurred + noise','Direct Fourier reconstruction'],args.output/'full-comparison.png')
    image_panel([xTrue,b,xGD,xCG],['Reference','Blurred + noise',f'GD: {gd_iterations}; converged={gd_converged}',f'CG: max {max(iterations)} iterations'],args.output/'analysis-comparison.png',2)
    def image_error(x, truth):
        return float(np.linalg.norm((clamp_image(x)-truth).ravel())/np.linalg.norm(truth.ravel()))
    results = dict(provenance=provenance, regularization=regularization, sigma=sigma, sigma2K=sigma2K,
                   noiseStd=noise_std, analysisSize=list(xTrue.shape), fullSize=list(xTrue2K.shape),
                   lambdaMin=lambda_min,lambdaMax=lambda_max,kappa=kappa,alpha=alpha,
                   gdTolerance=gd_tolerance,maxGDIterations=max_gd_iterations,gdIterations=gd_iterations,
                   gdConverged=gd_converged,gdRelativeGradient=relative_gradient(rhs_energy,np.abs(rho),gd_iterations),
                   cgTolerance=cg_tolerance,maxCGIterations=max_cg_iterations,cgIterationsEachChannel=iterations,
                   cgScipyInfo=flags,cgRelativeResiduals=relres,cgFinalRGB=float(cg_rgb[-1]),
                   errorBlur=image_error(b,xTrue),errorGD=image_error(xGD,xTrue),errorCG=image_error(xCG,xTrue),
                   error2K=image_error(xDeblur2K,xTrue2K),directSolveTime=direct_time,
                   sigmaList=sigma_list.tolist(),kappaOriginal=kappas,kappaJacobi=scaled,
                   iterationSamples=samples.tolist(),relativeGradientGD=relative_gd.tolist(),cgHistoryRGB=cg_rgb.tolist())
    if reference is not None:
        results['matlabComparison'] = {
            'transferMaxAbsDifference':float(np.max(np.abs(Hf-reference['Hf']))),
            'gdMaxAbsDifference':float(np.max(np.abs(xGD-reference['xGD']))),
            'cgMaxAbsDifference':float(np.max(np.abs(xCG-reference['xCG']))),
            'directMaxAbsDifference':float(np.max(np.abs(xDeblur2K-reference['xDeblur2K'])))}
    (args.output/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in results.items() if k not in ('iterationSamples','relativeGradientGD','cgHistoryRGB')},indent=2))


if __name__ == '__main__':
    main()
