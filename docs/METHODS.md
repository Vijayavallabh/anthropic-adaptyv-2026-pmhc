# Methods — de novo binders selective for KRAS G12D / HLA-A*11:01

## Target and objective
The designs target the KRAS G12D neoantigen peptide VVVGADGVGK presented on HLA-A*11:01 with
beta-2-microglobulin. Success requires three nested properties: (tier 1) preference for the G12D peptide
over the wild-type VVVGAGGVGK, which differ only at peptide position 6 (Asp6 vs Gly6); (tier 2) dependence
on a loaded peptide rather than binding empty HLA; and (tier 3) sufficient affinity. Analysis of the
crystal structures (7OW6/7OW4 for G12D, 7OW5/7OW3 for WT) shows the mutated Asp6 side chain is buried
(solvent-accessible surface ~8 A^2) and salt-bridged into the groove to HLA Arg114, so the discrimination
is an indirect, induced-fit effect rather than an exposed epitope. The design doctrine follows from this:
grip the exposed central bulge of the peptide (positions 4,5,7,8) and avoid the conserved alpha-1/alpha-2
helices, which would yield a peptide-independent, pan-peptide binder.

## Generation
Backbones and sequences were produced zero-shot by four independent routes, none seeded from any known
binder (the Poole TCR and known TCR-mimics were used only as scoring controls), all directed to the exposed
central bulge of the peptide (positions 4,5,7,8), not the conserved alpha-1/alpha-2 helices:
- BoltzGen de novo single-chain binders against the ordered pMHC (two generation rounds; the productive
  route). The sequences are co-designed de novo; they were folded directly, never re-sequenced.
- BoltzGen de novo nanobody CDRs on natural VHH frameworks.
- BoltzGen de novo Fab CDRs on natural VH/VL frameworks.
- RFdiffusion backbones (peptide-bulge hotspots) sequenced with SolubleMPNN.

Each route was carried only as far as it survived the in-silico gate below. Under rigorous multi-sample
scoring the Fab and RFdiffusion routes produced no candidate that cleared the full selectivity conjunction
(their best designs either bound an unrelated peptide as well as the target or did not reproduce a confident
interface across samples), so neither contributes to the front-loaded set; one RFdiffusion design is retained
only as a low-ranked reserve. The submitted set is therefore de novo single-chain proteins plus two de novo
nanobodies. Immunoglobulin V-domains emitted by the single-chain route (a known failure mode of the
"protein" protocol) were detected by a sequence/topology classifier and removed, so the single-chain set is
genuinely non-antibody.

## In silico evaluation
Every candidate was scored on a five-sample co-fold panel of the whole complex (binder + peptide + HLA heavy
chain + beta-2-microglobulin) in six states: the G12D peptide, the wild-type peptide, a composition- and
anchor-matched scramble of G12D, two dissimilar HLA-A*11:01 epitopes, and the peptide-free (empty) complex.
Five samples per state is load-bearing, not cosmetic: single-sample and few-state triage scores systematically
over-estimate, and three candidate families that looked strong at triage (an RFdiffusion lineage, a Fab
lineage, and several single-sample hits) collapsed when re-scored at five samples. Only the five-sample panel
was treated as decisive.

From that panel each design was judged on a conjunction of orthogonal conditions, each calibrated against
should-fail controls rather than trusted in isolation:
- Sequence-order specificity (primary tier-1 proxy): the binder-peptide interface score (ipSAE) for G12D
  minus that for the composition-matched scramble. A design that binds the scramble as well as the target
  reads composition or the HLA platform, not the peptide sequence, and was demoted.
- Peptide-identity specificity / promiscuity (second tier-1 proxy): G12D minus the best of the two unrelated
  HLA-A*11:01 epitopes. A design that grips an unrelated peptide as well as G12D (small margin, or an
  unrelated-peptide interface above an absolute ceiling) is a pan-peptide reader and was demoted.
- Peptide dependence (tier-2, scored directly): the binder-HLA interface in the empty, peptide-free state.
  A low value means the binder needs the peptide; a high value means it grips the conserved helices and would
  bind empty HLA. This is the single most discriminating axis and separated otherwise sequence-specific
  designs into genuine peptide-dependent binders and helix-readers; it carries a major weight in ranking.
