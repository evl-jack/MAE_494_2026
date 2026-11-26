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

## 4. Governing Fluid Mechanics

### 4.1 Conservation of Mass

The coolant is modeled as an incompressible Newtonian fluid with constant physical mass density.

The general conservation of mass equation is:

$$
\frac{\partial \rho_f}{\partial t}
+
\nabla\cdot(\rho_f\mathbf{u})
=
0
$$

For steady, incompressible flow with constant fluid density, this reduces to:

$$
\boxed{
\nabla\cdot\mathbf{u}=0
}
$$

In two-dimensional Cartesian coordinates:

$$
\frac{\partial u_x}{\partial x}
+
\frac{\partial u_y}{\partial y}
=
0
$$

This equation ensures that fluid mass is conserved throughout the computational domain.

Integrating over the complete fluid domain and applying the divergence theorem gives:

$$
\int_{\Omega}
\nabla\cdot\mathbf{u}\,d\Omega
=
\int_{\partial\Omega}
\mathbf{u}\cdot\mathbf{n}\,d\Gamma
=
0
$$

Consequently, the total inlet flow must equal the combined outlet flow:

$$
Q_{\mathrm{in}}
=
Q_{\mathrm{main}}
+
Q_{\mathrm{side}}
$$

This relationship also provides a global conservation test for the finite element solver.

### 4.2 Conservation of Momentum

The general momentum equation for a Newtonian fluid is:

$$
\rho_f
\left(
\frac{\partial\mathbf{u}}{\partial t}
+
(\mathbf{u}\cdot\nabla)\mathbf{u}
\right)
=
\nabla\cdot\boldsymbol{\sigma}
+
\mathbf{f}
$$

where:

- $\rho_f$ is the physical fluid mass density.
- $\mathbf{u}$ is the velocity vector.
- $\boldsymbol{\sigma}$ is the fluid stress tensor.
- $\mathbf{f}$ represents body forces per unit volume.
- $(\mathbf{u}\cdot\nabla)\mathbf{u}$ represents convective acceleration.

Because this investigation considers steady-state flow:

$$
\frac{\partial\mathbf{u}}{\partial t}=0
$$

Brinkman penalization introduces an additional resistance force:

$$
\mathbf{f}_B=-\alpha\mathbf{u}
$$

The resulting momentum equation is:

$$
\boxed{
\rho_f(\mathbf{u}\cdot\nabla)\mathbf{u}
=
\nabla\cdot\boldsymbol{\sigma}
-
\alpha\mathbf{u}
}
$$

Other body forces, including gravity, are neglected in the present model.

### 4.3 Newtonian Fluid Stress Tensor

The total fluid stress consists of pressure and viscous contributions:

$$
\boldsymbol{\sigma}
=
-p\mathbf{I}
+
\boldsymbol{\tau}
$$

For an incompressible Newtonian fluid:

$$
\boldsymbol{\tau}
=
2\mu\mathbf{D}(\mathbf{u})
$$

where the strain-rate tensor is:

$$
\mathbf{D}(\mathbf{u})
=
\frac{1}{2}
\left(
\nabla\mathbf{u}
+
\nabla\mathbf{u}^{T}
\right)
$$

Therefore:

$$
\boxed{
\boldsymbol{\sigma}
=
-p\mathbf{I}
+
\mu
\left(
\nabla\mathbf{u}
+
\nabla\mathbf{u}^{T}
\right)
}
$$

The symmetric viscous stress formulation is retained in the finite element implementation.

For constant dynamic viscosity:

$$
\nabla\cdot\boldsymbol{\sigma}
=
-\nabla p
+
\mu\nabla^2\mathbf{u}
+
\mu\nabla(\nabla\cdot\mathbf{u})
$$

Applying incompressibility gives:

$$
\nabla\cdot\boldsymbol{\sigma}
=
-\nabla p
+
\mu\nabla^2\mathbf{u}
$$

The resulting strong-form momentum equation is:

$$
\boxed{
\rho_f(\mathbf{u}\cdot\nabla)\mathbf{u}
=
-\nabla p
+
\mu\nabla^2\mathbf{u}
-
\alpha\mathbf{u}
}
$$

Although this simplified strong form is valid for incompressible flow, the finite element solver retains the symmetric stress formulation when assembling the viscous operator and applying natural traction boundary conditions.

### 4.4 Physical Interpretation of the Momentum Equation

Each term in the momentum equation represents a different physical mechanism.

| Term | Physical Mechanism | Interpretation |
|---|---|---|
| $\rho_f(\mathbf{u}\cdot\nabla)\mathbf{u}$ | Convective inertia | Momentum transported through the flow |
| $-\nabla p$ | Pressure force | Drives fluid from regions of higher pressure |
| $\mu\nabla^2\mathbf{u}$ | Viscous diffusion | Redistributes momentum through viscous stresses |
| $-\alpha\mathbf{u}$ | Brinkman resistance | Suppresses flow through solid or porous regions |

The Brinkman resistance coefficient depends on the design density field.

In fluid regions:

$$
\alpha\rightarrow0
$$

In solid regions:

$$
\alpha\rightarrow\alpha_{\max}
$$

A sufficiently large resistance suppresses velocity within numerically represented solid regions.

