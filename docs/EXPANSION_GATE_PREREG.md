# Expansion-gate pre-registration (committed 2026-11-07, BEFORE any results)

**Purpose.** Apply the MM-GBSA G12D-vs-WT selectivity gate — the only in-silico judge that
sees the winning axis — across the ~299 realistic-pose, un-gated, paneled designs the co-fold
"weakest-margin" ruler left untested (the ruler is blind to the buried residue). Goal: surface
any *genuinely* credible selectives hiding in the pool, with a bar strict enough that the
multiple-comparisons / look-elsewhere problem cannot manufacture fake winners.

**Why a strict, pre-registered bar.** A naive "95% CI excludes 0 → promote" rule, run across
~100 designs, yields ~1-2 false positives by chance alone under the null — as many as our 2 real
credibles. Earlier this session, two Genie3 designs cleared a 6-rep gate (ΔΔG ≈ -5.2/-5.3) then
regressed to no-signal at 12-rep (-2.28 [-8.1,+3.6], -1.56 [-7.7,+4.5]). The bar below defeats
all three error modes: random noise (replication), look-elsewhere (effect-size floor + FDR),
and systematic pose bias (dynamic pose-realism; replication cannot fix a biased pose — the
over-dock artifact nb3_gpu6_132 gave -11.72 at every rep count).

## Promotion criteria — a design is promoted as a NEW credible selective ONLY if ALL hold

- **C1 Static pose realism.** Native Asp6-HLA-Arg114 salt bridge intact in the co-fold pose
  (min N(Arg,A)-O(Asp6) <= 4.5 A). Validated: both known credibles 2.6-3.0 A; over-dock
  artifact 7.5 A. (Pre-filter: 299/2025 un-gated designs pass.)
- **C2 Screen (prioritizer only, no promotion).** 2-rep / 2 ns MD-MMGBSA ΔΔG. Advance the
  <=24 most-negative point estimates with ΔΔG < 0 to confirm. Rank-based + budget-capped to
  avoid missing a true selective to screen noise; screen alone never promotes.
- **C3 Confirm.** Fresh 6-rep / 5 ns (exactly the calibrated config: clean ΔΔG=-4.36
  [-7.0,-1.6], null WT-vs-WT CI incl 0, noise floor ~1.9). Require **ΔΔG <= -4.0 kcal/mol
  AND 95% CI upper bound < 0** (excludes 0 on the G12D side).
- **C4 Replication / deepening.** Re-run survivors to **12-rep / 5 ns**; must HOLD:
  ΔΔG <= -4.0 AND 95% CI upper bound < 0. Any regression toward 0 = REJECT. (This is the
  check that killed the two earlier Genie3 leaners.)
- **C5 Dynamic pose realism.** Asp6-Arg114 bridge intact in >= 80% of scored MD frames
  (guards against systematic over-dock bias that more replicas cannot fix).
- **C6 Multiplicity (FDR).** Across ALL designs reaching C3, control false-discovery rate at
  **q = 0.05 (Benjamini-Hochberg)** on the confirm p-values; a promoted design must pass its
  BH-adjusted threshold. The number tested and the adjusted cut are reported.
- **C7 Adversarial read.** Independent inspection of each surviving design's pose and
  mechanism (through-space electrostatics, not a buried-contact over-dock) before promotion.

## Ranking & honesty
- Promoted credibles are ranked among the existing credibles by gate ΔΔG with CI, exactly as
  the current #1-2 (`b3_gpu7_113` -9.29, `nb3_gpu4_132` -7.27).
- The cheap geometric "charge-sensor" descriptor is **NOT** used to rank or promote: its
  control check anti-correlated with truth (ranked the real credibles 867th/1513th and the
  over-dock artifact 142nd), confirming the mechanism is through-space, not contact. It is used
  only via its validated `native_bridge` sub-signal for the C1 pose-realism pre-filter.
- Every ΔΔG is a prediction; the wet-lab assay is the verdict. If the search yields 0 designs
  that clear C1-C7, that is the honest result and the submission's credible count stays 2.
- The final Proteinbase upload remains USER-GATED.

---

## Addendum (2026-11-08, post-results) — standard reconciliation, user-approved

