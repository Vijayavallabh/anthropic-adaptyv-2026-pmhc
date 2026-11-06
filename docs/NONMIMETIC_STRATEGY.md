# Non-mimetic strategy — KRAS-G12D / HLA-A\*11:01 selective binder

**Source:** cross-disciplinary deep-research workflow (`nonmimetic-pmhc-research`, 2026-11-04): 8 parallel
research angles → 6 triaged load-bearing claims → 6 adversarial verifications, 2.35M research tokens, all
grounded on the one ground-truth system for this exact target. Every control structure is local in `data/pdb/`.

**Ground truth (the anchor for everything below):** Poole et al. 2022, *Nat Commun* 13:5333
(DOI 10.1038/s41467-022-32811-1) — the only characterized >4000×-selective binder to *this* peptide/allele.
PDBs: **7OW3** apo-WT, **7OW4** apo-G12D (1.81 Å), **7OW5** TCR:WT, **7OW6** TCR:G12D, **7PB2** parental JDI TCR.
Same-allele decoy crystals now also exist (Zhu 2025, *Commun Biol* 9:26): **8K50** G12V, **8K4V** G12R,
**9WVE** G12A, **9WVF** G12S, **9UV8** G12D 9-mer (Asp *exposed*, alternate register).

---

## 0. Executive summary — the non-mimetic solution in one page

Our current pipeline is the **mimetic recipe**: shape/contact generators (BoltzGen + RFdiffusion1 + SolubleMPNN)
scored by single-pose co-fold ipSAE. The research confirms — on the exact target — that this recipe is
**blind by construction** to the axis that decides the challenge (G12D-vs-WT at the buried Asp6). That is not a
tooling gap we can tune away; it is a property of where the discriminating information lives.

The solution is to **stop trying to read the buried residue and instead copy the *mechanism* nature's only
proven discriminator uses** — which is not a mechanism any current de-novo pipeline implements:

1. **Design a charge-sensor paratope, not a shape reader.** The matured TCR discriminates by *through-space
   electrostatic complementarity* — pre-positioned cationic residues (R50α +2, K70α +0.88 kcal/mol) that read the
   **induced** more-negative surface field of G12D **without contacting Asp6** (the only D6 contact is a VdW
   tryptophan). Place 1–2 Arg/Lys/His over the position-6/F-pocket projection; let the interface **permit/drive
   the induced residue-6-down flip**; rigidify *around* the sensor (rigidity buys affinity, not selectivity).
2. **Bake "reject what they share" into *generation*, not just selection.** Multistate negative design
   (LigandMPNN negative `tied_beta`, log-likelihood-ratio objective) against the **real decoy ensemble** — WT,
   the G12V/R/A/S variant crystals, the exposed-Asp 9-mer register, empty groove, scramble, unrelated A\*11:01 —
   with an **outer minimax loop** that raises the weight on the currently-weakest competitor each round.
3. **Split the scoring by axis, with a loud-failing calibration gate.** Cheap co-fold/ipSAE rank the **large,
   measurable** axes (empty-HLA `bh_e`, scramble, unrelated). The **buried axis** is arbitrated *only* by
   orthogonal **ensemble physics on a shortlist** (APBS differential surface potential + ensemble MMPBSA ΔΔG;
   FEP as a low-throughput tie-breaker) — and **only if** that physics first recovers the known Poole G12D>WT
   window on 7OW6-vs-7OW5 and returns ~0 on a null. If it fails calibration, we do **not** physics-rank.
4. **Treat the ≤20 submission as coverage optimization under correlated noise.** Realistic zero-shot ceiling is
   **single-digit to low-tens-fold** intrinsic selectivity (not the >1000× of a matured TCR + cellular
   proofreading). So maximize the *expected number of truly-selective designs* across a few **diverse,
   decorrelated mechanistic bets**, each honestly argued — not a composite score.

**Honest ceiling:** every number above is a hypothesis. The buried G12D-vs-WT axis is recoverable *in principle*
by ensemble physics (Poole did it: MMPBSA ΔΔG 12.6 vs 10.8 kcal/mol experimental) but that physics is itself
**noisy in exactly this regime** (buried, charge-changing Gly→Asp; enthalpy–entropy compensation of −10.7 / +6.3
→ ~4.9 net means a ~20% enthalpy error flips the sign). The wet-lab assay is the only verdict.