Because the resistance is finite, however, Brinkman penalization does not produce an exactly impermeable solid.

This motivates the separate fitted-wall simulations used to evaluate the reconstructed geometry.

### 4.5 Fluid Properties and Operating Conditions

The numerical model uses fluid properties representative of liquid water.

| Physical Parameter | Symbol | Value |
|---|---|---:|
| Fluid mass density | $\rho_f$ | 998.2 kg/m³ |
| Dynamic viscosity | $\mu$ | 0.001002 Pa·s |
| Kinematic viscosity | $\nu$ | $1.0038\times10^{-6}$ m²/s |
| Reference channel height | $H$ | 0.004 m |
| Reynolds number | $Re$ | 50 |
| Mean inlet velocity | $U$ | 0.012548 m/s |
| Maximum inlet velocity | $U_{\max}$ | 0.018821 m/s |

Kinematic viscosity is calculated as:

$$
\nu
=
\frac{\mu}{\rho_f}
$$

Substituting the fluid properties gives:

$$
\nu
=
\frac{0.001002}{998.2}
=
1.0038\times10^{-6}
\ \mathrm{m^2/s}
$$

The fluid properties remain constant throughout all optimization and comparison studies.

### 4.6 Reynolds Number

The Reynolds number represents the relative importance of inertial and viscous effects within the fluid.

$$
\boxed{
Re
=
\frac{\rho_f U H}{\mu}
=
\frac{UH}{\nu}
}
$$

where:

- $U$ is the mean inlet velocity.
- $H$ is the reference channel height.
- $\rho_f$ is the fluid mass density.
- $\mu$ is the dynamic viscosity.

The reference length used in this investigation is the 4 mm main-channel height.

The Reynolds number is prescribed as:

$$
Re=50
$$

Rearranging the Reynolds number expression gives the required mean inlet velocity:

$$
U
=
\frac{Re\mu}{\rho_f H}
$$

Substituting the physical parameters:

$$
U
=
\frac{
50(0.001002)
}{
998.2(0.004)
}
$$

Therefore:

$$
\boxed{
U
=
0.012548\ \mathrm{m/s}
}
$$

At this operating condition, the model assumes laminar flow.

However, laminar flow does not imply negligible convective inertia.

The nonlinear momentum-transport term is retained because it may influence the flow distribution and optimal geometry near the manifold junction.

The significance of this term is investigated through a controlled comparison between Stokes and Navier–Stokes optimization.

### 4.7 Boundary Conditions

The computational model contains four types of boundary regions:

- Inlet.
- Main outlet.
- Side outlet.
- Impermeable walls.

The complete boundary can be expressed as:

$$
\partial\Omega
=
\Gamma_{\mathrm{in}}
\cup
\Gamma_{\mathrm{main}}
\cup
\Gamma_{\mathrm{side}}
\cup
\Gamma_{\mathrm{wall}}
$$

#### Inlet Boundary Condition

A fully developed parabolic velocity profile is prescribed at the inlet.

For a planar channel with height $H$:

$$
\boxed{
u_x(0,y)
=
6U
\frac{y}{H}
\left(
1-\frac{y}{H}
\right)
}
$$

The transverse velocity is prescribed as:

$$
u_y(0,y)=0
$$

This profile satisfies the no-slip condition at both channel walls:

$$
u_x(0,0)=0
$$

$$
u_x(0,H)=0
$$

The maximum velocity occurs at the center of the channel:

$$
y=\frac{H}{2}
$$

Therefore:

$$
U_{\max}
=
\frac{3}{2}U
$$

Substituting the mean inlet velocity:

$$
U_{\max}
=
0.018821\ \mathrm{m/s}
$$

The inlet flow rate per unit out-of-plane depth is:

$$
Q_{\mathrm{in}}
=
\int_0^H u_x(0,y)\,dy
$$

Substituting the velocity profile gives:

$$
Q_{\mathrm{in}}
=
\int_0^H
6U
\frac{y}{H}
\left(
1-\frac{y}{H}
\right)
dy
$$

Evaluating the integral:

$$
\boxed{
Q_{\mathrm{in}}
=
UH
}
$$

Thus:

$$
Q_{\mathrm{in}}
=
(0.01254759)(0.004)
$$

$$
\boxed{
Q_{\mathrm{in}}
=
5.0190\times10^{-5}
\ \mathrm{m^2/s}
}
$$

The inlet flow rate remains fixed throughout the optimization.

#### Wall Boundary Condition

The physical channel walls are modeled as stationary and impermeable.

A no-slip Dirichlet boundary condition is applied:

$$
\boxed{
\mathbf{u}=\mathbf{0}
\qquad
\text{on }\Gamma_{\mathrm{wall}}
}
$$

This condition prevents both normal and tangential fluid motion at the wall.

Within the immersed design region, solid behavior is approximated using Brinkman resistance rather than imposing no-slip conditions on every internal material interface.

After geometry reconstruction, the fitted-wall model applies no-slip conditions directly to the reconstructed physical boundaries.

#### Outlet Boundary Conditions

Both the main outlet and the side outlet use natural zero-total-traction boundary conditions:

$$
\boxed{
\boldsymbol{\sigma}\mathbf{n}
=
\mathbf{0}
}
$$

Expanding the stress tensor:

