# Adjoint-Based Topology Optimization of a Coolant Manifold Junction

Arizona State University · MAE 494 Design Optimization · Project 4

## 1. Summary

At Reynolds number 50, the optimized branch transition reduced fitted-wall pumping power by **4.84%** and increased the side outlet's share of inlet flow from **4.024% to 8.465%**. The adjoint was **60.48× faster** than serial finite differences, and the immersed KKT audit gave a projected stationarity residual of **1.369 × 10⁻⁸**. The main pipe and all ports stayed fixed. The raw Navier–Stokes reconstruction is the selected design because it passed the paired mesh screen and outperformed the Stokes-optimized geometry when both were evaluated with Navier–Stokes.

![Original, raw optimized, and smoothed junctions](https://raw.githubusercontent.com/evl-jack/Coolant_Manifold/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/assets/three_panel.png)

[Public interactive 3D viewer (pilot release)](https://evl-jack.github.io/Coolant_Manifold/) · [Technical appendix and checklist](Project%204%20Appendix.md) · [Final report and WebGL source](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/index.html) · [Numerical results](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/data/results.json) · [Optimization slide](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/optimization-slide.html)

## 2. Design and optimization problem

A coolant manifold divides flow between branches. The design goal was to reduce pumping power without starving the side outlet. The planar T-junction has a 20 × 4 mm main channel and an original 1 × 3 mm side branch centered at $x=10$ mm. The main channel and the side outlet collar $[9.5,10.5]\times[6,7]$ mm are fixed. Only $[8,12]\times[4,6]$ mm is editable. Its 0.25 mm cells give **128 independent, dimensionless densities** $m_i$, with $0\le m_i\le1$, zero representing solid and one fluid.

![Fixed passages and editable density grid](https://raw.githubusercontent.com/evl-jack/Coolant_Manifold/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/pilot/local/stage_03_beta_8/images/editable_brinkman_region.png)

For outward unit normal $n$, $Q_{\mathrm{side}}=\int_{\Gamma_s}u\cdot n\,ds$ and $Q_{\mathrm{in}}=-\int_{\Gamma_i}u\cdot n\,ds$. Define the net mechanical power across all three ports, side-flow fraction, and effective hydraulic resistance by

$$
P=-\int_{\Gamma_{\mathrm{ports}}}(p+\tfrac12\rho |u|^2)(u\cdot n)\,ds,\qquad
\eta=Q_{\mathrm{side}}/Q_{\mathrm{in}},\qquad R_{\mathrm{eff}}=P/Q_{\mathrm{in}}^2.
$$

Flow and power are per meter of out-of-plane depth, in m²/s and W/m. Resistance is in Pa·s/m². The discrete state $z=(u_h,p_h)$ satisfies $R(z,m)=0$. The optimization minimizes $f=P/P_{\mathrm{ref}}$ subject to the density bounds and

$$
g=(\eta_{\mathrm{ref}}-\eta)/0.001\le 0.
$$

Both reference values come from the original immersed design replayed at the same continuation stage. At $\beta=8$, $P_{\mathrm{ref}}=8.893614$ µW/m and $\eta_{\mathrm{ref}}=7.414738\%$. The floor is the original design's side delivery in the optimization model. The original fitted-wall share of 4.024% comes from a separate evaluation. The problem has one independent PDE performance inequality. Fluid area and maximum wall turn measured with 0.25 mm arc-length secants are reported as diagnostics.

## 3. Flow model and density map

The analysis assumes steady, planar, incompressible, laminar water flow with $\rho=998.2$ kg/m³ and $\mu=0.001002$ Pa·s. The prescribed parabolic inlet has mean velocity 0.01255 m/s and $Q_{\mathrm{in}}=5.0190\times10^{-5}$ m²/s. Walls are no-slip and both outlets have zero total traction. The model includes momentum transport and omits heat transfer.

For test velocity $v$ and pressure $q_p$, the incompressible Navier–Stokes–Brinkman weak form is

$$
\int_\Omega \left[2\mu D(u):D(v)+\rho((u\cdot\nabla)u)\cdot v+
\alpha u\cdot v-p\nabla\cdot v-q_p\nabla\cdot u\right]\,dA=0,
\qquad D(u)=\tfrac12(\nabla u+\nabla u^{T}).
$$

The in-house solver uses triangular Taylor–Hood elements (P2 velocity, P1 pressure) and damped Newton with both terms of the convection derivative. The optimization mesh has 2,848 triangles and 13,359 DOFs. The fitted-wall checks use independent meshes.

An anchored Helmholtz filter of radius 0.5 mm produces $\tilde\gamma$. On editable cells $E$, $H_{EE}\tilde\gamma_E=M_E m_E-H_{EF}m_{0,F}$, with $H=M+r_f^2K$ and fixed anchors $F$. A smooth Heaviside projection $\Pi_\beta$ at 0.5 produces $\bar\gamma$. Cellwise drag uses

$$
\alpha(\bar\gamma)=10^5\frac{0.1(1-\bar\gamma)}{0.1+\bar\gamma}\ \mathrm{kg/(m^3\,s)}.
$$

The projection sharpens through $\beta=0,2,8$. The $\bar\gamma=0.5$ contour gives the raw physical wall inside the design region. Its fitted-wall re-solve imposes impermeable no-slip walls directly.

## 4. Verification

The recovered FEM benchmarks below are historical. The final fixed-pipe study separately verified the design gradients and tested mesh sensitivity.

| Test | Expected result | Measured result |
|---|---|---|
| Element basis | Kronecker interpolation, partition of unity, zero gradient sum | Maximum defect $1.11\times10^{-16}$ |
| Exact straight pipe | Unit nondimensional flux | Relative error $8.22\times10^{-15}$ |
| Rotated pipe | Unit flux after rotation | Relative error $2.55\times10^{-15}$ |
| Global conservation | Zero net flux defect | Maximum $3.48\times10^{-14}$ across three pipe cases |
| Manufactured mesh convergence | Orders above 2.6 for velocity and 1.7 for pressure | 3.097 and 3.422 on the final interval |
| Nonlinear manufactured case | Velocity error below $10^{-2}$, tangent error below $10^{-7}$ | $1.70\times10^{-3}$ and $1.08\times10^{-11}$ |
| Uniform Brinkman channel | Analytical flux 0.29057005 | Relative error $2.15\times10^{-6}$ |
| Layered Brinkman channel | Analytical flux 0.17337432 at $\alpha=1600$ | Relative error $1.02\times10^{-6}$ |

For example, exact planar channel flux is $GH^3/(12\mu)$ for pressure-gradient magnitude $G$ and channel height $H$. The nondimensional benchmark uses $G=12$, $H=1$, and $\mu=1$. [Raw benchmark record](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/historical/baseline_verification.json) · [Verification code](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/source/project4_fem/verify.py)

## 5. Discrete adjoint and gradient checks

Differentiating $R(z,m)=0$ gives $R_z\,dz/dm=-R_m$. For either response $F=f,g$, solve $R_z^\top\lambda_F=\nabla_z F$ and compute $\nabla_m F=F_m-R_m^\top\lambda_F$. With fixed ports, the direct term $F_m$ vanishes. The state variations are

$$
\begin{aligned}
\delta f &= \delta P/P_{\mathrm{ref}},\\
\delta P &=-\int_{\Gamma_{\mathrm{ports}}}
[(\delta p+\rho u\cdot\delta u)(u\cdot n)+(p+\tfrac12\rho|u|^2)(\delta u\cdot n)]\,ds,\\
\delta g &=-1000\,\delta Q_{\mathrm{side}}/Q_{\mathrm{in}}.
\end{aligned}
$$

The prescribed inlet fixes $\delta Q_{\mathrm{in}}=0$. The gradient propagates from the drag quadrature term through the cell transfer, drag interpolation, projection, and transpose of the anchored filter. A single converged state and two adjoint right-hand sides give both complete gradients.

| Check | Result |
|---|---|
| Directional finite differences | 15/15 passed using centered differences in the interior and second-order inward differences at bounds |
| Taylor remainders | 9/15 passed the initial order screen. All six flagged directions reached orders 2.001–2.006 on a larger-step follow-up |
| Full 128-variable centered gradients | Max absolute discrepancies $2.38\times10^{-12}$ for normalized power and $1.10\times10^{-12}$ for side fraction |
| Matched serial timing | 120.379 s for 257 forward solves versus 1.990 s for the adjoint procedure, **60.48× faster** |
| Scaling at 52,347 DOFs | From 32 to 512 controls, adjoint time went from 10.672 to 12.741 s and eight-worker finite-difference elapsed time from 40.339 to 395.261 s |

![Taylor remainder follow-up on the six flagged directions](https://raw.githubusercontent.com/evl-jack/Coolant_Manifold/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/adjoint-coordinate-evidence/adjoint_taylor_remainders.png)

[Full gradient checks and timing evidence](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/README.md) · [Adjoint derivation](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/source/project4_fem/project43_topology/verification/ADJOINT_METHOD.md)

## 6. MMA optimization and KKT audit

The Method of Moving Asymptotes started from the original sharp T density field and carried the selected design forward between projection stages. The run recorded 97 unique MMA evaluations. Objective and constraint scaling used the reference power and 0.001 side-flow fraction, respectively.

| $\beta$ | Original → selected power (µW/m depth) | Original → selected side share |
|---:|---:|---:|
| 0 | 8.922988 → 8.860219 | 7.064579% → 7.977077% |
| 2 | 8.914472 → 8.853471 | 7.175007% → 8.084346% |
| 8 | 8.893614 → 8.830644 | 7.414738% → 8.412628% |

At $\beta=8$, normalized power was 0.992920 and the scaled flow constraint improved from 0 to −9.978905. The side-flow floor had 0.997891 percentage points of slack and a zero multiplier. The audit found 49 variables at the lower bound, 73 at the upper bound, and six interior. Projected stationarity was $1.369\times10^{-8}$ against a $10^{-4}$ threshold. Primal, dual, and complementarity residuals were zero. This supports local first-order stationarity of the immersed problem.

![MMA objective and first-order optimality history](https://raw.githubusercontent.com/evl-jack/Coolant_Manifold/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/kkt-results/fixed_pipe_kkt_history.png)

## 7. Effect of convective inertia

The Stokes optimization removes convection from momentum while retaining the design map, inlet, power definition, and final side-flow floor. Its immersed optimum met that floor under Stokes (7.414742%), then fell below it under nonlinear evaluation (6.990948%). The Navier–Stokes optimum delivered 8.412628% in the same nonlinear immersed evaluation.

Using identical fitted-wall Navier–Stokes settings, the Navier–Stokes design consumed **3.06% less power** and delivered **6.516 percentage points more side flow** than the Stokes design. The Stokes design also delivered less side flow than the original. At this operating point, removing convection changed the selected geometry and reversed its effect on branch delivery. [Matched nonlinear evidence](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/nonlinear/README.md)

## 8. Fitted-wall results and design decision

All rows use the finest tested target spacing of 0.0625 mm and the same nonlinear evaluator.

| Geometry | Power (µW/m depth) | Resistance (Pa·s/m²) | Side flow | Area (mm²) | Max wall turn |
|---|---:|---:|---:|---:|---:|
| Original | 9.275934 | 3682.28 | 4.024206% | 83.000 | 90.00° |
| Raw Navier–Stokes | **8.827238** | **3504.17** | **8.464686%** | 85.507 | 54.68° |
| Smoothed Navier–Stokes (provisional) | 8.858017 | 3516.38 | 8.229312% | 85.458 | 55.56° |
| Stokes optimized | 9.105665 | 3614.69 | 1.948290% | 86.228 | 88.25° |

The original and raw optimized geometries passed the mesh screen across 0.25, 0.125 and 0.0625 mm. The screen allowed at most 0.5% power change and 0.020 percentage points of side-flow change on each successive refinement. The raw power saving of 0.448696 µW/m exceeded the paired mesh-sensitivity estimate of 0.011197 µW/m and combined energy residual of 0.001788 µW/m. The smoothed geometry missed the side-flow screen on the first refinement (0.02505 percentage points), so the raw reconstruction remains the primary candidate. [Mesh refinement evidence](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/mesh-results)

## 9. Limitations, AI use, and reproduction

The study establishes a planar hydraulic improvement at one flow rate. It does not establish cooling effectiveness, 3D performance, or global optimality. Fluid area and the outlet split changed together, so the fitted comparison cannot isolate the effect of wall rounding. Finite Brinkman resistance permits leakage. The three-dimensional viewer depicts the planar solution on an extrusion and includes a conceptual cylindrical interpretation.

ChatGPT assisted with formulation, study planning, interpretation, and writing. Codex assisted with FEM and adjoint implementation, verification scripts, run execution, plotting, and report assembly. The evidence includes exact-flow comparisons, finite-difference and Taylor checks, KKT diagnostics, and fitted-wall mesh refinement. It does not document which checks the team derived independently or a specific bug caught in the graded laminar solver.

From the [project repository](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/README.md), run **python rebuild_site.py** to regenerate the report, viewer geometry, and numerical JSON from archived outputs. The separate [pilot](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/pilot/README.md), [verification](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/verification/README.md), and [nonlinear study](https://github.com/evl-jack/Coolant_Manifold/blob/cc9ecd49d64b4a5ff143a331d62f67eab14adf3f/evidence/nonlinear/README.md) records provide inputs and run instructions. A full end-to-end CFD rerun has not been established. [Course specification](https://designinformaticslab.github.io/DesignOptimization2025/project4.html)