---

## 1. The verified mechanistic picture (what survived adversarial scrutiny)

All six load-bearing claims were tested by an adversary instructed to refute them. None was refuted; the
corrections *sharpened* the design. The convergent picture:

**(a) The free target has no Asp6 to read — discrimination is a two-state, binder-*induced* effect.**
[claim `free-state-asp6-disordered-two-state` → **SUPPORTED**]
In apo 7OW4 (the entity a binder first meets) peptide Ala5+Asp6 are disordered — unmodeled in all four copies
(byte-verified REMARK 465; Poole: "no observable electron density in the central region"). The buried,
R114-salt-bridged, ~8 Å² Asp6 is a property of the **TCR-ordered** state (7OW6), reached by induced fit (P6 flips
up→down on binding). **Both** WT and G12D order on binding; only G12D completes the Asp6→Arg114/Gln70/Asp116
F-pocket network. The binder therefore has *agency* over Asp6's conformation — the premise "~8 Å² buried salt
bridge" describes the complex the binder *creates*, not a fixed target.

**(b) Discrimination is through-space electrostatic complementarity — no Asp6 contact required.**
[claims `direct-capture…`, `surface-esp-shadow…`, `conformational-selection…` → **PARTLY-SUPPORTED**, mechanism revised]
The matured TCR makes "virtually identical" direct contacts to WT and G12D (V-domain RMSD 0.29 Å) and does **not**
salt-bridge Asp6 itself. Specificity is carried by cationic TCR residues reading the induced negative field
(R50α, K70α — both >13 Å from Asp6; the sole D6 contact is W53α, VdW packing). ΔH −20.3 (G12D) vs −9.6 (WT),
TΔS −8.1 vs −1.8 → net ΔΔG ≈ 4.9 kcal/mol, KD 743 pM vs 3.0 µM (~4000×). This is the **indirect-readout**
principle from protein–DNA recognition, realized on a pMHC.

**(c) Energetics invert the naïve "rigid pre-organization" intuition.** G12D pays the *larger* disorder→order
entropy penalty and wins only because the electrostatic enthalpy overcompensates. Rigidity/pre-organization
raises affinity and cuts binder-side reorganization entropy but is **not** the source of selectivity; a strictly
rigid interface complementary only to the apo up-state *misses* the salt-bridge conformation. RMSF-collapse is the
**wrong** selectivity observable (ordering is a cost, and it is larger for G12D).

**(d) Single-pose interface scorers are blind — but the signal is recoverable by ensemble physics.**
[claim `buried-blindness-is-thermodynamic-not-tooling` → **PARTLY-SUPPORTED**]
Confirmed blind on this axis: ipSAE 0.713 (G12D) vs 0.711 (WT), z~0.05; ProteinMPNN-δ a wash; NetMHCpan
"comparable"; identical TCR contacts. This vindicates our prior finding and the "true G12D-vs-WT is a bench
measurement" stance. **But** blindness is specific to contact/PAE/≥8 Å-graph scorers — it is *not* thermodynamic:
Poole recovered the window with ensemble MD + MMPBSA. The signal lives in **two surface-readable terms**
(the induced surface-ESP shift; the disorder→order dynamics difference) **plus one truly-buried term**.

---

## 2. What died under scrutiny (the honest half — non-mimetic bets that failed)

Reporting these matters as much as the survivors; several were our own initial "clever" ideas.

