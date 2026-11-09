# anthropic-adaptyv-2026-pmhc

De-novo, zero-shot binder design for the **KRAS G12D neoantigen peptide `VVVGADGVGK`** presented on
**HLA-A\*11:01 + β2-microglobulin** — Anthropic × Adaptyv 2026 **Challenge 5 (Track 3, pMHC)**.

The task: ≤20 ranked de-novo designs that bind the G12D neoantigen **selectively**, discriminating it from the
wild-type peptide `VVVGAGGVGK` (differs only at the **buried** P6 residue), unrelated A\*11:01 epitopes, and the
empty HLA groove. Deadline **2026-11-08 23:59 AoE**. Submission upload is **user-gated** (Proteinbase portal).

## Start here

| File | What it is |
|---|---|
| `AGENTS.md` | Working contract: objective, invariants, the funnel, scoring axes, definition of done |
| `CLAUDE.md` | Working rules (autonomy, GPU, git, devil's-advocate) |
| `progress.md` | Newest-first running log with evidence (task ids, `rc`) |
| `session-handoff.md` | Where things stand right now + next actions + pending gated decision |
| `docs/SUBMISSION_SUMMARY.md` | Publishable, rubric-aligned cover doc (epitope, selectivity evidence, 3 screens, novelty, ranking) |
| `docs/ELIGIBILITY_PROVENANCE.md` | De-novo justification per class (framework+CDR provenance), prescreen status, verify-list |
| `runs/submission_screens.csv` | Per-design pLDDT / ipSAE / hydropathy / novelty + one-line reasons (the selection rubric's three screens) |
| `configs/target.yaml`, `data/targets/` | Target definition (HLA, β2m, peptide states, crystal refs) |
| `docs/` | Deeper notes: `METHODS.md`, `PLAN.md`, `RESEARCH_SOTA.md`, `RECON.md` |
| `specs/` | BoltzGen generation specs (pep-centric, nanobody, fab, helix-decoy) |

## Layout

```
scripts/      generators, co-fold builders, folders, scorers, funnel drivers, assembly/selection (+ vendored
              ipsae.py, run_boltz.sh)
configs/      target.yaml (HLA-A*11:01 + β2m + peptide panel)
data/targets/ g12d / wt / empty target structures + manifest (tracked)
runs/         co-fold outputs + scores (GITIGNORED, ~138 GB; curated result files force-added)
tools/        vendored foldseek+PDB-DB, ProteinMPNN weights, etc. (GITIGNORED, rebuilt via init.sh --tools)
```

## Key results (tracked under `runs/`)

- `runs/submission.csv` — the **finalized 20** (`name,sequence,molecule_class`), portal-validated (20/20 Passed).
  v8 (2026-11-09): the ruler+gate+pose-realism set hardened by the expansion gate + a 5-pose co-fold ensemble;
  **12 BoltzGen + 8 Genie3, 14 single_chain + 6 nanobody**, rank-ordered selectivity-evidence-first.
- `runs/submission.locked-2026-11-06.bak.csv` — the prior locked 20 (backup).
- `runs/campaign/final20_two_axis_recommended.csv` + `final20_two_axis_rationale.tsv` — the finalized set and its
  per-design rationale (tier, pose realism, gate ΔΔG + CI, weakest margin).
- `runs/campaign/weakest_objective.tsv` — the north-star minimax ruler for all candidates.
- `runs/campaign/gate/gate_results_{all,unified,merged,deepen2,rescue}.tsv`, `pose_realism.tsv`,
  `two_axis_{decision,sensitivity}.tsv` — the physics-gate + pose-realism evidence (see "central fact" below).
- `runs/campaign/{panel_reval,mpnn_diff_all,combined_all_ranked}.tsv` — upstream campaign co-fold/scoring evidence.

## Method (one line)

BoltzGen + RFdiffusion1 + SolubleMPNN **generate** → Boltz-2 5-sample, 6-state pocket-restrained **co-fold** →
selectivity **scoring** (ipSAE: `spec_scram`, `promisc_margin`, `bh_e`, `grip`) → survivors → `grip` + **MPNN δ**
(orthogonal, never a gate) + **novelty** (foldseek TM) → `assemble_final20` → `campaign_select` swap proposal →
**ensemble MM-GBSA physics gate** (OpenMM GBn2, `scripts/gate/`) as a *confirmatory filter* for the buried
G12D-vs-WT axis, with a **mandatory pose-realism (Asp6-burial) check** → `merge_and_emit` final-20 (the ruler
ranks; the gate only filters).

**North star (selection):** rank by the *weakest* discrimination margin `min(spec_scram, promisc_margin, bp−bh_e)`
— reject what the targets SHARE, don't worship the composite `sel` (see `scripts/weakest_objective.py` and
AGENTS.md → North star). Improve the weakest objective; one convincing pose is not discrimination; the experiment
is the verdict.

**The central fact:** the axis that actually decides the challenge — does the binder grab G12D and *not* the
near-identical WT at the single **buried** residue — is not reliably *ranked* in silico (co-fold is blind to it;
MPNN δ is a verified wash). An orthogonal **ensemble MM-GBSA gate** does recover a *confirmatory* signal on a
shortlist — but only on poses that keep Asp6 **buried** (the co-folder frequently over-docks it out of the groove,
faking selectivity), and only as a binary **filter**, never a rank. On that honest bar — after an expansion-gate
sweep of the un-gated pool and a 5-pose co-fold ensemble — **two** designs (`b3_gpu7_113`, `genie3_g6_28_m0`) are
**pose-robust** credible G12D-selectives (favor G12D on 5/5 independent poses) and **three** more
(`genie3_g2_103_m1`, `nb3_gpu4_132`, `genie3_g2_141_m1`) are **net-G12D-leaning** (4/5 poses, one flip, disclosed);
the rest of the portfolio is a diversified spread of
bets ranked on the pose-independent *measurable* proxies (`spec_scram`, `promisc_margin`, `bh_e`). True
G12D-vs-WT remains the **wet-lab's** verdict.

## Reproduce / bootstrap

See `init.sh` (`--check` to verify the environment, `--tools` to rebuild the gitignored vendored tools). The
Boltz-2 venv is external: `/home/prachh/v/sepiq-2026-challenge/.venv-boltz`.
