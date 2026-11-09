#!/usr/bin/env python
"""Re-rank v8: COMPLETE 5-pose ensemble — re-include g2_103 (my single-pose drop was wrong).

Gating ALL gate-candidates on the full 5-pose co-fold ensemble (models 0-4) gives:
  b3_gpu7_113    5/5 G12D, mean -5.8  ROBUST
  genie3_g6_28_m0 5/5 G12D, mean -6.2 ROBUST
  genie3_g2_103_m1 4/5 G12D, mean -7.3, sig 4/5  (strongest mean; I had DROPPED it on the one +1.0 pose)
  genie3_g2_141_m1 4/5 G12D, mean -4.8           (hydrophobic -> reserve)
  nb3_gpu4_132   4/5 G12D, mean -3.3, sig 2/5     (kept #3 earlier, but WEAKER than g2_103)
Keeping nb3_gpu4_132 while dropping the stronger g2_103 (both 4/5) is inconsistent -> re-include g2_103.

Final tiers (uniform ensemble bar): 2 pose-ROBUST (5/5) + 3 NET-G12D-LEANING (4/5, one flip, disclosed).
Assayed top-10 selectivity tier (soluble): b3_gpu7_113, g6_28, g2_103, nb3_gpu4_132; g2_141 stays reserve
(hydrophobic). Drop b2_gpu3_36 (weakest co-fold, no gate evidence) to make room. Emits submission.csv (CRLF)
+ submission_screens.csv, with backup. This is the complete-data final; the co-fold model ensemble is exhausted."""
import csv, os, shutil
ROOT = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"; S = f"{ROOT}/runs"
COLS = ["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
        "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"]
# merge current (v7) with the v4 backup (has g2_103 + b2_gpu3_36)
seq, carry = {}, {}
for src in [f"{S}/submission.pre-g2141-2026-11-08.bak.csv", f"{S}/submission.csv"]:
    for r in csv.DictReader(open(src)): seq[r["name"]] = (r["sequence"], r["molecule_class"])
for src in [f"{S}/submission_screens.pre-g2141-2026-11-08.bak.csv", f"{S}/submission_screens.csv"]:
    for r in csv.DictReader(open(src)): carry[r["name"]] = r

ORDER = [
 "b3_gpu7_113", "genie3_g6_28_m0",         # pose-ROBUST (5/5)
 "genie3_g2_103_m1", "nb3_gpu4_132",       # NET-G12D-LEANING (4/5), soluble -> assayed
 "nb3_gpu6_132", "genie3_8_m0", "b3_gpu7_181", "genie3_g4_121_m1", "nb3_gpu3_307", "b3_gpu4_211",
 "b3_gpu5_174", "genie3_g6_148_m1", "genie3_g5_72_m0", "nb3_gpu7_192", "genie3_g6_142_m1",
 "b3_gpu3_164", "nb3_gpu2_108", "nb3_gpu7_029", "b3_gpu4_161",
 "genie3_g2_141_m1",                       # #20 reserve: net-leaning but hydrophobic
]  # DROPPED vs v7: b2_gpu3_36 (weakest co-fold, no gate evidence)
assert len(ORDER) == 20 and len(set(ORDER)) == 20

OVER = {
 "genie3_g2_103_m1": dict(ipSAE_g12d="0.474", gate_ddG_kcalmol="-7.3 (5-pose mean)",
   gate_CI="4/5 poses G12D; [-12.5,+1.0]", reason=(
   "ORTHOGONAL-lineage (Genie3) de-novo single-chain; NET-G12D-leaning selective (pose-variable). On the "
   "5-pose co-fold ensemble the gate favors G12D on 4/5 poses (-12.5/-9.2/-10.1/+1.0/-5.8; ensemble-mean -7.3, "
   "significant on 4/5) -- the strongest ensemble mean among the gate-selectives. An earlier single-pose check "
   "hit the +1.0 outlier and briefly dropped it; the complete 5-pose ensemble reinstates it. Low per-pose "
   "interface confidence (0.47) = pose-variable, weaker than the 5/5 designs. pLDDT 89, soluble (KD -1.25); "
   "engages peptide bulge; low-complexity E/K N-term (disclosed). G12D-vs-WT = the assay's call.")),
 "nb3_gpu4_132": dict(reason=(
   "BoltzGen de-novo nanobody (public VHH framework, de-novo CDRs); NET-G12D-leaning selective, the weakest of "
   "the gate-selectives. 5-pose ensemble 4/5 G12D (-7.3/-3.5/-8.2/+2.7/-0.1; mean -3.3, significant on 2/5); "
   "binder-peptide interface confidence 0.72, soluble; pLDDT 81. Pose-variable -- disclosed. The assay is the verdict.")),
}

bak_s = f"{S}/submission.pre-reinclude-2026-11-09.bak.csv"; bak_c = f"{S}/submission_screens.pre-reinclude-2026-11-09.bak.csv"
if not os.path.exists(bak_s): shutil.copy(f"{S}/submission.csv", bak_s)
if not os.path.exists(bak_c): shutil.copy(f"{S}/submission_screens.csv", bak_c)

with open(f"{S}/submission.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\r\n"); w.writerow(["name", "sequence", "molecule_class"])
    for nm in ORDER:
        s, c = seq[nm]; w.writerow([nm, s, c])
with open(f"{S}/submission_screens.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\r\n"); w.writeheader()
    for i, nm in enumerate(ORDER, 1):
        r = dict(carry[nm]); r["rank"] = i
        if nm in OVER: r.update(OVER[nm])
        w.writerow(r)

from collections import Counter
gen = lambda n: "Genie3" if n.startswith("genie3") else "BoltzGen"
sub = list(csv.DictReader(open(f"{S}/submission.csv")))
print("wrote v8 (g2_103 re-included at #3, b2_gpu3_36 dropped)")
print("generators:", dict(Counter(gen(r["name"]) for r in sub)), "classes:", dict(Counter(r["molecule_class"] for r in sub)))
for i, nm in enumerate(ORDER[:4], 1):
    print(f"  #{i} {nm:<18} {carry[nm].get('gate_ddG_kcalmol') if nm not in OVER else OVER[nm].get('gate_ddG_kcalmol',carry[nm]['gate_ddG_kcalmol'])}")
