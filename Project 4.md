# Adjoint-Based Toplology opttimization of a Coolant FLow Manifold segment


### PDE-Constrained Design Optimization Using Navier–Stokes Equations and Brinkman Penalization

Arizona State University  
Design Optimization — Project 4

---


## Summary

Efficient coolant distribution is an important consideration in liquid-cooled engineering systems. Conventional manifold junctions can introduce abrupt changes in flow direction, increasing hydraulic losses and limiting coolant delivery to individual branches.

This project investigates the use of PDE-constrained topology optimization to improve the geometry of a coolant manifold junction. A custom finite element solver was developed to solve the steady incompressible Navier–Stokes equations, incorporating Brinkman penalization to represent a continuous distribution of fluid and solid material.

Using 128 independent density variables, discrete adjoint sensitivities, and the Method of Moving Asymptotes (MMA), the junction geometry was optimized to minimize pumping power while maintaining the required side-outlet flow.

The resulting design was evaluated using fitted-wall simulations, sensitivity verification, mesh-convergence studies, and Karush–Kuhn–Tucker (KKT) optimality conditions. A separate Stokes optimization was conducted to investigate the influence of nonlinear convective inertia on the final design.

The optimized Navier–Stokes geometry achieved a **4.84% reduction in pumping power while more than doubling coolant delivery to the side outlet.**


### Key Results

| Performance Metric | Original | Optimized | Improvement |
|---|---:|---:|---:|
| Pumping power (µW/m depth) | 9.2759 | 8.8272 | 4.84% reduction |
| Hydraulic resistance (Pa·s/m²) | 3682.28 | 3504.17 | 4.84% reduction |
| Side-outlet flow fraction | 4.024% | 8.465% | 110.3% increase |
| Maximum wall turning angle | 90.00° | 54.68° | 39.25% reduction |
| Fluid area (mm²) | 83.000 | 85.507 | 3.02% increase |

### Optimization and Numerical Achivements

| Metric | Result |
|---|---:|
| Independent design variables | 128 |
| Reynolds number | 50 |
| Adjoint speedup over finite differences | 60.48× |
| Projected KKT stationarity residual | 1.369 × 10⁻⁸ |
| Pumping-power reduction compared with Stokes-optimized design | 3.06% |
| Finest analysis mesh spacing | 0.0625 mm |

## 2. Engineering Motivation and Problem Definition

### 2.1 Engineering Motivation

Liquid cooling is used in applications such as data centers, high-performance computing, electric vehicles, and industrial thermal management systems.

A coolant manifold distributes fluid from a primary supply channel to individual cooling branches. The geometry of these connections influences the hydraulic resistance, pumping-power requirements, and distribution of coolant throughout the system.

Conventional T-junctions contain abrupt geometric transitions that can contribute to flow separation, recirculation, and additional hydraulic losses.

Traditional manifold design typically relies on predefined geometric parameters, such as channel widths, branch diameters, and fillet radii. Although effective, these approaches restrict the range of geometries that can be discovered.

This project investigates whether density-based topology optimization can automatically discover a more effective junction geometry without prescribing its final shape.

### 2.2 Engineering Objectives

The primary engineering objectives are to:

- Reduce the pumping power required to transport coolant.
- Maintain or improve coolant delivery to the side outlet.
- Reduce abrupt geometric transitions.
- Preserve the dimensions of the main pipe and connecting ports.
- Develop an efficient gradient-based optimization framework capable of handling a large number of design variables.

Wall smoothness is evaluated as a geometric performance metric rather than an explicitly enforced optimization constraint.

### 2.3 Original Manifold Geometry

The computational model consists of a two-dimensional planar manifold containing one inlet and two outlets.

The main channel is a straight rectangular passage, while the side outlet extends perpendicular to the primary flow direction.

| Geometric Parameter | Value |
|---|---:|
| Main channel length | 20 mm |
| Main channel height | 4 mm |
| Side outlet width | 1 mm |
| Side branch height | 3 mm |
| Side branch center | x = 10 mm |
| Original fluid area | 83 mm² |
| Number of inlets | 1 |
| Number of outlets | 2 |

The original geometry contains sharp 90-degree transitions between the main channel and the side branch.

<!-- Insert dimensioned original geometry figure here. -->

*Figure 2. Original planar coolant manifold geometry and port dimensions.*

### 2.4 Design Domain

The optimization is restricted to a rectangular region connecting the main channel to the side outlet.

The main channel and side-outlet collar remain fixed throughout the optimization.

The fixed main channel is defined as:

$$
\Omega_{\mathrm{main}}
=
[0,20]\times[0,4]
$$

