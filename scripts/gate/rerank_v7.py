#!/usr/bin/env python
"""Re-rank v7: report the POSE-ENSEMBLE gate result for the 3 credibles (screens-only update).

A side-agent review showed a gate ΔΔG rests on one co-fold pose, and the gate's CI captures only MD
noise, not co-fold POSE uncertainty. We therefore gated each credible on 5 independent co-fold poses:
  b3_gpu7_113  : -9.3/-3.2/-7.5/-3.5/-5.4  -> 5/5 G12D-direction, mean -5.8  (ROBUST)
  genie3_g6_28_m0: -7.7/-9.1/-4.5/-7.8/-1.8 -> 5/5 G12D-direction, mean -6.2  (ROBUST)
  nb3_gpu4_132 : -7.3/-3.5/-8.2/+2.7/-0.1  -> 4/5 G12D-direction, mean -3.3  (one pose flips; weakest)
The headline gate value is now the POSE-ENSEMBLE MEAN (honest, pose-uncertainty-aware), with the pose
range and direction-fraction, replacing the single lucky-pose ΔΔG. Ranking unchanged (reliability-first:
b3_gpu7_113 #1 on confidence 0.75 + 5/5; g6_28 #2 5/5; nb3_gpu4_132 #3 weakest 4/5). submission.csv
(sequences/order) is UNCHANGED; only submission_screens.csv gate columns + reasons update. With backup."""
import csv, os, shutil
ROOT = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"; S = f"{ROOT}/runs"
COLS = ["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
        "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"]
OVER = {
 "b3_gpu7_113": dict(gate_ddG_kcalmol="-5.8 (5-pose mean)", gate_CI="5/5 poses G12D; [-9.3,-3.2]", reason=(
   "BoltzGen de-novo single-chain; POSE-ROBUST credible selective. Gate ΔΔG favors G12D on ALL 5 "
   "independent co-fold poses (-9.3/-3.2/-7.5/-3.5/-5.4; ensemble-mean -5.8, significant on 3/5); "
   "binder-peptide interface confidence 0.75, stable across all 5 models; pLDDT 94, soluble. A single-pose "
   "ΔΔG understates uncertainty, so selectivity is judged on the pose ensemble (EXPANSION_GATE_PREREG.md "
   "addenda 2-3). G12D-vs-WT confirmed only at the bench.")),
 "genie3_g6_28_m0": dict(gate_ddG_kcalmol="-6.2 (5-pose mean)", gate_CI="5/5 poses G12D; [-9.1,-1.8]", reason=(
   "Genie3 (orthogonal generator) de-novo single-chain; POSE-ROBUST credible selective and the expansion-gate "
   "discovery. Gate ΔΔG favors G12D on ALL 5 co-fold poses (-7.7/-9.1/-4.5/-7.8/-1.8; ensemble-mean -6.2, "
   "significant on 3/5); engages peptide bulge 4/5/7/8; pLDDT 95; borderline hydropathy (KD +0.10, disclosed). "
   "G12D-vs-WT is the assay's call.")),
 "nb3_gpu4_132": dict(gate_ddG_kcalmol="-3.3 (5-pose mean)", gate_CI="4/5 poses G12D; [-8.2,+2.7]", reason=(
   "BoltzGen de-novo nanobody (public VHH framework, de-novo CDRs); credible selective, the MOST pose-variable "
   "of the three. Gate ΔΔG favors G12D on 4/5 co-fold poses (-7.3/-3.5/-8.2/+2.7/-0.1; ensemble-mean -3.3, one "
   "pose flips positive; significant on 2/5); binder-peptide interface confidence 0.72; pLDDT 81. Net "
   "G12D-leaning but weaker/noisier than #1-2 -- disclosed. G12D-vs-WT is the assay's call.")),
}
bak = f"{S}/submission_screens.pre-ensemble-2026-11-08.bak.csv"
if not os.path.exists(bak): shutil.copy(f"{S}/submission_screens.csv", bak)
rows = list(csv.DictReader(open(f"{S}/submission_screens.csv")))
with open(f"{S}/submission_screens.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\r\n"); w.writeheader()
    for r in rows:
        if r["name"] in OVER: r.update(OVER[r["name"]])
        w.writerow(r)
print("updated 3 credible rows with pose-ensemble values; submission.csv unchanged")
for r in csv.DictReader(open(f"{S}/submission_screens.csv")):
    if r["name"] in OVER: print(f"  #{r['rank']} {r['name']:<18} {r['gate_ddG_kcalmol']:<18} {r['gate_CI']}")
