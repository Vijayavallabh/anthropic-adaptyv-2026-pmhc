# Eligibility & provenance — Challenge 5 submission

Self-contained eligibility record for the finalized 20 in `runs/submission.csv`. Keep this together with the
submission confirmation and the exact-sequence prescreen result.

## Organizer clarifications on framework reuse (Proteinbase Slack, 2026-11-04/05)
The organizers explicitly clarified that reusing a constant framework while regenerating/mutating CDRs counts as
**de novo**, contingent on passing the submission-time novelty checker:
- **TCR** (Tudor, 2026-11-04): "I'd also consider constant frameworks and mutated (or novel) CDRs as de novo."
  Acceptance depends on passing the submission novelty checker.
- **Nanobody** (Tudor, 2026-11-05): "As long as your designs pass the novelty score at submission time … it's all
  good!" and "Maintaining the framework and replacing CDRs should be considered de novo."

Note: the organizers pointed to *this* competition's submission checker; they did **not** adopt another
competition's numerical edit-distance exemption. We rely on the Proteinbase checker, not an imported threshold, and
do not conceal derivation.

## Our submission under these rules

### Nanobodies (7 of 20) — VHH framework + de novo CDRs, not seeded
All seven use the canonical camelid VHH framework (BoltzGen nanobody generation). The framework is the **public VHH
consensus scaffold, not a specific/proprietary known binder**, and no CDRs were grafted from a known nanobody. The
shared framework is evident in the conserved FR1 / FR2-hallmark / FR4 and the canonical disulfide cysteines; the CDR
loops (the variable interior — CDR1 after `…SCAAS`, CDR2 after the FR2 `W[F/L/V]RQAPG…` hallmark, CDR3 before
`WG[R/Q]G…`) are de novo and differ by design:

| design | FR1 (conserved) | FR2 hallmark | FR4 (conserved) |
|---|---|---|---|
| nb3_gpu4_132 | EVQLVESGGGLVQAGGSLSISCAAS | WFRQAPGKEREFVAA | PFWGRGTQVTVSS |
| nb3_gpu6_132 | EVQLVESGGGLVQPGGSLRLSCAAS | WFRQAPGKGRELVAA | DYWGQGTQVTVSS |
| nb3_gpu3_307 | EVQLVESGGGLVQPGGSLRLSCAAS | WFRQAPGQEREFVAG | DYWGQGTLVTVSS |
| nb3_gpu7_192 | EVQLVESGGGLVQPGGSLRLSCAAS | WLRQAPGKEREFVAA | DFWGQGTLVTVSS |
| nb3_gpu5_130 | EVQLVESGGGLVQPGGSLRLSCAAS | WFRQAPGQEREFVAG | LYWGQGTLVTVSS |
| nb3_gpu6_432 | EVQLVESGGGLVQAGGSLSISCAAS | WFRQAPGKEREFVAA | PFWGRGTQVTVSS |
| nanobody_0202 | EVQLVESGGGVVQPGNSLRLSCAAS | WVRQAPGKGLEWVS | AFWGQGTLVTVSS |

Full sequences: `runs/submission.csv`. Per the challenge rules, nanobody novelty is judged on CDR diversity
(chiefly HCDR3); the natural VHH framework carries expected high whole-domain structural similarity to known VHHs
and is not penalized. This is exactly the case the organizers sanctioned.

### Single-chain miniproteins (13 of 20) — de novo, non-immunoglobulin
Generated zero-shot by BoltzGen (protein-anything) and RFdiffusion1 + SolubleMPNN against the ordered pMHC; the
sequences are co-designed de novo, folded directly, never re-sequenced from a natural protein. A sequence/topology
classifier removed any immunoglobulin V-domain emitted by the single-chain route, so the single-chain set is
genuinely non-antibody. No single-chain-TCR-mimetic or constant-domain format is used, so the open organizer
question about that specific format does not bear on this submission.

### Prescreen status (the checker the organizers point to)
The Proteinbase portal validated the **exact 20 submitted sequences as 20/20 Passed, 0 needing fixes** (2026-11-06),
each with its class + length recognized. Retain that result (screenshot + the collection link) with the submission
record, per the organizers' guidance that acceptance depends on passing this screen.

## Separation of claims (predictions are predictions)
Mutant (G12D) specificity, wild-type discrimination, and peptide-free-control behavior are kept as three separate
axes; every in-silico value is labeled a prediction. The confirmatory MM-GBSA gate is a filter, never a rank, and
true G12D-vs-WT is the wet-lab's verdict (see `docs/METHODS.md` → "On tier-1 selectivity").

## Items to verify directly (not settled by the Slack brief)
- The current Challenge 5 **deadline** and **track-specific design allowance** — verify on the portal; our records
  say 2026-11-08 23:59 AoE and ≤20 designs.
- **Modal/Claude compute balances + expiry** — credit extensions were being rolled out; verify the specific account.
- **Post-upload platform audit** — inspect individual candidate pages, not just the collection grid: a missing grid
  preview ("--" / "No preview available") is a known display bug, distinct from a genuinely missing prediction. If a
  prediction is truly absent, report account handle + collection link + candidate IDs + submission date +
  screenshots and request a pipeline rerun, rather than uploading a duplicate collection.

## Submission states (keep separate)
Submitted → eligible after prescreen → platform predictions available → selected for experimental characterization →
experimentally validated. A structure appearing on Proteinbase is not, by itself, a selection announcement.