- Peptide grip: the fraction of binder interface contacts on the peptide across samples, benchmarked against
  peptide-independent helix-reader decoys whose grip fraction set an explicit rejection ceiling.
- Foldability: a single ESMFold monomer pLDDT for every design (one consistent metric across classes); poor
  folders were demoted from the front-loaded set.
- Developability and integrity: free-cysteine, hydrophobicity and charge liabilities, exclusion of any
  long single-residue run, and removal of single-chain designs whose sequence/topology is an immunoglobulin
  V-domain.
- Structural novelty: single-sequence ESMFold followed by a maximum TM-score against the PDB (see Novelty).

Adversarial stress-testing (independent should-fail decoys; composition-matched and unrelated-peptide
controls) showed that any single axis is necessary but not sufficient: a high interface score alone, or a
single-sample peptide-dependence signal, does not separate designs from controls, and ranking by predicted
affinity alone preferentially selects non-selective, pan-peptide binders. Ranking therefore puts selectivity
(sequence-order and peptide-identity specificity) and peptide dependence ahead of predicted affinity, which
enters only as a minor term.

## Novelty
The hard requirement is Adaptyv novelty level >= 3. For the de novo single-chain proteins the sequence axes
are cleared by construction (the sequences are generated, not derived from any natural protein); the binding
axis that is genuinely at stake is structural. Each binder sequence was folded single-sequence with ESMFold
and compared to the PDB by maximum TM-score. Candidates split into a structurally novel/borderline group
(max-TM below ~0.89, calibrated against portal-verified ground truth from a sibling challenge) and a
higher-TM group. The front-loaded set is deliberately hedged: it is dominated by novelty-safe designs
(max-TM < 0.89) while retaining the strongest high-TM binders lower down, so the submission does not stake the
whole front on a single reading of the structural-novelty boundary. For the two nanobodies, novelty is judged
on CDR diversity (chiefly HCDR3) per the challenge rules; their frameworks are natural VHH scaffolds (high
whole-domain TM is expected and not penalised), and their CDR loops are de novo.

## Eligibility and cross-validation
Eligibility (the sequence-level prior-art / known-binder screen, distinct from the displayed novelty score)
was checked with the official Adaptyv binder-prescreen v0.5: all twenty designs pass. The two nanobodies'
paratopes sit at 0.29–0.33 identity to the nearest known binder (i.e. genuinely de novo CDRs, not a known
binder on a fresh framework); the single-chain designs have no match to any known target binder. This was
run before finalising and the report and tool version are kept with the submission record.

As an independent check we re-scored the top candidates with a second co-folder (Protenix), restrained
identically to the primary Boltz-2 run. Under this protocol all candidates — and, critically, a
crystal-verified positive control (a known TCR for this exact complex) — register the same low
binder-peptide interface score, because the second folder's pocket term is a soft conditioning feature
rather than a geometric potential and does not dock a de-novo binder without an MSA. The cross-check
therefore fails its positive control and is uninformative for ranking; we rely on the pocket-restrained
Boltz-2 panel. The honest reading is that absolute in-silico binder docking is restraint-dependent for de
novo binders, which is one more reason absolute affinity and the single-residue discrimination are treated
as experimental questions rather than in-silico claims.

## On tier-1 selectivity (G12D-vs-WT) and the confirmatory physics gate
Co-folding cannot *rank* the single-residue G12D-versus-WT difference (the predicted interface scores for the two
peptides are statistically indistinguishable), and the intrinsic selectivity is an intra-pMHC
electrostatic/conformational effect that is largely binder-independent. The co-fold panel therefore ranks only the
measurable proxies (sequence-order and peptide-identity specificity, peptide dependence, grip), and true
G12D-versus-WT is left to the assay.

