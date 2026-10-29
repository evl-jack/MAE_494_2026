# Learning reachability on a laptop: accuracy, gradients and control in Air3D

MAE 494 Project 3 — final technical analysis, 28 October 2026  
Scope: completed Experiments 1–5. The 3D final evaluation is complete; 6D results are development evidence.

## Abstract

We implemented a small DeepReach-style physics-informed neural network (PINN) for a two-vehicle collision-avoidance game and investigated improvements feasible on a CPU laptop. The original reduced model had final-horizon value mean absolute error (MAE) of .09150 m against an independent numerical reference. Reducing the terminal-loss multiplier improved development MAE to .04477 m; an output that enforces known terminal and obstacle conditions improved it to .02602 m. Subsequent optimization and additional training improved the selected 3D model, whose .02008 m MAE on previously unused final states confirmed the development trend. The formulation also helped a network using six joint coordinates, although that experiment represents the same intrinsically three-state game. Two further continuations improved final-horizon value error by about 10%, but residual-guided sampling showed no clear advantage over uniform sampling and no reduction in primary collision counts. The results support analytic constraints and broad evaluation before scaling training. They do not establish paper-scale reproduction, globally reliable control gradients or certified safety.

## 1. Research question and decision

**How much can formulation, optimization and sampling improve a small physics-trained reachability model, and do better value predictions produce better control?**

The practical motivation is fast repeated assessment of collision avoidance under an adversarial pursuer. The difficulty is learning a time-dependent value field accurately enough that both its sign and its derivatives are useful. We study a minimal public benchmark rather than a full quadrotor, noisy sensing or flight hardware. The work is primarily a diagnostic study with demonstrated formulation improvements. It does not identify a unique cause of every remaining error.

