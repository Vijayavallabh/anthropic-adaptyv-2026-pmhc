# CLAUDE.md

**Read `AGENTS.md` first** for the working contract (objective, invariants, the funnel, scoring axes,
verification, submission). This file adds the working rules.

## Working rules

- **Autonomous to the deadline (2026-11-08 23:59 AoE).** No step-by-step approval; make progress, record
  evidence in `progress.md` (newest-first, with task id + `rc`), surface blockers. The final upload to the
  Proteinbase portal is **USER-GATED** — prepare and recommend, never upload.
- **Queue heavy GPU work into idle windows.** 8× H100 local; verify with `nvidia-smi`, one process per GPU,
  never clobber a foreign job (**GPUs 0,1 are foreign**), cap CPU threads. Launch long jobs as tracked
  background commands so completion notifies.
- **De-novo, zero-shot, legitimate.** This is Anthropic's own therapeutic protein-design competition (a
  KRAS-G12D neoantigen is a bona-fide cancer target). No seeding from known binders; no target fine-tuning.
  Keep raw sequences in files, not chat.
- **Trust only the 5-sample, 6-state panel.** Single-sample co-fold is noise. The G12D-vs-WT discrimination is
  a bench measurement — co-fold is blind to the single buried residue and MPNN δ is a verified wash; never
  present an in-silico number as ranking that axis.
- **Devil's-advocate, then revise.** For any design or selection strategy, argue the strongest case against it
  (reads the platform not the peptide? binds empty HLA? Ig-fold? truly de-novo? proxy-overfit?) before spending
  compute or recommending a swap.
- **Latest SOTA, researched then adopted** — only where it adds an orthogonal signal or real gain, after
  checking availability + license. Never claim a capability is being used unless it is actually invoked.
- **Before a portfolio swap**, verify EVERY axis on the identical pipeline/ruler; a swap trading a higher axis
  for a lower one is churn. Score any orthogonal axis on BOTH portfolios before claiming it corroborates.

## Git / commits

- **Repo-local identity, no AI attribution.** Before committing:
  `git config user.name "Vijayavallabh"` and
  `git config user.email "88388452+Vijayavallabh@users.noreply.github.com"` (GitHub noreply; the global machine
  identity is NOT the user's — do not use it).
- **Stage source + docs + harness + curated result files only.** `runs/ tools/ third_party/ weights/ envs/
  .venv* scratchpad/` are gitignored. Force-add only the small human-readable results under `runs/`.
- **Scan for secrets/PII before any push.** Private repo (`github.com/Vijayavallabh/anthropic-adaptyv-2026-pmhc`).
  Push only when the user asks; creating/pushing GitHub repos needs explicit owner approval.
- Descriptive commit messages; commit at each checkpoint.
