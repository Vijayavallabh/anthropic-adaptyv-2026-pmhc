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

### Pending decision (reserved for the USER)
Choose one, then the (gated) portal upload is the user's to do:
- **(a)** finalize the full 12-swap (`combined_submission.csv`) — recommended on the evidence;
- **(b)** partial swap with two optional refinements first:
  1. replace one near-cousin nanobody (nb3_gpu3_307 ~ nb3_gpu5_130, 0.88 whole-seq id) for diversity;
  2. replace the one remaining `novelty_risk` design (retained `protein_0103`, TM 0.912) with a novel
     high-sel survivor if one exists (needs a quick campaign-pool check);
- **(c)** keep the locked 20 as-is.

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
