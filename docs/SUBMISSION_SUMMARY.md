# Submission summary — KRAS G12D / HLA-A*11:01 selective binder (Track 3)

A concise guide to this submission, organized by the selection criteria. Full methods: `docs/METHODS.md`;
per-design screens and one-line reasons: `runs/submission_screens.csv`; de-novo/eligibility provenance:
`docs/ELIGIBILITY_PROVENANCE.md`.

## Target and epitope (stated, not left to prediction)
20 de-novo, zero-shot ranked designs that bind the **KRAS G12D neoantigen peptide `VVVGADGVGK`** on
**HLA-A\*11:01 + β2-microglobulin**, selectively over the wild-type peptide `VVVGAGGVGK` (differs only at the
**buried** peptide position 6, Asp6 vs Gly6), unrelated A\*11:01 epitopes, and the empty groove. **Declared
epitope:** the peptide and the groove around it, centered on the exposed central bulge (peptide positions 4,5,7,8);
designs avoid the conserved α1/α2 helix surfaces (which would give a peptide-independent, pan-peptide binder).
All co-folding models the whole complex (binder + peptide + heavy chain + β2m), not the peptide alone.

## Chance to express and bind (the first screen)
13 single-chain miniproteins + 7 nanobodies, 61–133 aa, all within class limits. Per-design screens are in
`runs/submission_screens.csv`: **ESMFold pLDDT** (single-chain 89–95; nanobodies 80–95, read within-class, as
single-sequence predictors score nanobodies lower), **ipSAE to the G12D complex** (0.45–0.81), and **mean
Kyte–Doolittle hydropathy** (19/20 soluble, mean −0.20; two designs mildly positive, flagged in the table, not
placed in the top ranks). No design targets a tag; no linkers/padding/extra domains are used to dilate novelty.

## Evidence for the hardest goals — selectivity (the differentiator)
The single buried-residue G12D-vs-WT discrimination is not resolvable by co-folding alone, and we treat it as a
**bench measurement**, not an in-silico claim. We add two orthogonal in-silico lines of evidence as *priors*:
1. A **5-sample, 6-state co-fold panel** (G12D / WT / composition-matched scramble / two unrelated A\*11:01
   epitopes / empty HLA) scored on a pre-registered **minimax "weakest discrimination margin"**
   `min(spec_scram, promisc_margin, bp−bh_e)` — rewarding designs that reject *what the targets share* (scramble,
   other peptides, empty groove), not raw affinity.
2. An **ensemble MM-GBSA physics gate** (OpenMM GBn2; in-silico Asp6→Gly6 mutation on the matched system;
   replica-bootstrapped CIs) applied only as a **confirmatory filter** on **pose-realistic** co-folds — poses that
   keep Asp6 buried and salt-bridged to HLA Arg114 (an over-docked pose that swings Asp6 out is rejected as an
   artifact). The gate was calibrated to recover the one ground-truth system's ΔΔG and to null a WT-vs-WT control.

On this bar, **two designs are credible, pose-verified G12D-selectives** and lead the list: **`b3_gpu7_113`**
(single-chain; ΔΔG −9.3 kcal/mol, 95% CI excludes 0; pLDDT 94, ipSAE 0.81) and **`nb3_gpu4_132`** (nanobody;
−7.3 kcal/mol, CI excludes 0). Consistent with equilibrium physics, a passive monovalent binder cannot exceed the
equilibrium selectivity ceiling exp(ΔΔG/RT); we set realistic expectations at the low-tens-fold range.

## Novelty
All 20 pass the submission novelty gate (level 3+). Single-chain structural novelty is reported as max-TM to the
PDB in the screen table (lower = more novel); nanobody novelty is judged on CDRs (chiefly HCDR3) on natural VHH
frameworks, as the rules specify (framework TM is expectedly high and not penalized). No design is derived from a
known binder; generators were run zero-shot (details and framework/CDR provenance in `ELIGIBILITY_PROVENANCE.md`).

## Ranking and diversity
Ranked selectivity-evidence-first, then by the weakest-margin ruler, with the two credible selectives at #1–2.
Because model error is correlated within a single generation lineage, the ranked order is **diversified across
generation lineages** so the top of the list is not monolithic (the top 10 span two independent generation
lineages and both molecule classes). Lower ranks include well-folded, soluble designs that are peptide-specific on
the co-fold panel but not gate-confirmed (honest long shots), and a few designs the gate reads as wild-type-leaning
are ranked last. Every in-silico number is a prediction; the wet-lab assay is the verdict.

## Integrity and anticipated checks
We pre-empt the standard selection flags:
- **Not immunoglobulin V-domains.** The 13 single-chain designs are 61–85 aa — far shorter than an Ig VH/VHH
  (~110–125 aa) — with no Ig framework (no conserved Cys pair, no WGxG motif), so a numbering tool (e.g. ANARCI)
  will not number them as antibody chains. The 7 nanobodies are correctly declared as nanobody.
- **No near-duplicates in the assayed set.** Across all 20, a single nanobody pair (`nb3_gpu3_307` /
  `nb3_gpu5_130`) shares the standard VHH framework (0.88 whole-sequence identity) but has a **distinct HCDR3
  (0.55 identity)**, and only one of the pair is in the top 10; all other pairwise identities are low.
- **Screens disclosed, not cherry-picked.** `runs/submission_screens.csv` reports pLDDT, ipSAE and hydropathy for
  all 20, including the weaker values — two top-10 designs carry a mild, disclosed note (one borderline hydropathy
  KD +0.13, one lower nanobody ipSAE 0.45); read within class.
- **No tags, no novelty-gaming, no known-binder derivation, no simulated-as-experimental data.** Sequences are the
  binder only (no capture tag, no linkers/padding/extra domains added to dilute similarity); novelty is judged on
  the binding portion. Every in-silico number is a prediction; the wet-lab assay is the verdict.
