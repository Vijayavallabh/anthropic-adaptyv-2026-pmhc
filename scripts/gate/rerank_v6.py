#!/usr/bin/env python
"""Re-rank v6: POSE-ROBUSTNESS correction (a side-agent review flagged that the Genie3 credibles'
ΔΔG rested on low-confidence binder-peptide poses).

Decisive test: re-gated the 3 Genie3 credibles on INDEPENDENT co-fold poses (6-rep/5ns):
  genie3_g6_28_m0 : model_0 -7.66 -> alt pose -7.8 [-12.2,-3.6] p=0   => ROBUST (held)
  genie3_g2_141_m1: model_0 -5.0  -> alt pose -4.0 [-8.6,+0.37] p=0.08 => NOT robust (CI spans 0)
  genie3_g2_103_m1: model_0 -12.51-> alt pose +0.99 [-5.9,+7.5] p=0.76 => COLLAPSED (single-pose artifact)

So the −12.5 was pose-dependent. Corrected submission:
  - CREDIBLE tier = 3 ROBUST selectives, ranked reliability-first (strong ΔΔG AND stable high-confidence
    pose): b3_gpu7_113 (-9.29, binder-peptide ipSAE 0.75 stable), genie3_g6_28_m0 (-7.66/-7.8 robust),
    nb3_gpu4_132 (-7.27, ipSAE 0.72). b3_gpu7_113 is #1 (not the shaky -12.5).
  - g2_103 DROPPED (pose-refuted + co-fold weakest 0.011 = no evidence on any axis).
  - g2_141 demoted to #20 deep reserve (directional but pose-sensitive gate; hydrophobic; NOT credible).
  - ipSAE column made consistent = binder-PEPTIDE (C-P) interface confidence for the credibles.

Carries all other rows byte-exact. Emits runs/submission.csv (CRLF) + submission_screens.csv, with backups."""
import csv, os, shutil

ROOT = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"; S = f"{ROOT}/runs"
# merge the two clean backups: pre-g2141 (v4, has b2_gpu3_36) + pre-robust (v5, has g2_141).
# (the live submission.csv was truncated by an earlier failed run; the backups are authoritative.)
cur_seq, carry = {}, {}
for src in [f"{S}/submission.pre-g2141-2026-11-08.bak.csv", f"{S}/submission.pre-robust-2026-11-08.bak.csv"]:
    for r in csv.DictReader(open(src)):
        cur_seq[r["name"]] = (r["sequence"], r["molecule_class"])
for src in [f"{S}/submission_screens.pre-g2141-2026-11-08.bak.csv", f"{S}/submission_screens.pre-robust-2026-11-08.bak.csv"]:
    for r in csv.DictReader(open(src)):
        carry[r["name"]] = r
SCREEN_COLS = ["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
               "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"]

ORDER = [
 "b3_gpu7_113",          # credible #1  -9.29  (BoltzGen, binder-peptide ipSAE 0.75, robust+stable)
 "genie3_g6_28_m0",      # credible #2  -7.66  (Genie3, ROBUST: held -7.8 on independent pose)
 "nb3_gpu4_132",         # credible #3  -7.27  (BoltzGen VHH, ipSAE 0.72)
 "nb3_gpu6_132", "genie3_8_m0", "b3_gpu7_181", "genie3_g4_121_m1", "nb3_gpu3_307", "b3_gpu4_211",
 "b3_gpu5_174", "genie3_g6_148_m1", "genie3_g5_72_m0", "nb3_gpu7_192", "genie3_g6_142_m1",
 "b3_gpu3_164", "nb3_gpu2_108", "nb3_gpu7_029", "b3_gpu4_161", "b2_gpu3_36",
 "genie3_g2_141_m1",     # #20 deep reserve long-shot (pose-sensitive gate, hydrophobic, NOT credible)
]  # DROPPED: genie3_g2_103_m1 (pose-refuted -12.5->+0.99, co-fold weakest 0.011)
assert len(ORDER) == 20 and len(set(ORDER)) == 20

# consistent binder-PEPTIDE (C-P) ipSAE for the credibles + corrected reasons
OVERRIDE = {
 "b3_gpu7_113": {"ipSAE_g12d": "0.749"},
 "nb3_gpu4_132": {"ipSAE_g12d": "0.720"},
 "genie3_g6_28_m0": {"reason": (
    "ORTHOGONAL-lineage (Genie3, non-BoltzGen) de-novo binder; EXPANSION-GATE discovery and the one "
    "POSE-ROBUST new credible. MM-GBSA gate confirms G12D-over-WT selectivity (ddG -7.66 kcal/mol, 95% CI "
    "[-11.3,-4.0], 12-rep) and it HELD on an INDEPENDENT co-fold pose (-7.8 [-12.2,-3.6], p=0); Asp6<->HLA-"
    "Arg114 bridge intact in 100% of 6000 MD frames; binder-peptide ipSAE 0.59. pLDDT 95; engages peptide "
    "bulge 4/5/7/8; borderline hydropathy (KD +0.10, disclosed). G12D-vs-WT confirmed only at the bench.")},
 "genie3_g2_141_m1": {"gate_ddG_kcalmol": "-5.0*", "gate_CI": "[-8.6,-1.5]/alt[-8.6,+0.4]", "reason": (
    "ORTHOGONAL-lineage (Genie3) de-novo binder; peptide-selective on the co-fold panel (weakest +0.29). "
    "Gate direction favors G12D (ddG -5.0 on the gated pose) but is POSE-SENSITIVE: on an independent co-fold "
    "pose ddG -4.0 with the CI including 0 (p=0.08), so NOT counted as a credible selective -- held in deep "
    "reserve as a long-shot. pLDDT 94; HYDROPHOBIC (KD +0.52, expression risk, disclosed). The assay is the "
    "verdict.")},
}

for f in ["submission.csv", "submission_screens.csv"]:
    bak = f"{S}/{f.replace('.csv','')}.pre-robust-2026-11-08.bak.csv"
    if not os.path.exists(bak):
        shutil.copy(f"{S}/{f}", bak)

with open(f"{S}/submission.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\r\n"); w.writerow(["name", "sequence", "molecule_class"])
    for nm in ORDER:
        seq, cls = cur_seq[nm]; w.writerow([nm, seq, cls])

with open(f"{S}/submission_screens.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=SCREEN_COLS, lineterminator="\r\n"); w.writeheader()
    for i, nm in enumerate(ORDER, 1):
        row = dict(carry[nm]); row["rank"] = i
        row.update(OVERRIDE.get(nm, {}))
        w.writerow(row)

from collections import Counter
sub = list(csv.DictReader(open(f"{S}/submission.csv")))
gen = lambda n: "Genie3" if n.startswith("genie3") else "BoltzGen"
print("wrote submission.csv + screens (pose-robustness corrected)")
print("generators:", dict(Counter(gen(r["name"]) for r in sub)), "classes:", dict(Counter(r["molecule_class"] for r in sub)))
print("credible tier (robust, by ddG):")
for nm in ORDER[:3]:
    print(f"  #{ORDER.index(nm)+1} {nm:<18} {gen(nm):<9} ddG={carry[nm]['gate_ddG_kcalmol']} ipSAE={OVERRIDE.get(nm,{}).get('ipSAE_g12d',carry[nm]['ipSAE_g12d'])}")
print("dropped g2_103:", "genie3_g2_103_m1" not in ORDER, "| g2_141 at #", ORDER.index("genie3_g2_141_m1")+1)