| Dead route | Why it fails (verified) |
|---|---|
| **Direct "reach-in" salt bridge to buried Asp6 / OD1-OD2 atom hotspots** | Buried salt bridges are frequently net-*destabilizing* (Hendsch–Tidor 1994: 17/21, avg +3.5 kcal/mol); a new buried bridge must displace an Arg114 held bidentate by Asp6+Asp116. And it is *unnecessary* — the proven discriminator never contacts Asp6. |
| **Static apo-ESP "shadow" read from above by a positive patch** | The apo field is disordered/undefined (Asp6 unmodeled). The *ordered* field is locally neutralized by Arg114 and, after Debye screening (λ≈7.8 Å, 150 mM) + compensation, decays **sub-kT/e beyond ~3.5 Å** (coordinate-level screened-Coulomb on 7OW6). It is a **near-contact tie-breaker only**, not a long-range from-above signal. |
| **Capture a "pre-exposed up-rotamer" of Asp6** | No stable free rotamer exists — the center is two-state disordered. |
| **Rigid conformational *selection* of a pre-ordered salt-bridge state** | That state is **induced**, not pre-populated; rigidity ≠ selectivity (see §1c). |
| **FEP as a high-throughput front-load sign-*ranker*** | Not supported. Gly→Asp buried charge-change is the hardest FEP regime (Clark 2019; ~1.5–2.5 kcal/mol uncertainty); enthalpy–entropy compensation can give a confidently-wrong sign. Most surface designs have true coupling ≈ 0 and are *unrankable*. FEP is a **calibrated low-throughput tie-breaker**, not a ranker. |
| **Single-pose co-fold / ipSAE / MPNN-δ as a G12D-vs-WT ranker** | Confirmed blind (§1d). Keep them for the big axes only. |

---

## 3. The non-mimetic solution — four pillars

### Pillar 1 — Charge-sensor paratope (the design objective)
- Positive-design **1–2 pre-positioned cationic groups** (Arg/Lys/His) located over the surface projection of the
  position-6/F-pocket region, to read the induced G12D-negative field (the R50α/K70α *principle*, never the
  sequence). Pair with a defined positive-complement patch sized to the field; **forbid net-negative binder
  interface near P6**.
- **Permit/drive the residue-6-down induced flip** — design against an *ensemble* that includes the down-state,
  not the rigid apo up-state alone.
- Rigidify the scaffold *around* the sensor for affinity/entropy, not as the selectivity mechanism.
- Screen out the AF2/co-fold **ion-bridge artifact** (a Na⁺/Mg²⁺ bridging the interface faking selectivity) via
  trajectory ion-occupancy analysis.

### Pillar 2 — Multistate negative generation with a minimax objective
- **Real decoy ensemble**, not a generic scramble: WT 10-mer (7OW5), G12V/R/A/S variant crystals, the exposed-Asp
  9-mer register (9UV8 — an active confound to design *against*), empty groove, scramble, unrelated A\*11:01
  self-peptides.
- **LigandMPNN/ProteinMPNN negative `tied_beta`**: tie binder positions across per-state chain-copies, weight +1
  on G12D and −λ on each decoy → maximize `logP(seq|G12D) − Σλ·logP(seq|decoy)` (public code, batch size 1).
- **Outer minimax loop**: soft-min / log-sum-exp over competitor margins; each round raise λ on the
  currently-weakest competitor. This *is* "improve the weakest objective" moved from selection into generation.
- **Geometric grip-gate at generation**: hotspots on exposed peptide atoms + a hard binder–peptide contact so
  empty-groove / scramble binding is excluded by construction.
- Optional physics-steered generation: Feynman-Kac/SMC resampling of RFdiffusion (`FK-RFdiffusion`) with a
  two-state selectivity reward; or exact multistate sequence optimization (iCFN / Rosetta RECON) on a handful of
  specificity-molding positions.

### Pillar 3 — Split scoring + loud-failing calibration gate
- **Measurable axes** (empty-HLA `bh_e`, vs-scramble, vs-unrelated): keep the existing 5-sample pocket-restrained
  Boltz-2 co-fold + ipSAE. These are large and our pipeline handles them well.