DeepReach introduced sinusoidal neural PDE approximation for high-dimensional Hamilton–Jacobi reachability without explicit solution labels. We reproduce that core workflow at reduced scale. We do not compare our error percentages directly with paper metrics from different domains, horizons, model sizes or evaluation protocols. [Bansal and Tomlin, DeepReach](https://arxiv.org/abs/2011.02082).

## 2. Minimal game and governing equation

Two planar vehicles travel at equal constant speed $v=.75$ m/s. The evader chooses turn rate $u$ and the pursuer chooses $d$, each bounded by $\omega=3$ rad/s. Contact occurs at center separation $R=.25$ m. The trained horizon is $T=.5$ s.

In the evader's heading frame, $s=(x,y,\psi)$ contains relative position and relative heading:

$$
\dot x=v(\cos\psi-1)+uy,\qquad
\dot y=v\sin\psi-ux,\qquad
\dot\psi=d-u.
$$

The collision function is $l(s)=\sqrt{x^2+y^2}-R$. For time-to-go $\tau$, the avoid-game value satisfies

$$
\max\{V_\tau-H(s,\nabla_sV),\ V-l\}=0,
\qquad V(0,s)=l(s).
$$

Writing $p=\nabla_sV$, maximization by the evader and minimization by the pursuer give

$$
H=v[(\cos\psi-1)p_x+\sin\psi\,p_y]
+\omega|yp_x-xp_y-p_\psi|-\omega|p_\psi|.
$$

The ideal value's nonpositive set identifies states where collision can be forced within the horizon. The candidate feedback is

$$
u^*=\omega\operatorname{sign}(yp_x-xp_y-p_\psi),\qquad
d^*=-\omega\operatorname{sign}(p_\psi).
$$

These controls depend on derivatives, not simply on moving along the spatial gradient. A learned scalar value and its derived controller require separate tests.

The 6D extension uses $z=(x_p,y_p,\theta_p,x_e,y_e,\theta_e)$ with ordinary planar constant-speed vehicle dynamics. The exact relative-coordinate reduction recovers the same $s$. Thus six joint states test redundant representation, translation/rotation consistency and gradient lifting; they do not demonstrate a new intrinsically six-dimensional flight game. Time is an additional input in both networks.

## 3. Models, training and numerical comparison

The principal networks have three sine hidden layers of width 64: 8,705 parameters for the four-input relative network and 8,897 for the seven-input joint network. Adam uses learning rate $10^{-4}$ and batches of 2,048 points, including 256 zero-time rows. Automatic differentiation supplies the time and state derivatives in the physics residual. Collocation points are sampled during training; a conventional fixed table of supervised training labels is not required.

The baseline combines a soft terminal penalty with physics training after terminal pretraining. The constrained alternative is

$$
V_\theta(\tau,s)=l(s)-.25(\tau/T)g_\theta(\tau,s)^2.
$$

It guarantees $V_\theta(0,s)=l(s)$ and $V_\theta\le l$, eliminating the soft terminal penalty and its pretraining stage. It does not enforce periodic headings, monotonicity in horizon or the separate physical lower bound $V\ge-R$.

The independent comparator is a first-order local Lax–Friedrichs grid solver, with periodic heading, CFL-controlled stepping, target projection and constant spatial boundary extension. The principal relative reference domain is $[-2,2]^2\times[-\pi,\pi)$, evaluated inside $[-.6,.6]^2$ in position. Dependency-region checks keep these encounters away from the outer boundary over .5 s. Fine and comparison grids are $129\times129\times96$ and $97\times97\times72$; selected local diagnostics also use finer grids. Reference values are approximate evaluation labels, never PINN training targets or reference-derived value bounds.

The difficulty knob is **evaluation look-ahead**, sampled at 21 times from zero through .5 s for networks trained through .5 s. This measures error growth inside the trained interval; it is not a sweep of independently trained maximum horizons or extrapolation beyond training.

## 4. Results by experiment

### Experiments 1–3: relative-state formulation and optimization

The table below uses the corresponding 3D development comparisons. Rounded cross-stage values summarize the progression; the archived records identify each state's seed and reference snapshots. They are not pooled with final-test or 6D results.

| Experiment | Change | MAE at .5 s (m) | Interpretation |
|---|---|---:|---|
| 1 | Reduced soft-terminal baseline | .09150 | Core workflow ran, accuracy inadequate |
| 2A | Terminal multiplier divided by ten | .04477 | Loss balance materially affected this run |
| 2B | Spatially focused sampling | .07189 | Helped baseline; induced loss calibration also changed |
| 2C | Extra 10,000 full-horizon physics steps | .06048 | More updates helped, at extra cost |
| 3A | Exact terminal/obstacle output | .02602 | Large gain without more physics updates |
| 3B | Periodic heading features | .03517 | Fixed heading aliases, worsened overall MAE |
| 3C | Mixed curriculum/full-horizon times | .02996 | More late-time exposure alone did not fix error |
| 3D | Adam continuation, +200 updates | .02282 | Short refinement helped; longer was not uniformly better |
| 3E | Width-64 model continued to 22,000 updates | .01985 | Best value result in that development comparison |
| 3E | Fresh width-96 model, 10,000 updates | .02127 | Capacity helped, but not a controlled equal-runtime win |

The baseline's MAE rose from .04230 m at .25 s to .09150 m at .5 s. At .5 s it predicted safe on 46.42% of reference-unsafe development states. Reducing the terminal multiplier cut MAE by 51.1%; exact-output 3A then reduced it by a further 41.87% versus 2A. The latter comparison also removes pretraining and changes initialization, so it measures a formulation package rather than the output equation in isolation.

Parameter-gradient diagnostics found strong local learning signals. Several short directions and optimizer-history probes reduced physics loss without improving value MAE. Periodic features and time mixtures improved selected outliers while worsening broader performance. These are useful negative results: neither lower residual nor selected-case improvement reliably ranked the methods. They do not prove that all periodic features, sampling strategies or alternative optimizers would fail.

![Baseline and initial modifications over 21 look-ahead values](figures/lookahead.png)

### Completed 3D final evaluation

After freezing the selected models and protocol, 24,000 previously unused states confirmed the improvement:

| Fixed checkpoint | Final-set MAE at .5 s (m) | Unsafe-set IoU |
|---|---:|---:|
| Original 3A | .02628533 | .79701 |
| Adam +200 | .02297716 | .81636 |
| Long22000 | **.02008032** | **.84239** |

Long22000 reduced MAE by **12.61%** versus Adam +200, with a paired 95% sampling interval of **11.93–13.25%**, and improved MAE at all 20 nonzero horizons. The maximum final-time error was still .26455 m. No false-safe classifications were observed against the approximate reference at those horizons; this is not a uniform error or controller-safety guarantee. This final set is now consumed and was not reused as untouched evidence for later 6D development.

### Experiment 4: transfer to joint coordinates and control diagnostics

On the same grouped 6D development encounters, soft-output 4A had MAE .08695 m, exact-output 4B .02631 m, and its longer continuation 4C .02573 m. The formulation package reduced error 69.75% from 4A to 4B. Additional updates reduced it 2.19% from 4B to 4C. The fixed 3D Long model had .01943 m MAE on those same encounters, outperforming 4C. Redundant coordinates therefore introduced measurable representation difficulty in these runs.

The raw joint model was not exactly invariant: rotating or translating equivalent encounters could change its prediction. Derivative and rollout tests also exposed localized turning failures despite high aggregate gradient agreement. Fine-grid local checks supported a displaced learned switching transition, while refinement showed that the numerical derivative itself was sensitive near some transitions. Native physics residuals detected the difficult region, but large residual did not reliably distinguish its correct and incorrect turns. This motivated Experiment 5 rather than establishing sampling as the unique cause.

### Experiment 5: matched-update uniform versus residual-guided sampling

Both branches inherited 4C weights, Adam moments and base sampling states, adding exactly 2,000 updates to reach 24,000. Uniform 5U retained random collocation. Mixed 5R replaced 25% of nonterminal rows with points selected from a residual bank. Its 40 refreshes scored 327,680 extra candidates. Budgets match optimizer updates and batch size, not total compute.

All three models were evaluated on a **new** development set: 6,000 relative groups, four equivalent poses each, and 21 horizons. Poses stay together in the paired bootstrap.

| Model | MAE at .5 s (m) | Improvement over 4C | Contacts vs reference pursuer on 628 reference-safe poses |
|---|---:|---:|---:|
| Parent 4C | .02543785 | — | 8 |
| 5U: uniform | .02284501 | 10.19% | 8 |
| 5R: residual-guided | .02277261 | 10.48% | 8 |

5R's MAE advantage over 5U was **0.3169%**, with a paired 95% group-sampling interval of **−0.2478% to +0.8802%**. This does not establish superiority or equivalence. Both continuations improved values relative to the parent, but the added sampling mechanism offered no clear primary gain.

The mixed model reduced late-time residuals and some residual tails. Its average common-domain residual, evader turn-sign agreement, equivalent-pose spread and heading-alias metric were worse than 5U's. Neither branch corrected the old initial-turn failure. The seven-policy, two-time-step rollout matrix contained 78,400 trajectories. Primary learned contact counts remained unchanged when the time step was halved, and all saved control updates were replayed successfully.

The approximate reference controller also collided in four of the 628 reference-safe poses. Both numerical grids labeled that initial encounter safe with a margin, but sampled feedback reached .24521 m separation against the .25 m radius. Thus the numerical value/feedback combination is an imperfect comparator. The eight learned-model contacts occurred in states all three PINNs initially classified as unsafe; they are not initially declared-safe collisions by those models.

![Experiment 5 values, classification and equivalent-pose spread](figures/experiment5.png)

## 5. What the evidence establishes

| Question | Supported conclusion | Boundary of the claim |
|---|---|---|
| Can this laptop implement neural HJI reachability? | Yes, with checked equations, training and reference comparisons | Small fixed Air3D benchmark, not paper-scale accuracy |
| Can changes help before increasing physics updates? | Loss rebalancing and analytic output constraints helped substantially | Single-seed comparisons; formulation effects partly bundled |
| Does extra training help? | It improved selected value results, including a completed 3D final evaluation | Intermediate accuracy can regress; necessity is not proved |
| Does a smaller residual mean a better controller? | It was not a reliable ranking criterion in these tests | No theorem linking residuals, value error and control was tested |
| Did residual-guided sampling improve the latest model? | Some diagnostics improved; no clear overall advantage was established | One fixed bank rule and paired training history |
| Did 6D establish high-dimensional scaling? | It tested joint-coordinate representation and transferred formulation | Same intrinsic game; no 9D/10D replication or scaling law |
| Is the resulting controller certified safe? | No | Finite samples, approximate references and unresolved failures |

The most useful research finding is the distinction between **value accuracy, objective reduction and decision reliability**. The experiments improve the first while demonstrating why it cannot substitute for the other two. The controlled comparisons narrow explanations; they do not isolate one universal failure mechanism.

## 6. Assignment diagnostics and measured cost

The experiment addresses the [Project 3 diagnostic requirements](https://designinformaticslab.github.io/DesignOptimization2025/project3.html#pinn-pino-diagnostic-kit-required). P1 is the checked numerical comparator. P2 is the saved terminal/physics loss history. P3 is the 21-point look-ahead curve. P4 comprises saved space–time fields and spatial/heading error spectra. P5 includes hardware, training and inference timings. Their exact source paths and hashes are in [the evidence register](evidence.json).

![Spatial and heading error spectra for the initial models](figures/spectra.png)

The spectra characterize centered/windowed errors; they do not alone establish spectral bias or exclude reference diffusion and heading seams. The knob curve similarly does not prove a causality mechanism.

Hardware was an Intel Core Ultra 7 165U laptop with about 31.45 GiB RAM, CPU-only PyTorch 2.5.1 and two Torch threads. Historical baseline training took 206.38 s. A separately timed fine-grid build took 136.73 s. Warm baseline value inference took 351.14 microseconds for a single state and 2.69 microseconds/state in batches of 1,024; cached grid interpolation took 352.38 and .89 microseconds/state respectively. Loading, conversion and gradient/control work were excluded. These timings are not accuracy-matched and do not establish an operational speed advantage.

For this fixed game, the honest repeated-query comparison is

$$
T_{\rm train}+Nt_{\rm NN}\quad\text{versus}\quad
T_{\rm grid\ build}+Nt_{\rm interpolation}.
$$

The grid can also be cached; a new full solve must not be charged for every state query. Near-equal single-query timings yielded very large, workload-sensitive illustrative crossover counts in the original diagnostic. Batched grid queries were faster. Those old measurements are not a break-even claim for the improved models, whose inference was not benchmarked under the same protocol. Each Experiment 5 continuation recorded about 49 s inside its run timer, excluding imports/debugger startup. Additional candidate work must still be counted even though their observed wall times were similar.

## 7. Limitations, stopping decision and future work

The study uses predominantly one training seed per configuration, a short fixed horizon, simplified deterministic dynamics and approximate grid labels. Bootstrap intervals quantify sampled-state variation conditional on checkpoints and reference; they omit training-seed and solver uncertainty. Equivalent poses and reused horizons are correlated. Error spectra, strong local gradients and failed probes do not prove a universal root cause. Several comparisons change more than one practical aspect of training.

We recommend **concluding this experimental study with these limits stated**. Keep the uniform continuation as the simpler 6D comparison baseline, rather than promoting 5R because of its tiny MAE lead. The best confirmed 3D value result remains Long22000 on its completed final evaluation. These roles must not be combined into a claim that one model wins every metric or dataset.

Further work can first distinguish numerical-reference and feedback errors in the newly identified collision case, then test a targeted gradient/representation remedy across multiple seeds. Genuinely higher-dimensional games require separate formulations and validation. Hybrid reference supervision, trust-region training, two-network safety/direction models and real-world flight tests were discussed but not demonstrated here.

The reserved 6D final set remains unused. A future frozen confirmatory evaluation could strengthen claims about a selected 6D method, but this report explicitly concludes from completed development evidence rather than implying such a test occurred.

## 8. Reporting and reproducibility

See [the evidence and claims register](evidence.json), [reproduction and artifact guide](REPRODUCIBILITY.md), and [recommendation memo draft](RECOMMENDATION_MEMO.md). Figures are copied from existing verified results; no new training or experiment was run to write this report. Archived phase reports are historical records and are preserved even where their original next-step descriptions are now superseded.

The technical analysis is complete for review. A course submission also needs the actual outreach/interview log, confirmation of researcher review/permission where applicable, and the researcher-facing memo delivery record. Earlier project notes attribute the original research direction to Professor Yi (Max) Ren; this report does not invent interview details, direct quotations, approval, delivery or a response. The memo is a draft and has not been sent. GitHub publication and course submission are separate actions.

## References

1. Bansal, S., and Tomlin, C. *DeepReach: A Deep Learning Approach to High-Dimensional Reachability*. [arXiv:2011.02082](https://arxiv.org/abs/2011.02082).
2. [Official DeepReach source at the project-pinned revision](https://github.com/smlbansal/deepreach/tree/a8127aa7825d58623e9646211644876c83dd71d0). Local provenance and notices are retained in the code project.
3. [Project 3: PINN/PINO in the Field](https://designinformaticslab.github.io/DesignOptimization2025/project3.html). Used to organize the reporting requirements; experiment findings come from this project's saved artifacts.