$$
\left[
-p\mathbf{I}
+
\mu
\left(
\nabla\mathbf{u}
+
\nabla\mathbf{u}^{T}
\right)
\right]\mathbf{n}
=
\mathbf{0}
$$

This condition is applied on both outlets:

$$
\Gamma_{\mathrm{main}}
\cup
\Gamma_{\mathrm{side}}
$$

The individual outlet flow rates are not prescribed.

Instead, they are determined by the solution of the governing equations and the hydraulic characteristics of the geometry.

Applying identical traction conditions allows the influence of the junction geometry on flow distribution to be investigated without introducing unequal external outlet loads.

Zero total traction must not be confused with independently prescribing both zero pressure and zero viscous stress.

### 4.8 Boundary Condition Summary

| Boundary | Mathematical Condition | Boundary Type |
|---|---|---|
| Inlet | Prescribed parabolic velocity | Dirichlet |
| Main outlet | $\boldsymbol{\sigma}\mathbf{n}=0$ | Natural traction |
| Side outlet | $\boldsymbol{\sigma}\mathbf{n}=0$ | Natural traction |
| Physical walls | $\mathbf{u}=0$ | Dirichlet |
| Immersed solid regions | $-\alpha\mathbf{u}$ | Brinkman resistance |

<!-- Insert boundary-condition schematic here. -->

*Figure 5. Prescribed inlet velocity, no-slip walls, and natural traction outlet conditions.*

### 4.9 Nondimensionalization

Nondimensionalization is used to improve numerical scaling and express the governing equations in terms of dimensionless physical parameters.

The reference quantities are:

$$
L_{\mathrm{ref}}=H
$$

$$
U_{\mathrm{ref}}=U
$$

A viscous pressure scale is selected:

$$
p_{\mathrm{ref}}
=
\frac{\mu U}{H}
$$

The dimensionless variables are defined as:

$$
\mathbf{x}^{*}
=
\frac{\mathbf{x}}{H}
$$

$$
\mathbf{u}^{*}
=
\frac{\mathbf{u}}{U}
$$

$$
p^{*}
=
\frac{pH}{\mu U}
$$

The dimensional gradient operator transforms according to:

$$
\nabla
=
\frac{1}{H}\nabla^{*}
$$

The Brinkman resistance is nondimensionalized using:

$$
\boxed{
\alpha^{*}
=
\frac{\alpha H^2}{\mu}
}
$$

Substituting these definitions into the dimensional momentum equation gives:

$$
\frac{\rho_f U^2}{H}
(\mathbf{u}^{*}\cdot\nabla^{*})
\mathbf{u}^{*}
=
-
\frac{\mu U}{H^2}
\nabla^{*}p^{*}
+
\frac{\mu U}{H^2}
\nabla^{*2}\mathbf{u}^{*}
-
\alpha U\mathbf{u}^{*}
$$

Dividing by the viscous-force scale:

$$
\frac{\mu U}{H^2}
$$

produces:

$$
\boxed{
Re
(\mathbf{u}^{*}\cdot\nabla^{*})
\mathbf{u}^{*}
=
-\nabla^{*}p^{*}
+
\nabla^{*2}\mathbf{u}^{*}
-
\alpha^{*}\mathbf{u}^{*}
}
$$

The dimensionless continuity equation becomes:

$$
\boxed{
\nabla^{*}\cdot\mathbf{u}^{*}=0
}
$$

These equations correspond to the nondimensional formulation used by the finite element implementation.

### 4.10 Reference Scales and Physical Unit Recovery

The following reference scales are used to recover dimensional quantities from the numerical solution.

| Quantity | Reference Scale | Numerical Value |
|---|---|---:|
| Length | $H$ | 0.004 m |
| Velocity | $U$ | 0.012548 m/s |
| Pressure | $\mu U/H$ | 0.00314317 Pa |
| Flow per unit depth | $UH$ | $5.0190\times10^{-5}$ m²/s |
| Power per unit depth | $\mu U^2$ | $1.57757\times10^{-7}$ W/m |
| Brinkman resistance | $\mu/H^2$ | 62.625 kg/(m³·s) |

The maximum dimensional Brinkman resistance used in the optimization is:

$$
\alpha_{\max}
=
10^5\ \mathrm{kg/(m^3\cdot s)}
$$

Its dimensionless equivalent is:

$$
\alpha_{\max}^{*}
=
\frac{\alpha_{\max}H^2}{\mu}
$$

Substituting the model parameters:

$$
\alpha_{\max}^{*}
=
\frac{
10^5(0.004)^2
}{
0.001002
}
$$

Therefore:

$$
\boxed{
\alpha_{\max}^{*}
=
1596.81
}
$$

The nondimensional mechanical port-power functional is:

$$
P^{*}
=
-\int_{\Gamma_{\mathrm{ports}}^{*}}
\left(
p^{*}
+
\frac{Re}{2}
\lVert\mathbf{u}^{*}\rVert^2
\right)
(\mathbf{u}^{*}\cdot\mathbf{n})
\,d\Gamma^{*}
$$

Dimensional pumping power is recovered through:

$$
\boxed{
P
=
\mu U^2P^{*}
}
$$

This physical-unit conversion is distinct from the objective normalization used by the optimizer.