- **Buried axis (G12D-vs-WT)** — arbitrated only on a **shortlist**, by orthogonal ensemble physics:
  1. **APBS/PDB2PQR Poisson–Boltzmann differential surface potential** (G12D − WT, both ordered, ensemble-averaged
     at 150 mM) — the electrostatic-complementarity ranker; cheap (CPU, minutes), leaves H100s for folding.
  2. **Ensemble MMPBSA/MMGBSA ΔΔG(G12D−WT)** and/or LIE from short replicate explicit-solvent MD (as Poole:
     ~25×3–4 ns), demanding the signal localizes near the mutation.
  3. **FEP/TI** as a low-throughput **confirmatory tie-breaker** on the few designs whose paratope is predicted to
     couple to the P6/R114 region — bound-leg Gly6↔Asp6 (free leg cancels in ranking), charge finite-size
     correction, ff19SB/OPC bias leg, enhanced sampling, per-replicate bootstrap CIs, **sign only if CI excludes 0**.
- **CALIBRATION GATE (load-bearing — §4).** Before trusting *any* physics ranker, require it to (i) recover
  Poole's G12D>WT window on **7OW6 vs 7OW5** above seed noise (CI excludes 0) **and** (ii) return ~0 on a **null**
  (empty groove / pan-peptide helix-reader). Quantify-and-subtract the ff14SB/TIP3P salt-bridge overstabilization
  bias with one ff19SB+OPC leg. **If either control fails → do not physics-rank; fall back to diversify-and-titrate.**

### Pillar 4 — Portfolio as coverage optimization
- Structure the ≤20 as a few **distinct, honestly-argued hypotheses (2–3 designs each)**, caps on near-cousins ~2:
  (a) electrostatic charge-sensor single_chains; (b) **de-novo-CDR nanobodies** with a reach-down CDR-H3-like loop
  (novelty-robust — Adaptyv judges nanobodies on CDR-H3 edit-distance only, framework/TM exempt → Level 3 by
  construction, and the most developable format); (c) a **mixed α/β novelty slot** (Level 4 needs max-TM <~0.5–0.65,
  which a β-sheet paratope reaches where a helical bundle to a groove sits at 0.83–0.95 ≈ Level 2); (d) a
  peptide-grip single_chain.
- Developability tie-breakers (sequence-only, no GPU): prefer ~55–90 aa, 0 unpaired Cys, no long hydrophobic
  runs / high GRAVY / N-glyc sequons; C-terminal Twin-Strep capture pose filter (paratope not occluded by surface
  capture; C-terminus toward the surface).
- State plainly in the methods text: **tier-1 (G12D-vs-WT) is a bench measurement**; the portfolio is ranked on
  the measurable proxies, buried axis used only to break ties among mechanism-bearing designs.

---

## 4. The calibration gate — the single go/no-go experiment

This decides whether Pillar 3 (and hence a physics-gated campaign) is viable **at all**, using only public,
local structures. It is read-only and non-destructive.

- **Positive control:** does APBS-differential-ESP + ensemble MMPBSA on **7OW6 (G12D) vs 7OW5 (WT)** reproduce a
  G12D>WT margin with a bootstrapped CI excluding 0, in the ballpark of Poole's ΔΔG ≈ 10.8 kcal/mol experimental /
  12.6 MMPBSA? (Not merely a CI excluding 0 — sign **and** approximate magnitude.)
- **Null control:** empty groove / a pan-peptide helix-reader must return ~0 (no spurious separation).
- **Bias leg:** one ff19SB+OPC (or NBFIX) run to measure and subtract ff14SB salt-bridge overstabilization.
- **Decision:** PASS → physics-gate the shortlist and launch the generation campaign (§3). FAIL → the honest
  strategy is diversify-and-titrate on the measurable axes; do not burn the remaining days on a dead ranker.

---

## 5. Highest-value *new* signal we have not computed (research gaps, ranked)

1. **HLA α1/α2-helix differential dynamics (free-vs-free, 7OW4 vs 7OW3).** The large, always-solvent-exposed helix
   surface a de-novo binder actually sits on. No angle characterized whether the buried mutation *allosterically*
   reshapes this surface's ensemble — the analog of the HLA-A\*03:01 "dynamic gate" (Ma 2025, *Nat Commun*;
   Ma 2026, *PNAS*). **This is the most promising uncharacterized readable surface and is directly runnable on our
   box.** If a G12D-enriched helix conformer exists, it is a cleaner design target than the near-contact ESP.
