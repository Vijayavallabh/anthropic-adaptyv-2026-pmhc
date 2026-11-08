#!/usr/bin/env python
"""Re-rank v4: promote the 2 EXPANSION-GATE discoveries into the submission.

The expansion gate (apply the MM-GBSA selectivity judge across the ~2000 paneled designs the
co-fold-blind ruler never tested; pre-registered bar docs/EXPANSION_GATE_PREREG.md) surfaced TWO
new credible G12D-selectives, BOTH Genie3 (orthogonal generator), that cleared the full bar:
C1 static pose-realism, C2 screen, C3 6-rep confirm (ddG<=-4 & CI excl 0), C4 12-rep HOLD,
C5 dynamic bridge (100% of 6000 frames intact), C6 BH-FDR q=0.05 across all 24 confirm tests,
C7 adversarial read (engage peptide bulge 4/5/7/8, 0 Cys, through-space mechanism):
  genie3_g2_103_m1 (rfd_des_g2_pmhc_g12d_103_m1): ddG -12.51 [-17.2,-7.4] -- STRONGEST in campaign,
    yet co-fold weakest-margin 0.011 (ruler-invisible) = direct proof the ruler is blind to the axis.
  genie3_g6_28_m0  (rfd_des_g6_pmhc_g12d_28_m0):  ddG -7.66  [-11.3,-4.0].

Credible count 2 -> 4, now spanning BOTH generators (2 BoltzGen + 2 Genie3) = breaks the
single-generator correlation. Credibles ranked by gate ddG; interleaves generators (G3,BG,G3,BG).
The 2 weakest reserve designs are dropped (b3_gpu6_132 gate +10.1 WT-leaning; nb3_gpu6_432).

Carries ALL existing 20 rows byte-exact from the committed CSVs (zero drift); only inserts the 2
new rows + renumbers. Emits runs/submission.csv (CRLF) + runs/submission_screens.csv, with backups."""
import csv, os, shutil