### 4.11 Linear and Nonlinear Fluid Models

Two governing models are considered to investigate the influence of convective inertia on the optimized geometry.

#### Linear Stokes Model

The Stokes approximation neglects convective inertia:

$$
\boxed{
-\nabla p
+
\mu\nabla^2\mathbf{u}
-
\alpha\mathbf{u}
=
0
}
$$

The incompressibility constraint remains:

$$
\nabla\cdot\mathbf{u}=0
$$

At a fixed material density field, the resulting state equations are linear in velocity and pressure.

#### Nonlinear Navier–Stokes Model

The Navier–Stokes model retains convective inertia:

$$
\boxed{
\rho_f
(\mathbf{u}\cdot\nabla)\mathbf{u}
=
-\nabla p
+
\mu\nabla^2\mathbf{u}
-
\alpha\mathbf{u}
}
$$

The nonlinear term can be expanded in two dimensions as:

$$
(\mathbf{u}\cdot\nabla)\mathbf{u}
=
\begin{bmatrix}
u_x\frac{\partial u_x}{\partial x}
+
u_y\frac{\partial u_x}{\partial y}
\\[6pt]
u_x\frac{\partial u_y}{\partial x}
+
u_y\frac{\partial u_y}{\partial y}
\end{bmatrix}
$$

The velocity field appears both as the transported quantity and as the quantity responsible for transporting momentum.

This produces a nonlinear system of governing equations.

### 4.12 Importance of the Nonlinear Component

The side branch introduces a change in flow direction that makes the transport of momentum particularly relevant.

The linear Stokes model neglects this transport mechanism, while the nonlinear Navier–Stokes model retains it.

| Characteristic | Stokes | Navier–Stokes |
|---|---|---|
| Pressure forces | Included | Included |
| Viscous stresses | Included | Included |
| Brinkman resistance | Included | Included |
| Convective inertia | Neglected | Included |
| State equation | Linear | Nonlinear |
| Numerical solution | Linear system | Newton iterations |
| Design optimization | Generally nonlinear | Generally nonlinear |

Both models are evaluated using identical inlet velocities, fluid properties, geometry restrictions, and optimization requirements.

The same mechanical port-power functional is retained for the controlled comparison.

Consequently, the principal difference between the models is the inclusion or omission of convective inertia in the governing momentum equation.

The resulting optimized geometries are compared later in the report to establish whether the additional nonlinear physics improves engineering performance.

## 5. Brinkman Penalization and Density Filtering

### 5.1 Density-Based Topology Optimization

Traditional shape optimization modifies a predefined set of geometric parameters, such as channel widths, branch diameters, or corner radii.

Density-based topology optimization instead introduces a spatial material distribution that determines where fluid is permitted to flow.

The computational domain remains fixed throughout the optimization, while the material distribution changes.

This eliminates the need to regenerate the finite element mesh after every optimization iteration and allows the optimizer to discover geometries that are not restricted to predefined shapes.

The material density is represented by:

$$
m_i \in [0,1]
$$

where zero represents solid material and one represents fluid.

The density-based formulation introduces three distinct representations of the material distribution:

| Density Representation | Symbol | Purpose |
|---|---|---|
| Raw density | $m$ | Independent optimization variables |
| Filtered density | $\tilde{\gamma}$ | Spatially regularized material distribution |
| Projected density | $\bar{\gamma}$ | Sharpened fluid-solid distribution |

The complete material-processing sequence is:

$$
\mathbf{m}
\xrightarrow{\text{Helmholtz filter}}
\tilde{\boldsymbol{\gamma}}
\xrightarrow{\text{Projection}}
\bar{\boldsymbol{\gamma}}
\xrightarrow{\text{Brinkman interpolation}}
\boldsymbol{\alpha}
$$

The resulting Brinkman resistance field is supplied to the finite element solver.

### 5.2 Brinkman Penalization

Brinkman penalization represents solid material by introducing a resistance force into the fluid momentum equation.

The resistance force per unit volume is:

$$
\boxed{
\mathbf{f}_B=-\alpha\mathbf{u}
}
$$

where $\alpha$ is a material-dependent resistance coefficient.

The governing momentum equation becomes:

$$
\rho_f(\mathbf{u}\cdot\nabla)\mathbf{u}
=
-\nabla p
+
\mu\nabla^2\mathbf{u}
-
\alpha\mathbf{u}
$$

The physical behavior depends on the magnitude of the Brinkman coefficient.

#### Fluid Region

When the projected density approaches one:

$$
\bar{\gamma}\rightarrow1
$$

the resistance approaches zero:

$$
\alpha\rightarrow0
$$

The governing equations reduce to the ordinary incompressible Navier–Stokes equations.

#### Solid Region

When the projected density approaches zero:

$$
\bar{\gamma}\rightarrow0
$$

the resistance approaches its maximum value:

$$
\alpha\rightarrow\alpha_{\max}
$$

The resistance force suppresses fluid motion within the numerical solid.

#### Intermediate Region

For intermediate density values:

$$
0<\bar{\gamma}<1
$$

the material behaves as an artificial porous medium with finite resistance.

These intermediate states are introduced to maintain differentiability during optimization. They are not necessarily intended to represent physically manufactured porous materials.

