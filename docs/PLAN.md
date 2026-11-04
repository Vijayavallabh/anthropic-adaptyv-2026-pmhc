# PLAN — KRAS G12D / HLA-A*11:01 de novo binder campaign

Assistant-drafted (Claude), 2026-10-27. Deadline 2026-11-08 23:59 AoE (~12 days). See `RECON.md` for
the evidence behind every choice and `configs/target.yaml` for the frozen facts.

## Objective (winner clears ALL three tiers, in order)
1. **Mutation-specific**: measurable KD(G12D), no detectable WT binding. 2. **Peptide-dependent**:
no binding to empty HLA. 3. **Affinity**: low KD(G12D). Optimise each design's **weakest** tier
(max-min); diversity breaks ties. Submit ≤20 ranked, **front-load the best ~10** (selector takes ≤10
from the top of a ranked list).

## Design doctrine (from the geometry — see RECON §2)
- **Peptide-centric, electrostatic-complementary.** Grip the up-bulged central backbone (G4/G7) and
  **P8 Val**; present a **net-positive surface over the P4–P7 bulge** to complement the G12D-induced
  negative shift. D6 is buried (8.3 Å²) → NO direct salt-bridge gimmick; a supporting contact near D6
  at most. **Avoid α1/α2 helix contacts** (the empty-MHC / pan-peptide failure mode — this is how the
  Baker designs beat it).
- **Design to the ORDERED (7OW6-like) conformation**, not the disordered free state — the binder, like
  the TCR, must select/stabilise an ordered bulge.
- **Negative design is built in from step 1** (WT 10-mer + empty HLA as explicit negative states),
  because WT is co-presented and the differential is subtle. Single-state + weak counter-screen = a
  WT-cross-reactive or HLA-reading dud.

## Pipeline
**A. Target prep.** From 7OW6 strip to A(HLA)+B(β2m)+C(peptide) → 3 scoring states: (1) G12D pMHC,
(2) WT pMHC (mutate C D6→G6, or 7OW5/7OW3), (3) empty HLA (drop C). Build counter-peptide panel for the
peptidome scan: SMC1A self-peptide, 9-mer register (9UV8), other A*11:01 binders. RCSB-CIF target for
BoltzGen specs (needs `_entity_poly_seq`).

**B. Generate (diverse classes + lineages; cap ~2/lineage in the final 20).**
- BoltzGen `protein-anything` + `nanobody-anything` — primary; hotspots on the P4–P7 bulge + P8.
- RFdiffusion (Baker Science-2025 recipe: arc over groove, hotspots = outward peptide residues) → ProteinMPNN. RFd3 atom-level H-bond/burial conditioning around the bulge if rebuildable.
- PXDesign — 2nd lineage. scFv/Fab arm (RFantibody if available; else BoltzGen VHH) for the antibody classes, with extra peptide-centric filtering.
- Oversample heavily (pMHC per-trajectory yield is low): 10³–10⁴/arm.

**C. Judge — FIX AND VALIDATE BEFORE GENERATING (the critical de-risk).**
- Co-fold the full 4-chain complex in **Boltz-2** (primary) + **Chai-1** (consensus), identical settings,
  groove pocket/contact restraints, deep MSA for HLA+β2m / single-seq for peptide+binder, 5 models × ≥5
  seeds, rank by **cross-seed pose consistency**.
- **af2ig = honest binding gate** (co-folders over-dock): binder_rmsd<2 ∧ pae_interaction<10 ∧ plddt_binder>80.
- **Three-state differential** per surviving design vs {G12D, WT, empty}: ipSAE (interface; global ipTM
  is diluted by HLA+β2m), ipAE, and **ProteinMPNN per-peptide-position conditional log-prob** (does the
  binder read the bulge; does →WT drop it). Peptide-centricity = fraction of interface contacts on the
  peptide vs the HLA helices (want high).
- **Conjunction filter (not a single axis):** PASS = af2ig-binds-G12D ∧ peptide-centric ∧
  Δipsae(G12D−WT) > decoy-null-95 ∧ Δipsae(G12D−empty) > decoy-null-95 ∧ reads-P6/bulge. Bootstrapped.
- **Controls (fail-loud):** POSITIVE = Poole TCR (Vα/Vβ from 7OW6) through the SAME pipeline — must
  recover G12D>WT + loaded>empty, else the differential metric is blind → fix before generating.
  DECOY (false-crown) = de-novo binders to OTHER targets (sibling challenges) + empty-HLA binders → must
  FAIL the conjunction; they calibrate the null.

**D. Developability + novelty.** SolubleMPNN; GRAVY / net charge / aggregation / longest-contiguous-run /
Cys audit; novelty **level ≥3, target 4** (seq ≤30% id vs SwissProt/PDB/patents/PLAbDab AND low
structural TM; **binding part only**; ANARCI + CDRH3 novelty for Ab classes). Calibrate a local novelty
oracle; byte-verify thresholds.

**E. Portfolio.** ≤20 ranked, front-loaded best ~10, diverse across classes (protein/nanobody/scFv/Fab)
and lineages (~2/lineage), each optimising its weakest tier. Record the 3 selector screens per design
(pLDDT, ipSAE vs G12D, mean Kyte-Doolittle) + ipTM + stated peptide-centric epitope + predicted complex.
Maybe 1 declared mechanism control (peptide-agnostic HLA binder) as the last pick — decide at assembly.

## Pacing (today → Nov 8)
- **Now (d1-2):** foundation ✓, target-prep, judge stand-up + control validation (gate: positive control recovers known selectivity).
- **d3-7:** generation campaigns → MPNN → af2ig gate → 3-state scoring, sharded into idle GPU windows (never clobber the ESMFold2 jobs; one proc/GPU; cap threads).
- **d8-10:** Boltz+Chai consensus rescoring, negative-design counter-screens + peptidome scan, novelty/developability, portfolio assembly.
- **d11-12:** `validate_submission.py`, methods writeup, final byte-checked CSV; owner review → gated upload.

## Gated (owner only) / honesty
- **Portal upload/submission** = owner's click. GitHub repo create/push; destructive changes to shared
  tool installs — all gated.
- Never claim a tool ran unless it ran. Every in-silico selectivity number is a prior, not proof
  (wet-lab dual-tetramer FACS is the real arbiter). Re-validate the exact final sequence end-to-end
  (submit == folded == scored). No prompt-like text in the CSV/methods.
