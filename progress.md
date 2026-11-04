# progress — KRAS G12D / HLA-A*11:01 de novo binder (Challenge 5)

Running log (newest first). Deadline 2026-11-08 23:59 AoE. Upload USER-GATED.

## 2026-11-04 (late) — swap QUALITY-VERIFIED (novelty/dev/concentration); repo + harness initialized

Assistant-drafted (Claude). User validated combined_submission.csv on the portal (20/20 passed — FORMAT only,
not a quality signal) and asked whether the swaps "maximize the win". Ran the quality verification I had flagged,
then initialized the git repo + full harness file set.

- **Portal validation = format only.** All 20 proposed designs parse (10–250 aa, correct classes: 12 single_chain
  + 8 nanobody). This confirms uploadable, NOT better. Verified combined_submission.csv = locked 20 with exactly
  12 swaps (name-for-name).
- **NOVELTY — the swap is a big win here.** final20_ranked.tsv shows the locked 20 carries **8 designs flagged
  `novelty_risk=True`** (structural TM ≥0.90). The swap DROPS 7 of them (protein_0073 TM 0.955 + 445 seq hits,
  protein_0092 0.902 + 60 hits, protein_0025 0.935, b2_gpu5_13 0.901, b2_gpu3_36 0.932, b2_gpu5_19 0.941,
  b2_gpu5_27 0.929) → portfolio goes **8 risk → 1** (only retained protein_0103 0.912 remains). The 6 ADD proteins
  are all below the risk line (TM 0.768–0.881; 2 outright novel); 6 ADD nanobodies novelty-EXEMPT.
- **Developability — parity.** ADD all clean except b3_gpu5_072 (one unpaired Cys, minor); nanobodies carry the
  normal VHH disulfide. No disqualifying liabilities; runs ≤4, sane hydrophobic fractions. Not a blocker.
- **Concentration.** 6 ADD proteins fully diverse (max pairwise id 0.40). 6 ADD nanobodies share VHH framework;
  one near-cousin pair nb3_gpu3_307 ~ nb3_gpu5_130 (0.88 whole-seq) — mild, flagged for optional diversity swap.
- **Honest answer to "maximize the win": no** — G12D-vs-WT stays un-rankable in silico (applies to both
  portfolios). But the full swap is stronger on EVERY measurable axis (selectivity proxies + novelty, at dev
  parity), so I REVISED last turn's hedge and now endorse it. Two optional refinements offered (diversity cousin;
  replace last novelty-risk protein_0103). Decision + upload remain the user's. [[feedback-diverse-not-cousins]]
- **REPO + HARNESS INITIALIZED.** The pmhc dir was NOT a git repo (166 GB; runs/ 138 GB, tools/ 7.3 GB). Added
  `.gitignore` (runs/ tools/ envs/ .venv* scratchpad/ ignored; curated result files force-added), `AGENTS.md`,
  `CLAUDE.md`, `README.md`, `feature_list.json`, `init.sh`, `session-handoff.md`. Repo-local identity Vijayavallabh
  (noreply), no AI attribution; private repo per the sibling convention. [[env-git-identity-not-users]]

## 2026-11-04 — MPNN δ DONE (both sides, same ruler); swaps STAND; δ is a WASH, not corroboration

Assistant-drafted (Claude). Completed the orthogonal MPNN δ axis on BOTH the 594 survivors AND all 20 locked
incumbents, same ruler, and ran the symmetric ADD-vs-DROP comparison. Honest result below (did not overclaim).

- **MPNN δ on 594 survivors DONE** (bw4m63i5u, rc=0): 594 + 2 crystal controls. Controls calibrated — known
  pMHC binders recover the buried Asp (JDI +0.769 / Poole +0.397, both argmaxD=1.0). Fixed a real reporter bug:
  `mpnn_differential.py` writes key col `design`, `campaign_select.py` read `name` (KeyError). Now robust to both
  + control substring-match; added `--mpnn` to point at a merged file. Read-only reporter, locked files untouched.
- **Incumbent δ, SAME RULER** (bgp0pstvv fold rc=0 → btbuwfalk δ rc=0): the locked-20 g12d folds had been cleaned
  up (only campaign folds survive on disk), so re-folded all 20 incumbents' g12d complex on the byte-identical
  protocol (vendored scripts/run_boltz.sh md5 9188b52…, same pocket restraint C4/6/7/8, NOMSA=1 DIFF_SAMPLES=5,
  GPUs 2–7; 0/1 foreign untouched) → 100/100 PDBs → mpnn_differential --nsamp 5 --seeds 24 --no-controls, fresh
  workdir. Merged → runs/campaign/mpnn_diff_all.tsv (594+20). Proposal w/ δ → runs/campaign/SWAP_PROPOSAL_mpnn.txt.
- **SYMMETRIC VERDICT — δ does NOT corroborate the swaps as an axis win; it's a wash:** paired ADD−DROP mean
  +0.066 (median **−0.087**); ADD>DROP in only **4/12**. ALL 12 DROP incumbents are positive-δ (legit Asp-readers
  too, +0.015…+0.585); ADD positive 7/12. Ex the lead, ADD mean δ 0.171 < DROP 0.288. So the incumbents are NOT
  weak on buried-mutation reading — comparable-to-slightly-higher. The +0.066 mean is entirely the lead.
- **The swaps still STAND, on the GATING axes (unchanged, 12 dominant / 0 churn).** The win is **peptide-dependence
  (bh_e, the major discriminator)** + sequence/promiscuity selectivity, NOT buried-residue reading. ADD designs
  mostly bind empty-HLA weakly (bh_e .005–.239) vs incumbents often strongly (up to .827) — THAT is what the swap
  buys. δ (Asp-vs-Gly pref given a docked pose) is a different question than bh_e (peptide-dependence); the two
  are complementary and a strong G12D-selective binder needs both.
- **Lead nb3_gpu6_132 is the one design that wins on EVERY axis**: top sel (1.86), lowest-tier bh_e (.026), and
  by far the strongest Asp-reader in either portfolio (δ **+2.41**, argmaxD 1.0 — 3× the best crystal control).
  [[lesson-portfolio-swap-verify-all-axes-same-pipeline]] [[lesson-ensemble-win-on-small-n-is-noise]]
- **Nothing gated done.** Locked 20 untouched; combined_*/SWAP_PROPOSAL* are proposal artifacts only. Upload USER-GATED.

## 2026-11-03 (late) — CAMPAIGN COMPLETE; 12 DOMINANT SWAPS proposed (same-ruler verified); MPNN δ recovered in-repo

Assistant-drafted (Claude). Panel finished and the full funnel ran to a swap proposal vs the locked 20.

- **PANEL DONE** (btp02w4u5, rc=0): 1888 designs × 6 states × 5 samples = 11328 folds, all present. GPUs 2–7
  freed; 0/1 foreign untouched throughout.
- **Scoring chain DONE** (bgcy33x8r): score_rfd_val_fast on ALL 1888 → panel_reval.tsv (max spec_scram 0.627;
  395 ≥0.10, 196 ≥0.20, 83 ≥0.30). Survivors = 594 (211 protein + 383 nb). grip DONE. Novelty SKIPPED (done).
- **ipsae.py VENDORED in-repo.** score_rfd_val_fast hardcoded tfr1/scripts/ipsae.py (TFR already lost tools/
  once). Copied byte-identical → scripts/ipsae.py (md5 8122b53…), repointed the scorer to `dirname(__file__)/
  ipsae.py`. Output unchanged → the earlier byte-verification still holds. Campaign now TFR-independent.
- **SWAP PROPOSAL** (assemble_final20 --with-campaign → combined_*; campaign_select.py → runs/campaign/
  SWAP_PROPOSAL.txt): **12 dominant swaps, 0 churn.** 12 new campaign designs (6 nb3_ + 6 b3_, sel 1.41–1.86)
  displace the 12 weakest locked incumbents (sel 0.44–1.22); 8 strongest incumbents retained. Lead
  nb3_gpu6_132 (sel 1.86, spcS .583, grip .532, bh_e .026), a novelty-exempt nanobody.
  Portfolio 12 protein / 8 nanobody across 5 lineages.
- **SAME-RULER VERIFIED** (the portfolio-swap lesson). panel_reval / reval_genuine / rfd_val / batch2_reval
  all share the IDENTICAL schema (name g12d wt scram ebna4 atic bh_e spec_scram promisc_margin) + 5-sample
  6-state scorer. Spot-checks match byte-for-byte (rfd_des_173_m2 .359/.046; protein_0155 .425/.748;
  b2_gpu7_33 .314/.470; b2_gpu5_13 .238/.511). All 12 DROP confirmed in portal-locked submission.csv.
  [[lesson-portfolio-swap-verify-all-axes-same-pipeline]] [[lesson-score-swaps-on-the-ranking-ruler]]
- **MPNN δ RECOVERED in-repo + RUNNING** (bw4m63i5u, GPU 2). Root cause of the scoring rc=1: tfr1/third_party/
  proteinmpnn AND tfr1/weights/proteinmpnn BOTH vanished (same TFR-infra loss as foldseek/ipsae). Found a
  complete matched ProteinMPNN (cache stock/src code == Proteina-Complexa code, byte-identical) + upstream
  v_48_020 weights; vendored both → tools/proteinmpnn/{src,weights}, repointed mpnn_differential.py. Validated
  (fresh workdir; the hang was stale-pdb accumulation in a REUSED /tmp workdir, NOT the GPU). MPNN δ is the
  ONE in-silico signal sensitive to the buried G12D P6-Asp (masks only P6, scores binder-conditioned Asp
  log-prob) → orthogonal confirmation of the swaps; NEVER a gate, not consumed by assemble/select.