### 5.3 Brinkman Interpolation Function

A rational interpolation function is used to calculate the resistance coefficient from the projected material density:

$$
\boxed{
\alpha(\bar{\gamma})
=
\alpha_{\max}
\frac{q(1-\bar{\gamma})}
{q+\bar{\gamma}}
}
$$

where:

- $\alpha_{\max}$ is the maximum resistance.
- $q$ controls the shape of the material interpolation.
- $\bar{\gamma}$ is the projected material density.

The interpolation satisfies the required endpoint conditions:

$$
\alpha(0)=\alpha_{\max}
$$

$$
\alpha(1)=0
$$

The optimization uses:

$$
\alpha_{\max}
=
100000\ \mathrm{kg/(m^3\cdot s)}
$$

and:

$$
q=0.10
$$

The parameter $q$ remains constant throughout the final fixed-pipe optimization.

The resulting resistance values are:

| Projected Density | Brinkman Resistance (kg/(m³·s)) |
|---:|---:|
| 0.00 | 100,000 |
| 0.10 | 45,000 |
| 0.25 | 21,428.57 |
| 0.50 | 8,333.33 |
| 0.75 | 2,941.18 |
| 0.90 | 1,000 |
| 1.00 | 0 |

The nonlinear interpolation allows the local resistance to change continuously as the optimizer modifies the density distribution.

### 5.4 Brinkman Interpolation Derivative

Gradient-based optimization requires the derivative of the resistance coefficient with respect to projected density.

Starting from:

$$
\alpha(\bar{\gamma})
=
\alpha_{\max}q
\frac{1-\bar{\gamma}}
{q+\bar{\gamma}}
$$

Applying the quotient rule:

$$
\frac{d\alpha}{d\bar{\gamma}}
=
\alpha_{\max}q
\frac{
-(q+\bar{\gamma})
-
(1-\bar{\gamma})
}{
(q+\bar{\gamma})^2
}
$$

Simplifying gives:

$$
\boxed{
\frac{d\alpha}{d\bar{\gamma}}
=
-\alpha_{\max}
\frac{q(q+1)}
{(q+\bar{\gamma})^2}
}
$$

The derivative is negative throughout the admissible density interval.

Consequently, increasing the projected density always decreases the local Brinkman resistance.

This derivative is used in the discrete adjoint sensitivity calculation.

### 5.5 Brinkman Penetration Length

Although Brinkman penalization suppresses fluid motion inside solid regions, a finite resistance does not produce a perfectly impermeable material.

A characteristic penetration length can be obtained by balancing viscous diffusion and Brinkman resistance:

$$
\mu\frac{u}{\ell_B^2}
\sim
\alpha u
$$

Rearranging gives:

$$
\boxed{
\ell_B
=
\sqrt{\frac{\mu}{\alpha}}
}
$$

Using the maximum resistance:

$$
\ell_B
=
\sqrt{
\frac{0.001002}{100000}
}
$$

Therefore:

$$
\ell_B
\approx
1.001\times10^{-4}\ \mathrm{m}
$$

or:

$$
\boxed{
\ell_B\approx0.1001\ \mathrm{mm}
}
$$

The initial analysis mesh spacing is 0.25 mm, which is larger than this characteristic penetration length.

Consequently, the initial optimization mesh cannot be assumed to fully resolve the Brinkman transition layer.

Increasing the maximum resistance reduces the penetration length but may also increase numerical stiffness and mesh-resolution requirements.

For this reason, Brinkman penalization is used primarily as a differentiable geometry-discovery method.

The final reconstructed designs are subsequently evaluated using explicit impermeable-wall finite element simulations.

### 5.6 Density Discretization

The independent design variables are defined on a uniform cell-centered density grid.

The editable transition region has dimensions:

$$
4\ \mathrm{mm}\times2\ \mathrm{mm}
$$

Each square density cell has dimensions:

$$
h_d\times h_d
=
0.25\ \mathrm{mm}\times0.25\ \mathrm{mm}
$$

The area of each density cell is:

$$
A_c=h_d^2=0.0625\ \mathrm{mm}^2
$$

The editable grid therefore contains:

$$
N_x=\frac{4}{0.25}=16
$$

$$
N_y=\frac{2}{0.25}=8
$$

giving:

$$
N_d=N_xN_y=128
$$

The original side branch initializes 32 editable cells as fluid and the remaining 96 editable cells as solid.

All 128 editable densities may change during optimization.

The existing density-grid implementation also retains prescribed cells outside the editable region. These cells provide fixed material values for the filtering and reconstruction operations.

The density grid is independent of the finite element analysis mesh.

### 5.7 Need for Spatial Regularization

Without spatial regularization, density-based optimization may produce:

- Highly oscillatory material distributions.
- Checkerboard patterns.
- Small isolated material features.
- Mesh-dependent designs.
- Irregular fluid-solid interfaces.

To reduce these effects, a Helmholtz density filter is applied before evaluating the Brinkman resistance.

The filter introduces spatial coupling between neighboring design variables, discouraging abrupt cell-to-cell changes.

### 5.8 Helmholtz Density Filter

The continuous equation motivating the Helmholtz filter is:

$$
\boxed{
-r_f^2\nabla^2\tilde{\gamma}
+
\tilde{\gamma}
=
m
}
$$