An orthogonal **ensemble MM-GBSA physics gate** (OpenMM, GBn2/mbondi3, single-trajectory, replica-bootstrapped
confidence intervals; `scripts/gate/`) was added as a *confirmatory filter* — never a ranker — for that buried
axis. On a matched system it scores ΔΔG = ΔG_bind(G12D) − ΔG_bind(in-silico Asp6→Gly6 WTmut) over 6–12 independent
MD replicas per state. It was calibrated to fire correctly before use: it recovered the Poole ground-truth
matched-scaffold window (ΔΔG = −4.36 kcal/mol, 95% CI [−7.0, −1.6]; experimental −4.9) and returned ~0 on a
WT-vs-WT null (CI including 0 → a structural/build noise floor ≈ 1.9 kcal/mol). A design is called
G12D-SELECTIVE only if ΔΔG ≤ −4 kcal/mol **and** its CI excludes 0. (The ante-MMPBSA→sander MM-PBSA path was found
corrupt in this environment — phantom energies from an atom-order mismatch — so the self-consistent OpenMM GBn2
path is used throughout.)

**Pose realism is mandatory.** The gate scores whatever pose the co-folder produced, and the co-folder frequently
*over-docks* the buried Asp6 — swinging it ~8 Å out of the groove to hydrogen-bond the binder's carboxylate
directly, destroying the native Asp6↔HLA-Arg114 salt bridge. The single-trajectory MM-GBSA then reports a strong
but artefactual "selectivity" (the WTmut merely loses that direct binder–Asp6 bond, while the buried bridge the
real geometry would have to pay for is already broken in the pose). A geometry audit (`scan_saltbridge_all.py` →
`runs/campaign/gate/pose_realism.tsv`) classifies every scored pose: PRESERVED (native bridge intact, <4 Å →
through-space discrimination, the intended non-mimetic mechanism) vs BROKEN (over-dock artifact). Across the 58
gated designs, 42 preserve the bridge and 15 break it. Only a **preserved-pose** selective call is credible; an
over-docked selective is denied gate credit and ranked on the ruler. A pose-rescue (`find_rescue_poses.py`)
re-gated the two over-docked selectives that had a preserved co-fold shard — both went null on the realistic pose
(ΔΔG flipped from ≈ −11 / −6 to +7.4 / +1.9), confirming their apparent selectivity was the artifact.

On this honest bar, exactly **two** designs are credible, pose-verified G12D-selectives: `b3_gpu7_113`
(single_chain, ΔΔG −9.29 [−14.2, −4.3], bridge preserved at 2.98 Å) and `nb3_gpu4_132` (nanobody, −7.27
[−11.7, −2.8], 2.61 Å). They lead the submission. The gate stays a filter: the overall ranking is the
pre-registered weakest-objective ruler, and the final verdict on G12D-vs-WT is the wet-lab assay.

## Selection
The 20 are ranked by the north-star weakest-objective ruler, with the confirmatory gate acting only as a filter:
the two credible, pose-verified G12D-selectives (`b3_gpu7_113`, `nb3_gpu4_132`) are floated to the top; the
ruler-clean core follows in weakest-margin order; designs whose gate-selectivity rests on an over-docked pose are
kept only on their ruler merit and flagged (e.g. `nb3_gpu6_132`, the ruler leader at +0.583); and five
anti-selective designs (gate WT-favored on realistic poses) with positive ruler margins fill the last five slots
as explicit padding. This finalized set replaced an earlier locked 20 (overlap 8/20): the 12 dropped designs were
verified on the identical ruler to be seven platform-binders (negative weakest margin — they bind what the targets
share) plus five anti-selectives, and the locked set contained neither credible selective. True G12D-vs-WT is used
only to filter, never to rank, and remains the assay's call.

## Submitted designs
Ranked final set (`runs/submission.csv`; per-design screens + one-line reasons in `runs/submission_screens.csv`).
Ordered selectivity-evidence-first (the 2 credible MM-GBSA selectives lead), then by the weakest-margin ruler
balanced against novelty, pose-realism and expression. The set spans **two independent generators** — BoltzGen and
Genie3 (an orthogonal diffusion model; the five `genie3_*` designs = Genie3 backbones through the identical
funnel) — so the assayed top 10 (cap is 10 designs/submission) is diversified across both generators and both fold
families (single-chain miniprotein + VHH nanobody): 2 credible selectives + 5 BoltzGen + 3 Genie3. All 20 are
positive on the weakest-margin ruler (no anti-selective padding). Hydrophobic or novelty-risk designs are held in
reserve below the cap (disclosed).
Three screens per design (read within class): ESMFold **pLDDT**, **ipSAE** to the G12D complex, and mean
Kyte-Doolittle **hydropathy** (KD; <=0 soluble). `gate ddG` (kcal/mol, G12D - WTmut) is a *confirmatory* value,
NOT a rank, credible only on a preserved pose with a CI excluding 0 - tier-1 is the assay's call, not in-silico.

