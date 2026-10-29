# Learning reachability on a laptop: accuracy, gradients and control in Air3D

MAE 494 Project 3 — final technical analysis, 28 October 2026.  
Completed Experiments 1–5. The 3D final evaluation is complete; 6D results are development evidence. Outreach/interview documentation is omitted here. The recommendation memo is a draft and has not been sent.

## 1. Problem brief — DeepReach Air3D replication

**How much can formulation, optimization and sampling improve a small physics-trained reachability model, and do better value predictions produce better control?**

The practical motivation is fast repeated assessment of collision avoidance under an adversarial pursuer. The difficulty is learning a time-dependent value field accurately enough that both its sign and its derivatives are useful. We study a minimal public benchmark rather than a full quadrotor, noisy sensing or flight hardware. The work is primarily a diagnostic study with demonstrated formulation improvements. It does not identify a unique cause of every remaining error.

DeepReach introduced sinusoidal neural PDE approximation for high-dimensional Hamilton–Jacobi reachability without explicit solution labels. We reproduce that core workflow at reduced scale. We do not compare our error percentages directly with paper metrics from different domains, horizons, model sizes or evaluation protocols. [Bansal and Tomlin, DeepReach](https://arxiv.org/abs/2011.02082).

We implemented a small DeepReach-style physics-informed neural network (PINN) for a two-vehicle collision-avoidance game and investigated improvements feasible on a CPU laptop. The original reduced model had final-horizon value mean absolute error (MAE) of .09150 m against an independent numerical reference. Reducing the terminal-loss multiplier improved development MAE to .04477 m; an output that enforces known terminal and obstacle conditions improved it to .02602 m. Subsequent optimization and additional training improved the selected 3D model, whose .02008 m MAE on previously unused final states confirmed the development trend. The formulation also helped a network using six joint coordinates, although that experiment represents the same intrinsically three-state game. Two further continuations improved final-horizon value error by about 10%, but residual-guided sampling showed no clear advantage over uniform sampling and no reduction in primary collision counts. The results support analytic constraints and broad evaluation before scaling training. They do not establish paper-scale reproduction, globally reliable control gradients or certified safety.

## 2. Minimal case formulation and replication

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

### Network, training and evaluation scope

The principal networks have three sine hidden layers of width 64: 8,705 parameters for the four-input relative network and 8,897 for the seven-input joint network. Adam uses learning rate $10^{-4}$ and batches of 2,048 points, including 256 zero-time rows. Automatic differentiation supplies the time and state derivatives in the physics residual. Collocation points are sampled during training; a conventional fixed table of supervised training labels is not required.

The baseline combines a soft terminal penalty with physics training after terminal pretraining. The constrained alternative is

$$
V_\theta(\tau,s)=l(s)-.25(\tau/T)g_\theta(\tau,s)^2.
$$

It guarantees $V_\theta(0,s)=l(s)$ and $V_\theta\le l$, eliminating the soft terminal penalty and its pretraining stage. It does not enforce periodic headings, monotonicity in horizon or the separate physical lower bound $V\ge-R$.

The independent comparator is a first-order local Lax–Friedrichs grid solver, with periodic heading, CFL-controlled stepping, target projection and constant spatial boundary extension. The principal relative reference domain is $[-2,2]^2\times[-\pi,\pi)$, evaluated inside $[-.6,.6]^2$ in position. Dependency-region checks keep these encounters away from the outer boundary over .5 s. Fine and comparison grids are $129\times129\times96$ and $97\times97\times72$; selected local diagnostics also use finer grids. Reference values are approximate evaluation labels, never PINN training targets or reference-derived value bounds.

The difficulty knob is **evaluation look-ahead**, sampled at 21 times from zero through .5 s for networks trained through .5 s. This measures error growth inside the trained interval; it is not a sweep of independently trained maximum horizons or extrapolation beyond training.

## 3. Baseline and diagnostics — P1–P5

The [project diagnostic kit](https://designinformaticslab.github.io/DesignOptimization2025/project3.html#pinn-pino-diagnostic-kit-required) organizes this central evaluation section. The **conventional baseline** is the independent numerical grid solver; the **original PINN baseline** is Experiment 1. Later trained models and fixed-model diagnostics are described afterward.

### P1 — Conventional baseline: accuracy and solve cost

The independent solver uses local Lax–Friedrichs finite differences, explicit Euler with a CFL restriction, target-obstacle projection, periodic heading and constant spatial boundary extension. We compare in an interior region and check sensitivity to a larger spatial domain.

The finest approximate reference uses 129 × 129 spatial nodes and 96 headings. Later comparisons extend the time evaluation to 21 saved direct snapshots at 0.025 s spacing; the original three-time measurements remain preserved. The original 3D development runs share 24,000 interior states at 0, 0.25 and 0.5 s remaining; later cohorts are distinguished below. Separate full-box diagnostic samples measure terminal error and the variational-inequality (VI) residual. No reference values or gradients enter training.

The baseline reference checks used 65/97/129 spatial-node grids with 48/72/96 headings. At 0.5 s, successive refinement MAEs decreased from 0.004420 m to 0.002206 m; the matched-spacing expanded-domain maximum change was 1.11e-16 m. These checks support using the grid for comparison but do not provide a rigorous error bound. Its first-order discretization retains numerical diffusion and nonsmooth-target error.

| Look-ahead | MAE between 65- and 97-node references [m] | MAE between 97- and 129-node references [m] | Expanded-domain maximum change [m] |
|---|---:|---:|---:|
| 0.25 s | 0.003914 | 0.001955 | 0 |
| 0.5 s | 0.004420 | 0.002206 | 1.11e-16 |

A standalone 129×129×96 solve took **136.73 s** and exactly reproduced the original saved three-time reference. The older **696.7 s** timing covers a multi-solve verification suite and must not be presented as the single-solve cost. The separate 21-output solve took 132.99 s and differs slightly because output times shorten Euler steps. These measurements do not imply that requesting more snapshots makes the solver faster; machine conditions and step schedules differ.

Analytic no-turn and frozen-dynamics checks complement refinement and boundary checks. Grid-to-grid agreement is evidence of numerical sensitivity, not a rigorous bound on exact-solution error.



### Metric and cohort definitions

Value MAE is mean absolute PINN-minus-reference error. Relative L² is

$$
100\sqrt{\frac{\sum_i(V_\theta(\tau,s_i)-V_{\mathrm{ref}}(\tau,s_i))^2}
{\sum_i V_{\mathrm{ref}}(\tau,s_i)^2}}\ \%.
$$

IoU is intersection/union of predicted and reference unsafe regions. False-safe means PINN > 0 and reference ≤ 0, divided by the reference-unsafe count. False-unsafe means PINN ≤ 0 and reference > 0, divided by the reference-safe count. These are reference-relative classifications, not certified labels.

Full-box terminal error and interior zero-time value error use different samples. The original 0.00891 m full-box terminal MAE and 0.01184 m interior zero-time MAE should not be treated as contradictory estimates on the same points.

The original development states, completed 3D final states, initial 6D development groups and fresh Experiment 5 development groups are separate cohorts. Four joint poses of one relative encounter are correlated and must remain together when resampling. Tables retain their original cohort; they are not pooled into a single cross-dataset ranking.

### P2 — Separate training-loss components

The baseline records terminal and physics losses separately; terminal pretraining is followed by an expanding-time physics curriculum. The initially calibrated terminal multiplier is fixed afterward. Weighted total loss must be interpreted alongside the individual terms and held-out errors: a small or declining training loss does not demonstrate an accurate value function.

![Baseline separate training-loss history](https://raw.githubusercontent.com/evl-jack/MAE_494_2026/ed8a645c080b8aaf0ac0c0625fc514da7c3cc7e9/outputs/deepreach/experiments/experiment_1/figures/training_history.png)

*Training-loss diagnostic. Saved baseline history; this measures training batches, not the held-out reference error in P3.*

For 3A–3E, 4B/4C and their 5U/5R continuations, the analytic terminal condition is exact by construction, so the analytic terminal loss is identically zero and has zero training weight. Zero-time coordinates still contribute to the physics residual. Logarithmic plots must handle a zero terminal term explicitly rather than inventing a positive value.

The later 6D training histories separate the soft-terminal 4A baseline from the constrained 4B/4C runs:

![6D terminal and physics training histories](report_assets/project3_20261028/revision2/evidence/experiments_6d/training_history.png)

*Training histories are not value-error or controller-safety measurements. 4C continues 4B rather than starting an independent fresh run.*

The per-run histories are preserved in the experiment workspace. Full component-plot coverage and log-axis presentation across every candidate remain a reporting check; this revision does not claim that a single baseline figure completes that work for all runs.



The final Experiment 5 training records also distinguish update time, sampler time and candidate-scoring work. Its sampled losses average different collocation distributions and cannot rank the two arms; the later evaluation uses a common uniform physics audit.

### P3 — Difficulty knob and relative L² graph

The difficulty knob is **evaluation look-ahead τ**, varied from 0 to 0.5 s at 21 points spaced 0.025 s apart, with each checkpoint held fixed. Longer look-ahead tests the fitted value function farther from its known terminal condition. This is difficulty within a fixed trained horizon, not an independent maximum-horizon training sweep or a precise collapse threshold.

![Relative L2 error versus evaluation look-ahead at 21 times](report_assets/project3_final_20261028/source_packet/figures/lookahead.png)

*The left panel is relative L² [%] versus the difficulty knob; the other panels show value MAE and false-safe rate. These curves use the original four models and reused development states. They do not include later constrained models or final-test states.*

The independently solved 21-time reference stores direct snapshots, without time interpolation. Shortened output-aligned Euler steps cause a maximum shared-snapshot difference of 0.00001375 m from the original three-time solve. The original measurements remain preserved.

![Relative L2 and other metrics on the fixed 3D final set](report_assets/project3_20261028/revision2/evidence/evaluation/final_evaluation_20261028/final_comparison.png)

*The separate completed 3D final evaluation uses previously unused states. Long22000 has final-horizon relative L² of 15.48% and MAE 0.02008032 m. This set is now consumed; see Section 4 for its protocol and limitations.*

### P4 — Error fields and Fourier spectra

![Selected space-time error fields](report_assets/project3_20261028/evidence/diagnostics_20261027/space_time_error.png)

*Selected space–time slices for the initial models. These are fixed-state/look-ahead queries, not drone trajectories.*

![Spatial and heading error spectra for the initial models](report_assets/project3_final_20261028/source_packet/figures/spectra.png)

The spatial spectra use centered/windowed interior fields; heading spectra use periodic transforms with the mean removed. Their centered RMS values differ from held-out value RMSE. Most centered/windowed error energy is at lower frequencies. These descriptive spectra do not alone establish spectral bias, a unique error cause or the absence of numerical diffusion and heading seams. Three snapshots do not support a time Fourier spectrum.

Later research examines local errors, invariance, turning transitions and physics residuals. It does not claim that this original spectrum characterizes every later network.

### P5 — Hardware, training and inference cost

Hardware was an Intel Core Ultra 7 165U laptop with about 31.45 GiB RAM, CPU-only PyTorch 2.5.1 and two Torch threads. Historical baseline training took 206.38 s. A separately timed fine-grid build took 136.73 s. Warm baseline value inference took 351.14 microseconds for a single state and 2.69 microseconds/state in batches of 1,024; cached grid interpolation took 352.38 and .89 microseconds/state respectively. Loading, conversion and gradient/control work were excluded. These timings are not accuracy-matched and do not establish an operational speed advantage.

For this fixed game, the honest repeated-query comparison is

$$
T_{\rm train}+Nt_{\rm NN}\quad\text{versus}\quad
T_{\rm grid\ build}+Nt_{\rm interpolation}.
$$

The grid can also be cached; a new full solve must not be charged for every state query. Near-equal single-query timings yielded very large, workload-sensitive illustrative crossover counts in the original diagnostic. Batched grid queries were faster. Those old measurements are not a break-even claim for the improved models, whose inference was not benchmarked under the same protocol. Each Experiment 5 continuation recorded about 49 s inside its run timer, excluding imports/debugger startup. Additional candidate work must still be counted even though their observed wall times were similar.

The latest primary value/reference evaluation took 157.44 s and rollout evaluation 145.96 s within their phase timers, excluding startup and later checking/reporting. Experiment 5's matching budget is 2,000 updates per arm, not equal total computation: 5R additionally scored 327,680 candidate points. The recorded run times were 49.138 s (5U) and 49.090 s (5R), and scoring is already included in sampler time.

### Diagnostic scope

P1, P3, P4 and P5 fill the earlier missing numerical-reference timing, relative-L², spectrum and inference measurements. P2 records separate losses and displays baseline/joint histories; complete per-candidate component-plot coverage and final display polish remain reporting tasks. The later trained models were not all rebenchmarked under the original warm-inference protocol. No accuracy-matched speedup is claimed.

## 4. Experiments, research and final conclusions

### How to read the progression

Experiments 1–3 use the relative-state representation; Experiment 4 tests the same game in redundant joint coordinates; Experiment 5 compares two matched-update continuations on fresh development encounters. All trained comparisons remain predominantly single-seed. Numerical-reference values, gradients and reference-derived bounds were excluded from training.

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

The baseline and initial-modification look-ahead graph appears under P3.

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

![Experiment 5 values, classification and equivalent-pose spread](report_assets/project3_final_20261028/source_packet/figures/experiment5.png)

### Cross-experiment findings

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

### Limitations, stopping decision and future work

The study uses predominantly one training seed per configuration, a short fixed horizon, simplified deterministic dynamics and approximate grid labels. Bootstrap intervals quantify sampled-state variation conditional on checkpoints and reference; they omit training-seed and solver uncertainty. Equivalent poses and reused horizons are correlated. Error spectra, strong local gradients and failed probes do not prove a universal root cause. Several comparisons change more than one practical aspect of training.

We recommend **concluding this experimental study with these limits stated**. Keep the uniform continuation as the simpler 6D comparison baseline, rather than promoting 5R because of its tiny MAE lead. The best confirmed 3D value result remains Long22000 on its completed final evaluation. These roles must not be combined into a claim that one model wins every metric or dataset.

Further work can first distinguish numerical-reference and feedback errors in the newly identified collision case, then test a targeted gradient/representation remedy across multiple seeds. Genuinely higher-dimensional games require separate formulations and validation. Hybrid reference supervision, trust-region training, two-network safety/direction models and real-world flight tests were discussed but not demonstrated here.

The reserved 6D final set remains unused. A future frozen confirmatory evaluation could strengthen claims about a selected 6D method, but this report explicitly concludes from completed development evidence rather than implying such a test occurred.

Detailed older reports remain available as [the previous research synthesis](https://github.com/evl-jack/MAE_494_2026/blob/5461fdf9d07c7a170a6b1803a585fc2a1b1994b3/Project_3.md). Their stage-specific “next work” statements are historical; the final analysis above records the completed status.

## 5. Reproducibility and evidence

The [source final-report packet](report_assets/project3_final_20261028/source_packet/REPORT.md), [evidence and claims register](report_assets/project3_final_20261028/source_packet/evidence.json), and [reproduction guide](report_assets/project3_final_20261028/source_packet/REPRODUCIBILITY.md) retain the main chat's final analysis and provenance. The register lists original project-root source paths and SHA256 hashes, not paths relative to the GitHub asset folder. Its 22 evidence-source hashes, copied figures and all packet-file hashes were checked before publication.

The final packet is a reporting artifact, not a complete runnable checkpoint archive. Large arrays, checkpoints, full training histories and source snapshots remain in the project copies. The register and archived guides identify the required environment, scripts and original locations; previous public implementation code is linked in the existing project documentation. Completing the portable reproduction package remains separate from claiming the saved local workflows ran.

New Experiment 5 [training records](report_assets/project3_final_20261028/evidence/experiments_6d/experiment_5_sampling/TRAINING_RESULTS.md), [common development evaluation](report_assets/project3_final_20261028/evidence/experiments_6d/experiment_5_sampling/evaluation/README.md), and [evaluation/rollout methodology](report_assets/project3_final_20261028/evidence/experiments_6d/experiment_5_sampling/evaluation/METHODOLOGY.md) are included with selected smaller tables, protocols and verification records. Saved-array checks covered 63 value rows, six gradient rows, 72 switching rows, six physics-audit rows, 294 rollout rows and replay of 5.88 million saved control updates. These checks reproduce saved metrics; they do not establish scientific validity or safety by themselves.

The completed 3D final set must not be reused as untouched evidence. The reserved 6D final set remains unused; no such final evaluation is implied by this report.

## 6. Recommendation memo — draft, not sent

The [recommendation memo](report_assets/project3_final_20261028/source_packet/RECOMMENDATION_MEMO.md) summarizes the supported conclusions for a research collaborator. It recommends retaining uniform 5U as the simpler 6D comparison baseline, treating Long22000 as the best confirmed 3D value result, and resolving numerical-reference/feedback uncertainty before another control intervention. Drafting or publishing this file is not memo delivery.

## 7. Presentation and submission status

The final technical analysis preserves the agreed problem → formulation → P1–P5 → experiments order. Equations, graphs and tables distinguish evaluation cohorts and completed results from future work. The original main-chat packet is archived unchanged; publication-status statements inside it describe its preparation stage.

Outreach/interview details remain omitted as requested. Actual researcher-facing context, any review record, the memo delivery record and final portable-code/presentation polish still need the user's records and later completion. No interview quotations, approval, message delivery or response are invented here. The technical report is published on GitHub; course submission and researcher correspondence are separate actions.

## References

1. Bansal, S., and Tomlin, C. *DeepReach: A Deep Learning Approach to High-Dimensional Reachability*. [arXiv:2011.02082](https://arxiv.org/abs/2011.02082).
2. [Official DeepReach source at the project-pinned revision](https://github.com/smlbansal/deepreach/tree/a8127aa7825d58623e9646211644876c83dd71d0). Local provenance and notices are retained in the code project.
3. [Project 3: PINN/PINO in the Field](https://designinformaticslab.github.io/DesignOptimization2025/project3.html). Used to organize the reporting requirements; experiment findings come from this project's saved artifacts.