2. **Assay-resolution / kinetics:** the KD window and selectivity ratio the SPR/assay verdict actually resolves —
   sets the ambition bar and the counter-selection stringency.
3. **Buried Asp6 pKa / protonation** (constant-pH MD): upstream of both the ESP magnitude and the FEP charge-change
   setup.
4. **Decision-theory portfolio coverage** under correlated-noise rankers: formalize the ≤20 objective.
5. **Cross-reactivity failure base-rate** of anti-G12D-pMHC binders with WT: the realistic prior.

---

## 6. Feasibility on 8×H100 in ~4 days (open tools only; GPUs 2–7, never 0/1)

| Step | Tool (env) | Cost | Status |
|---|---|---|---|
| APBS differential surface ESP | APBS + PDB2PQR (install) / DelPhi | minutes, CPU | control structures local |
| Ensemble MMPBSA calibration | AmberTools `MMPBSA.py` (`ambertools` env) + OpenMM/GROMACS MD | hours | env present |
| α1/α2 free-vs-free dynamics | OpenMM/GROMACS MD + MDAnalysis | hours | env present |
| FEP tie-breaker (shortlist) | `pmx` (`pmxfep` env) / OpenFE / Perses | ~1–2 GPU-days for ~20 | env present |
| Charge-sensor generation | RFdiffusion/RFd3 + LigandMPNN (+ BindCraft/RFantibody) | 1–2 days | installed/open |
| Multistate negative MPNN | LigandMPNN negative `tied_beta` | hours | open |
| Co-fold big-axis scoring | Boltz-2 5-sample (existing pipeline) | existing | in place |

**Gated / avoid:** Schrödinger FEP+, Desmond, Flare; Latent-X (API). None required.

---

## 7. Reconciliation with the locked 20 (upload remains USER-gated)

- The research **confirms** our existing portfolio is honestly ranked on the measurable proxies and that true
  G12D-vs-WT is a bench measurement — that framing holds and is vindicated, not overturned.
- The non-mimetic *upgrade* is net-new: the charge-sensor design objective, multistate negative generation against
  the real variant crystals, and the calibrated ensemble-physics gate. If the calibration (§4) passes and a focused
  campaign yields mechanism-bearing designs, they become **candidate swaps** — evaluated same-ruler against the
  locked 20, by the weakest-objective minimax, exactly as before.
- **Nothing here changes the submission or uploads anything.** The locked 20 stand; swaps and the Proteinbase
  upload remain the user's gated decision. Computational confidence is a hypothesis; the experiment is the verdict.

---

## 8. Key citations (peer-reviewed unless noted)

- **Poole et al. 2022**, *Nat Commun* 13:5333 — the ground-truth selective TCR; PDB 7OW3/7OW4/7OW5/7OW6/7PB2.
- **Zhu et al. 2025**, *Commun Biol* 9:26 — G12 variant crystals (8K50/8K4V/9WVE/9WVF, 9UV8); buried-Asp "masks identity".
- **Ma et al. 2025**, *Nat Commun* (+ 2026, *PNAS*) — neoantigen-vs-WT selectivity from differential dynamics / "dynamic gate" (HLA-A\*03:01).
- **Liu et al. 2025**, *Science* 389:380–385 — de-novo pMHC binders over *outward-facing* residues; specificity via MPNN peptide-mutation scan.
- **Johansen/Wolff et al. 2024**, bioRxiv 2024.11.27.624796 (preprint) — de-novo pMHC binder, MD-LIE specificity, single-mutant cross-reactivity.
- **Hendsch & Tidor 1994**, *Protein Sci* — buried salt bridges frequently net-destabilizing.
- **Clark et al. 2019**, *JMB* — charge-changing buried-residue FEP is the hardest regime; **Zhang et al. 2023**, *JCTC* (Perses) — open-stack charge-change RMSE ~1.6 kcal/mol; **Molecules 2024**, 29:881 — charge-changing peptide mutations a physics weak spot.
- **Dauparas et al.** ProteinMPNN/LigandMPNN; **Watson et al.** RFdiffusion; **Bennett et al. 2024** de-novo scFv to pMHC (epitope insight only — no grafting).