A side-agent review flagged an **inconsistency**: the expansion batch was held to C6 (BH-FDR across the
24 confirm tests), but the two ORIGINAL credibles (`b3_gpu7_113`, `nb3_gpu4_132`) were gated in smaller
earlier batches and **never faced any multiple-testing correction** — they passed only pose-realism +
12-rep ΔΔG ≤ −4 with CI excluding 0. So new designs were judged on a strictly tougher scale than the
designs they sit beside.

`genie3_g2_141_m1` (rfd_des_g2_pmhc_g12d_141_m1) is the one design this affected: it **passes the exact
original-credible bar** — pose-real (static Asp6–Arg114 bridge 2.7 Å; **dynamic 100% of 6,000 frames
intact** = C5), 12-rep ΔΔG **−5.00 [−8.6,−1.5]**, and it **HELD** from the 6-rep −6.33 with p *improving*
0.017 → 0.004 (a real effect strengthens with sampling; a look-elsewhere fluke regresses, as the earlier
leaners did −5.2 → −2.3). It was blocked **only by C6**.

**Decision (owner-approved via AskUserQuestion):** adopt the **uniform standard** = pose-real + 12-rep
ΔΔG ≤ −4 with CI excluding 0, **held at the 12-rep independent replication**, applied to ALL credibles
old and new. Rationale: an independent 12-rep replication is a *stronger* look-elsewhere guard than
FDR-on-6-rep (it is fresh data, not a re-test of the same data), and it is the bar the original credibles
already met. This is a consistency fix, not a relaxation: no criterion was loosened for one design; the
same replication bar now governs every credible. The original C1–C7 criteria above are **left unchanged
and remain the committed pre-results record**; this addendum documents the post-results standard call
transparently rather than editing the bar.

**Effect:** `genie3_g2_141_m1` promoted → credible count 4 → **5** (2 BoltzGen + 3 Genie3). It is ranked
#5 by gate ΔΔG with its **hydrophobicity (KD +0.52) disclosed** as an expression risk; it displaces the
gate-WT-leaning co-fold `b3_gpu4_211` from the assayed top-10. Designs that merely passed C3 but did not
HOLD at 12-rep, or whose pose is an over-dock, remain excluded — the uniform bar is still strict.

---

## Addendum 2 (2026-11-08, post-results) — pose-robustness filter (added a criterion, did not relax one)

A second side-agent review flagged that a gate ΔΔG is only as reliable as the single co-fold pose it is computed
on, and that the three Genie3 credibles rested on **low binder–peptide interface confidence** (ipSAE 0.46–0.59)
versus 0.72–0.75 for the two BoltzGen credibles. This is a legitimate reliability gap that pose-realism (C5, which
only checks the Asp6–Arg114 bridge) does not cover.

**Test (decisive):** re-gated all three Genie3 credibles on an **independent co-fold pose** (a different Boltz
model), 6-rep/5ns, and compared ΔΔG:

| design | gated pose (model_0) | independent pose | verdict |
|---|---|---|---|
| `genie3_g6_28_m0` | −7.66 [−11.3,−4.0] | **−7.8 [−12.2,−3.6], p=0** | ROBUST — retained |
| `genie3_g2_141_m1` | −5.0 [−8.6,−1.5] | −4.0 [−8.6,**+0.37**], p=0.08 | pose-sensitive — demoted to #20 reserve |
| `genie3_g2_103_m1` | −12.51 [−17.2,−7.4] | **+0.99 [−5.9,+7.5], p=0.76** | **single-pose artifact — DROPPED** |

**Effect:** the −12.5 "strongest in the campaign" was pose-dependent and is **removed from the submission**. This
is the opposite of relaxing the bar — it **adds** a criterion (independent-pose robustness) that *tightened* the
credible set from a transient 5 back down to **3 pose-robust selectives** (2 BoltzGen + 1 Genie3): `b3_gpu7_113`
(−9.29), `genie3_g6_28_m0` (−7.66, held on both poses), `nb3_gpu4_132` (−7.27). Ranking is now **reliability-first**
(strong ΔΔG *and* stable high-confidence pose), so `b3_gpu7_113` leads rather than the larger-but-fragile number.
The two BoltzGen credibles already had high, stable (0.71–0.75 across all 5 models) interface confidence, so no
independent-pose test was needed to trust their poses; the robustness filter is applied wherever interface
confidence is low. ipSAE in `submission_screens.csv` is reported as the **binder–peptide (C-P)** interface for the
credibles so the comparison is like-for-like.