The fixed side-outlet collar is defined as:

$$
\Omega_{\mathrm{collar}}
=
[9.5,10.5]\times[6,7]
$$

The editable design region is defined as:

$$
\Omega_d
=
[8,12]\times[4,6]
$$

All dimensions are expressed in millimeters.

The design region has a total area of:

$$
A_d = 4(2) = 8\ \mathrm{mm}^2
$$

The region is discretized into square density cells with a side length of 0.25 mm.

The total number of independent design variables is therefore:

$$
N_d
=
\frac{4}{0.25}
\frac{2}{0.25}
=
128
$$

<!-- Insert design-domain and density-grid figure here. -->

*Figure 3. Fixed fluid regions and editable Brinkman density design domain.*

### 2.5 Design Philosophy

The main channel is intentionally excluded from the optimization domain to prevent the optimizer from introducing unwanted restrictions, downstream contractions, or unnecessary modifications to the primary flow passage.

Only the transition between the main channel and the side outlet is optimized.

Unlike conventional shape optimization, the final junction geometry is not restricted to a predefined circular fillet, spline, or parametric curve.

Instead, the optimizer controls a distributed density field that determines the local resistance to fluid motion.

The final geometry is reconstructed from the optimized density field.

### 2.6 Scope and Assumptions

To maintain a computationally manageable optimization problem, the following assumptions are adopted:

- Steady-state fluid flow.
- Two-dimensional planar geometry.
- Incompressible Newtonian fluid.
- Laminar flow.
- Constant fluid density and dynamic viscosity.
- Prescribed inlet flow.
- Rigid, stationary channel walls.
- No-slip conditions at impermeable walls.
- Zero total traction at both outlets.
- Reynolds number of 50.
- Isothermal flow without thermal transport.

The investigation focuses on hydraulic performance rather than heat-transfer performance.

Although the intended engineering application is liquid cooling, temperature distributions and cooling effectiveness are not directly calculated.

The three-dimensional cylindrical manifold displayed on the website represents a conceptual engineering interpretation of the optimized planar geometry.

All quantitative performance results are obtained from the two-dimensional numerical model.


## 3. Mathematical Optimization Formulation

### 3.1 Design Variables

The design variables represent the distribution of fluid and solid material within the editable transition region.

The design vector is defined as:

$$
\mathbf{m}
=
\begin{bmatrix}
m_1 & m_2 & \cdots & m_{128}
\end{bmatrix}^{T}
$$

where each design variable satisfies:

$$
0 \leq m_i \leq 1
$$

The density variables have the following physical interpretation:

| Density | Material Interpretation |
|---|---|
| $m_i = 0$ | Solid material |
| $0 < m_i < 1$ | Intermediate porous material |
| $m_i = 1$ | Fluid region |

The density variable represents the numerical material distribution and should not be confused with the physical mass density of the fluid.

The intermediate density values allow the optimization problem to remain differentiable.

The main channel and side-outlet collar remain fixed fluid regions and are excluded from the independent design vector.

### 3.2 State Variables

The fluid state is described by the velocity and pressure fields:

$$
\mathbf{u}(x,y)
=
\begin{bmatrix}
u_x(x,y)\\
u_y(x,y)
\end{bmatrix}
$$

$$
p=p(x,y)
$$

After finite element discretization, the complete state vector is written as:

$$
\mathbf{z}
=
\begin{bmatrix}
\mathbf{u}_h\\
\mathbf{p}_h
\end{bmatrix}
$$

The state variables are determined implicitly by the governing fluid equations:

$$
\mathbf{R}(\mathbf{z},\mathbf{m})=\mathbf{0}
$$

where $\mathbf{R}$ represents the assembled discrete Navier–Stokes and Brinkman residual.

Changing the material distribution changes the resistance to fluid motion, which subsequently changes the velocity and pressure fields.

Therefore:

$$
\mathbf{z}=\mathbf{z}(\mathbf{m})
$$

The objective and flow constraint are functionals of this computed fluid state.

### 3.3 Volumetric Flow Rate

The volumetric flow rate through a boundary is obtained by integrating the normal velocity:

$$
Q_{\Gamma}
=
\int_{\Gamma}
\mathbf{u}\cdot\mathbf{n}\,d\Gamma
$$

where $\mathbf{n}$ is the outward unit normal vector.

Because the analysis is two-dimensional, the calculated flow rates are expressed per unit out-of-plane depth, with units of $\mathrm{m^2/s}$.

The positive inlet flow rate is defined as:

