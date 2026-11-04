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

- `runs/submission.csv` — the **locked, portal-accepted 20** (`name,sequence,molecule_class`).
- `runs/final20_ranked.tsv` — the locked 20 with all axes.
- `runs/campaign/combined_submission.csv` — **proposed** portfolio (12 same-ruler swaps); portal-format-validated,
  **not uploaded**.
- `runs/campaign/{panel_reval,mpnn_diff_all,combined_all_ranked}.tsv`, `SWAP_PROPOSAL*.txt` — campaign evidence.

## Method (one line)

BoltzGen + RFdiffusion1 + SolubleMPNN **generate** → Boltz-2 5-sample, 6-state pocket-restrained **co-fold** →
selectivity **scoring** (ipSAE: `spec_scram`, `promisc_margin`, `bh_e`, `grip`) → survivors → `grip` + **MPNN δ**
(orthogonal, never a gate) + **novelty** (foldseek TM) → `assemble_final20` → `campaign_select` swap proposal.

**North star (selection):** rank by the *weakest* discrimination margin `min(spec_scram, promisc_margin, bp−bh_e)`
— reject what the targets SHARE, don't worship the composite `sel` (see `scripts/weakest_objective.py` and
AGENTS.md → North star). Improve the weakest objective; one convincing pose is not discrimination; the experiment
is the verdict.

**The central fact:** the axis that actually decides the challenge — does the binder grab G12D and *not* the
near-identical WT at the single **buried** residue — is not reliably rankable in silico (co-fold is blind to it;
MPNN δ is a verified wash). The portfolio is therefore a diversified spread of bets ranked on the *measurable*
selectivity proxies (`bh_e` peptide-dependence, `spec_scram`, `promisc_margin`), with true G12D-vs-WT left to the
wet-lab assay.

## Reproduce / bootstrap

See `init.sh` (`--check` to verify the environment, `--tools` to rebuild the gitignored vendored tools). The
Boltz-2 venv is external: `/home/prachh/v/sepiq-2026-challenge/.venv-boltz`.
