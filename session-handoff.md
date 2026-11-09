# session-handoff.md

Where things stand, for the next session. Newest state at top; full history in `progress.md`.

## As of 2026-11-09 (latest) — FINAL v8: expansion gate + complete 5-pose ensemble; 2 pose-robust + 3 net-leaning

The submission has advanced well past the 2026-11-06 state below. Arc since: applied the MM-GBSA gate (the only
judge of the buried G12D-vs-WT axis) across the ~2,000 paneled-but-un-gated designs (the blind co-fold ruler leaves
credibles un-gated at low ranks) → then hardened every gate-selective against co-fold POSE uncertainty on a full
5-pose ensemble (models 0–4). Net result (complete-data final; the 5-model ensemble is exhausted):
- **2 pose-ROBUST credibles** (G12D on 5/5 poses, never flip): `b3_gpu7_113` (BoltzGen, mean ΔΔG −5.8, ipSAE 0.75)
  and `genie3_g6_28_m0` (Genie3, mean −6.2; the expansion-gate discovery).
- **3 net-G12D-leaning selectives** (4/5 poses, one flip, disclosed): `genie3_g2_103_m1` (mean −7.3, strongest),
  `nb3_gpu4_132` (−3.3), and `genie3_g2_141_m1` (−4.8, #20 reserve: hydrophobic).
- **submission.csv = 12 BoltzGen + 8 Genie3, 14 single_chain + 6 nanobody.** Assayed top-10 = #1 b3_gpu7_113,
  #2 genie3_g6_28_m0, #3 genie3_g2_103_m1, #4 nb3_gpu4_132 (2 robust + 2 net-leaning) + 6 co-fold ruler designs.
  `b2_gpu3_36` (the 11-06 "#4") was dropped (weakest co-fold, no gate evidence).
- Honest ceiling: in-silico selectivity is pose-dependent/noisy — only the 2 designs are 5/5 pose-robust; the
  single buried-residue G12D-vs-WT call is still the **bench's**, never ranked by an in-silico number.
- Trail: `scripts/gate/rerank_v{4..8}.py`; pre-reg + addenda 1–4 in `docs/EXPANSION_GATE_PREREG.md`; docs
  (METHODS/SUBMISSION_SUMMARY/ELIGIBILITY) synced two-tier; details newest-first in `progress.md`.
- **Only remaining step = owner's Proteinbase upload (USER-GATED).** Upload all 20 as ONE collection in rank
  order; confirm the designated collection holds exactly those 20; eyeball a platform-computed pLDDT on each
  (watch the 6 nanobodies, ESMFold 80–88). No deadline extension: 2026-11-08 23:59 AoE (Nov 9 11:59 UTC).

---

## As of 2026-11-06 — ORTHOGONAL Genie3 run → 2-generator hedge in the assayed top-10

The devil's-advocate verdict's one conceded risk (all-BoltzGen monoculture) is now **resolved**: the user opted to
run an orthogonal generator, and it succeeded. **Genie3** (rebuilt from the official anthropics repo) generated 1200
backbones → PULCHRA full-bb → SolubleMPNN (97% foldable, median pLDDT 93) → g12d triage → the SAME 5-sample 6-state
panel + weakest ruler + MM-GBSA gate, all isolated under `runs/genie3/` (never touched `runs/campaign/`).
- **No 3rd credible selective** (honest): the top co-fold design (0.670, beats our best 0.583) was gate-**refuted**
  as WT-favored; the one gate-selective was an over-dock artifact; and a **12-rep deepening** of the two
  gate-*leaning* Genie3 designs showed the 6-rep −5.2/−5.3 were small-n noise (regressed to −2.3/−1.6, CI-incl-0).
  Credible selectives stay **2** (both BoltzGen, #1-2, 12-rep-confirmed). Screens/docs carry the 12-rep values.
- **But the orthogonal hedge is real:** 5 Genie3 designs are preserved-pose, positive-weakest, not-WT-favored.
  `scripts/gate/rerank_v3.py` promoted them — **3 into the assayed top-10** (`genie3_8_m0` 0.49, `genie3_g4_121_m1`
  0.42 novel, `genie3_g6_148_m1` 0.38 gate-leaning), 2 hydrophobic ones in reserve. New top-10 = 2 credible
  selectives + 5 BoltzGen + 3 Genie3 (two generators + both classes); the added Genie3 OUTRANK the displaced
  BoltzGen on the ruler = strict gain + diversity gain. All 20 now positive-weakest (dropped the WT-favored pads).
- **`runs/submission.csv` is the new hedged 20** (13 single + 7 nanobody); backups
  `runs/submission*.pre-genie3-2026-11-06.bak.csv` (and `*.pre-advocate-*`). Integrity audit re-passed. Docs synced.
- Genie3 infra (gitignored): `third_party/uplifting-biomolecular-modeling`, `weights/genie3`; scripts
  `setup_genie3_pmhc.sh`, `prep_genie3_pmhc.py`, `gen_genie3_pmhc.sh`, `build_genie3_fullbb_pmhc.py`,
  `funnel_genie3_pmhc.sh`, `gate/gate_genie3.sh`, `gate/rerank_v3.py`. PULCHRA at the `.claude-private/jobs/5045f83d`
  recon venv. `mpnn_binder.py` now points at vendored `tools/proteinmpnn`.
- **Pending (USER):** attach the evidence package if the portal allows, then Submit the 20. Upload USER-GATED.

## As of 2026-11-06 — devil's-advocate audit → novelty-aware re-rank

The user ran `/devil-advocate` on the finalized 20. A cold adversary's kill shot was **half right**: the prior order
did bury stronger survivors on our own weakest-margin ruler — but its naive "rank by weakest" fix (and the adversary)
**missed novelty**: the omitted high-weakest designs are mostly structural-novelty-risk (maxTM 0.95-0.98), which the
competition penalizes. So the fix was a **novelty-aware** multi-axis re-rank, not the adversary's.
- **`runs/submission.csv` re-ranked (`scripts/gate/rerank_v2.py`; backups `runs/submission*.pre-advocate-2026-11-06.bak.csv`).**
  5 swapped: IN `b3_gpu4_161`, `nb3_gpu7_029`, `b3_gpu3_164`, `nb3_gpu2_108`, `b3_gpu6_132`; OUT `b2_gpu7_33`,
  `nb3_gpu5_130`, `protein_0103`, `b2_gpu5_13`, `b2_gpu5_27`. **Assayed top-10 is a strict upgrade:** meanWeak
  0.407->0.433, min 0.141->0.316, **novelty-risk 1->0** (the 2 novelty-risk designs demoted to reserve #11-12);
  dropping `nb3_gpu5_130` also clears the one flagged near-dup pair. Now 12 single_chain + 8 nanobody; `#1-2` credible
  selectives unchanged; CRLF intact; integrity audit re-passed; docs (SUBMISSION_SUMMARY, METHODS) synced.
- **Verdict PROCEED on the re-ranked 20.** The one conceded attack (all-BoltzGen monoculture) has **no feasible +EV
  fix in the window**: no orthogonal generator is installed, install is slow/env-drift-risky, and the prior RFd
  attempt scored anti-selective. Submission spans 2 fold families (partial decorrelation); monoculture disclosed.
  Standing offer: attempt an orthogonal (RFd3/Genie) campaign on the 6 idle GPUs only if the user wants to risk the
  window on a low-probability diversity lottery.
- **Pending (USER):** same as below — attach the evidence package if the portal allows, then Submit the re-ranked
  `submission.csv`. Upload USER-GATED.

## As of 2026-11-06 (late) — selection-prompt-aligned re-rank + evidence package

The competition's published **design-selection prompt** (a Claude workflow) is now known: **cap 10 designs per
submission, taken in our ranked order, then graded globally**; priority **express+bind first**, then selectivity
evidence, novelty (4>3), diversity; **3 screens** (pLDDT, ipSAE, mean Kyte-Doolittle hydropathy); the selector
**reads the method description**. So only our **top ~10** matter, and our selectivity evidence is a differentiator.
- **`runs/submission.csv` re-ranked to a moderate lineage hedge** (`scripts/gate/rank_and_evidence.py`): top-10 =
  the 2 credible selectives (`b3_gpu7_113`, `nb3_gpu4_132`) + the 6 strongest co-fold-ruler designs + the 2 best
  **soluble independent-lineage** designs (`b2_gpu3_36` #4, `b2_gpu7_33` #10); weak/hydrophobic/debunked designs
  kept below the cut. Pure reorder (sequences byte-identical; ruler-order kept at
  `runs/submission.ruler-order-2026-11-06.bak.csv`).
- **Evidence package (publishable, neutral):** `docs/SUBMISSION_SUMMARY.md` (rubric-aligned cover doc) +
  `runs/submission_screens.csv` (per-design pLDDT/ipSAE/hydropathy/novelty + one-line reasons). `docs/METHODS.md`
  table rebuilt to the shipped order with screens.
- **First-principles backing:** deep-research (abstract math/physics/chem) validated the method and the ranking math
  — see [[ranked-submission-win-math-posterior-diversity-conjunctive]]. No new physics lever exists (buried-charge
  electrostatics angle returned nothing).
- **Adversarial self-audit done** (`scripts/gate/selector_audit.py`): ran the published selection prompt's own
  checks on our 20 — clean on all hard rules + set-aside flags (no Ig-V-domain misclassification: single_chain are
  61-85 aa; no near-duplicate in the top-10: the one 0.88 nanobody pair shares the VHH framework but has distinct
  HCDR3 0.55 with only one in the top-10; two mild disclosed within-class screen notes). `SUBMISSION_SUMMARY.md`
  gained an "Integrity and anticipated checks" section pre-empting the flag list.
- **Pending (USER):** if the portal accepts a method description, attach `SUBMISSION_SUMMARY.md` +
  `submission_screens.csv`; then Submit the (re-ranked) `submission.csv`. No design re-gen, no seeding.

## As of 2026-11-06

**Status: submission FINALIZED and portal-validated. The only remaining step is the user's gated portal submit.**

### What is in `runs/submission.csv` (the finalized 20)
The user chose the **"Recommended 20"** (2026-11-06) — the ruler+gate+pose-realism portfolio. It replaced the
earlier locked 20 (overlap was only 8/20); the prior set is preserved at `runs/submission.locked-2026-11-06.bak.csv`.
- 13 single_chain + 7 nanobody, rank-ordered, portal-parsed as **20/20 Passed, 0 needing fixes** (lengths +
  sequence ends byte-matched to the file).
- Rank structure: **#1–2 `b3_gpu7_113`, `nb3_gpu4_132`** = the two credible, pose-verified G12D-selectives;
  **#3 `nb3_gpu6_132`** tops the north-star ruler (0.583) but its gate-selectivity is a flagged over-dock artifact
  (no gate credit); **#4–15** ruler-ranked core; **#16–20** anti-selective padding (ranked last).
- Generator: `scripts/gate/merge_and_emit.py` → `runs/campaign/final20_two_axis_recommended.csv` →
  promoted to `runs/submission.csv`. Rationale: `runs/campaign/final20_two_axis_rationale.tsv`.

### The decisive new axis (since the 2026-11-04 handoff): an orthogonal physics gate + pose-realism
Co-fold is still blind to the buried P6 and MPNN δ is still a wash — but an **ensemble MM-GBSA physics gate**
(OpenMM GBn2, matched in-silico Asp6→Gly6 mutation, replica-bootstrap CIs; `scripts/gate/`) recovers a
**confirmatory** G12D-vs-WT signal. It is a **FILTER, never a ranker** (the pre-registered ruler still orders the
portfolio), so the invariant "G12D-vs-WT is a bench measurement, not an in-silico rank" **still holds**.
- Calibrated: recovered the Poole ground-truth matched-scaffold ΔΔG = −4.36 [−7.0,−1.6] (exp −4.9) and nulled a
  WT-vs-WT control (noise floor ~1.9). Criterion: SELECTIVE iff ΔΔG ≤ −4 **and** CI excludes 0.
- **MANDATORY pose-realism check** (`scripts/gate/scan_saltbridge_all.py` → `runs/campaign/gate/pose_realism.tsv`):
  the co-folder often **over-docks** — swings the buried Asp6 ~8 Å out of the groove to H-bond the binder — and the
  naive gate scores those as falsely selective. Only poses that PRESERVE the native Asp6↔HLA-Arg114 bridge
  (through-space discrimination) are credible. 42/58 preserved, 15/58 broken.
- **Pose-rescue** (re-gate over-docked selectives on a preserved shard): both rescuable ones (`nb3_gpu6_432`,
  `protein_0103`) went **null** on their realistic poses → their selectivity was the over-dock artifact, confirmed.
- **Result: credible G12D-selective count is DEFINITIVELY 2** (`b3_gpu7_113`, `nb3_gpu4_132`). Earlier "5 selectives"
  framing was over-docked artifact and has been corrected. Gate tables: `runs/campaign/gate/gate_results_*.tsv`.

### Pending (reserved for the USER)
- **The portal submit of `runs/submission.csv` to Proteinbase** — the user's to click (USER-GATED). The loaded set
  is validated and correct; deadline 2026-11-08 23:59 AoE (~2.5-day buffer).

### Eligibility / provenance (recorded 2026-11-06)
`docs/ELIGIBILITY_PROVENANCE.md` holds the de-novo justification for the finalized 20 under the organizers' Slack
clarifications (2026-11-04/05: constant framework + regenerated CDRs = de novo, contingent on the submission novelty
checker). Our 7 nanobodies are public VHH-framework + de-novo CDRs (not seeded); the 13 single_chain are de-novo
non-Ig. Portal prescreen passed all 20 — keep that result with the submission record. Verify directly (NOT settled by
the brief): current deadline + track allowance, and Modal/Claude credit balances + expiry.

### Next actions (non-gated, if asked)
- Optional "best-quality 20": the base-32 pool has only 15 ruler-clean, non-anti-selective designs; #16–20 are
  anti-selective padding. Vetting 5 ruler-clean designs from the expansion pool to replace the padding would need
  a short compute pass (the user declined this for now, chose the Recommended 20 as-is).
- Optional hardening: several `scripts/*.py` carry hardcoded absolute paths (boltz venv, sibling repos); the gate
  scripts (`scripts/gate/*.py`) likewise. Refactor to dynamic roots with a byte-identical regression check — not
  before the deadline.

## As of 2026-11-04

**Status: the whole in-silico funnel is exhausted. One decision is pending (the user's), then a gated upload.**

### What is locked / submitted
- `runs/submission.csv` = the **portal-accepted 20** (18 single_chain + 2 nanobody). Untouched. This stands
  unless the user chooses to update it.

### What is proposed (NOT uploaded)
- `runs/campaign/combined_submission.csv` = a **12-swap** portfolio from the b3/nb3 scale-up campaign. It is
  **portal-format-validated** (20/20 passed) and verified stronger than the locked 20 on every *measurable* axis:
  - selectivity proxies (sel 1.41–1.86 vs 0.44–1.22; much lower `bh_e` = better peptide-dependence),
  - **novelty** (removes 7 of the 8 `novelty_risk` designs in the locked 20 → 8 risk drops to 1),
  - developability parity, equal vetting (same campaign funnel/ruler).
- The deciding axis (**G12D-vs-WT**, the single buried residue) remains **un-rankable in silico** — co-fold is
  blind to it and MPNN δ is a verified wash. So no portfolio "maximizes" the win; the swap improves the
  measurable bets only.

### Selection lens — the north star (use this, not composite `sel`)
Rank by the **weakest discrimination margin** `min(spec_scram, promisc_margin, bp−bh_e)` (reject what the targets
SHARE — scramble, other peptides, empty HLA), balanced with diversity. Tool: `scripts/weakest_objective.py` →
`runs/campaign/weakest_objective.tsv`. Finding (2026-11-04): the proposed 20 are all positive on the weakest
margin; the **7 locked designs with a negative weakest margin are exactly the DROP set**. This is a **consistency
check**, not independent proof — the margins come from the same co-fold scores that chose the swap — so it explains
*why* the dropped designs are weak (they bind what the targets share) but does not predict lab behavior. The
wet-lab assay is the only verdict.

### Pending decision (reserved for the USER)
Choose one, then the (gated) portal upload is the user's to do:
- **(a)** finalize the full 12-swap (`combined_submission.csv`) — recommended; all 20 are positive-weakest.
- **(b)** a sharper **minimax refinement**: the proposed 20's own weakest links are retained incumbents
  (`protein_0103` weakest-rank 155/1943, `b2_gpu5_37` 164, `nanobody_0081` 84, `b2_gpu3_27` 40). Replacing the
  lowest-weakest retained designs with higher-weakest campaign survivors — while preserving lineage diversity and
  the one near-cousin-nanobody nit (nb3_gpu3_307 ~ nb3_gpu5_130, 0.88) and the one `novelty_risk` design
  (protein_0103, TM 0.912) — would yield a more balanced discriminator set. (Does not touch G12D-vs-WT, which
  stays a bench call.)
- **(c)** keep the locked 20 as-is (note: it carries 7 negative-weakest designs that bind what the targets share).

### Next actions (non-gated, if asked)
- If (b): run the diversity swap + the protein_0103-replacement search, regenerate a tightened
  `combined_submission.csv`, re-validate format.
- Optional hardening follow-up: several `scripts/*.py` carry hardcoded absolute paths to sibling repos / the
  boltz venv; refactor to dynamic repo-roots (see the TNF-repo hardening pattern) — do this with a byte-identical
  pipeline regression check, and not in a way that risks the working pipeline before the deadline.

### Environment notes
- 8× H100; **GPUs 0,1 FOREIGN** (never touch); campaign used 2–7, now free.
- Vendored in-repo (gitignored, rebuild via `init.sh --tools`): foldseek+PDB-DB, ProteinMPNN, ipsae.py, run_boltz.sh.
- Boltz-2 venv is external: `/home/prachh/v/sepiq-2026-challenge/.venv-boltz`.
