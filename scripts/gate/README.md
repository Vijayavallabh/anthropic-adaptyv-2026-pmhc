# scripts/gate — confirmatory G12D-vs-WT physics gate

An orthogonal ensemble MM-GBSA gate that acts as a *confirmatory binary FILTER* (never a ranker) for the buried
G12D-vs-WT axis the co-fold panel is blind to. See `docs/METHODS.md` → "On tier-1 selectivity" and `AGENTS.md`
→ the funnel (step 7) for the full rationale and calibration.

## Pipeline (per shortlisted design, on a co-fold-stable pose)
1. `gate_prep.py <design> <g12d_pose.pdb> <outroot>` — build the matched G12D system + an in-silico Asp6→Gly6
   WTmut (backbone kept), solvate, emit prmtops + masks. Helpers: `build_md.py`, `build_parmed.py` (ParmEd
   order-preserving mbondi3), `gate_sanity.py`.
2. `gate_run.py <designsdir> <list> <nrep> <ns> <gpus>` — OpenMM CUDA MD (HMR 4 fs; min→NVT→NPT→prod),
   `nrep` replicas/state, resume-safe. Helper: `md_run.py`.
3. `gate_score.py <designsdir> <list>` — single-trajectory OpenMM GBn2 MM-GBSA per replica. Helper: `score_gbsa.py`.
   GOTCHA: the ante-MMPBSA→sander path is corrupt in this environment (phantom energies) — use this OpenMM GBn2 path.
4. `gate_analyze.py <designsdir> <list> <out.tsv>` — replica-bootstrap ΔΔG(G12D − WTmut) + 95% CI.
   SELECTIVE iff ΔΔG ≤ −4 kcal/mol AND CI excludes 0. Calibration: recovers Poole −4.36 [−7.0,−1.6]; nulls WT-vs-WT
   (noise floor ≈ 1.9).

## Pose realism (MANDATORY before trusting any selective call)
- `scan_saltbridge_all.py` — measures the native Asp6↔HLA-Arg114 salt bridge across all gated poses →
  `runs/campaign/gate/pose_realism.tsv` (preserved <4 Å = credible; broken ≈8 Å = over-dock artifact).
- `analyze_pose.py`, `analyze_p6.py`, `analyze_saltbridge.py` — per-pose geometry probes.
- `find_rescue_poses.py` — for an over-docked selective, find a preserved+bound co-fold shard to re-gate.

## Decision
- `merge_and_emit.py` — merges the gate verdicts + pose realism + the weakest-objective ruler into the final-20.
  The ruler RANKS; the gate only FILTERS (promote a preserved-pose CI-excl-0 selective; deny credit to an
  over-docked one; demote a confirmed anti-selective to padding). Emits
  `runs/campaign/final20_two_axis_recommended.csv` + `final20_two_axis_rationale.tsv`.

## Environments
- MD + scoring (OpenMM CUDA; `gate_run`/`md_run`/`gate_score`/`score_gbsa`): the `pepglad` conda env.
- Prep + analysis (tleap/cpptraj/ParmEd; the pose scripts; `merge_and_emit`): the `ambertools` conda env.

Caveat: several scripts carry hardcoded absolute paths (conda envs, the gate dir); a dynamic-root refactor is a
tracked follow-up (see `session-handoff.md`). Run any script that reads a downloaded/untrusted PDB with `python -I`.
