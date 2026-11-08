#!/usr/bin/env python
"""Re-rank v5: promote the 3rd expansion-gate Genie3 credible (g2_141) on the UNIFORM standard.

A side-agent review flagged that the expansion batch faced an FDR multiple-testing correction that
the original 2 credibles (gated in smaller batches) never faced — an inconsistent standard.
`genie3_g2_141_m1` (rfd_des_g2_pmhc_g12d_141_m1) passes the EXACT bar the original credibles passed:
pose-real (Asp6-Arg114 bridge intact 100% of 6000 MD frames) + 12-rep ΔΔG -5.00 [-8.6,-1.5] with the
CI excluding 0, and it HELD from the 6-rep -6.33 (p improving 0.017->0.004 — a real effect, not a
look-elsewhere fluke, which would regress). It was blocked ONLY by the FDR step. The user settled the
standard to the uniform 12-rep-replication bar (docs/EXPANSION_GATE_PREREG.md addendum, dated), under
which g2_141 is credible. The independent 12-rep replication is a stronger look-elsewhere guard than
FDR-on-6-rep, so this is a consistency fix, not a relaxation.

Credible count 4 -> 5 (now 2 BoltzGen + 3 Genie3). g2_141 ranks #5 by gate ΔΔG (hydrophobic KD +0.52
disclosed); it displaces the gate-WT-leaning co-fold `b3_gpu4_211` from the assayed top-10, and the
weakest co-fold `b2_gpu3_36` drops off the 20. Carries all other rows byte-exact from the committed
CSVs. Emits runs/submission.csv (CRLF) + runs/submission_screens.csv, with backups."""
import csv, os, shutil

ROOT = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
S = f"{ROOT}/runs"
cur_seq = {r["name"]: (r["sequence"], r["molecule_class"]) for r in csv.DictReader(open(f"{S}/submission.csv"))}
carry = {r["name"]: r for r in csv.DictReader(open(f"{S}/submission_screens.csv"))}
SCREEN_COLS = ["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
               "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"]

NEW_NAME = "genie3_g2_141_m1"
NEW_SEQ = "DGAARAALRAALRALGVSEDQADAILAALDAGDLERALALFRAAGLTADQVDALAALAEELGLPARAAALRAVAEALRAAAG"
NEW_ROW = dict(rank=0, name=NEW_NAME, **{"class": "single_chain"}, length=str(len(NEW_SEQ)),
    plddt="94.000", ipSAE_g12d="0.464", mean_KD_hydropathy="+0.515", novelty_maxTM_or_basis="0.804",
    weakest_margin="+0.288", gate_ddG_kcalmol="-5.00", gate_CI="[-8.6,-1.5]",
    reason=("ORTHOGONAL-lineage (Genie3, non-BoltzGen) de-novo binder; EXPANSION-GATE discovery "
            "(3rd Genie3 credible). MM-GBSA gate confirms G12D-over-WT selectivity at 12-rep (ddG "
            "-5.00 kcal/mol, 95% CI [-8.6,-1.5]; HELD from the 6-rep -6.33 with p improving "
            "0.017->0.004; Asp6<->HLA-Arg114 bridge intact in 100% of 6000 MD frames). Judged on the "
            "uniform 12-rep-replication standard applied to all credibles (docs/EXPANSION_GATE_PREREG.md "
            "addendum); its independent replication defeats the look-elsewhere concern the FDR step "
            "guards. pLDDT 94; engages peptide bulge 4/5/7/8; HYDROPHOBIC (KD +0.52, expression risk, "
            "disclosed). G12D-vs-WT confirmed only at the bench."))
assert len(NEW_SEQ) == 82

ORDER = [
 "genie3_g2_103_m1", "b3_gpu7_113", "genie3_g6_28_m0", "nb3_gpu4_132",
 "genie3_g2_141_m1",                        # NEW credible #5 (-5.00, Genie3)
 "nb3_gpu6_132", "genie3_8_m0", "b3_gpu7_181", "genie3_g4_121_m1", "nb3_gpu3_307",
 "b3_gpu4_211", "b3_gpu5_174", "genie3_g6_148_m1", "genie3_g5_72_m0", "nb3_gpu7_192",
 "genie3_g6_142_m1", "b3_gpu3_164", "nb3_gpu2_108", "nb3_gpu7_029", "b3_gpu4_161",
]  # dropped vs v4: b2_gpu3_36 (weakest co-fold)
assert len(ORDER) == 20 and len(set(ORDER)) == 20

for f in ["submission.csv", "submission_screens.csv"]:
    bak = f"{S}/{f.replace('.csv','')}.pre-g2141-2026-11-08.bak.csv"
    if not os.path.exists(bak):
        shutil.copy(f"{S}/{f}", bak)

with open(f"{S}/submission.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\r\n")
    w.writerow(["name", "sequence", "molecule_class"])
    for nm in ORDER:
        if nm == NEW_NAME:
            w.writerow([nm, NEW_SEQ, "single_chain"])
        else:
            seq, cls = cur_seq[nm]; w.writerow([nm, seq, cls])

with open(f"{S}/submission_screens.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=SCREEN_COLS, lineterminator="\r\n")
    w.writeheader()
    for i, nm in enumerate(ORDER, 1):
        if nm == NEW_NAME:
            row = dict(NEW_ROW); row["rank"] = i
        else:
            row = dict(carry[nm]); row["rank"] = i
        w.writerow(row)

print("wrote submission.csv + submission_screens.csv (21->20 with g2_141 promoted, b2_gpu3_36 dropped)")
print("credible tier (by gate ddG):")
for nm in ORDER[:5]:
    dd = NEW_ROW["gate_ddG_kcalmol"] if nm == NEW_NAME else carry[nm]["gate_ddG_kcalmol"]
    print(f"  #{ORDER.index(nm)+1} {nm:<20} ddG={dd}")
