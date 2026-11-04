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

## On tier-1 selectivity
Co-folding cannot resolve the single-residue G12D-versus-WT difference (the predicted interface scores for
the two peptides are statistically indistinguishable), and the intrinsic selectivity is an intra-pMHC
electrostatic/conformational effect that is largely binder-independent. In-silico scores are therefore used
to rank the proxies for selectivity (peptide-shape specificity and peptide grip), while true G12D-versus-WT
discrimination is treated as a measurement for the experimental assay rather than an in-silico claim.

## Selection
The submitted set is front-loaded by the selectivity conjunction above and ordered so the strongest, most
confidently selective designs come first (the submission is ranked; only the top entries are expected to be
assayed). The top of the list spans distinct binding hypotheses — sequence-specificity-dominant designs, a
peptide-grip-dominant design, and two de novo nanobodies for class diversity — and is deliberately hedged on
structural novelty (dominated by novelty-safe designs, with the strongest high-TM binders retained lower
down). The two lowest-ranked entries are reserves that did not clear the promiscuity gate and are included
only to complete the list; they are not expected to be assayed.

## Submitted designs
Ranked final set (metrics are five-sample co-fold means; bh_e is the empty-HLA / peptide-dependence axis,
lower = better; max-TM is single-sequence ESMFold vs PDB, lower = more structurally novel). Tier-1
(G12D-vs-WT) is not an in-silico claim for any design (see above) — it is the experimental measurement.

| # | design | class | spec_scram | promisc_margin | bh_e | grip | ESM pLDDT | max-TM | rationale |
|--:|--------|-------|-----------:|---------------:|-----:|-----:|----------:|-------:|-----------|
| 1 | nanobody_0202 | nanobody | 0.49 | 0.44 | 0.20 | 0.33 | 0.91 | — (CDR-judged) | de novo CDR3 nanobody; high seq-specificity, clean tier-2, grips peptide |
| 2 | b2_gpu3_15 | single_chain | 0.40 | 0.59 | 0.12 | 0.17 | 0.89 | 0.86 | high seq-specificity, clean tier-2, novelty-safe |
| 3 | b2_gpu4_26 | single_chain | 0.27 | 0.41 | 0.20 | 0.26 | 0.95 | 0.83 | seq-specific, clean tier-2, novelty-safe |
| 4 | nanobody_0081 | nanobody | 0.33 | 0.42 | 0.35 | 0.38 | 0.86 | — (CDR-judged) | de novo CDR3 nanobody; seq-specific, grips peptide |
| 5 | b2_gpu3_27 | single_chain | 0.32 | 0.61 | 0.46 | 0.22 | 0.89 | 0.88 | seq-specific, high identity-margin, novelty-safe |
| 6 | protein_0103 | single_chain | 0.12 | 0.49 | 0.02 | 0.50 | 0.92 | 0.91 | strongest peptide grip + cleanest tier-2; novelty-risk |
| 7 | b2_gpu5_05 | single_chain | 0.36 | 0.27 | 0.41 | 0.18 | 0.89 | 0.86 | high seq-specificity, novelty-safe |
| 8 | b2_gpu5_37 | single_chain | 0.17 | 0.12 | 0.04 | 0.35 | 0.91 | 0.88 | clean tier-2, grips peptide, novelty-safe |
| 9 | b2_gpu7_33 | single_chain | 0.31 | 0.35 | 0.47 | 0.19 | 0.87 | 0.81 | seq-specific, best structural novelty |
| 10 | protein_0155 | single_chain | 0.42 | 0.48 | 0.75 | 0.22 | 0.89 | 0.89 | high seq-specificity (tier-2 weaker) |
| 11 | protein_0212 | single_chain | 0.23 | 0.18 | 0.51 | 0.16 | 0.81 | 0.88 | seq-specific, novelty-safe |
| 12 | protein_0073 | single_chain | 0.38 | 0.20 | 0.69 | 0.14 | 0.93 | 0.95 | high seq-specificity (tier-2 weaker; novelty-risk) |
| 13 | protein_0092 | single_chain | 0.16 | 0.14 | 0.67 | 0.28 | 0.86 | 0.90 | seq-specific, grips peptide (tier-2 weaker) |
| 14 | protein_0025 | single_chain | 0.23 | 0.29 | 0.83 | 0.17 | 0.87 | 0.94 | seq-specific (tier-2 weaker; novelty-risk) |
| 15 | b2_gpu5_13 | single_chain | 0.24 | 0.39 | 0.51 | 0.15 | 0.91 | 0.90 | seq-specific (novelty-risk) |
| 16 | b2_gpu3_36 | single_chain | 0.25 | 0.47 | 0.35 | 0.19 | 0.90 | 0.93 | seq-specific, moderate tier-2 (novelty-risk) |
| 17 | b2_gpu5_19 | single_chain | 0.19 | 0.19 | 0.07 | 0.34 | 0.83 | 0.94 | clean tier-2, grips peptide (novelty-risk) |
| 18 | b2_gpu5_27 | single_chain | 0.15 | 0.14 | 0.46 | 0.28 | 0.93 | 0.93 | seq-specific, grips peptide (novelty-risk) |
| 19 | rfd_des_173_m2 | single_chain | 0.36 | -0.12 | 0.05 | 0.29 | 0.85 | 0.60 | reserve (RFdiffusion; fails promiscuity gate) |
| 20 | b2_gpu7_02 | single_chain | 0.13 | -0.07 | 0.04 | 0.15 | 0.89 | 0.86 | reserve (fails promiscuity gate) |
