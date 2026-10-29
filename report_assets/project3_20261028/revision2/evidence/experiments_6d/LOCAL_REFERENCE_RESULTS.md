# Local reference refinement completed

[Full report, local switching maps and reference checks](local_reference_refinement/README.md)

The unchanged solver was checked at 129x129x96, 161x161x120 and 193x193x144. Both numerical derivative estimators choose the negative initial turn on every level, whereas 4C and 3D_Long choose the positive turn. At the finest level the estimates are about -0.188 and -0.191 m/rad.

The initial direction mismatch persists, while coefficient magnitude and nearby switching position still change with resolution. The last grid-gradient change is about 15.4%. The heading-cut switch is on the positive side of the initial state for all three references and the negative side for both learned models. No training, policy modification or new rollout occurred. The next diagnostic is the local physics residual near this misplaced learned transition.