$$
Q_{\mathrm{in}}
=
-\int_{\Gamma_{\mathrm{in}}}
\mathbf{u}\cdot\mathbf{n}\,d\Gamma
$$

The main-outlet flow rate is:

$$
Q_{\mathrm{main}}
=
\int_{\Gamma_{\mathrm{main}}}
\mathbf{u}\cdot\mathbf{n}\,d\Gamma
$$

The side-outlet flow rate is:

$$
Q_{\mathrm{side}}
=
\int_{\Gamma_{\mathrm{side}}}
\mathbf{u}\cdot\mathbf{n}\,d\Gamma
$$

Conservation of mass requires:

$$
Q_{\mathrm{in}}
=
Q_{\mathrm{main}}+Q_{\mathrm{side}}
$$

### 3.4 Objective Function: Pumping Power

The primary objective is to minimize the mechanical pumping power required to transport fluid through the manifold.

The mechanical energy per unit fluid volume consists of pressure energy and kinetic energy:

$$
e_{\mathrm{mech}}
=
p+\frac{1}{2}\rho_f
\lVert\mathbf{u}\rVert^2
$$

The corresponding mechanical port power is:

$$
P(\mathbf{m})
=
-\int_{\Gamma_{\mathrm{ports}}}
\left(
p+\frac{1}{2}\rho_f
\lVert\mathbf{u}\rVert^2
\right)
(\mathbf{u}\cdot\mathbf{n})
\,d\Gamma
$$

where:

- $p$ is the fluid pressure.
- $\rho_f$ is the physical fluid mass density.
- $\mathbf{u}$ is the fluid velocity.
- $\mathbf{n}$ is the outward unit normal.
- $\Gamma_{\mathrm{ports}}$ contains the inlet and both outlets.

Equivalently:

$$
P=P_{\mathrm{in}}
-P_{\mathrm{main}}
-P_{\mathrm{side}}
$$

where each individual port contribution uses the corresponding positive flow orientation.

The kinetic-energy contribution is retained because the inlet and outlet velocity distributions are not necessarily identical.

For the planar numerical model, pumping power is reported per unit out-of-plane depth:

$$
[P]=\mathrm{W/m}
$$

The normalized objective is:

$$
f(\mathbf{m})
=
\frac{P(\mathbf{m})}{P_{\mathrm{ref}}}
$$

where $P_{\mathrm{ref}}$ is the fixed reference-power normalization used by the optimization implementation.

Normalization improves numerical scaling without changing the location of the optimum.

### 3.5 Hydraulic Resistance

Effective hydraulic resistance provides an additional measure of the energy required to transport fluid through the manifold.

It is defined using the mechanical-power functional:

$$
R_{\mathrm{eff}}
=
\frac{P}{Q_{\mathrm{in}}^2}
$$

This definition is consistent with the conventional hydraulic relationship:

$$
P=\Delta p\,Q
$$

$$
R=\frac{\Delta p}{Q}
$$

when the mechanical-power requirement reduces to pressure-drop work.

For the two-dimensional model:

$$
[R_{\mathrm{eff}}]
=
\mathrm{Pa\cdot s/m^2}
$$

Since the inlet flow rate remains fixed throughout the optimization, minimizing pumping power is equivalent to minimizing the effective hydraulic resistance defined above.

### 3.6 Outlet-Flow Distribution

The side-outlet flow fraction is defined as:

$$
\eta_{\mathrm{side}}(\mathbf{m})
=
\frac{Q_{\mathrm{side}}(\mathbf{m})}
{Q_{\mathrm{in}}}
$$

Similarly, the main-outlet flow fraction is:

$$
\eta_{\mathrm{main}}(\mathbf{m})
=
\frac{Q_{\mathrm{main}}(\mathbf{m})}
{Q_{\mathrm{in}}}
$$

For a mass-conserving solution:

$$
\eta_{\mathrm{main}}
+
\eta_{\mathrm{side}}
=
1
$$

Minimizing pumping power without considering outlet-flow distribution could allow the optimizer to restrict coolant delivery to the side outlet.

Consequently, a minimum side-flow requirement is imposed.

### 3.7 Performance Constraint

The optimized design must maintain or improve the side-outlet flow relative to the corresponding original immersed reference.

The constraint is expressed as:

$$
\eta_{\mathrm{side}}(\mathbf{m})
\geq
\eta_{\mathrm{ref}}
$$

In standard inequality form:

$$
g(\mathbf{m})
=
\eta_{\mathrm{ref}}
-
\eta_{\mathrm{side}}(\mathbf{m})
\leq 0
$$

The immersed reference is evaluated using the unchanged original density design under the corresponding continuation-stage settings.

