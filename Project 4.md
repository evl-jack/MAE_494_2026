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