| # | design | class | pLDDT | ipSAE | KD | novelty | weakest | gate ddG [CI] |
|--:|--------|-------|------:|------:|---:|---------|--------:|--------------:|
| 1 | b3_gpu7_113 | single_chain | 94.000 | 0.808 | -0.237 | 0.768 | +0.471 | -9.29 [-14.2,-4.3] |
| 2 | nb3_gpu4_132 | nanobody | 81.000 | 0.616 | -0.216 | CDR-judged(HCDR3) | +0.266 | -7.27 [-11.7,-2.8] |
| 3 | nb3_gpu6_132 | nanobody | 95.000 | 0.642 | -0.331 | CDR-judged(HCDR3) | +0.583 | -11.72 [-15.6,-8.0] |
| 4 | genie3_8_m0 | single_chain | 94.000 | 0.646 | -0.501 | 0.840 | +0.492 | -1.96 [-10.3,+6.2] |
| 5 | b3_gpu7_181 | single_chain | 91.000 | 0.774 | -0.330 | 0.881 | +0.526 | +4.22 [-0.7,+8.8] |
| 6 | genie3_g4_121_m1 | single_chain | 92.000 | 0.546 | +0.171 | 0.682 | +0.423 | +2.58 [-3.5,+8.4] |
| 7 | nb3_gpu3_307 | nanobody | 89.000 | 0.538 | -0.156 | CDR-judged(HCDR3) | +0.460 | +2.93 [-6.0,+12.8] |
| 8 | b3_gpu4_211 | single_chain | 94.000 | 0.666 | +0.129 | 0.801 | +0.485 | +4.88 [-1.7,+11.6] |
| 9 | b3_gpu5_174 | single_chain | 89.000 | 0.729 | -0.151 | 0.864 | +0.489 | +1.67 [-6.1,+9.1] |
| 10 | genie3_g6_148_m1 | single_chain | 91.000 | 0.738 | -0.279 | 0.866 | +0.377 | -2.28 [-8.1,+3.6] |
| 11 | genie3_g5_72_m0 | single_chain | 93.000 | 0.700 | +0.779 | 0.893 | +0.388 | -1.56 [-7.7,+4.5] |
| 12 | nb3_gpu7_192 | nanobody | 88.000 | 0.446 | -0.234 | CDR-judged(HCDR3) | +0.405 | +4.79 [-2.5,+11.8] |
| 13 | genie3_g6_142_m1 | single_chain | 96.000 | 0.679 | +0.602 | 0.932 | +0.408 | -1.52 [-5.0,+1.8] |
| 14 | b3_gpu3_164 | single_chain | 92.000 | 0.773 | -0.738 | 0.946 | +0.423 | +4.81 [-1.6,+11.5] |
| 15 | nb3_gpu2_108 | nanobody | 90.000 | 0.645 | -0.151 | CDR-judged(HCDR3) | +0.346 | -5.11 [-13.7,+4.2] |
| 16 | nb3_gpu7_029 | nanobody | 92.000 | 0.620 | -0.137 | CDR-judged(HCDR3) | +0.324 | +0.38 [-5.8,+6.0] |
| 17 | b3_gpu4_161 | single_chain | 91.000 | 0.615 | -0.052 | 0.850 | +0.316 | -2.37 [-5.9,+1.0] |
| 18 | b2_gpu3_36 | single_chain | 90.000 | 0.657 | -0.290 | 0.932 | +0.246 | +0.41 [-4.1,+4.9] |
| 19 | b3_gpu6_132 | single_chain | 92.000 | 0.489 | -0.132 | 0.869 | +0.262 | +10.11 [-1.1,+19.8] |
| 20 | nb3_gpu6_432 | nanobody | 80.000 | 0.690 | -0.006 | CDR-judged(HCDR3) | +0.286 | +7.39 [-0.3,+14.8] |
