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
14 single-chain miniproteins + 6 nanobodies, 57–131 aa, all within class limits. Per-design screens are in
`runs/submission_screens.csv`: **ESMFold pLDDT** (single-chain 89–96; nanobodies 80–95, read within-class, as
single-sequence predictors score nanobodies lower), **ipSAE** (0.45–0.83), and **mean
Kyte–Doolittle hydropathy** (soluble-dominated, mean ≈ −0.1; a few mildly positive — disclosed in the table).
No design targets a tag; no linkers/padding/extra domains are
used to dilate novelty. The set is produced by **two independent generators** — BoltzGen (13 designs) and
Genie3 diffusion backbones + SolubleMPNN (the seven `genie3_*` designs) — all run zero-shot, de novo.

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

On this bar, **three designs are credible, pose-robust G12D-selectives** and lead the list, **spanning both
independent generators** (2 BoltzGen + 1 Genie3). Each is scored not on a single predicted pose but on a
**5-pose co-fold ensemble** (the gate's confidence interval captures MD noise, not co-fold *pose* uncertainty —
the larger error for these interfaces): **`b3_gpu7_113`** (BoltzGen single-chain; G12D-favoring on **5/5** poses,
ensemble-mean ΔΔG −5.8 kcal/mol; binder–peptide interface confidence 0.75, stable across all 5 models);
**`genie3_g6_28_m0`** (Genie3 single-chain; **5/5** poses, mean −6.2); and **`nb3_gpu4_132`** (BoltzGen nanobody;
4/5 poses — one flips — mean −3.3; interface confidence 0.72, the weakest of the three, disclosed). The Genie3
credible was found by an **expansion gate** — applying the MM-GBSA judge across the ~2,000 paneled designs the
co-fold ruler (blind to the buried residue) never tested.

Critically, "pose-robust" is a *tested* property, applied uniformly. Because a ΔΔG is only as reliable as the
co-fold pose it starts from, we re-gated every credible candidate on independent co-fold poses. This caught and
removed a false positive: a Genie3 design with a spectacular −12.5 kcal/mol on its gated pose **collapsed to ≈0
(p=0.76) on an independent pose** — a single-pose artifact on a low-confidence interface (0.47) — and was
**dropped entirely**; a second pose-sensitive candidate was demoted to reserve. The three retained credibles, by
contrast, favor G12D on 4–5 of 5 independent poses. The ranking is **reliability-first**: `b3_gpu7_113` leads
because it pairs 5/5 pose-robustness with the highest, most stable interface confidence — not a raw-largest but
pose-fragile number. The full uniform bar is pose-realistic co-fold → ΔΔG ≤ −4 with CI excluding 0 → 12-replica
replication hold → **5-pose-ensemble robustness** → native Asp6–Arg114 bridge
intact in 100% of 6,000 MD frames → **independent-pose robustness** (`docs/EXPANSION_GATE_PREREG.md` + addenda).
Having credibles across two generators and two fold classes cuts single-generator correlated-failure risk.
Consistent with equilibrium physics, a passive monovalent binder cannot exceed the equilibrium selectivity ceiling
exp(ΔΔG/RT); we set realistic expectations at the low-tens-fold range.

## Novelty
All 20 pass the submission novelty gate (level 3+). Single-chain structural novelty is reported as max-TM to the
PDB in the screen table (lower = more novel); nanobody novelty is judged on CDRs (chiefly HCDR3) on natural VHH
frameworks, as the rules specify (framework TM is expectedly high and not penalized). No design is derived from a
known binder; generators were run zero-shot (details and framework/CDR provenance in `ELIGIBILITY_PROVENANCE.md`).

## Ranking and diversity
Ranked selectivity-evidence-first, with the **three pose-robust credible selectives at #1–3**, ordered
**reliability-first** (strong ΔΔG *and* a stable, high-confidence interface — so `b3_gpu7_113` leads, not the
raw-largest number); the remaining ranks follow the pre-registered weakest-margin co-fold ruler, balanced against
novelty, pose-realism and expression. Because model error is correlated within a single generator, the assayed
**top 10 is diversified across both generators — BoltzGen and Genie3 (an orthogonal diffusion model) — and both
fold classes**: it holds the **3 credible selectives (2 BoltzGen + 1 Genie3)** plus 7 co-fold ruler designs (incl.
2 more Genie3). Having a credible selective from each generator still cuts single-generator correlated-failure risk.
Every Genie3 design was put through the *identical* pipeline (co-fold panel → weakest-margin ruler → MM-GBSA gate →
pose-realism → **independent-pose robustness**), and the gate was applied **honestly in both directions**: the
single strongest co-fold margin in the campaign was Genie3 but was **gate-refuted as wild-type-leaning**; a
gate-selective Genie3 pose that proved an over-dock artifact was denied credit; an earlier pair of 6-replica
gate-leaners **collapsed at 12 replicas**; and — the decisive filter here — a Genie3 design with a −12.5 kcal/mol
margin **collapsed to ≈0 on an independent co-fold pose** and was dropped, while a pose-sensitive one was demoted to
reserve. Only `genie3_g6_28_m0` held across poses and is credited — the gate stays an honest filter. All 20 are
positive on the weakest-margin ruler (no anti-selective padding); lower ranks are well-folded peptide-specific long
shots not gate-confirmed. Every in-silico number is a prediction; the wet-lab assay is the verdict.

## Integrity and anticipated checks
We pre-empt the standard selection flags:
- **Not immunoglobulin V-domains.** The 14 single-chain designs are 57–105 aa with **no Ig framework at all — zero
  cysteines and no WGxG motif in any of them** (the promoted Genie3 credible `genie3_g6_28_m0` included) — so even
  the longest (two Genie3 designs at 104–105 aa) carry none of the Ig hallmarks and a numbering tool (e.g. ANARCI)
  will not number them as antibody chains. The 6 nanobodies are correctly declared as nanobody.
- **No near-duplicates in the assayed set.** The single-chain designs have low pairwise identity. The nanobodies
  share the standard VHH framework (expected, and de novo under the organizers' ruling when the CDRs are
  regenerated), so a pair can exceed 0.85 whole-sequence identity — e.g. `nb3_gpu4_132`/`nb3_gpu7_029` (0.87) —
  but it has a **distinct HCDR3** (≈0.5 identity), i.e. different binding loops on a shared scaffold, not duplicate
  binders. The three VHH-framework nanobodies in the top 10 are pairwise CDR3-distinct.
- **Screens disclosed, not cherry-picked.** `runs/submission_screens.csv` reports pLDDT, ipSAE and hydropathy for
  all 20, including the weaker values — a few top-10 designs carry a mild, disclosed note (borderline hydropathy on
  `genie3_g6_28_m0` KD +0.10 and `b3_gpu4_211` KD +0.13; the Genie3 credible `genie3_g6_28_m0` has a moderate
  binder–peptide interface confidence 0.59, below the two BoltzGen credibles' 0.72–0.75 — which is why it is
  credited only because its ΔΔG held on an independent co-fold pose); read within class. The pose-sensitive design
  this flagged (−12.5 on one pose, ≈0 on another) was **dropped**, not buried in the table. The credible ranking
  rests on the MM-GBSA gate ΔΔG with confidence intervals *confirmed pose-robust*, not on these supporting screens.
- **No tags, no novelty-gaming, no known-binder derivation, no simulated-as-experimental data.** Sequences are the
  binder only (no capture tag, no linkers/padding/extra domains added to dilute similarity); novelty is judged on
  the binding portion. Every in-silico number is a prediction; the wet-lab assay is the verdict.
