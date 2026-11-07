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