where:

- $m$ is the raw material density.
- $\tilde{\gamma}$ is the filtered material density.
- $r_f$ is the filter length-scale parameter.

The filter used in this project has:

$$
r_f=0.5\ \mathrm{mm}
$$

Relative to the density-cell spacing:

$$
\frac{r_f}{h_d}
=
\frac{0.5}{0.25}
=
2
$$

The filter therefore introduces spatial regularization over neighboring density cells.

The filter radius is a regularization parameter and should not be interpreted as a strict guarantee of minimum geometric feature size or minimum wall-curvature radius.

### 5.9 Discrete Helmholtz Filter

The cell-centered discretization of the Helmholtz equation gives:

$$
\boxed{
(\mathbf{M}+r_f^2\mathbf{K})
\tilde{\boldsymbol{\gamma}}
=
\mathbf{M}\mathbf{m}
}
$$

where:

- $\mathbf{M}$ is the diagonal cell-area matrix.
- $\mathbf{K}$ is the discrete diffusion matrix.
- $\mathbf{m}$ is the raw density vector.
- $\tilde{\boldsymbol{\gamma}}$ is the filtered density vector.

For uniform square density cells:

$$
\mathbf{M}=h_d^2\mathbf{I}
$$

The two-dimensional diffusion matrix is constructed using one-dimensional neighboring-cell operators:

$$
\mathbf{K}
=
\mathbf{I}_y\otimes\mathbf{K}_x
+
\mathbf{K}_y\otimes\mathbf{I}_x
$$

where $\otimes$ denotes the Kronecker product.

For a cell with four neighboring cells, the corresponding discrete filtering equation is:

$$
(h_d^2+4r_f^2)\tilde{\gamma}_i
-
r_f^2
\sum_{j\in\mathcal{N}(i)}
\tilde{\gamma}_j
=
h_d^2m_i
$$

where $\mathcal{N}(i)$ denotes the neighboring cells.

This equation shows how the filtered value depends on both the raw density and the surrounding filtered density values.

### 5.10 Anchored Helmholtz Filter

Applying an unrestricted density filter could unintentionally modify the fixed main pipe or outlet collar.

An anchored Helmholtz filter is therefore implemented.

The complete density vector is partitioned into two index sets:

$$
E=\text{editable cells}
$$

$$
F=\text{fixed cells}
$$

Define the Helmholtz matrix as:

$$
\mathbf{H}
=
\mathbf{M}+r_f^2\mathbf{K}
$$

The matrix system can be partitioned as:

$$
\begin{bmatrix}
\mathbf{H}_{EE} & \mathbf{H}_{EF}\\
\mathbf{H}_{FE} & \mathbf{H}_{FF}
\end{bmatrix}
\begin{bmatrix}
\tilde{\boldsymbol{\gamma}}_E\\
\tilde{\boldsymbol{\gamma}}_F
\end{bmatrix}
=
\begin{bmatrix}
\mathbf{M}_E\mathbf{m}_E\\
\mathbf{M}_F\mathbf{m}_F
\end{bmatrix}
$$

Rather than solving the filtering equation for every cell, the fixed density values are prescribed directly:

$$
\tilde{\boldsymbol{\gamma}}_F
=
\mathbf{m}_{0,F}
$$

where $\mathbf{m}_{0,F}$ contains the original binary material values.

Substituting these prescribed values into the editable equations gives:

$$
\boxed{
\mathbf{H}_{EE}
\tilde{\boldsymbol{\gamma}}_E
=
\mathbf{M}_E\mathbf{m}_E
-
\mathbf{H}_{EF}\mathbf{m}_{0,F}
}
$$

The fixed outlet collar above the standard density-grid boundary is represented using additional prescribed neighboring-cell contributions.

This allows the filter to account for the fluid collar and adjacent solid material at the upper boundary of the editable region.

The anchored filter ensures that the raw, filtered, and projected density values outside the editable region retain their prescribed material values.

The fixed main pipe and outlet collar therefore remain protected throughout the optimization.

Unlike an unrestricted Helmholtz filter with homogeneous Neumann boundary conditions, this anchored formulation does not necessarily conserve the total density integral.

No density-volume conservation requirement is imposed in the final optimization.

### 5.11 Filter Sensitivity

The anchored filtering equation is linear in the independent design variables.

Differentiating with respect to the editable density vector gives:

$$
\mathbf{H}_{EE}
\frac{
d\tilde{\boldsymbol{\gamma}}_E
}{
d\mathbf{m}_E
}
=
\mathbf{M}_E
$$

Therefore:

$$
\boxed{
\frac{
d\tilde{\boldsymbol{\gamma}}_E
}{
d\mathbf{m}_E
}
=
\mathbf{H}_{EE}^{-1}\mathbf{M}_E
}
$$

The fixed-cell and collar contributions have zero derivative because their prescribed material values do not depend on the independent design variables.

For an objective function $F$, reverse differentiation through the filter requires:

$$
\nabla_{\mathbf{m}_E}F
=
\mathbf{M}_E^T
\mathbf{H}_{EE}^{-T}
\nabla_{\tilde{\boldsymbol{\gamma}}_E}F
$$

Rather than explicitly forming the inverse matrix, the implementation solves:

