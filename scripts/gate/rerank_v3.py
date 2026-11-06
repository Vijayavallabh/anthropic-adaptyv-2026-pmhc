#!/usr/bin/env python
"""Final re-rank incorporating the ORTHOGONAL Genie3 designs (post gate + pose-realism + novelty).

Rationale: the orthogonal-generator run (Genie3, non-BoltzGen) produced competitive, novel, preserved-pose
peptide-selective designs on the SAME weakest-margin ruler. None is a credible selective (the one gate-selective
was an over-dock artifact; the top co-fold design _176 was gate-WT-favored = refuted), but 5 are preserved-pose,
positive-weakest, not-WT-favored -- the same evidence tier as the BoltzGen ruler core, from an independent
generator. Promoting them is the correlated-failure hedge (ranked-submission-win-math: cap within-lineage
correlation for P(>=1 win)). The 2 gate-confirmed credible selectives stay at #1-2 (only designs with evidence on
the G12D-vs-WT axis). Gate-WT-favored and over-dock Genie3 designs are EXCLUDED (honest: the gate refuted them).

Result: all-positive-weakest 20 spanning TWO generators (BoltzGen+Genie3) + both classes; the 5 BoltzGen
WT-favored anti-selective pads are dropped. Pure reorder/replacement of EXISTING sequences; no re-gen, no seeding.
Emits runs/submission.csv (CRLF) + runs/submission_screens.csv, with backups."""
import csv, os, shutil, datetime

ROOT="/home/prachh/v/anthropic-adaptyv-2026-pmhc"
S=f"{ROOT}/runs"; G=f"{ROOT}/runs/genie3"

# ---- Genie3 sources ----
g3seq={r["name"]:r["sequence"] for r in csv.DictReader(open(f"{G}/funnel/panel_pool.csv"))}
g3pl={r["name"]:float(r["plddt"])*100 for r in csv.DictReader(open(f"{G}/funnel/genie3_plddt.csv"))}
g3panel={r["name"]:r for r in csv.DictReader(open(f"{G}/funnel/panel_reval.tsv"),delimiter="\t")}
g3wk={r["name"]:float(r["weakest"]) for r in csv.DictReader(open(f"{G}/funnel/weakest.tsv"),delimiter="\t")}
g3gate={r["design"]:(float(r["ddG"]),float(r["ci_lo"]),float(r["ci_hi"]),r["verdict"]) for r in csv.DictReader(open(f"{G}/gate/gate_results_genie3.tsv"),delimiter="\t")}
# prefer the DEEPER 12-rep estimate where available (the 6-rep gate-lean on 148/72 was small-n noise)
_deep=f"{G}/gate/gate_results_genie3_deep.tsv"
if os.path.exists(_deep):
    for r in csv.DictReader(open(_deep),delimiter="\t"):
        g3gate[r["design"]]=(float(r["ddG"]),float(r["ci_lo"]),float(r["ci_hi"]),r["verdict"])
g3nov={r["name"]:float(r["singleseq_maxTM_pdb"]) for r in csv.DictReader(open(f"{G}/funnel/genie3_novelty.csv"))}
g3pose={ # Asp6<->HLA salt-bridge (computed): all 5 promotable preserved (<4A)
 "rfd_des_pmhc_g12d_8_m0":2.59,"rfd_des_g4_pmhc_g12d_121_m1":2.76,"rfd_des_g6_pmhc_g12d_142_m1":2.78,
 "rfd_des_g5_pmhc_g12d_72_m0":2.94,"rfd_des_g6_pmhc_g12d_148_m1":2.93}
# clean display names (strip misleading rfd_ prefix; these are Genie3)
RENAME={"rfd_des_pmhc_g12d_8_m0":"genie3_8_m0","rfd_des_g4_pmhc_g12d_121_m1":"genie3_g4_121_m1",
 "rfd_des_g6_pmhc_g12d_142_m1":"genie3_g6_142_m1","rfd_des_g5_pmhc_g12d_72_m0":"genie3_g5_72_m0",
 "rfd_des_g6_pmhc_g12d_148_m1":"genie3_g6_148_m1"}
G3SET=set(RENAME)

# ---- BoltzGen carry-over from the committed screens ----
carry={r["name"]:r for r in csv.DictReader(open(f"{S}/submission_screens.csv"))}
bseq={r["name"]:r["sequence"] for r in csv.DictReader(open(f"{S}/submission.csv"))}

# ---- THE FINAL ORDER (internal Genie3 names; renamed on emit) ----
ORDER=[
 "b3_gpu7_113","nb3_gpu4_132",                                   # 1-2 credible selectives (gate-confirmed)
 "nb3_gpu6_132",                                                 # 3 top co-fold margin (over-dock; pLDDT 95)
 "rfd_des_pmhc_g12d_8_m0",                                       # 4 Genie3 lead orthogonal (wk 0.49, soluble -0.50)
 "b3_gpu7_181",                                                  # 5
 "rfd_des_g4_pmhc_g12d_121_m1",                                  # 6 Genie3 NOVEL (maxTM 0.68)
 "nb3_gpu3_307",                                                 # 7 nanobody class hedge
 "b3_gpu4_211",                                                  # 8 BoltzGen (wk 0.485, novel 0.80)
 "b3_gpu5_174",                                                  # 9
 "rfd_des_g6_pmhc_g12d_148_m1",                                  # 10 Genie3 gate-leans-selective (-5.2), soluble
 # 11-20 reserve (positive-weakest; not assayed within the cap). Hydrophobic Genie3 (72/142) held here.
 "rfd_des_g5_pmhc_g12d_72_m0","nb3_gpu7_192","rfd_des_g6_pmhc_g12d_142_m1","b3_gpu3_164","nb3_gpu2_108",
 "nb3_gpu7_029","b3_gpu4_161","b2_gpu3_36","b3_gpu6_132","nb3_gpu6_432",
]
assert len(ORDER)==20 and len(set(ORDER))==20
def disp(n): return RENAME.get(n,n)
def klass(n):
    if n in G3SET: return "single_chain"
    return carry[n]["class"]
