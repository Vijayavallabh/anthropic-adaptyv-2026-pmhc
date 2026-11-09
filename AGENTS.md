# AGENTS.md — working contract

De-novo, zero-shot binder design for the **KRAS G12D neoantigen** on **HLA-A\*11:01 + β2-microglobulin**
(Anthropic × Adaptyv 2026 **Challenge 5 / Track 3, pMHC**).

Read this first, then `progress.md` (newest-first running log) and `session-handoff.md` (where things stand now).

## Objective

Design ≤20 ranked de-novo binders that are **SELECTIVE for the G12D neoantigen peptide** and discriminate it from:
- **WT** `VVVGAGGVGK` — differs only at peptide position 6 (G12D's **Asp6**, which is **buried** and salt-bridged
  to HLA **Arg114**, ~8 Å² SASA). This single buried residue is the crux of the whole challenge.
- **Unrelated A\*11:01 epitopes** (ebna4 `AVFDRKSDAK`, atic `ASFKHWPFLK`).
- **Empty HLA** (peptide-free groove).
- A composition+anchor-matched **scramble** `VVGAVGDGVK` (tests sequence-reading vs platform-reading).

Target neoantigen: `VVVGADGVGK` (KRAS 7–16, P6 = D). Target definition: `configs/target.yaml`, `data/targets/`.

Submission: ≤20 designs, classes `{single_chain, nanobody, scfv, fab_kappa, fab_lambda, TCR}`, 10–250 aa,
schema `name,sequence,molecule_class` (see `runs/submission.csv`).

## North star (organizers' design philosophy — internalized)

Let **discernment, not strength alone**, guide the work. Recognize G12D on HLA-A\*11:01 while leaving the
**WT complex** and the **peptide-free MHC** untouched. Operating principles:

1. **Rank by the weakest objective, not the highest score.** A design discriminates only as well as its weakest
   "reject what they share" margin: `weakest = min(spec_scram, promisc_margin, bp−bh_e)` over
   {scramble, other A\*11:01 peptides, empty HLA}. Improve the weakest margin; do not worship composite `sel`.
   Lens: `scripts/weakest_objective.py` → `runs/campaign/weakest_objective.tsv`.
2. **Test every design against all three targets** (G12D, WT, empty). Begin simply; obey the rules.
3. **One convincing predicted pose is not proof of discrimination.** Co-fold gives a confident pose but is blind
   to the single buried P6 residue. Add complexity only when it brings clearer evidence.
4. **Diverse designs, honest reasoning.** A spread of bets across lineages; say what each design does and does not
   show. Computational confidence is a **hypothesis**, selection an **opportunity**, the **experiment the verdict**.

The recurring question for every design and every swap:
> **"What shows that this design recognizes the difference, rather than merely what the targets share?"**

Consistency check, NOT independent evidence (2026-11-04): because these margins are computed from the SAME co-fold
ipSAE scores that `sel` and the swap already used, the minimax lens agreeing with the swap is expected — re-slicing
one data source, not new proof. Its value is the ABSOLUTE sign: of the locked 20, the 7 designs with a *negative*
weakest margin (they bind the empty groove or an unrelated peptide ≥ G12D = read what the targets SHARE) are
exactly the DROP set, which shows *why* they are weak. Independent evidence requires an orthogonal source (a
different folder, physics, or the bench); treat every in-silico score as a hypothesis — the wet-lab is the verdict.

## Invariants (do not violate)

- **De-novo only, zero-shot only.** No seeding from known binders/TCRs/antibodies; no fine-tuning on the target.
  (Antibody/nanobody *framework* is allowed for the nanobody class; CDRs are de-novo.)
- **Upload is USER-GATED.** The Proteinbase portal upload/submission is the user's decision — never upload.
  `runs/submission.csv` is the finalized, portal-validated 20 (v8, 2026-11-09: the ruler+gate+pose set hardened by
  the expansion gate + a 5-pose co-fold ensemble; 12 BoltzGen + 8 Genie3, 14 single_chain + 6 nanobody; the
  2026-11-06 locked set and every re-rank checkpoint are backed up under `runs/submission*.bak.csv`).
- **Keep raw sequences in files, not chat.** Reference designs by name.
- **8× H100 local. GPUs 0,1 are FOREIGN** — never clobber them. Campaign uses GPUs 2–7. Verify with `nvidia-smi`,
  one process per GPU, cap CPU threads.
- **No AI attribution** in commits/PRs. Repo-local git identity is `Vijayavallabh` (see CLAUDE.md). Private repo.
- **The deciding axis (G12D-vs-WT) is a BENCH measurement — never RANKED in silico.** Co-fold is blind to the
  single buried residue and MPNN δ does not rank it (verified wash). The ensemble MM-GBSA gate (see the funnel) is
  a *confirmatory binary FILTER* on a pose-realistic shortlist, not a ranker: it may promote or flag a design, but
  the pre-registered weakest-objective ruler does the ordering. Never present an in-silico number as a RANK of
  G12D-vs-WT.

## The funnel (generate → fold → score → select)

1. **Generate** (`gen_campaign.sh`): BoltzGen (protein / nanobody / antibody-anything) + RFdiffusion1 + SolubleMPNN.
2. **Prep/triage** (`funnel_prep.sh`, `funnel_triage.sh`, `extract_pool.py`): sharded ESMFold monomer pLDDT →
   g12d-only 2-sample triage co-fold (`score_pmhc.py`) → per-lineage pLDDT/ipSAE cut (`funnel_select_panel.py`).
3. **Panel** (`funnel_panel.sh`): the TRUSTED 5-sample, **6-state** co-fold (`build_pepswap_cofold.py` for
   g12d/wt/scram/ebna4/atic + `build_design_cofold.py --states empty`), binder = chain **P**, pocket restraint on
   the peptide bulge `[[C,4],[C,6],[C,7],[C,8]]` max 8 Å. Runner: `run_boltz.sh` with `NOMSA=1 DIFF_SAMPLES=5`.
