# SOTA research synthesis — de novo selective KRAS-G12D / HLA-A*11:01 pMHC binder

Deep multi-agent literature scan (2026-11-02; 111 agents, 28 sources fetched, 133 claims extracted, 25
adversarially verified → 14 confirmed 3-0, 11 refuted). Peer-reviewed primaries weighted over preprints/
blogs. This is a methodology record; it does NOT seed designs from any known binder.

## Bottom line
Our pipeline **is** the published state of the art, and our core doctrine (rank selectivity not affinity;
treat G12D-vs-WT as a bench measurement) is now triple-confirmed by peer-reviewed primaries. The research's
main value is (a) confirming the approach, (b) **refuting** several tempting levers that fail specifically on
a *buried* discriminator, and (c) one orthogonal selectivity layer worth adding.

## Confirmed findings (peer-reviewed unless noted)

1. **SOTA de novo pMHC-I route = RFdiffusion (hotspot the peptide's OUTWARD/upward-facing residues) →
   ProteinMPNN/SolubleMPNN → AF2 fold-and-bind filter.** Three back-to-back *Science* papers, 24 Jul 2025:
   - Liu/Greenwood/Bonzanini (Baker), `science.adv0185` — 11 pMHC targets, 8 gave peptide-specific T-cell
     activation; PDB 9O5S. "RFdiffusion targeted to the outward-facing residues of the bound peptide."
   - Garcia/Householder, `science.adv3813` (PMC12313176) — de novo α-helical TCR-mimic, NY-ESO-1/HLA-A*02
     at **9.5 nM**, **no detectable MART-1** on the same allele (PDB 9MIN) = de novo single-peptide
     discrimination on one MHC, proven.
   - DTU/Johansen, `science.adv0422` (PMID 40705893) — rapid de novo minibinder, NY-ESO-1, cryo-EM 9NNF,
     CAR-functional.
   → **This is essentially our RFdiffusion1+SolubleMPNN+BoltzGen stack.** Only refinement: explicit
   exposed-residue hotspotting + maximize peptide-contact / minimize MHC-contact (we already hotspot the
   exposed bulge C4,5,7,8 and gate on f_pep + empty-HLA bh_e → aligned).

2. **Feasibility wall (highest decision-impact).** Every published success — including all single-residue
   wins (CTNNB1 S45F, etc.) — keys off a **solvent-exposed** side chain. KRAS G12D's Asp6 is **buried**
   (~8 Å², salt-bridged Arg114, H-bonded Q70; Poole 2022, Nat Commun, PDB 7PB2). Even a ~10⁶-fold
   affinity-matured therapeutic TCR discriminates G12D-vs-WT through **indirect electrostatics, not a direct
   contact.** → restraint-free co-fold scoring direct contacts is **blind** to the discriminator; the
   single-residue call is a **bench measurement**. (Exactly our standing doctrine.)

3. **Orthogonal selectivity layers that are adoptable** (Baker adv0185 + DTU adv0422, both 3-0):
   (a) **ProteinMPNN differential peptide scoring** — in the designed-binder context, the on-target peptide
   must score higher than off-target peptides; (b) fine-tuned/differential AF2 co-fold keeping designs that
   bind on-target "considerably more confidently"; (c) in-silico cross-panning + short MD rescoring. All
   open/installable. **Caveat:** validated on EXPOSED-residue discrimination → a weak prior on the buried
   G12D axis; use as enrichment, never a hard gate. In the papers these filters only *ranked*; true
   specificity came from experimental counter-selection.

4. **FEP/HREX of the reverse mutation** is the published method-of-record for single-residue pMHC (Xie 2025,
   preprint) — adopted because "AF2 is insensitive to single-residue changes." **But** it is independently,
   quantitatively documented (Clark 2019 PMC6453258; Sampson 2024 PMID 38844044, by the FEP+ developers) to
   be **least accurate and to systematically OVERPREDICT the penalty for exactly the buried, charge-
   introducing, salt-bridge class** that G12D (Gly→Asp ↔ Arg114) exemplifies (MAE ~2.8 kcal/mol, ~3 kcal/mol
   overprediction). → at best a weak, bias-aware tie-breaker; **do NOT hard-gate on it.** (Vindicates our
   earlier decision not to sink days into FEP.)

5. **StaB-ddG / zero-shot ProteinMPNN ddG** (Deng 2025, ICML, arXiv:2507.05502) — fast free ddG proxy,
   ≈FoldX accuracy, fits the zero-shot constraint; buried-pMHC transfer unvalidated → fast triage pre-filter
   only.

## Refuted — do NOT rely on these (adversarially voted down)
- **MD/APBS charge-complementarity** (rescued p53 R175H, an *exposed* charge) — 0-3 for transfer to buried G12D.
- **MPNN interface-optimization as the KRAS fix** (from G12V/HLA-A*03, which *lacks* the salt-bridge) — 0-3 transfer.
- **FEP ~1.2 kcal/mol accuracy** — 0-3; that is the *non-buried* RMSE; buried is ~1.8+ and biased.
- **JBC meeting-abstract "de novo KRAS pMHC discrimination"** — 0-3, qualitative only, allele unnamed.
- **BindCraft as the SOTA generator-of-record here / StaB-ddG "1000× FoldX for binding"** — overstated.

## Other fetched, relevant (not in the 5 synthesized findings)
- **ProtDBench 2026** (arXiv 2605.04118): head-to-head RFdiffusion-3 vs BoltzGen vs PXDesign vs BindCraft on
  10 targets incl. flat-polar. **RFdiffusion3/RFD3** (bioRxiv 2025.11.19, all-atom), **PXDesign** (bioRxiv
  2025.08.15, zero-shot 20-73% nM hit rate), **Proteina-Complexa** (arXiv 2603.27950). β-sheet-conditioned
  RFdiffusion for polar targets (bioRxiv 2024.10.11, 137 pM–nM).
- **Verifier-dependent bias** (arXiv 2026.05.05): co-fold verifiers show substantial bias and limited mutual
  agreement → *do not trust a single co-fold verifier as a gate* (independently supports our 2-folder caution
  and explains the uninformative Protenix cross-check).
- **Co-folding prospective eval** (eLife 110475): AF3/Boltz-2/Chai head-to-head (general, not pMHC-specific).
- **Adaptyv novelty gate**: the organizer's own EGFR-comp-2 repo defines the sequence prior-art screen
  (`similarity_check = identity × coverage`) — consistent with the v0.5 binder-prescreen we ran (all 20 pass).

## Actionable recommendations, ranked by impact × feasibility (~5 days, 8×H100)
1. **(Done/aligned)** Keep RFdiffusion1+SolubleMPNN+BoltzGen; hotspot the exposed bulge; rank selectivity not
   affinity; WT+empty as decoys; single-residue call = bench. ✓ already our pipeline.
2. **(Add — highest new value)** ProteinMPNN **differential peptide scoring** as an orthogonal, non-docking
   selectivity layer on the front-load: score the on-target peptide vs scramble/WT/unrelated A*11:01 epitopes
   in each design's binder context. Orthogonal to Boltz co-fold → directly shores up the single-verifier
   weakness the Protenix check exposed. Enrichment, not a hard gate.
3. **(Optional, low-cost)** zero-shot ProteinMPNN/StaB-ddG triage pre-filter for any future large pool.
4. **(Optional, bias-aware)** short MD (OpenMM) rescoring of the top few; relative FEP only as a weak
   tie-breaker expecting ~2-3 kcal/mol overprediction — never a gate.
5. **(Do NOT)** charge-complementarity / APBS / FEP hard-gating on the buried G12D axis.
