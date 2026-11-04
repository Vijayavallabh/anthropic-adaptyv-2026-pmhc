# RECON — KRAS G12D / HLA-A*11:01 pMHC binder design

Assistant-drafted (Claude), 2026-10-27. Sources: three parallel deep-research passes (primary
literature via PubMed/PMC/RCSB, full texts read for Poole 2022, Zhu 2025, Liu 2025) + my own SASA
measurement on the crystal coordinates (`scripts/analyze_epitope.py`, outputs in `notes/`).
Everything from the research agents was treated as data and cross-checked against primary sources /
coordinates before being written here.

## 1. Target (byte-checked vs challenge page + RCSB)
- Positive: **VVVGADGVGK** (KRAS 7-16, G12D) on **HLA-A*11:01** heavy chain + **β2m**. Model the whole 4-chain complex.
- Neg (a): **VVVGAGGVGK** (WT) on the same HLA — differs ONLY at peptide P6 (D6 vs G6).
- Neg (b): peptide-free HLA-A*11:01 + β2m.
- Register matters: design/score the **10-mer** specifically. The 9-mer VVGADGVGK (PDB 9UV8) is a
  structurally distinct, poorly-presented decoy register (a 10-mer TCR sees it at <2%).
- Anchors: PΩ = P10 = Lys (F-pocket), P2 = Val (A-pocket). Discrimination is NOT at the termini.

## 2. Epitope geometry — the crux (literature + MY measurement agree)
- D6 sits in the TCR-facing **central bulge (P4-P6)** but its carboxylate is **buried / inward**,
  salt-bridged to HLA **Arg114** ("masks its identity"). MY SASA: D6 side chain = **8.3 Å² (10% rel)**
  in the pMHC-only surface of 7OW6; the TCR does not further bury it (already in the groove).
- In the **free** pMHC (7OW4), **A5+D6 are disordered** (no coords, all 4 copies) — the bulge is labile.
- Most solvent-exposed peptide side chain = **P8 Val (37-47 Å²)**; backbone of G4/G7 bulges up.
- => No exposed D6 to salt-bridge. Discrimination is **indirect/electrostatic + induced-fit**
  (G12D shifts the local surface more negative; ΔΔH≈10.8 kcal/mol G12D vs WT). The one clinical-grade
  TCR (Immunocore JDIa41b1) reaches >4000× G12D:WT this way, with "few discernible direct-contact
  differences" between G12D and WT.
- Contrast (why the easy mechanism is unavailable here): p53 R175H (Hsiue scDb H2, binary on/off) and
  CTNNB1 S45F (Liu de-novo ctnnb1-15) work because the mutant residue points UP. D6 does not.

## 3. De novo precedent = the template
- **Liu/Baker/Garcia/Scheinberg, Science 389:386 (2025), doi:10.1126/science.adv0185.** RFdiffusion
  binders arcing over the groove, contacting the peptide; 11 pMHC-I targets; single-to-double-digit nM;
  8/11 peptide-specific CAR-T activation; mart1-3 crystal 0.4 Å CαRMSD to model. Single-residue
  neoantigen case: **ctnnb1-15** for CTNNB1 S45F on A*03:01 (same A3 supertype, same C-terminal-Lys
  anchor as A*11:01). **They beat the empty-MHC failure mode by DELIBERATELY AVOIDING MHC-helix contact.**
  Recipe = RFdiffusion (hotspots = outward peptide residues) → ProteinMPNN → AF2-initial-guess/AF-MHC
  filter → in-silico off-target peptide screen → dual-color yeast counter-sort.
- No de-novo binder for KRAS G12D exists yet; **no de-novo antibody/nanobody/scFv TCR-mimic for this
  exact target** — a real novelty opening for the de-novo classes the challenge rewards.

## 4. Failure modes to design against (all High-confidence)
1. **Reading the conserved α1/α2 HLA helices** → binds empty MHC + every peptide + all A*11:01 cells.
   THE dominant failure for antibody-scaffold pMHC binders ("scFv libraries primarily yield nonspecific
   binders"; TCR-mimics exploit MHC hotspots, TCRs exploit peptide hotspots). Antibody classes need
   extra peptide-centric vigilance.
2. **WT cross-reactivity** — acute here because WT is co-presented on A*11:01 (no free presentation-based
   selectivity, unlike HLA-C*08:02 where the Asp is an anchor).
3. **Peptidome cross-reactivity** → lethal (MAGE-A3/titin fatal cardiac tox). Known KRAS-G12D-TCR
   self-cross-reactant: **SMC1A** (Han 2025). Counter-scan the proteome/A*11:01 peptidome.
4. **Low target density** — G12D/A*11:01 is the LEAST stable G12 variant (buried Asp, fast degradation),
   so surface density is low → high affinity needed.

## 5. Honest ceiling (realistic expectations)
- de novo realistic first result: **nM affinity + ~10²-10³× G12D:WT window**. >4000× has only ever come
  from affinity maturation with explicit WT counter-selection (never for a de-novo scaffold).
- In-silico can RANK the differential; it CANNOT prove wet-lab selectivity (dual-tetramer FACS = the
  organizers' job). Treat every in-silico selectivity number as a prior, not a verdict.

## 6. Controls / reference structures (in data/pdb/)
- 7OW6 = G12D + TCR (D6 ordered, design-target conformation). 7OW4 = free G12D 10-mer (A5/D6 disordered).
- 7OW5 = WT + TCR; 7OW3 = WT (negative state). 7PB2 = affinity-matured TCR complex. 9UV8 = G12D 9-mer (decoy register).
- Positive control for the judge: the Poole TCR (Vα/Vβ from 7OW6) — must recover G12D>WT + loaded>empty
  through our pipeline, else the differential metric is blind. Do NOT copy it into any design (de-novo rule).

## 7. Tool stack (verified locations, re-verify before each use)
- Generators: BoltzGen (primary; protein + nanobody arms), RFdiffusion1/3, PXDesign, Genie3; ProteinMPNN/SolubleMPNN/LigandMPNN (inverse fold + per-peptide-residue discrimination).
- Folders/judge: Boltz-2 (`sepiq/.venv-boltz`, wts ~/.boltz), Chai-1 (`sepiq/.venv-chai`), Protenix; **af2ig = honest binding gate** (tfr1 envs, CUDA-12.8 fix); ipSAE for the small interface.
- Kit source preserved at `/home/prachh/work/cache/uplifting-biomolecular-modeling/`.