4. **Score all axes** (`funnel_score.sh` → `score_rfd_val_fast.py`, parallel ipSAE via `ipsae.py`):
   emits `name g12d wt scram ebna4 atic bh_e spec_scram promisc_margin`.
5. **Survivors** (`campaign_survivors.py`): generous selectivity gate → `grip` (peptide-contact fraction) +
   **MPNN δ** (`mpnn_differential.py`) + **novelty** (`robust_novelty.py`, foldseek structural TM).
6. **Assemble + select** (`assemble_final20.py --with-campaign`, `campaign_select.py`): rank by `sel`, catch
   Ig-folds/low-complexity, propose same-ruler swaps vs the locked 20.
7. **Confirmatory physics gate + pose-realism** (`scripts/gate/`, OpenMM GBn2 ensemble MM-GBSA): on a co-fold-stable
   shortlist, score ΔΔG(G12D − in-silico Asp6→Gly6 WTmut) with replica-bootstrap CIs (`gate_prep/run/score/analyze.py`),
   calibrated to recover the Poole ground truth and null a WT-vs-WT control (SELECTIVE iff ΔΔG ≤ −4 **and** CI excludes 0).
   **MANDATORY pose-realism check** (`scan_saltbridge_all.py`): a selective call counts only if the pose PRESERVES the
   native buried Asp6↔Arg114 bridge; over-docked poses (Asp6 swung out to grab the binder) fake selectivity and get no
   credit (`find_rescue_poses.py` re-gates any that have a preserved shard). `merge_and_emit.py` emits the final-20 —
   **the ruler ranks, the gate only filters.** GOTCHA: the ante-MMPBSA/sander path is corrupt here; use the OpenMM GBn2 path.

## Scoring axes (what each means)

| axis | definition | better |
|---|---|---|
| `spec_scram` | ipSAE(g12d) − ipSAE(scramble) — sequence-order specificity | higher |
| `promisc_margin` | ipSAE(g12d) − max(ipSAE(atic), ipSAE(ebna4)) — peptide-identity specificity | higher |
| `bh_e` | empty-HLA binding — peptide-DEPENDENCE (tier-2, **the major real discriminator**) | **lower** |
| `grip` | peptide-contact fraction of the binder interface | higher |
| `bp` | g12d ipSAE (raw affinity proxy) | higher |
| `esm` | ESMFold monomer pLDDT (foldability) | higher |
| `maxtm` | foldseek structural-TM to PDB — novelty proxy for the sequence-based gate | **lower** |
| `mpnnD` | ProteinMPNN differential logP(Asp)−logP(Gly) at buried P6 | orthogonal; **NEVER a gate** |
| `sel` | composite ranking score (a convenience aggregate, NOT the final selector) | higher |
| `weakest` | `min(spec_scram, promisc_margin, bp−bh_e)` — minimax discrimination across the 3 shared targets | **higher — the primary selection lens** |
| `gate_ΔΔG` | ensemble MM-GBSA ΔΔG(G12D − WTmut) — confirmatory G12D-vs-WT **FILTER** (only on a preserved pose, CI-excl-0) | more negative = G12D-selective; **a filter, never a rank** |
| `pose_realism` | native Asp6↔HLA-Arg114 salt bridge preserved (<4 Å) vs broken (over-dock artifact) | **preserved** = credible; broken = no gate credit |

## Verification / definition of done

- A design axis is only trusted on the **5-sample, 6-state** panel scored by `score_rfd_val_fast.py` — single
  sample is noise (gate on within-sample consistency + Cohen-d).
- A **portfolio swap** is valid only if BOTH sides are scored on the **identical pipeline/ruler** (same TSV schema,
  byte-spot-checked). A swap that trades a higher axis for a lower one is churn, not progress.
- **Select by the weakest objective, balanced with diversity** (north star): prefer designs robustly positive on
  all three discrimination margins over one-axis spikers with a high `sel`. A negative weakest margin means the
  design binds what the targets SHARE (empty groove or an unrelated peptide) — reject it. Never pick on `sel` alone.
- An orthogonal/never-a-gate axis (MPNN δ) only "corroborates" a change if scored on **both** portfolios same-ruler.
- The **G12D-vs-WT confirmatory gate** is trusted only when (a) calibrated (recovers the Poole ground-truth ΔΔG and
  nulls a WT-vs-WT control, noise floor ~1.9) and (b) on a **pose-realistic** co-fold (native Asp6 burial preserved).
  A credible selective is the intersection of **preserved pose AND CI-excludes-0**; an over-docked-pose selective call
  is an artifact — deny it gate credit and rank the design on the ruler. More replicas sharpen the number but never
  fix a wrong pose.
- Positive controls must fire (crystal binders 7PB2/7OW6 recover the buried Asp in the MPNN δ assay).
- Record evidence in `progress.md` with the background-task id and `rc`. Never claim a tool ran unless it ran.

## Environment & vendored deps

- Boltz-2 + Python: `/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/{boltz,python}` (external venv).
- Vendored IN-REPO under `tools/` (gitignored; rebuilt via `init.sh --tools`): foldseek + PDB DB, ProteinMPNN
  (`src` + `v_48_020` weights). `scripts/ipsae.py` and `scripts/run_boltz.sh` are vendored byte-identical copies
  (TFR sibling deps kept vanishing — the campaign is now self-contained).
- Known caveat: several scripts still carry hardcoded absolute paths to sibling repos / the boltz venv. The
  pipeline works as-is; a dynamic-root refactor is a tracked follow-up (see `session-handoff.md`).