ROOT = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
S = f"{ROOT}/runs"
KD = {'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'Q':-3.5,'E':-3.5,'G':-0.4,'H':-3.2,'I':4.5,
      'L':3.8,'K':-3.9,'M':1.9,'F':2.8,'P':-1.6,'S':-0.8,'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2}

# ---- current committed submission (carry byte-exact) ----
cur_seq = {r["name"]: (r["sequence"], r["molecule_class"]) for r in csv.DictReader(open(f"{S}/submission.csv"))}
carry = {r["name"]: r for r in csv.DictReader(open(f"{S}/submission_screens.csv"))}
SCREEN_COLS = ["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
               "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"]

# ---- the 2 new expansion-gate credibles ----
g3foldable = {r["name"]: r["sequence"] for r in csv.DictReader(open(f"{ROOT}/runs/genie3/funnel/genie3_foldable.csv"))}
def kd(seq): return sum(KD.get(a,0) for a in seq)/len(seq)
NEW = {
 "genie3_g2_103_m1": dict(internal="rfd_des_g2_pmhc_g12d_103_m1", cls="single_chain",
    plddt="89.000", ipsae="0.474", nov="0.872", weak="+0.011", ddg="-12.51", ci="[-17.2,-7.4]",
    reason=("ORTHOGONAL-lineage (Genie3, non-BoltzGen) de-novo binder; EXPANSION-GATE discovery. "
            "Co-fold ruler-invisible (weakest +0.01) yet the ensemble MM-GBSA gate confirms the "
            "STRONGEST G12D-over-WT selectivity in the campaign (ddG -12.51 kcal/mol, 95% CI "
            "[-17.2,-7.4], 12-rep; FDR-significant q=0.05 across 24 tests; Asp6<->HLA-Arg114 bridge "
            "intact in 100% of 6000 MD frames = NOT an over-dock). pLDDT 89, soluble (KD -1.25); "
            "engages peptide bulge 4/5/7/8. Note: low-complexity E/K N-terminal segment (disclosed). "
            "G12D-vs-WT confirmed only at the bench.")),
 "genie3_g6_28_m0": dict(internal="rfd_des_g6_pmhc_g12d_28_m0", cls="single_chain",
    plddt="95.000", ipsae="0.593", nov="0.895", weak="+0.178", ddg="-7.66", ci="[-11.3,-4.0]",
    reason=("ORTHOGONAL-lineage (Genie3, non-BoltzGen) de-novo binder; EXPANSION-GATE discovery. "
            "Ensemble MM-GBSA gate confirms G12D-over-WT selectivity (ddG -7.66 kcal/mol, 95% CI "
            "[-11.3,-4.0], 12-rep; FDR-significant q=0.05; Asp6<->HLA-Arg114 bridge intact in 100% of "
            "6000 MD frames). pLDDT 95; engages peptide bulge 4/5/7/8; borderline hydropathy "
            "(KD +0.10, disclosed). G12D-vs-WT confirmed only at the bench.")),
}
for nm, d in NEW.items():
    seq = g3foldable[d["internal"]]
    d["seq"] = seq; d["len"] = str(len(seq)); d["kd"] = f"{kd(seq):+.3f}"

# ---- FINAL ORDER (20): 4 credibles by gate ddG (interleaved generators), then co-fold tier ----
ORDER = [
 "genie3_g2_103_m1",   # NEW credible  -12.51  (Genie3)
 "b3_gpu7_113",        # credible      -9.29   (BoltzGen protein)
 "genie3_g6_28_m0",    # NEW credible  -7.66   (Genie3)
 "nb3_gpu4_132",       # credible      -7.27   (BoltzGen vhh)
 "nb3_gpu6_132", "genie3_8_m0", "b3_gpu7_181", "genie3_g4_121_m1", "nb3_gpu3_307", "b3_gpu4_211",
 "b3_gpu5_174", "genie3_g6_148_m1", "genie3_g5_72_m0", "nb3_gpu7_192", "genie3_g6_142_m1",
 "b3_gpu3_164", "nb3_gpu2_108", "nb3_gpu7_029", "b3_gpu4_161", "b2_gpu3_36",
]  # dropped: b3_gpu6_132 (gate +10.1 WT-leaning), nb3_gpu6_432
assert len(ORDER) == 20 and len(set(ORDER)) == 20

# ---- backups (preserve earliest) ----
for f in ["submission.csv", "submission_screens.csv"]:
    bak = f"{S}/{f.replace('.csv','')}.pre-expansion-2026-11-08.bak.csv"
    if not os.path.exists(bak):
        shutil.copy(f"{S}/{f}", bak)

# ---- emit submission.csv (CRLF) ----
with open(f"{S}/submission.csv", "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\r\n")
    w.writerow(["name", "sequence", "molecule_class"])
    for nm in ORDER:
        if nm in NEW:
            w.writerow([nm, NEW[nm]["seq"], NEW[nm]["cls"]])
        else:
            seq, cls = cur_seq[nm]
            w.writerow([nm, seq, cls])

# ---- emit submission_screens.csv ----
with open(f"{S}/submission_screens.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=SCREEN_COLS, lineterminator="\r\n")
    w.writeheader()
    for i, nm in enumerate(ORDER, 1):
        if nm in NEW:
            d = NEW[nm]
            w.writerow(dict(rank=i, name=nm, **{"class": d["cls"]}, length=d["len"], plddt=d["plddt"],
                            ipSAE_g12d=d["ipsae"], mean_KD_hydropathy=d["kd"],
                            novelty_maxTM_or_basis=d["nov"], weakest_margin=d["weak"],
                            gate_ddG_kcalmol=d["ddg"], gate_CI=d["ci"], reason=d["reason"]))
        else:
            row = dict(carry[nm]); row["rank"] = i
            w.writerow(row)

print(f"wrote {S}/submission.csv + submission_screens.csv (20 designs; 2 new credibles promoted)")
print("credible tier (by gate ddG):")
for nm in ORDER[:4]:
    src = NEW[nm]["ddg"] if nm in NEW else carry[nm]["gate_ddG_kcalmol"]
    print(f"  {ORDER.index(nm)+1}. {nm:<20} ddG={src}")