For the final projection stage, $\beta=8$, the reference side-flow fraction was:

$$
\eta_{\mathrm{ref}}
=
0.07414738
$$

or approximately:

$$
\eta_{\mathrm{ref}}=7.4147\%
$$

This constraint prevents the optimization from obtaining an apparent pumping-power improvement simply by reducing the coolant supplied to the side outlet.

The immersed reference is distinct from the original fitted-wall flow fraction of approximately 4.0242%.

These values belong to different numerical representations and must not be interchanged.

### 3.8 Density Bounds

Every independent density variable is constrained by:

$$
0\leq m_i\leq1,
\qquad i=1,\ldots,128
$$

These bounds prevent nonphysical material-density values.

The equivalent inequality constraints are:

$$
-m_i\leq0
$$

$$
m_i-1\leq0
$$

The material densities outside the editable design domain remain prescribed.

### 3.9 Complete Optimization Problem

The complete PDE-constrained optimization problem is:

$$
\boxed{
\begin{aligned}
\underset{\mathbf{m},\mathbf{z}}{\text{minimize}}
\quad&
\frac{P(\mathbf{z},\mathbf{m})}{P_{\mathrm{ref}}}
\\[6pt]
\text{subject to}
\quad&
\mathbf{R}(\mathbf{z},\mathbf{m})=\mathbf{0},
\\[4pt]
&
\eta_{\mathrm{ref}}
-
\eta_{\mathrm{side}}(\mathbf{z})
\leq0,
\\[4pt]
&
0\leq m_i\leq1,
\\[4pt]
&
i=1,\ldots,128.
\end{aligned}
}
$$

The governing PDE acts as an equality constraint that determines the fluid state for a given material distribution.

By solving the governing equations internally, the problem can be expressed in reduced form:

$$
\boxed{
\begin{aligned}
\underset{\mathbf{m}}{\text{minimize}}
\quad&
f(\mathbf{m})
\\[4pt]
\text{subject to}
\quad&
g(\mathbf{m})\leq0,
\\[4pt]
&
\mathbf{0}\leq\mathbf{m}\leq\mathbf{1}.
\end{aligned}
}
$$

The reduced formulation allows the optimizer to operate directly on the 128 independent density variables while the finite element solver computes the associated velocity and pressure fields.

### 3.10 Additional Geometric Performance Metrics

Although pumping power and outlet-flow distribution define the optimization problem, additional geometric quantities are measured to assess the engineering usefulness of the reconstructed design.

#### Physical Fluid Area

The reconstructed fluid area is:

$$
A_f
=
\int_{\Omega_f}1\,d\Omega
$$

where $\Omega_f$ is the reconstructed physical fluid domain.

#### Maximum Wall Turning Angle

Wall smoothness is evaluated using the angle between incoming and outgoing wall secants over a prescribed arc-length interval.

$$
\theta(s)
=
\cos^{-1}
\left(
\frac{
\mathbf{t}_{-}(s)\cdot\mathbf{t}_{+}(s)
}{
\lVert\mathbf{t}_{-}(s)\rVert
\lVert\mathbf{t}_{+}(s)\rVert
}
\right)
$$

The maximum wall turning angle is:

$$
\theta_{\max}
=
\max_s\theta(s)
$$

The turning-angle measurement uses a wall arc-length interval of 0.25 mm.

Smaller turning angles indicate less abrupt geometric transitions at this measurement scale.

Neither fluid area nor wall turning angle is explicitly constrained in the final optimization formulation.

### 3.11 Summary of Optimization Quantities

| Quantity | Symbol | Role | Units |
|---|---|---|---|
| Material density | $m_i$ | Design variable | Dimensionless |
| Fluid velocity | $\mathbf{u}$ | State variable | m/s |
| Fluid pressure | $p$ | State variable | Pa |
| Pumping power | $P$ | Primary performance metric | W/m |
| Normalized pumping power | $f$ | Objective function | Dimensionless |
| Side-outlet flow fraction | $\eta_{\mathrm{side}}$ | Performance constraint | Dimensionless |
| Hydraulic resistance | $R_{\mathrm{eff}}$ | Performance metric | Pa·s/m² |
| Fluid area | $A_f$ | Geometric diagnostic | mm² |
| Maximum wall turn | $\theta_{\max}$ | Geometric diagnostic | Degrees |

The optimization problem is nonlinear and generally nonconvex.

Discrete adjoint differentiation is used to calculate the reduced objective and constraint gradients efficiently, while the Method of Moving Asymptotes updates the density distribution.

The governing equations, material interpolation, numerical discretization, and sensitivity derivations are developed in the following sections.