def seqof(n): return g3seq[n] if n in G3SET else bseq[n]

KD={'I':4.5,'V':4.2,'L':3.8,'F':2.8,'C':2.5,'M':1.9,'A':1.8,'G':-0.4,'T':-0.7,'S':-0.8,
    'W':-0.9,'Y':-1.3,'P':-1.6,'H':-3.2,'E':-3.5,'Q':-3.5,'D':-3.5,'N':-3.5,'K':-3.9,'R':-4.5}
def kd(s): return sum(KD.get(a,0) for a in s)/len(s)

def vals(n):
    if n in G3SET:
        g=g3gate.get(n);
        return dict(plddt=g3pl[n], ipsae=float(g3panel[n]["g12d"]), kd=kd(g3seq[n]),
                    nov=f"{g3nov[n]:.3f}", wk=g3wk[n],
                    ddg=(f"{g[0]:.2f}" if g else ""), ci=(f"[{g[1]:.1f},{g[2]:.1f}]" if g else ""),
                    verdict=(g[3] if g else ""), pose=g3pose.get(n))
    c=carry[n]
    return dict(plddt=float(c["plddt"]), ipsae=float(c["ipSAE_g12d"]) if c["ipSAE_g12d"] else None,
                kd=float(c["mean_KD_hydropathy"]), nov=c["novelty_maxTM_or_basis"], wk=float(c["weakest_margin"]),
                ddg=c["gate_ddG_kcalmol"], ci=c["gate_CI"], verdict="", pose=None)

CRED={"b3_gpu7_113","nb3_gpu4_132"}
def reason(n):
    v=vals(n); pl=v["plddt"]; w=v["wk"]; kdv=v["kd"]
    sol="soluble" if kdv<=0 else f"borderline hydropathy (KD {kdv:+.2f})"
    if n in CRED:
        return (f"Co-fold panel + ensemble MM-GBSA on an Asp6-buried pose predict G12D-over-WT selectivity "
                f"(ddG {v['ddg']} kcal/mol, 95% CI {v['ci']} excludes 0); pLDDT {pl:.0f}, {sol}. "
                f"G12D-vs-WT confirmed only at the bench.")
    if n=="nb3_gpu6_132":
        return (f"Strongest co-fold selectivity margin (weakest {w:+.2f}); MM-GBSA not credited (over-docked pose); "
                f"pLDDT {pl:.0f}, {sol}.")
    if n in G3SET:
        gate_note=("gate leans selective (ddG "+v["ddg"]+", CI incl 0)" if v["verdict"]=="null(CI-incl-0)" and float(v["ddg"])<=-3
                   else "gate CI includes 0")
        novn=f"structural novelty maxTM {v['nov']}"
        return (f"ORTHOGONAL-lineage (Genie3, non-BoltzGen) de-novo binder; peptide-selective on the co-fold panel "
                f"(weakest {w:+.2f}), preserved Asp6-buried pose; {gate_note}; pLDDT {pl:.0f}, {sol}, {novn}. "
                f"Independent generator = correlated-failure hedge. G12D-vs-WT left to the assay.")
    # BoltzGen core/reserve
    return (f"Peptide-selective on the co-fold panel (weakest {w:+.2f}); gate CI includes 0; pLDDT {pl:.0f}, {sol}. "
            f"G12D-vs-WT left to the assay.")

stamp=datetime.date.today().isoformat()
# preserve the FIRST backup (clean post-advocate version); never overwrite on re-run
for src,bak in [(f"{S}/submission.csv",f"{S}/submission.pre-genie3-{stamp}.bak.csv"),
                (f"{S}/submission_screens.csv",f"{S}/submission_screens.pre-genie3-{stamp}.bak.csv")]:
    if not os.path.exists(bak): shutil.copy(src,bak)

with open(f"{S}/submission.csv","w",newline="") as f:
    w=csv.writer(f,lineterminator="\r\n"); w.writerow(["name","sequence","molecule_class"])
    for n in ORDER: w.writerow([disp(n),seqof(n),klass(n)])

with open(f"{S}/submission_screens.csv","w",newline="") as f:
    w=csv.writer(f,lineterminator="\r\n")
    w.writerow(["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
                "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"])
    for i,n in enumerate(ORDER,1):
        v=vals(n)
        w.writerow([i,disp(n),klass(n),len(seqof(n)),f"{v['plddt']:.3f}",
                    (f"{v['ipsae']:.3f}" if v['ipsae'] is not None else ""),f"{v['kd']:+.3f}",
                    v['nov'],f"{v['wk']:+.3f}",v['ddg'],v['ci'],reason(n)])

ng=sum(1 for n in ORDER if n in G3SET); nb=sum(1 for n in ORDER if klass(n)=="nanobody")
print(f"wrote submission.csv + screens (backups *.pre-genie3-{stamp}.bak.csv)")
print(f"20 designs: {20-nb} single_chain + {nb} nanobody; lineages: {20-ng} BoltzGen + {ng} Genie3(orthogonal)")
print(f"top-10 Genie3: {sum(1 for n in ORDER[:10] if n in G3SET)}; top-10 nanobody: {sum(1 for n in ORDER[:10] if klass(n)=='nanobody')}")
print("all-positive-weakest:", all(vals(n)['wk']>0 for n in ORDER))