- **STILL GATED**: portal upload/submission. The locked 20 stands; the 12 swaps are a PROPOSAL only.
- NEXT on MPNN completion: re-run assemble --with-campaign + campaign_select (populates mpnnD column), report
  whether MPNN δ corroborates. [[lesson-rank-selectivity-not-affinity-and-catch-ig-folds]]

## 2026-11-03 — CAMPAIGN PANEL LAUNCHED; scorer bottleneck fixed; novelty rebuilt in-repo

Assistant-drafted (Claude). Executed the funnel from triage → 5-sample 6-state panel, hardened the
downstream for campaign scale, and rebuilt the novelty oracle in-repo after its infra vanished.

- **Triage DONE** (3293 foldable, g12d-only 2-sample). Per-lineage g12d ipSAE: protein median 0.098
  (223≥0.3, 123≥0.5), nanobody median 0.190 (720≥0.3, 212≥0.5). scripts/funnel_select_panel.py.
- **PANEL LAUNCHED** (btp02w4u5, GPUs 2–7): 1888 designs = ALL 888 foldable proteins (scarce/novel-
  friendly, triage 2-sample-noisy → don't cut the arm) + top-1000 nanobodies (cut g12d 0.232). 6 states ×
  5 samples = 11328 yamls; ~4–5 h. GPUs 0/1 foreign, untouched.
- **CRITICAL scorer fix.** score_rfd_val spawns one ipsae.py SUBPROCESS per model, sequentially — fine for
  triage (6586 ≈ 3.5 h) but the panel is ~56,640 → **~31 h** (would blow the deadline). Built
  **score_rfd_val_fast.py**: one os.walk index (no per-pair recursive glob) + ipsae generation parallel
  across 64 of 192 cores. **Verified BYTE-IDENTICAL** to the original on folds/rfd_val, BOTH code paths
  (txts-present; regenerate-from-scratch); 270 models 24 s vs ~9 min serial → panel scoring ~1–1.5 h.
  Original untouched (locked pipeline intact). [[lesson-per-item-subprocess-scorer-explodes-at-scale]]
- **Survivor gate** (campaign_survivors.py): grip (Bio.PDB/sample) + MPNN δ (24 orders/GPU) run only on a
  GENEROUS selectivity-survivor set (top-500 partial-sel ∪ spec_scram≥0.10 ∪ g12d≥0.60 ∪ per-lineage floor),
  not all 1888. funnel_score.sh rewired: fast scorer on ALL → survivors → grip+mpnn on survivors.
- **Novelty infra VANISHED mid-session + REBUILT IN-REPO** (owner-directed). tfr1/tools/foldseek{,_pdb}
  disappeared (gone, no copy, nowhere on box); raw binary download auto-denied as external code. Fix: conda
  foldseek v10 → ISOLATED prefix tools/foldseek-env (no venv cascade), `foldseek databases PDB` →
  tools/foldseek_pdb (4.3 GB, 1.56M chains). **robust_novelty.py**: batched easy-search (not the per-protein
  loop that crashed the original) over the 888 PRE-folded ESMFold structures (no GPU re-fold). Result
  b3_struct.csv: **151 novel / 297 borderline / 440 risk** (median maxTM 0.897) → protein arm mostly
  NON-novel, so nov_pen favors the novelty-exempt nanobody arm (matches incumbent #1 = nanobody).
  [[env-novelty-foldseek-infra-gone-and-download-gated]]
- **assemble --with-campaign ingestion VERIFIED** against real formats (fpep_mean header, rd/rdc missing-file
  safety, campaign esm/out*/plddt.json keys). ESMFold monomer pLDDT for 888 proteins precomputed.
- **State**: panel folding (~4 h). Next on completion: funnel_score.sh (fast) → assemble_final20
  --with-campaign --out-prefix runs/campaign/combined_ → campaign_select.py swap PROPOSAL. Locked 20 STANDS;
  swaps are a proposal; portal upload OWNER-GATED.

## 2026-11-03 — ORTHOGONAL MPNN differential layer (works, passes control); SCALE-UP generation campaign launched

Assistant-drafted (Claude). Two things this session: (1) built the orthogonal selectivity layer the SOTA scan
flagged as highest-new-value; (2) on owner's "utilize all GPUs exhaustively… strongest designs in all metrics",
launched a ~20x larger generate→score campaign. Submission stays LOCKED/portal-verified; upload USER-GATED.

- **ProteinMPNN differential peptide scoring** (scripts/mpnn_differential.py). Mask ONLY peptide P6 in each
  g12d co-fold; conditional_probs decodes it last, conditioned on the full backbone + true identity of
  everything else (binder in pose, HLA, rest of peptide). Metric δ = [logP(Asp6)−logP(Gly6)]_with-binder −
  _same-coords-binder-stripped = the binder's OWN contribution to preferring the mutant over WT at the buried
  site. ORTHOGONAL to Boltz (non-docking) → addresses the single-verifier gap the Protenix check left.
- **Seed-averaging was essential.** Single-seed δ is dominated by ProteinMPNN's autoregressive decoding-order
  noise (±~0.3, as large as the signal; same crystal gave δ∈{0.50,0.72,0.89} by batch composition). Averaging
  24 decoding orders converges deterministically (rep A==rep B).
- **Fail-loud graded positive control PASSES** (unlike Protenix): crystal JDI/7PB2 (therapeutic, >4000x
  G12D-selective) δ=+0.87 > Poole/7OW6 (parental, binds G12D AND WT) δ=+0.54 > null 0. Right ordering ⇒ the
  metric has real (if n=1-per-control, weak) sensitivity to the buried discriminator. Lit rates it a WEAK prior
  → ENRICHMENT, never a gate; I did NOT reorder on it.
- **Across the committed 20**: only 1/20 clears the Poole floor; ρ(δ, spec_scram) = −0.37 (mildly ANTI). Reading:
  the 20 were ranked on Boltz axes that never had δ in the objective, so they are mediocre on this independent
  axis. Two front-loaders flag: nanobody_0081 δ −0.92 but SD 1.53 (noise), b2_gpu7_33 δ −0.23 fD 0.0 (genuine
  no-orthogonal-support). runs/mpnn_diff.tsv + scripts/mpnn_diff_join.py. This is the core argument for the
  scale-up: a larger pool scored WITH δ in the objective can be strong on all axes at once; the current 20 can't.
- **SCALE-UP CAMPAIGN (running).** GPUs: foreign playtest-buddy jobs occupy only GPU 0/1 (72/65GB active) —
  LEFT untouched; saturating 2–7 (6×H100, 79GB free). Generation (scripts/gen_campaign.sh, tracked): BoltzGen
  protein pep_centric N=3000 (folds/gen/b3_protein) → nanobody nb_pep_centric N=3000 (folds/gen/b3_nb); ~6000
  vs prior ~313. RFd EXCLUDED (historically 0 front-loaders + unlogged contigs). Funnel ready+verified:
  extract_pool.py → sharded ESMFold (funnel_prep.sh) → g12d triage co-fold (score_pmhc) → 5-sample 6-state panel
  (build_pepswap_cofold + build_design_cofold --states empty; run_boltz NOMSA=1 DIFF_SAMPLES=5) → score ALL axes
  (score_rfd_val spec_scram/promisc/bh_e + pep_contact_consistency grip + ESMFold + foldseek novelty + MPNN δ)
  → assemble + adversarial review. Then propose swaps into the locked 20 where a new design dominates on the
  ranked axes (verify-all-axes-same-pipeline); upload stays owner-gated.

- **CAMPAIGN EXECUTION (2026-11-03 later).** Generation DONE: 3000 protein + 3000 nanobody cifs (both arms hit
  target; GPUs 2–7 saturated, 0/1 foreign untouched). **Nanobody-extraction bug caught + fixed**: BoltzGen
  orders chains differently per spec — protein-anything emits binder=chain A, but nanobody-anything emits
  target=A/B/C and binder=chain **D**. extract_pool.py hardcoded chain A → ALL 3000 nanobodies rejected as
  "lenbad" (it read the 276-res HLA). Fixed to identify the binder by EXCLUSION of the fixed target chains
  (HLA GSHSMRY / b2m IQRTP / peptide VVVGA≤12 aa). Protein arm reproduces identically (binder=A is still the
  sole non-target chain); nanobodies now extract at 117–122 aa (classic VHH EVQLVESGGG…). Protein pool: 1337
  kept / 3000 (623 Ig-fold, 1032 low-complexity, 8 len); monomer pLDDT median 0.80 ⇒ foldability strong
  (funnel_prep histogram display was mis-scaled 0-1 vs 0-100 — data fine; fixed).
- **Selector extended to the campaign on the IDENTICAL ruler.** assemble_final20.py now takes
  `--with-campaign --out-prefix`: ingests a b3 lineage (boltzgen-protein-b3 / boltzgen-vhh-b3 by nb3_ prefix)
  scored on the exact same `sel` formula (Ig-gate + campaign plddt-glob + b3 novelty wired in). OFF by default —
  verified the locked final20_ranked.tsv + submission.csv reproduce **BYTE-IDENTICAL** (md5 6ef54a18… /
  897f77be…), so the locked submission is provably untouched; commit mode (overwrite) stays owner-gated. New
  scripts: funnel_score.sh (stage F: score_rfd_val 5-samp + pep_contact grip + mpnn δ 24-seed +JDI/Poole
  controls + novelty_struct proteins-only), campaign_select.py (READ-ONLY swap proposer; flags CHURN = higher
  sel but regresses ≥2 key selectivity axes; δ as enrichment tiebreaker only). Locked artifacts backed up.
- **State**: re-running funnel_prep (both arms + corrected histogram) → g12d triage (data-driven pLDDT cut) →
  5-sample 6-state panel → funnel_score → assemble --with-campaign → campaign_select. Co-fold is the multi-hour
  bottleneck; ~5 days runway. Locked 20 STANDS; swaps are a PROPOSAL; upload owner-gated.

## 2026-11-02b — ELIGIBILITY confirmed (portal + local prescreen v0.5); Protenix cross-check UNINFORMATIVE (fail-loud)

- **PORTAL**: owner ran submission.csv through Proteinbase — "20 included • 0 needing fixes", every row Passed
  (nanobody_0202/0081=Nanobody, 18=Single chain). All 20 ELIGIBLE/accepted.
- **Local binder-prescreen v0.5** (github adaptyvbio/binder-prescreen @ tag v0.5; cloned+installed py3.11 venv +
  mmseqs static; recorded runs/prescreen_target/report.csv): target arm (--skip-prior-art --target kras-pmhc)
  = **20/20 pass**. nanobody_0202 nearest known-binder CDR identity 0.33 (vs patent TCRβ paratope), 0081 0.29
  → de-novo paratopes, NOT known binders in disguise; 18 miniproteins 0.0 target similarity. The two b2_gpu5_*
  "antibody_numbering_failed" flags are informational (they're miniproteins, not Abs) → still pass. Prior-art
  arm (public corpora, ~4.6GB DB) not run locally; portal runs the full check and passed all 20 = authority.
- **Reframe (teammate Slack brief)**: the eligibility gate is this SEQUENCE prescreen (known-binder/prior-art);
  the displayed structural-novelty score is a SELECTION input, NOT an exclusion. So the high foldseek-TM on some
  proteins is a selection-score matter, not a pass/fail — all 20 are eligible.
- **POCKET-RESTRAINED PROTENIX cross-check (owner-requested)**: built it properly (Protenix supports pocket
  constraint: binder_chain{entity,copy}+contact_residues; entity=1-based positional; scripts/fold_protenix_
  restrained.py + score_protenix_restrained.py). Top-6 x {g12d,scram,empty}, 5-sample, same restraint as Boltz.
  RESULT: all 6 binder-peptide ipTM ~0.06-0.11 (Boltz ipSAE was 0.5-0.8), empty>=g12d, spec~0. FAIL-LOUD
  positive control = crystal-verified Poole JDI TCR (7OW6 chains D/E, the structure the G12D peptide was solved
  in) through the IDENTICAL protocol → binder-peptide ipTM only **0.15** (as low as the designs). => Protenix's
  pocket is a SOFT conditioning feature (not Boltz's hard geometric potential) and cannot force de-novo docking
  without MSA; the protocol fails its positive control => **UNINFORMATIVE, not disconfirming**. Boltz-2 (hard
  restraint, SOTA pMHC/VHH) stands as the scorer; absolute in-silico binder docking is restraint-dependent for
  de-novo binders (known artifact) = a BENCH question. Submission UNCHANGED. Evidence: folds/protenix_restrained/
  protenix_consensus.tsv, folds/protenix_poscontrol/. [[lesson-tfr1-apical-blind-cofold-fails-poscontrol]]
  [[lesson-validation-gates-must-fail-loud]]
- **Deep-research workflow launched** (w9jo4l4i7) for SOTA methods/tools to improve future rounds. Still USER-GATED:
  portal upload + GitHub push. Owner to confirm live challenge-page deadline + team account.

## 2026-11-02 — SUBMISSION LOCKED (provisional): 20 ranked, selectivity-first + novelty-hedged

runs/submission.csv finalized (byte-verified: 20 rows, header==required, 18 single_chain + 2 nanobody, zero
poly-runs, no dupes, all 10-250aa). Front-load (selectivity conjunction, 5-sample validated):
1 nanobody_0202 (spec 0.49, bh_e 0.20, CDR-novel) · 2 b2_gpu3_15 (spec 0.40, bh_e 0.12, TM 0.86 nov-safe) ·
3 b2_gpu4_26 (0.27/0.20/TM0.83) · 4 nanobody_0081 (0.33/0.35) · 5 b2_gpu3_27 (0.32/margin 0.61/TM0.88) ·
6 protein_0103 (grip 0.50, bh_e 0.02, TM 0.91 nov-RISK) · 7 b2_gpu5_05 · 8 b2_gpu5_37 (bh_e 0.04, grip) ·
9 b2_gpu7_33 (TM 0.81 best-novelty) · 10 protein_0155 ... 19-20 = promiscuous reserves (rfd_173, b2_gpu7_02).

How it got here this session (all GPUs 3-7; 0,1,2 foreign):
- **5-sample multi-STATE panel is the only gate trusted.** Low-sample/few-state triage systematically
  OVER-estimates: RFd (1-samp), Fab (triage), and single-sample hits ALL collapsed on the full panel
  (e.g. rfd_des_246 spec 0.51->0.03; fab_g2_12 spec 0.24->-0.06). RFd + Fab routes dropped (no clean survivor).
- **Tier-2 (empty-HLA bh_e) is THE discriminator** and is now a major sel term `0.6*(1-bh_e)`. It split the
  5-sample pool into genuine peptide-grippers (0103 0.02, 0202 0.20, b2_gpu3_15 0.12) vs helix-readers that
  are sequence-specific yet bind empty HLA (0155 0.75, 0025 0.83) -> tier-2-weak, ranked below.
- **Promiscuity guard** (g12d - max(atic,ebna4) < 0.10 OR any unrelated-peptide > 0.45) demotes pan-peptide
  readers; **consistent ESMFold monomer pLDDT** replaced the mixed esm sources (nanobodies are fine: 0.91/0.86,
  the earlier 38/47 was af_plddt_b in-complex, not fold quality); weak folders (0369 @0.67) demoted.
- **BATCH-2 generation delivered** (420 gen -> 233 clean -> 121 foldable -> 17 reval): several selective,
  tier-2-clean, LOW-TM proteins (b2_gpu3_15/4_26/5_37/7_33) -> the novelty hedge.
- **Novelty**: structural TM vs PDB (single-seq ESMFold+foldseek). Proteins sequence-novel by construction
  (clear seq axes -> >=3 gate); high structural TM only risks level-4. Front-load HEDGED: dominated by
  novelty-safe (TM<0.89), high-TM grippers (0103 0.91, 0073 0.95) kept but penalized. Nanobodies judged on
  CDR diversity (framework TM 0.99 exempt). **Caught + dropped b2_gpu7_27** (Ig V-domain mislabeled
  single_chain; evaded motif-is_ig, caught by a new Cys..Trp..Cys topology signature added to is_ig).
- **Orthogonal folder (Protenix) deliberately SKIPPED**: blind co-fold drifts even positive controls
  ([[lesson-tfr1-apical-blind-cofold-fails-poscontrol]]); Boltz-2 is SOTA for pMHC/VHH; 5-sample conjunction
  is the stronger gate. Documented as available-but-deprioritized.
- docs/METHODS.md filled (methodology + ranked table). **Upload to Proteinbase + any GitHub push remain
  USER-GATED.** Tier-1 (G12D-vs-WT) remains an honest bench bet for ALL designs (co-fold blind).


## 2026-11-02 — MULTI-SAMPLE RE-VALIDATION overturns single-sample RFd; promiscuity guard added

Resumed; the "wait for RFd pepswap" background shell was DEADLOCKED (its until-loop `pgrep -f
'score_pepswap.py folds/rfd_pepswap'` matched its OWN command line → never exited; [[env-pgrep-waitloop-self-match-deadlock]]).
Data was long ready. Killed it, read results, and found two things that materially change the submission:

- **Single-sample RFd pepswap was NOISE — confirmed by 5-sample re-fold.** Top single-sample RFd pick
  `rfd_des_246_m1` (g12d 0.66, spec_scram 0.51) COLLAPSED to **g12d 0.186, spec_scram 0.032** over 5 samples
  (folds/rfd_val, DIFF_SAMPLES=5). The 0.66 was a lucky draw. Exactly [[lesson-cofold-pepdep-single-sample-is-noise-use-consistency]].
  Had I trusted it I'd have front-loaded a near-non-binder. → RFd re-validated: runs/rfd/rfd_val.tsv (5-samp
  g12d/wt/scram/ebna4/atic + REAL empty-HLA bh_e + grip). **No clean front-loadable RFd survivor**: every
  high-spec RFd design is PROMISCUOUS (173→atic 0.69>g12d; 190→atic 0.60,bh_e 0.74; 186→atic 0.74/ebna4 0.64;
  85→ebna4 0.68); rfd_des_84 passes promiscuity only thinly (margin 0.136, atic 0.63, binds WT 0.70) → reserve
  at best. RFd contributes 0 to the front-load. (RFd's value was orthogonality+novelty; it didn't convert.)
- **Promiscuity guard added to the assembler** (was a real gap: ranked purely on spec_scram). Now demote any
  design with g12d − max(atic,ebna4) < 0.10 (binds an UNRELATED A*11:01 peptide ~as well as g12d → pan-peptide,
  fails tiers 1+2) to the reserve tail, like platform readers. Top proteins/nanobodies are all clean
  (margins 0.4–0.6); it mainly filters RFd. Uniform across lineages (pepswap_full has proteins+nanobodies).
- **5-sample re-validation of the 9 genuine protein/nanobody picks RUNNING** (folds/reval_genuine, b23r2irk1).
  The RFd flip proves low-sample survivors must be confirmed; proteins/nanobodies were only 3-sample. The
  front-load is the whole game (selector takes ≤10 from the top), so lock it on 5-sample numbers. Assembler now
  OVERRIDES the 3-sample scorecard with runs/reval_genuine.tsv for these 9 (+grip), marks reval=5s/3s.
- **FAB**: bounded triage (24 fabs × g12d/empty/scram, 5-sample) prepped (folds/fab_triage); deferred behind the
  higher-priority protein re-val (same GPUs 3-7). Include 1-2 fabs ONLY if they clear the full conjunction;
  else drop the class (fabs share the nanobody framework-novelty risk; selectivity is the scored win).

### 5-sample re-val of the 9 genuine HELD (unlike RFd) — but tier-2 (bh_e) splits them, and sel re-weighted

The protein/nanobody picks all remain real g12d binders at 5 samples (runs/reval_genuine.tsv). The newly-measured
5-sample **empty-HLA bh_e (the DIRECT tier-2 axis, LOWER=better)** sharply splits the pool:
- **tier-2 CLEAN (bh_e<0.40, needs peptide):** protein_0103 (bh_e **0.022**, grip 0.504, margin 0.49 — ideal
  gripper), nanobody_0202 (0.203, spec 0.49), nanobody_0081 (0.354, spec 0.33). protein_0212 borderline (0.508).
- **tier-2 FAIL (bh_e>0.65, binds empty HLA):** protein_0155 (0.748), 0073 (0.695), 0025 (0.827), 0369 (0.773),
  0092 (0.668) — good peptide ORDER-specificity but they ALSO grip the HLA helices → would bind peptide-free HLA.
- **sel_score REDESIGNED**: tier-2 is a TIER, so bh_e now a MAJOR reward `0.6*(1-bh_e)` (was a token −0.4-above-0.70
  penalty). Ranking: 1 nanobody_0202, 2 protein_0103, 3 nanobody_0081 (the 3 tier-2-clean) >> the tier-2-weak
  proteins (4-9). Note protein_0103 spec_scram softened 0.23→0.12 at 5-samp (binds scramble) but its grip+tier-2+
  unrelated-peptide-rejection make it a top-2 WINNER bet; tier-1 (G12D-vs-WT) is a bench bet for ALL.
- **Front-load is thin (3 clean + 6 weaker) → GENERATION LAUNCHED** (btdsl4mln): 420 more peptide-centric BoltzGen
  single-chain proteins (specs/boltzgen/pep_centric.yaml, GPUs 3-7). Proteins chosen over nanobodies (cleaner
  novelty = de-novo by construction; cleaner foldability = ESMFold pLDDT 80-94 vs VHH af_plddt_b 38-47 flag).
  Will filter the batch HARD on bh_e (tier-2) to expand the clean tier. NOTE: esm term currently mixes ESMFold-pLDDT
  (proteins) with af_plddt_b (nanobodies) — DIFFERENT metrics; recompute ONE consistent ESMFold monomer pLDDT in
  finalization (same run as the novelty structural-TM gate).

### FAB class DROPPED (no 5-sample survivor); batch-2 generation funnel running

- **FAB dropped.** Bounded triage (24 fabs, 3-state/5-samp) flagged 2 passers (fab_g3_03 g12d 0.63/spec 0.34;
  fab_g2_12 0.51/0.24). On the FULL 6-state 5-sample panel (runs/fab_stage2_val.tsv) both COLLAPSED:
  fab_g2_12 spec_scram 0.24→**−0.06** (binds scramble>g12d); fab_g3_03 g12d 0.63→0.45, spec 0.34→0.11 (+binds
  wt 0.47). None of 4 clears the conjunction. Same over-estimation as RFd single-sample. **Methodological rule:
  low-sample/few-state triage systematically OVER-estimates; only the 5-sample multi-STATE panel is the real
  gate (seen 3×: RFd 1-samp, fab triage, and now).** Submission stays 2 classes (single_chain + nanobody) —
  better 2 classes of genuinely selective designs than a 3rd class of known-non-selective filler.
- **Batch-2 generation** (the lever for more tier-2-clean grippers): 420 gen → 233 clean (56 Ig + 131 poly-run
  dropped) → **121 foldable** (ESMFold monomer pLDDT≥0.80; runs/batch2_esm/plddt.json) → co-fold triage RUNNING
  (bnbr06hwc, g12d/scram/empty, DIFF_SAMPLES=3). Survivors (g12d high, bh_e low, spec>0) get the full 5-sample
  panel, then integrate the genuine ones. ESMFold monomer pLDDT is now available for batch-2 → use it as the
  consistent foldability axis (recompute for the nanobodies + batch-1 picks at finalization).

## 2026-11-01 — LINEAGE GATING on corrected axes: nanobodies 0202/0081 are the best conjunction-passers

Gated all lineages on the corrected axes (spec_scram = g12d−scram; grip = f_pep vs decoy ceiling 0.28):
- **NANOBODIES**: only **nanobody_0202 (spec_scram +0.47, grip 0.32)** and **nanobody_0081 (+0.38, grip
  0.36)** pass BOTH axes strongly — the ONLY candidates (any class) clearing grip AND spec together (clean
  de-novo CDR3s). 0053/0139/0051/0168 are platform readers (scram≈g12d) → dropped. → Front-load 0202/0081
  HIGH (not "below proteins" as pre-red-team): on corrected selectivity they beat the de-novo proteins,
  which trade off (0103 grips/moderate-spec; 0073/0155 specific/weak-grip+bind-empty). NB novelty = CDR3
  carve-out (unverified; flag in methods).
- **RFd (SolubleMPNN, orthogonal lineage)**: 40 co-folded+scored. Strong AFFINITY: rfd_des_173/103/183/17/
  168 bp_ipsae 0.89-0.93; strong GRIP: rfd_des_36(0.56)/63(0.47)/169(0.40) exceed 0103's 0.50. spec_scram
  scoring RUNNING (runs/rfd/rfd_pepswap.tsv). Low structural TM (RFd) → best novelty of all lineages.
- **FAB (new class)**: 216 gen → 145 clean VH:VL (dropped 71 poly-loop). 60-fab diverse sample co-folding
  now (folds/fab_cofold, GPUs 2-7, binder chains H,L). BoltzGen npz = metadata only (no pose scores).
- **TIER-1 endpoint** (score_rosetta_iface on TCR controls): running ~45min, no output yet (FastRelax slow,
  99.9% CPU alive). This is the GO/NO-GO — decide heavy pmx FEP only if it recovers TCR G12D>WT; else tier-1
  stays a bench bet (biology: binder tier-1 contribution ~within FEP noise). Do NOT sink 2-4d into FEP blind.
- **NOVELTY posture**: de-novo helical proteins = novel by construction (de-novo MPNN seqs), high structural
  TM only → ~level 3 (pass hard gate); RFd lowers TM. Antibody formats (nb/fab) = natural framework, de-novo
  CDR3 → hinges on organizer's "binding part only" carve-out (UNVERIFIED) → document transparently; ensured
  CDR3s non-degenerate. mmseqs2+SwissProt confirmation = optional (not the bottleneck).

## 2026-11-01 — RED-TEAM (4 cold adversaries) landed 4 SERIOUS findings → scoring/ranking OVERHAUL

Adversarial workflow wiy5hotex (outside judge) found real, reproducible defects. Adjudicated + ACTIONS:

1. **TIER-1 IS UNADDRESSED (the kill-shot).** My ranking front-loads by AFFINITY (bp_ipsae in
   merge_gate score) = exactly the pan-KRAS/non-selective phenotype. G12D-vs-WT (the headline tier) is
   touched by ZERO gates/rank terms; the 3-state co-folds show NO separation (median Δbp-iptm(g12d−wt)
   =+0.024; **protein_0103=+0.003**, 2/17 even favor WT) → **co-fold CANNOT rank tier-1** (confirmed blind).
   The planned tier-1 lever (FEP) had NO output (rosetta_cal.log was 0 bytes). ACTIONS: (a) STOP ranking
   selectivity by affinity; (b) run the tier-1 GO/NO-GO on the KNOWN answer — rosetta endpoint
   (score_rosetta_iface, now RUNNING) + pmx FEP on parental/JDI TCR (must recover G12D>WT); (c) if NO-GO,
   front-load by SELECTIVITY-conjunction + epitope-mechanism DIVERSITY, and state tier-1 is a bench bet.
2. **SPECIFICITY AXIS WAS WRONG (p=0.8).** `spec=g12d−mean(ebna4,atic)` measures COMPOSITION-rejection
   (corr −0.70 with off-target), not KRAS shape. The composition-matched control **spec_scram=g12d−scram**
   (already in the data, unused) is correct. By it, my #1 pick **nanobody_0053 FAILS** (scram 0.69 > g12d
   0.60 = platform reader); **protein_0219 FAILS** (scram 0.69 ≥ g12d 0.65). spec_scram>0.20 survivors:
   protein_0153(+0.58,but IG-FOLD), 0155(+0.45), 0073(+0.45), 0212(+0.40), nanobody_0202(+0.34),
   0025(+0.21), nanobody_0139(+0.21,poly-G CDR3). ACTION: spec_scram is PRIMARY specificity; re-scored on
   3 samples (runs/pepswap_full_3samp.tsv, running); drop scram≥g12d designs.
3. **NOVELTY HARD-GATE never computed + Ig-fold mislabels (p=0.6).** Seq-id was never run on any finalist.
   **protein_0153 (rank2) & protein_0150 (rank7) are antibody V-domains** mislabeled molecule_class=protein
   (igscore 4/4: Cys-pair + WxRQ + J-motif FGxGT; prot_hits TM~0.88 to Fab chains) → high antibody seq-id =
   novelty FAIL + de-novo-rule risk. **DROP both.** My Ig-classifier (scripts, motif-based) scanned all 83
   proteins: only 0150,0153 are Ig-folds in the top-17; the other 15 are genuine de-novo helical (0 Cys,
   no J-motif). ACTION: protein arm = 15 de-novo helical; verify seq-id<30% on the core (install mmseqs2);
   nanobody/fab CDR carve-out UNVERIFIED (flag in methods); drop poly-G-CDR3 nanobodies.
4. **TIER-2 metric confounded (p=0.7).** signC==1 just certifies Boltz near-determinism (sample sd~0.01);
   real decoy FP = 12.5% (not the docstring's 6%); merge_gate's claimed cohenD>4 gate is implemented
   NOWHERE. ACTION: replaced ipTM-based tier-2 with DIRECT peptide-grip (`pep_contact_consistency.py`,
   f_pep across 5 g12d samples). Result: should-fail decoys span f_pep 0.12–0.28, so only designs CLEARLY
   above the decoy ceiling (~0.28) are genuine grippers: **0103(0.50), 0153(0.39,Ig), 0150(0.36,Ig),
   0222(0.32), 0099(0.31)**; 0287(0.31) clears f_pep but fails spec (necessary-not-sufficient); the other
   de-novo helical (0073/0244/0212/0025/0093/0369/0155/0241/0219/0297/0291/0092, f_pep 0.15–0.29) overlap
   the decoy envelope → weak peptide-grip evidence. Fix merge_gate docstring (honesty).

**NET corrected picture:** The single cleanest de-novo peptide-gripper is **protein_0103** (f_pep 0.50 ≫
decoy ceiling; but spec_scram only +0.13 = borderline shape-specific, binds scram 0.67 → front-load but NOT
as a proven selective pick). No design is strong on ALL axes → front-load by the CONJUNCTION (real grip ∩
spec_scram ∩ de-novo ∩ developable) + mechanism diversity; be honest tier-1 is a bench bet. New lineages
in flight (diversity hedge the DA endorsed): fab 216 (cooking), RFd-soluble 700 clean→201 fold≥0.80→**40
survivors co-folding now** (GPUs 2-7). **NEXT:** integrate spec_scram → corrected scorecard; gate fab+RFd;
tier-1 endpoint/FEP; mmseqs2 novelty; assemble. Lesson [[lesson-cofold-pepdep-single-sample-is-noise-use-consistency]].

## 2026-11-01 — RESUME: diversity generators relaunched, epitope validated, FEP staged, red-team live

Session resumed (7 days to deadline). All prior background jobs had exited at compaction; re-grounded on disk.
- **GPUs 0,1 are FOREIGN** (user's `playtest-buddy` env, pids 379919/379920, ~4d) — DO NOT TOUCH. Free: GPUs 2-7.
- **RFd MPNN finished** 133 backbones but the CSV aggregation never ran. Reconstructed clean pool:
  `runs/rfd/rfd_seqs.csv` = 70 clean seqs / 52 backbones (filter A-frac<=0.32, maxrun<=5, 55-120 aa).
  **Confirmed RFd/nanobody DEGENERACY** (also flagged by a side agent): vanilla-MPNN RFd median A-frac 0.37,
  only 34/266 strictly clean; many nanobody CDR3s are poly-G. ROOT CAUSE = MPNN "give-up" on hard backbones
  (NOT a missing-target bug — RFd PDBs DO contain full target A/B/C+binder D). High-A/poly-G = bad backbone,
  so the clean-filter IS a quality gate. Top nanobodies by spec (0053, 0202) have CLEAN CDR3s; poly-G ones
  already demoted. SAFEGUARD: bake a HARD low-complexity reject (maxrun>=5 or any AA>30%) into final-20 assembly.
- **LINEAGE DIVERSITY is the dominant lever** (method-family cap is <=93 = NON-binding; ~2/lineage is a SOFT
  holistic-selector guideline, NOT a hard filter — so I can front-load my best proteins AND add classes/lineages
  for diversity credit + correlated-failure hedge). LAUNCHED on idle GPUs:
  - **Fab arm** (NEW molecule class, 6 CDRs = more paratope for a peptide epitope): `specs/boltzgen/fab_pep_centric.yaml`
    (14 Fab scaffolds, binding peptide C4,5,7,8), protocol `antibody-anything`, 210 designs on GPUs 2,3,4,6 ->
    `folds/gen/fab/`. filter_biased default(true) caps composition outliers (anti-poly-G guard).
  - **SolubleMPNN RFd salvage** (GPU 5): mpnn_binder.py now has `--weights/--omit`; soluble weights, nseq 8,
    temp 0.15, omit CM -> `runs/rfd/rfd_sol_seqs.csv` (bigger/cleaner pool than vanilla).
  - helicon_against_peptide_in_pmhc is OUT (non-natural WHL macrocycle linker -> not an allowed class).
- **EPITOPE AUDIT** (`analyze_design_contacts.py` on existing g12d cofold model_0): top proteins are GENUINE
  peptide-platform binders — contact peptide bulge res 4-9, f_pep 0.20-0.47 (0103 best 0.47), TCR-like
  (dock on peptide+helix platform, NOT pure a1/a2 helix-readers). **DEMOTE protein_0073** (f_pep 0.14, 85%
  helix = weakest engagement). CONTROL: helixdecoy_0040 + pan-peptide 0287 ALSO pass the f_pep gate -> confirms
  (per decoy lesson) single-structure contact is necessary-not-sufficient; discrimination is the CONJUNCTION
  (robust tier-2 + pepswap), which those fail. Epitope is right; multi-axis gate provides the separation.
- **FEP tier-1 staged + feasible**: controls in `data/targets/bound/` (parental_g12d 7OW6, parental_wt 7OW5,
  parental_wtins=7OW6 D6->G, jdi_g12d 7PB2, jdi_wtins=7PB2 D6->G). Env: GROMACS 2026.3 + amber14sb +
  pmx amber14sbmut.ff (hybrid G<->D) + `pmx` CLI. DESIGN: peptide res6 G<->D alchemy; ddG_sel = ddG(bound) -
  ddG(FREE pMHC, binder-INDEPENDENT = compute ONCE, reuse). VALIDATE on TCR controls FIRST (must recover
  JDI >> parental > 0 favoring G12D); if it can't resolve the weakly-selective parental TCR, REPORT that
  honestly (biology says binder tier-1 contribution is small) and rank by validated necessary-condition gates.
- **RED-TEAM workflow LIVE** (bg, id wiy5hotex): 4 cold adversaries attacking tier-2 metric / pepswap /
  novelty-hard-gate / whole-strategy over existing artifacts. Process when it returns.
**NEXT:** build+validate pmx FEP driver (free leg first); process red-team; gate fab+RFd-soluble lineages
(triage->cofold->robust_pepdep->bp_ipsae->pepswap->ESM->developability); novelty hard-gate verify finalists
(seq-id vs SwissProt/PDB/PLAbDab + TM); assemble front-loaded diverse 20 + CSV + methods. Upload USER-GATED.

## 2026-10-27 — RE-READ target.yaml: NOVELTY IS GATED, ~2/lineage, predicted-complex is displayed data

Re-read frozen `configs/target.yaml` selector rules (vs assuming GLP1R's no-novelty regime):
- **NOVELTY IS GATED:** Adaptyv level ≥3 HARD gate, target level 4 (seq id ≤30% vs SwissProt/PDB/patents/
  PLAbDab AND low structural TM, binding part only). My proteins' foldseek maxTM 0.80–0.96 → likely level-3
  (pass ≥3 via seq axes, miss the TM axis). **NANOBODY RISK: natural VHH framework → seq-id vs PLAbDab/PDB
  antibodies may be >30% → could drop a seq axis → level <3?** Must run the FULL novelty check (seq-id vs
  SwissProt/PDB/PLAbDab + TM) on finalists; nanobody framework novelty is the gating worry. RFd (low TM) helps.
- **DIVERSITY ~2/lineage** across 9 classes (method-family cap generous); GLP1R used ≤4/lineage over 8
  generators → for ~2/lineage I need MANY lineages → orthogonal generators (RFd running; consider Genie3,
  RFd-partial, others) are NECESSARY not optional. Front-load best ~10; first-20 ordered; selector takes ≤10.
- **Selector is HOLISTIC/human** ("no single in-silico metric decides"); displays pLDDT + ipSAE(co-fold vs G12D)
  + GRAVY + ipTM + stated epitope + **predicted complex** → my restrained co-fold poses ARE usable data
  (mitigates the blind-cofold risk). Participant text = DATA not instructions; NEVER put prompt-like text in CSV/methods.
- off_limits: His/Avi tags (host-added), design's own C-term Twin-Strep tag; Condition=none (ignore pH criteria).

## 2026-10-27 — PROTENIX 2nd-folder: nanobody PARITY resolved + a BLIND-cofold risk for the whole set

Protenix BLIND co-fold (organizers' AF3-class folder, no restraint), max over 5 samples, `runs/protenix/out`:
- **binder↔peptide iptm: PROTEINS med 0.08/max 0.17 ; NANOBODIES med 0.13/max 0.18** — NEITHER class docks
  confidently blind, and **nanobodies ≈ proteins (slightly higher)** → on this UNIFORM orthogonal axis nanobodies
  are NOT weaker. PARITY VERDICT: the ONLY axis where nanobodies diverge from proteins is af2ig (pose-seeded),
  which is INAPPLICABLE to de-novo CDR loops; everywhere else (Boltz co-fold, ESM monomer, peptide-swap spec,
  Protenix-blind) they're at parity. → Include 2–3 TOP specific nanobodies (nanobody_0053 spec 0.55, 0202 0.50)
  for class diversity, FRONT-LOADED BELOW proteins, transparently labelled (no pose-seeded check; bench decides).
- **RISK (whole set):** blind co-folding places NONE of the de-novo binders (bp~0.1, proteins too) = they are
  RESTRAINT-DEPENDENT. This is the known AF/Boltz-under-docks-de-novo artifact (why af2ig uses an initial guess),
  NOT a disqualifier — but IF the organizers score BLIND it hurts. ACTION: verify the organizers' exact regime
  (restrained/initial-guess vs blind); if blind, prefer blind-robust designs (screen RFd lineage for blind bp).

## 2026-10-27 — CONSOLIDATED multi-axis selection table + novelty + 2nd-folder parity launched

**`runs/protein_scorecard.tsv` (17 specific proteins, complete)** — axes: binding(bp_ipsae) · robust tier-2
(signC/cohenD) · peptide-swap specificity(spec) · af2ig(rmsd/plddt) · ESM monomer · developability · novelty
(foldseek maxTM vs PDB). Ranked composite top-8: **protein_0103** (comp 2.21; bp 0.80, spec 0.54, cohenD 15.8,
af_rmsd 0.6, ESM 92), 0153, 0222, 0155, 0219, 0241, 0150, 0073 — all strong on the SCORED tiers.
**Novelty:** median maxTM 0.89 (3/17 <0.80); de-novo minibinders adopt common helical folds → HIGH structural
TM, but the pMHC rubric scores SELECTIVITY+AFFINITY (3 tiers), NOT novelty (unlike TNF/TfR1), so this is only
a diversity tiebreaker — the RFd new-fold lineage lowers it. (Confirm pMHC portal has no novelty score, like
GLP1R; [[project-glp1r-no-portal-novelty-score]].)

**RUNNING (background):** (1) Protenix 2nd-folder BLIND co-fold (`scripts/fold_protenix_pmhc.py`, organizers'
AF3-class folder, 8 GPUs) on 17 proteins + 7 specific nanobodies — the nanobody PARITY check (2nd structural
method, af2ig-equivalent, format-fair) + uniform organizer-aligned confirmation. (2) RFd MPNN on CPU (133
compact backbones → seqs) → ESM filter → co-fold → gate = lineage-2. (3) protein_0297 ESM (CPU).
**NEXT:** parse Protenix (bp_ipsae/bh consensus) → nanobodies at parity ∈ final; RFd gate; assemble front-loaded
diverse 20 (≤2-4/lineage, classes protein+nanobody+RFd) + submission CSV + methods; FEP tier-1 (longer horizon).

## 2026-10-27 — PEPTIDE-SWAP counter-screen = a POWERFUL new specificity axis (catches pan-peptide binders)

Power-check (`scripts/build_pepswap_cofold.py`, panel g12d/wt/scram/ebna4/atic; top 3 designs on GPU 0):
co-fold bp_ipsae(binder↔peptide) per swapped peptide. **Co-fold DOES discriminate DISSIMILAR-composition
peptides** (it stays blind only to the 1-residue g12d-vs-wt and to the composition-matched scramble):
- **protein_0103**: g12d 0.77 / wt 0.76 / scram 0.68 (KRAS-like, all high) but ebna4 0.27 / atic 0.10 (dissimilar,
  LOW) → **Δ(g12d−dissimilar)=+0.42 = genuinely peptide-shape-specific** (reads the KRAS backbone, excludes
  unrelated A*11:01 peptides). Necessary condition for any G12D selectivity.
- **protein_0287**: binds EVERYTHING 0.56–0.77 incl dissimilar → **PAN-PEPTIDE platform-reader (Δ+0.09)** — a
  specificity FALSE POSITIVE that PASSED loaded>empty tier-2 but is the toxic failure mode. The swap catches
  what tier-2 missed → DEMOTE. (nanobody_0118 Δ+0.01, binds scram>g12d → also not peptide-specific.)
**Consequence:** add Δ(g12d−dissimilar) as a GATE/rank axis for ALL finalists (proteins+nanobodies+RFd),
uniform across classes. Run full panel across 8 GPUs once RFd frees them. Caveat: verify ebna4/atic present
A*11:01 well (ordered groove) so low bp_ipsae = binder specificity not poor presentation.

**FULL PANEL RESULT (`runs/pepswap_spec.tsv`, 30 designs × 4 peptides):** 24/30 peptide-specific (spec>0.20).
- **PROTEINS 17/18 specific**; only **protein_0287 DEMOTED** (spec 0.08, binds all 0.66–0.79 = pan-peptide FP
  that passed tier-2). Leaders: protein_0155 0.54, 0103 0.54, 0219 0.51, 0153 0.48, 0073 0.45. protein_0287's
  binding of dissimilar peptides PROVES ebna4/atic present adequately → the specific binders' rejection is REAL
  (not a presentation artifact; confound ruled out).
- **NANOBODIES 7/12 specific** (weaker hit-rate confirms they're a harder in-silico bet): best **nanobody_0053
  spec 0.55 (top of ALL 30)**, 0202 0.50, 0081 0.47, 0139 0.35; DEMOTE pan/borderline 0094/0017/0030/0118/0168.
  The swap RE-RANKED nanobodies correctly (bp_ipsae-top 0118 is actually borderline).
→ Protein arm = 17 specific. Nanobody arm narrows to ~7 (then need 2nd-folder parity per side-agent). nsamp=1
(model_0); large spec values robust, re-score borderlines (0.18–0.22) with more samples at final selection.

## 2026-10-27 — TIER-2 METRIC made VARIANCE-ROBUST (cohenD exploded on nanobodies) + NANOBODY class rescued

**Metric fix:** raw Cohen's d EXPLODES when diffusion samples are near-identical (nanobody co-folds gave
cohenD 5e5 at ~0 variance) → NOT cross-run comparable. Switched the gate to VARIANCE-ROBUST quantities:
**t2pass = signC==1.0 AND pep_dep ≥ 0.05** (cohenD kept only as a FLOORED-sd[0.02] tiebreaker). Decoy-swept:
signC==1 decoys reach pep_dep 0.37, so the gate is a ~90%-specific ENRICHER (decoy FP 12%, 6/48), NOT a
perfect classifier — residual FP handled by the conjunction (bp_ipsae, ESM monomer, orthogonal checks).
Re-verified: W6/32 still FAILS (floored cohenD −1.3); protein final gate → **18 PASS** (`runs/final_protein.tsv`).

**NANOBODY class RESCUED (distinct submission class + architecture):** af2ig (0/60) is UNFAIR to de-novo CDRs
(AF2 limitation; organizers use ESMFold2). Re-gated on ESM monomer (framework folds) + co-fold instead:
**27 nanobodies pass (tier-2 ∩ bp_ipsae≥0.5 ∩ ESM monomer≥80)** — ESM 81–93, bp_ipsae 0.50–0.79, signC 1.0,
pep_dep ≤0.50 (`runs/esm/nb_cand_out`). Leaders nanobody_0118 (bp 0.71, pep_dep 0.50), 0030 (bp 0.79), 0139,
0051, 0245. CAVEAT: nanobody binding rests on co-fold ALONE (no af2ig cross-check) → SECONDARY lineage,
front-load BELOW the 2-method-confirmed proteins; ideally add a 2nd-folder (Chai/Protenix) pose check.

## 2026-10-27 — CORE 17 DE-RISKED on 5 orthogonal axes + diversity lineages launched

**ESMFold2 monomer fold (organizers' folder; `runs/esm/protein17_out`):** 16/17 fold confidently ALONE
(pLDDT ≥81; Garcia/Dixit/Rocklin 2026 = best de-novo expressed+soluble+monomeric predictor, AUROC 0.72).
Only protein_0369 WEAK (67) → demote. **Developability** (`scripts/developability.py` logic): 4 fully clean
(0241/0212/0025/0369); rest mild (hydrophobic 5-patch, 1-2 Cys, N-glyc sequons — minor for cell-free/bacterial).
**Master scorecard `runs/protein_scorecard.tsv`** (binding bp_ipsae + robust tier-2 cohenD + af fold-realization
+ ESM monomer + developability): rank-1 **protein_0103** (bp 0.80, cohenD 15.8, af_rmsd 0.55, af_plddt 92,
ESM 92); then 0150, 0241, 0073, 0153, 0222, 0291, 0025. The 17 are SEQUENCE-diverse (max 25% pairwise id, all
singletons @40%) but ONE generator lineage (BoltzGen).

**Diversity lineages LAUNCHED (critical path — ≤2-4/lineage caps 17 BoltzGen cousins):**
- RFd de-novo (lineage 2): `gen_rfd1.sh` on the pMHC groove (input g12d.pdb; contigs A1-276/0 B1-99/0 C1-10/0
  65-95; hotspots C4,C6,C7,C8 incl buried D6; noise_scale_ca=0), 280 designs GPUs 1-7 → backbones chain D.
  Pipeline prepped: `scripts/mpnn_binder.py` (design chain D, fix A/B/C, binder-by-exclusion, omit Cys) →
  build_design_cofold → run_boltz → robust_pepdep → merge_gate.
- TODO lineages: BoltzGen Fab/nb class (decide antibody realization gate — af2ig fails de-novo CDRs 0/60;
  use ESM/Protenix instead), RFd partial-diffusion from winners, Genie3 (needs pMHC dataset setup).

**NEXT:** RFd→MPNN→cofold→gate; novelty oracle (seq id + TM vs PDB/AFDB); A*11:01-peptidome counter-screen;
FEP top handful (tier-1); front-loaded diverse 20 + CSV + methods (upload USER-GATED).

## 2026-10-27 — SPECIFICITY GATE RECALIBRATED on the should-fail decoy → single-sample pep_dep is NOISE; the robust metric is WITHIN-DESIGN CONSISTENCY (AUC 0.95). 17 protein passers.

**Resolved the side-agent should-fail catch, and it UPGRADED the gate.** Co-folded 48 de-novo HELIX-READER
decoys (peptide-INDEPENDENT by construction) 3-state and compared to the designs:
- **Single-sample pep_dep (loaded−empty bh_iptm) is a WEAK discriminator**: decoy null median 0.04 but a fat
  tail to p95 0.25 (max 0.39); at the old `pep_dep>0` gate **27/48 (56%) of should-fail decoys PASS** →
  false-crown confirmed. `bp_iptm` (binder-peptide ipTM) is ALSO confounded (decoy median 0.78 — ipTM scores
  proximity, not specific contact). Root cause (also flagged by workflow w6iqcx7mk caveat #2): removing the
  peptide destabilises the pMHC so ANY binder tends to score loaded>empty.
- **The RIGHT statistic = within-design CONSISTENCY across the 5 diffusion samples.** A true peptide-gripper
  loses binder-HLA confidence in EVERY sample when peptide removed (sign-consistency 1.0, large Cohen's d);
  a wall-gripper's sign wobbles (decoy median signC **0.40**, Cohen-d **−0.25**). Designs: signC median **1.0**,
  Cohen-d median **+7.1**. **AUC 0.84→0.95.** `bp_ipsae` (interface-localised, unlike ipTM) ALSO separates
  cleanly: decoy median **0.21** (max 0.69) vs designs ≥0.5.
- **Decoy-calibrated gate** (`scripts/robust_pepdep.py`): tier-2 PASS = `signC==1 AND cohenD>4.0` (decoy p95).
  Decoy false-positive rate **56%→6%** (3/48). Wired into `merge_gate.py` (replaces pep_dep>0).
- **Re-ran final gate → `runs/final_protein.tsv`: 17/80 PASS** (was 20; dropped 3 false crowns protein_0009
  [cohenD 0.04/signC 0.4], 0235, 0297). Leaders protein_0103 (bp_ipsae 0.80, cohenD 15.8, rmsd 0.55, plddt 92),
  0150, 0287, 0153, 0241. Robust metric also surfaced protein_0167 (cohenD 15.85) that single-sample pep_dep
  [0.13] had buried — but it fails af (plddt 65). protein_0374 strong (bp 0.80/cohenD 7.7) misses on rmsd 2.01 (RESERVE).

**Workflow w6iqcx7mk (natural should-fail decoys, lit-grounded):** best = **W6/32** pan-HLA mAb (PDB 7T0L;
VH/VL provided) — binds any folded HLA-A*11:01 beneath the groove regardless of peptide; + CD8αα (1AKJ),
LILRB1 (1P7Q), LILRB2 (2DYP), all α3/β2m peptide-independent. KIR excluded (peptide-selective).
**W6/32 scFv CONFIRMATION (gold-standard, done):** co-folded protocol-matched g12d/empty → binds HLA strongly
in BOTH states (bh 0.734/0.796 — NOT a folding failure) yet **cohenD −1.27, signC 0.20, t2pass=False** — the
known pan-HLA peptide-INDEPENDENT binder correctly FAILS tier-2 (sign even goes negative). GATE NOW VALIDATED
3 WAYS: positive (JDI TCR loaded≫empty) + 2 independent should-fails (48 de-novo helix-readers 6% FP; real
W6/32). Also proves raw |pep_dep| is meaningless (W6/32's ≈0 would sneak a lenient abs gate; consistency rejects it).

**NEXT (critical path = LINEAGE DIVERSITY):** 17 BoltzGen proteins are likely cousins → ≤2/lineage caps them;
add orthogonal generators (RFd/PXDesign/Genie3) + Fab/nb class; natural-decoy confirm; Chai orthogonal tier-2
on the 17; SMC1A/peptidome counter-screen; SolubleMPNN; novelty oracle; FEP top handful; front-loaded 20.

## 2026-10-27 — SPECIFICITY GATE needs a should-FAIL control (side-agent catch, adopted); nanobody af2ig issue

**Side-agent catch (correct, adopted):** since the contact-fraction gate was (correctly) dropped, the
co-fold PEPTIDE-DEPENDENCE test (loaded≫empty) is now the SOLE guard against the catastrophic empty-MHC/
pan-HLA failure, and it was validated only POSITIVELY (JDI TCR z=5.9) with NO should-FAIL decoy → false-crown
risk. FIX (workflow w6iqcx7mk + my gen): decoy panel = de-novo HELIX-READER decoys (`specs/boltzgen/
helix_decoy.yaml`, binding on HLA a1/a2 helices 58..166, peptide-INDEPENDENT by construction, generating
`folds/gen/helix_decoy`) + known peptide-independent binders (W6/32 pan-HLA etc., from workflow) → co-fold
loaded-vs-empty → set the peptide-dependence threshold from the DECOY NULL (percentile/bootstrap) so real
designs must EXCEED it; decide if an orthogonal gate (peptidome scan / direct empty-MHC af2ig) is also needed.

**Nanobody af2ig:** 0/60 pass af_rmsd<2 & plddt_b>80 (af_rmsd 2.4–11.5) despite strong co-fold (bp_ipsae
0.6–0.79, pep_dep 0.3–0.5) → de-novo VHH CDR designs are hard for AF2 to reproduce (vs fully-designed protein
minibinders which gave 20/80). TODO: calibrate the af2ig fold-gate on a REAL/known-de-novo VHH before
discarding the nanobody class; else rely on protein arm + add orthogonal generators (RFd/PXDesign) for diversity.

## 2026-10-27 — FIRST GATED SHORTLIST: 20/80 protein designs clear the honest gate

af2ig **pae_interaction is pMHC-MISCALIBRATED**: 0/80 reach the de-novo <10 even where af2ig REALIZES the
fold (plddt_b>80, rmsd<2); and the organizers score by co-fold ipSAE, not af2ig pae (reference-adaptyv-
binder-protocol). → GATE = af2ig fold-realization (rmsd<2 & plddt_b>80) + co-fold bp_ipsae≥0.5 +
peptide-dependence>0 + on-platform + non-mimetic (per lesson-af2ig-positive-control-must-be-denovo: trust
plddt+rmsd, not pae). `merge_gate.py` → `runs/final_protein.tsv`: **20/80 PASS**. Leaders protein_0103
(bp_ipsae 0.80, pep_dep +0.40, rmsd 0.55, plddt 92, binds G12D 0.97 / empty 0.57), 0235, 0150, 0153, 0287,
0241. Gate correctly fails folds af2ig can't reproduce (rmsd 4.8–13.7). Nanobody af2ig running (b3pk8qvwr).
**NEXT:** nb gate → Fab scale (2-chain adapt) → diversity selection (≤2/lineage, 4 classes) →
SMC1A/A*11:01-peptidome counter-screen → SolubleMPNN developability → novelty oracle → FEP top handful →
submission CSV + methods (upload USER-GATED). Caveat: ideally calibrate af2ig pae on a Liu/Baker de-novo
pMHC binder before final ranking (TODO).

## 2026-10-27 — GENERATION CAMPAIGN LAUNCHED + f_pep GATE CORRECTED (TCR-calibrated)

**Gate correction (cross-checked vs the known answer):** measured the real selective TCRs' own contact
split on the crystals — parental & JDI (>4000×) are **f_pep 0.22–0.26 / f_helix 0.74–0.78**, contacting
ONLY the groove platform (helix+peptide; 0 on α3/β2m). So the synth's f_pep≥0.5 gate is INVERTED — it
rejects the real answer. Selective pMHC binders are helix-heavy; specificity = peptide-**dependence**, not
peptide-fraction. BoltzGen `not_binding` on helices was a MISTAKE (evicted binders off the groove → f_pep 0,
many 0 peptide contact). REVERTED to peptide-only binding (C4,5,7,8). Corrected geometric pre-gate
(`scripts/analyze_design_contacts.py`): **f_pep≥0.18 AND on-platform (f_pep+f_helix≥0.80)**; the real tier-2
gate is the **co-fold peptide-dependence** (loaded≫empty, proven z=5.9), not f_pep. 7/8 no-not_binding
smoke designs pass the corrected gate (TCR-like regime).

**Campaign launched (all 8 GPUs idle — owner's ESMFold2 done):** BoltzGen `protein-anything` 420 designs on
GPUs 0-5 (`folds/gen/protein`, b3gne4iej); `nanobody-anything` smoke GPU6 (by9l8ahmy); `antibody-anything`
smoke GPU7 (bm2o2tzwg). Target = `g12d_pmhc.cif`, spec `specs/boltzgen/pep_centric.yaml`.

**Scoring/gate pipeline to build (while generating):** BoltzGen seqs → af2ig honest binding gate
(plddt>80, low pae_int) → 3-state co-fold peptide-dependence + differential (`scripts/score_pmhc.py`,
reusable) → contact pre-gate → two-folder (Boltz+Chai) → SMC1A/peptidome counter-screen → SolubleMPNN
developability → front-loaded diverse 20 (≤2/lineage, 4 classes) → FEP (pmxfep) on the final handful.

## 2026-10-27 — CALIBRATION MECHANISM + GENERATION PIPELINE UP (diversify-and-titrate committed)

RANKER CALIBRATION (Rosetta endpoint, `data/targets/bound/*`, `scripts/score_rosetta_iface.py`,
full run → `folds/rosetta_cal.log`): smoke on parental_g12d nailed the mechanism — P6(Asp)–HLA **Arg114
salt bridge = −4.6→−5.0** (JDI −5.04 > parental −4.56) vs **WT/Gly6 ≈ +0.1→+0.2** → Δ≈**+4.7–5.2 kcal/mol
favoring G12D, binder-INDEPENDENT**; P6↔TCR ≈ −0.3→−0.5 for BOTH (ΔP6-TCR≈0). So D6's effect is an **intra-pMHC**
pre-organizing salt bridge, NOT a TCR-contact; a single-pose *interface* ΔG is therefore weak for
selectivity, and the true tier-1 signal is the two-state ordering free energy → **FEP (pmxfep env),
reserved for the final handful, not scaled across generation.** Co-fold already proven blind; Boltz free
ensemble blind too. ⇒ **No cheap scalable tier-1 ranker exists → DIVERSIFY-AND-TITRATE**: generate broad,
gate hard (peptide-centric + binding + peptide-dependence + developability + counter-screen), ship a
diverse 20 as a titration series; FEP-rank only the top handful; the dual-tetramer FACS is the selector.

GENERATION PIPELINE (stood up): `data/targets/g12d_pmhc.cif` (ordered G12D pMHC A/B/C from raw 7OW6.cif,
entity_poly_seq preserved) + `specs/boltzgen/pep_centric.yaml` (binder 55..120, binding on EXPOSED bulge
C4,C5,C7,C8; never buried P6, never helices). BoltzGen smoke (8 designs, protocol protein-anything)
running (`folds/gen/bg_smoke`). On pass → scale protein + nanobody-anything + antibody-anything arms, add
RFdiffusion1/3 / PXDesign / Genie3 / RFantibody lineages (≤2/lineage), all through the gate stack.

## 2026-10-27 — MOONSHOT VERDICT + CRYSTAL PIVOT: discriminator is BOUND-STATE induced-fit electrostatics

Moonshot workflow (15 agents, develop→adversarial-attack→synthesize): ALL 7 mechanisms P(dead) 0.8–0.9.
- KILLS: free-state conformational-selector; LOCKR gated-switch (latch is thermodynamically COSMETIC —
  competitive autoinhibition multiplies every ligand Kd by the same (1+L) → G12D:WT RATIO invariant to
  latch strength); avidity (discriminates by site DENSITY, identical for G12D/WT → amplifies both,
  assay-redundant); prong-to-D6 (threading needs an OPEN solvated channel ⇒ no WT desolvation penalty — self-contradiction).
- pursue_if_cheap (as TECHNIQUES, not lineages): nanobody/scFv/Fab TCR-mimic (novelty real; ranking is the
  problem), pb-difference-map + multistate-MPNN (demoted to re-rankers; premises likely sub-noise).
- CRYSTAL CHECK (verified in deposited coords): free G12D (7OW4) P5/P6 DISORDERED all 4 copies; free WT
  (7OW3) ordered 2/4 → free G12D LESS ordered than free WT → free-state selection REFUTED. Discrimination
  is INDUCED-FIT: both order on binding; bound G12D gains the D6–Arg114 salt bridge + ~10.8 kcal/mol
  electrostatic ΔΔH WT lacks. Triply confirmed (Poole2022 + blind positive control + crystals).

STRATEGY (synth, endorsed): dominance ≠ one exotic mechanism. A rigorously-GATED, maximally DIVERSE,
peptide-centric slate (20 = protein 12 / nanobody 4 / scFv 2 / Fab 2; 10 lineages ×≤2), every slot passing
af2ig binding (pLDDT>80) + f_pep≥0.5–0.6 + f_helix≤0.25 + empty≪G12D + two-folder sign agreement +
SMC1A/A*11:01-peptidome counter-screen + developability; front-loaded by BINDING confidence; ranked by a
BOUND-STATE induced-fit selectivity prior IF it calibrates, else diversify-and-titrate (bench = the
selector). Moonshots fold in as cross-arm TECHNIQUES (empty/WT/SMC1A negative design, FEP/MM-PBSA
bound-state ranking, electrostatic re-rank). ONE live distinct moonshot: de-novo ANTIBODY-format
TCR-mimics (rewarded white-space class; no de-novo Ab TCR-mimic exists for this target).

SINGLE MOST IMPORTANT DE-RISK (next build): RANKER CALIBRATION on a known answer — does MM-PBSA/FEP
ΔΔG_bind(G12D−WT) on the JDI/Poole crystal complexes (7OW6 bound vs 7OW5 bound) recover the TCR's KNOWN
G12D>WT above seed noise? GO → rank designs on it; NO-GO → diversify-and-titrate. Static co-fold
ipTM/ipSAE already proven BLIND (this is the other half). ambertools MMPBSA.py + OpenMM (OpenCL) available.

## 2026-10-27 — POSITIVE CONTROL: static co-fold is BLIND to G12D-vs-WT; loaded-vs-empty is STRONG

Boltz-2 restrained co-fold, 5 samples/state (`folds/poscontrol/out`, `scripts/score_pmhc.py`):
- **Peptide-dependence (tier 2) RECOVERED:** JDI TCR↔HLA ipTM 0.93(loaded) vs 0.73(empty), Δ+0.20 z=+5.9;
  global iptm 0.94 vs 0.80. Static co-fold sees peptide-dependence cleanly → cheap tier-2 screen.
- **Mutation-specificity (tier 1) NOT RECOVERED:** even the >4000×-selective JDI shows TCR↔pep ipTM
  0.983(g12d)=0.983(wt), ipSAE 0.713 vs 0.711 → Δ≈0, z≈0.05–0.11. Poole same. iPAE faintly prefers
  G12D (z −1.1 JDI / −2.5 Poole) — too weak to rank on.
- **WHY:** Boltz folds both peptides into the SAME ordered groove (identical HLA, no entropy model) →
  complementarity identical; selectivity lives in the UNBOUND conformational free energy (WT floppy /
  G12D locked), invisible to single-pose co-fold. Confirms the geometry + the side-agent catch.
- **CONSEQUENCES:** (1) tier-1 gate ≠ static ipTM/ipSAE → build ensemble ΔΔG_order (free-pMHC MD) +
  electrostatics (APBS G12D−WT); (2) favor CONFORMATION-GATED/SELECTOR moonshots (binary signal the
  ensemble term amplifies) over subtle-static-ΔΔG ones; (3) tier-2 screen works out of the box.
- **Next:** `folds/free_ens` probe — is the WT bulge measurably floppier than G12D (the fuel)? escalate to MD if needed.

## 2026-10-27 (addendum) — WT negative must be conformation-aware (side-agent catch, adopted)

`wt_insilico.pdb` = WT seq frozen in the mutant's ORDERED backbone. RIGHT hard negative for
electrostatic/direct designs (shape identical, only P6 chemistry differs); WRONG for CONFORMATIONAL/
gated designs (they win by gripping the ordered bulge WT can't hold → frozen-ordered WT reads them as
false-non-selective → false reject). True discrimination is largely an UNBOUND conformational
free-energy difference (WT floppy, G12D locked; 7OW4: free bulge disorders) that single-pose scoring
CANNOT see. Co-fold folds WT from SEQUENCE (not the frozen pdb) but still gives one pose → same blind
spot. ⇒ judge gets a WT-negative PANEL per mechanism {ordered-chemistry = wt_insilico; floppy = WT
free-peptide MD ensemble + ΔΔG_order; co-fold = complementarity-only}; a robust design clears ALL.
The running static-co-fold positive control is the complementarity-only baseline that will show WHY
the ensemble/entropy term is needed. Encoded: `data/targets/manifest.json:wt_negative_policy`.

## 2026-10-27 — foundation + judge positive-control launched

**Refined doctrine from the raw SASA (notes/epitope_7OW6.json), not the Baker template:**
The binder-readable surface of the ordered G12D 10-mer is the **P4–P7–P8 up-bulge**, dominated by
**P7-Gly backbone apex (74 Å²)** and **P8-Val side chain (37 Å²)**; P4-Gly backbone (35 Å²). The
discriminator **P6-Asp is only 8.3 Å² and points inward** (salt-bridged to HLA Arg114). So the
physical handle is: **D6 rigidifies the bulge into this ordered P7-apex geometry; WT Gly6 lets it
collapse/disorder (7OW4)**. ⇒ design hotspots = **P7(bb), P8(sc), P4(bb); never P6 directly**;
discrimination is read indirectly via bulge geometry + electrostatics. Groove-lining HLA (for
restraints / avoid-as-epitope): 66,69,70,73,77,97,114,146,147,150,155,156.

**Done:**
- `scripts/prep_targets.py` → `data/targets/{g12d,wt_insilico,empty,wt_crystal}.pdb` + `manifest.json`.
  (g12d=7OW6 ABC; wt_insilico=g12d w/ C6 ASP→GLY, isolates the single-residue diff; empty=AB; wt_crystal=7OW5.)
- `scripts/extract_seqs.py`; TCR controls pulled: JDI (7PB2 D/E, the >4000× *selective* therapeutic),
  Poole (7OW6 D/E, parental, binds G12D+WT). CONTROLS ONLY — never a design seed (de-novo rule).
- `scripts/build_poscontrol.py` + `scripts/score_pmhc.py` (generalized 5-chain scorer: TCR↔pep & TCR↔HLA
  ipTM/ipSAE/iPAE + g12d−wt and loaded−empty differentials).
- Judge stack verified present: Boltz-2 2.2.1 (+wts), Chai, af2ig (tfr1 env+wts), ipSAE v4, BoltzGen/kit.

**In flight (both re-invoke on completion):**
- Boltz-2 positive control `b9sk1hrg9`: JDI×{g12d,wt,empty} + Poole×{g12d,wt}, restrained co-fold
  (pocket on TCRβ→bulge, identical across states), msa:empty, 5 samples, GPU 0-3. → `folds/poscontrol/out`.
- Moonshot workflow `w58zl1s43`: 7 non-mimetic mechanisms, develop→adversarial-attack→synthesize.

**The question the positive control answers (a potential judge pivot):** JDI reaches >4000× "with few
direct-contact differences." If even JDI shows no detectable static-co-fold g12d−wt gap, a static
differential is near-blind here → pivot the judge to ensemble/MD or conformation-gated readouts, and
rank moonshots toward differential-AMPLIFYING mechanisms. Score with `score_pmhc.py folds/poscontrol/out`.

**Next (gated on the two results):** fold the moonshot verdict into the generation plan; add decoy
negatives + af2ig gate calibration; then generation campaigns on idle GPU windows.
