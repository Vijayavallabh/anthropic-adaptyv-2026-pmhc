# session-handoff.md

Where things stand, for the next session. Newest state at top; full history in `progress.md`.

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