$$
\mathbf{H}_{EE}^{T}\boldsymbol{\psi}
=
\nabla_{\tilde{\boldsymbol{\gamma}}_E}F
$$

followed by:

$$
\boxed{
\nabla_{\mathbf{m}_E}F
=
\mathbf{M}_E^{T}\boldsymbol{\psi}
}
$$

The filter matrix remains constant during the optimization, allowing its sparse factorization to be reused.

### 5.12 Heaviside Density Projection

While Helmholtz filtering provides spatial regularization, it also produces intermediate density values near material interfaces.

A differentiable Heaviside projection is applied to sharpen the filtered distribution toward solid and fluid states.

The projection function is:

$$
\boxed{
\bar{\gamma}
=
\frac{
\tanh(\beta\theta)
+
\tanh[\beta(\tilde{\gamma}-\theta)]
}{
\tanh(\beta\theta)
+
\tanh[\beta(1-\theta)]
}
}
$$

where:

- $\theta$ is the projection threshold.
- $\beta$ is the projection sharpness parameter.
- $\tilde{\gamma}$ is the filtered density.
- $\bar{\gamma}$ is the projected density.

The threshold is fixed at:

$$
\theta=0.5
$$

Consequently, the projection simplifies to:

$$
\boxed{
\bar{\gamma}
=
\frac{
\tanh(\beta/2)
+
\tanh[\beta(\tilde{\gamma}-0.5)]
}{
2\tanh(\beta/2)
}
}
$$

For $\beta=0$, the limiting projection is the identity mapping:

$$
\bar{\gamma}=\tilde{\gamma}
$$

Increasing $\beta$ sharpens the transition around the threshold.

In the limit of large $\beta$, the projection approaches a discontinuous material classification.

Finite values of $\beta$ maintain differentiability for gradient-based optimization.

### 5.13 Projection Derivative

Differentiating the Heaviside projection gives:

$$
\boxed{
\frac{d\bar{\gamma}}
{d\tilde{\gamma}}
=
\frac{
\beta\operatorname{sech}^{2}
[\beta(\tilde{\gamma}-\theta)]
}{
\tanh(\beta\theta)
+
\tanh[\beta(1-\theta)]
}
}
$$

For the selected threshold of 0.5:

$$
\boxed{
\frac{d\bar{\gamma}}
{d\tilde{\gamma}}
=
\frac{
\beta\operatorname{sech}^{2}
[\beta(\tilde{\gamma}-0.5)]
}{
2\tanh(\beta/2)
}
}
$$

At $\beta=0$, the derivative is defined by its limiting value:

$$
\frac{d\bar{\gamma}}
{d\tilde{\gamma}}=1
$$

This derivative is included in the material sensitivity chain.

### 5.14 Projection Continuation

Immediately applying a highly sharpened projection can make the optimization more difficult because many density variables may have small projection derivatives.

A continuation strategy is used to progressively increase the projection sharpness.

The completed fixed-pipe optimization uses three stages:

| Stage | Interpolation Parameter $q$ | Projection Parameter $\beta$ | Maximum Resistance |
|---|---:|---:|---:|
| 1 | 0.10 | 0 | 100,000 |
| 2 | 0.10 | 2 | 100,000 |
| 3 | 0.10 | 8 | 100,000 |

The maximum resistance is expressed in kg/(m³·s).

The filter radius remains constant at 0.5 mm.

Each stage begins from the selected design of the preceding stage, with the first stage initialized using the original sharp T-junction density distribution.

The unchanged original immersed design is evaluated at each stage to establish the corresponding objective normalization and side-flow requirement.

The continuation strategy allows the optimizer to initially explore a smoother material distribution before developing a sharper fluid-solid interface.

### 5.15 Transfer to the Finite Element Mesh

The density grid and finite element mesh serve different purposes.

The density grid defines the material distribution, while the finite element mesh approximates the velocity and pressure fields.

The analysis mesh is constructed so that element boundaries align with the density-cell boundaries.

Each finite element inside the editable region is assigned the Brinkman resistance of its corresponding density cell.

For element $e$ associated with density cell $i$:

$$
\alpha_e
=
\alpha_i(\bar{\gamma}_i)
$$

The dimensionless resistance supplied to the governing equations is:

$$
\boxed{
\alpha_e^{*}
=
\frac{H^2}{\mu}\alpha_i
}
$$

Elements outside the editable region belong to fixed fluid passages and receive zero resistance.

The resulting resistance is constant within each assigned element and is evaluated consistently at its integration points.

This mapping allows the finite element analysis mesh to be refined independently of the 128-variable design discretization.

### 5.16 Complete Material Sensitivity Chain

The dependence of Brinkman resistance on the independent design variables is:

$$
\mathbf{m}
\rightarrow
\tilde{\boldsymbol{\gamma}}
\rightarrow
\bar{\boldsymbol{\gamma}}
\rightarrow
\boldsymbol{\alpha}
$$

Using the chain rule:

$$
\frac{d\boldsymbol{\alpha}}
{d\mathbf{m}}
=
\frac{d\boldsymbol{\alpha}}
{d\bar{\boldsymbol{\gamma}}}
\frac{d\bar{\boldsymbol{\gamma}}}
{d\tilde{\boldsymbol{\gamma}}}
\frac{d\tilde{\boldsymbol{\gamma}}}
{d\mathbf{m}}
$$

Restricting the derivatives to the editable cells:

$$
\boxed{
\frac{d\boldsymbol{\alpha}_E}
{d\mathbf{m}_E}
=
\mathbf{D}_{\alpha}
\mathbf{D}_{\pi}
\mathbf{H}_{EE}^{-1}
\mathbf{M}_E
}
$$

where:

$$
\mathbf{D}_{\alpha}
=
\operatorname{diag}
\left(
\frac{d\alpha_i}{d\bar{\gamma}_i}
\right)
$$

and:

$$
\mathbf{D}_{\pi}
=
\operatorname{diag}
\left(
\frac{d\bar{\gamma}_i}{d\tilde{\gamma}_i}
\right)
$$

The reverse sensitivity is therefore:

$$
\boxed{
\nabla_{\mathbf{m}_E}F
=
\mathbf{M}_E^T
\mathbf{H}_{EE}^{-T}
\mathbf{D}_{\pi}
\mathbf{D}_{\alpha}
\nabla_{\boldsymbol{\alpha}_E}F
}
$$

The resistance sensitivity is obtained from the fluid adjoint and transferred back from the finite element integration points to the density cells.

The complete fluid adjoint derivation is presented in the sensitivity analysis section.

### 5.17 Physical Geometry Reconstruction

The final density field represents a continuous numerical material distribution rather than an explicit manufactured geometry.

An impermeable physical geometry is reconstructed from the projected density field using a threshold of:

$$
\bar{\gamma}=0.5
$$

The material classification is:

$$
\begin{cases}
\bar{\gamma}\geq0.5
&
\text{Fluid},
\\
\bar{\gamma}<0.5
&
\text{Solid}.
\end{cases}
$$

The cell-centered density values are interpreted using bilinear interpolation between neighboring density centers.

A marching-squares-type procedure locates the threshold crossings and constructs polygonal approximations of the fluid regions.

Ambiguous contour configurations are resolved using the bilinear saddle structure.

The reconstructed geometry is restricted to the editable transition region.

Let:

- $\Omega_0$ denote the original physical fluid domain.
- $\Omega_r$ denote the reconstructed threshold region.
- $\Omega_d$ denote the editable design region.

The final physical domain is:

$$
\boxed{
\Omega_f
=
(\Omega_0\setminus\Omega_d)
\cup
(\Omega_r\cap\Omega_d)
}
$$

This operation ensures that the geometry outside the editable region remains unchanged.

The reconstruction is checked for:

- Valid polygonal geometry.
- Preservation of the main channel.
- Preservation of the outlet collar.
- Preservation of the physical inlet and outlet ports.
- Connectivity between the ports.
- Disconnected fluid regions and enclosed solid islands.

The final raw projected-density reconstruction is retained as the primary optimized design.

### 5.18 Immersed and Fitted-Wall Models

Two distinct numerical representations are used throughout the investigation.

| Characteristic | Immersed Brinkman Model | Fitted-Wall Model |
|---|---|---|
| Computational geometry | Fixed envelope | Reconstructed fluid domain |
| Solid representation | Finite resistance | Impermeable boundary |
| Material density | Continuous | Explicit fluid-solid classification |
| Mesh during optimization | Fixed | Not used for optimization updates |
| Fluid-solid interface | Regularized | Explicit physical wall |
| Primary purpose | Gradient-based design discovery | Physical performance evaluation |

The immersed model provides a computationally efficient differentiable optimization framework.

The fitted-wall model removes the artificial porous material and imposes no-slip conditions directly on the reconstructed physical boundaries.

The two models are not assumed to produce identical hydraulic performance.

Agreement between their predictions is assessed through separate numerical experiments.

### 5.19 Summary of Material Model Parameters

| Parameter | Symbol | Value |
|---|---|---:|
| Independent density variables | $N_d$ | 128 |
| Density-cell spacing | $h_d$ | 0.25 mm |
| Density-cell area | $A_c$ | 0.0625 mm² |
| Filter radius | $r_f$ | 0.5 mm |
| Projection threshold | $\theta$ | 0.5 |
| Reconstruction threshold | | 0.5 |
| Brinkman interpolation parameter | $q$ | 0.10 |
| Maximum Brinkman resistance | $\alpha_{\max}$ | 100,000 kg/(m³·s) |
| Maximum dimensionless resistance | $\alpha_{\max}^{*}$ | 1596.81 |
| Characteristic solid penetration length | $\ell_B$ | 0.1001 mm |
| Projection continuation | $\beta$ | 0, 2, 8 |

The combination of spatial filtering, differentiable projection, and Brinkman interpolation enables the optimizer to modify the material distribution while maintaining a fixed computational mesh.

The reconstructed geometry is subsequently evaluated using explicit fitted-wall CFD to establish its hydraulic performance.

### Implementation References

The material model is implemented in the following project source files:

- `project43_topology/density.py`
- `project43_topology/fixed_pipe_pilot_model.py`
- `project43_topology/wall_displacement_density_v1.py`
- `project43_topology/evaluator.py`
- `project43_topology/reconstruction.py`
- `project43_topology/fixed_pipe_pilot.py`

---
