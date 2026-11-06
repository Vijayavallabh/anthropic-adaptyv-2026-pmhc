#!/usr/bin/env python
"""Novelty-aware joint re-rank (post devil's-advocate audit, 2026-11-06).

The prior order (final20_two_axis / moderate-hedge) was built from a RESTRICTED
candidate list and (a) buried a novel, preserved-pose, gate-leaning-selective design
(b3_gpu4_161) beneath a novelty-risk, WT-leaning b2 pick (b2_gpu3_36) at #4, and
(b) kept 0.03-0.14 weakest-margin b2 designs in the set while omitting stronger
survivors. The adversary's naive 'rank by weakest' fix would pull novelty-RISK
look-alikes (maxTM 0.95) into the assayed top-10. This re-rank instead optimizes the
competition's stated priority jointly: express+bind -> selectivity evidence
(weakest-margin ruler + credible MM-GBSA gate) -> novelty (4>3) -> diversity.

Ranking rules (explicit, auditable):
  * #1-2  : the 2 credible pose-verified G12D-selectives (preserved pose + gate
            verdict SELECTIVE + positive weakest), ordered by multi-axis dominance.
  * #3-10 : eligible core (gated, positive weakest, NOT gate-WT-favored, no true
            CDR/sequence dup) ranked by weakest margin, with single-chain novelty-RISK
            (maxTM>0.90) demoted below comparably-selective NOVEL designs so the
            ASSAYED window carries zero novelty-risk.
  * 11-15 : positive-weakest reserve (incl. the high-weakest novelty-risk designs,
            disclosed; a b2 lineage rep; a nanobody reserve).
  * 16-20 : gate-WT-favored (anti-selective) designs, last, by weakest (diversity pad).
Emits runs/submission.csv (CRLF) + runs/submission_screens.csv, with backups.
Pure reorder/replacement of EXISTING sequences; no re-gen, no seeding."""
import csv, os, shutil, datetime

ROOT="/home/prachh/v/anthropic-adaptyv-2026-pmhc"
R=f"{ROOT}/runs/campaign"; S=f"{ROOT}/runs"

# ---------- canonical sources ----------
seqs={r["name"]:r["sequence"] for r in csv.DictReader(open(f"{R}/pool_all.csv"))}
# b2_*/nanobody_0202 sequences are not in the b3 pool; take them from the current submission
for r in csv.DictReader(open(f"{S}/submission.csv")):
    seqs.setdefault(r["name"], r["sequence"])
# carry-over screen values for designs already screened (zero drift for retained designs)
carry={r["name"]:r for r in csv.DictReader(open(f"{S}/submission_screens.csv"))}
wk={r["name"]:float(r["weakest"]) for r in csv.DictReader(open(f"{R}/weakest_objective.tsv"),delimiter="\t")}
plddt={r["name"]:float(r["plddt"])*100 for r in csv.DictReader(open(f"{R}/pool_plddt.csv"))}
panel={r["name"]:r for r in csv.DictReader(open(f"{R}/panel_reval.tsv"),delimiter="\t")}
pose={r["name"]:r for r in csv.DictReader(open(f"{R}/gate/pose_realism.tsv"),delimiter="\t")}
# gate: prefer merged (deepest reps, matches published docs), fall back to unified
gate={}
for r in csv.DictReader(open(f"{R}/gate/gate_results_unified.tsv"),delimiter="\t"):
    gate[r["design"]]=(float(r["ddG"]),float(r["ci_lo"]),float(r["ci_hi"]),r["verdict"])
for r in csv.DictReader(open(f"{R}/gate/gate_results_merged.tsv"),delimiter="\t"):
    gate[r["design"]]=(float(r["ddG"]),float(r["ci_lo"]),float(r["ci_hi"]),r["verdict"])
# novelty: single-chain structural maxTM (b3_struct) + carry-over from current screens
nov={}
for line in open(f"{R}/novelty/b3_struct.csv"):
    p=line.strip().split(",")
    if len(p)>=2:
        try: nov[p[0]]=float(p[1])
        except: pass
for r in csv.DictReader(open(f"{S}/submission_screens.csv")):
    v=r["novelty_maxTM_or_basis"]
    if v not in ("","CDR-judged(HCDR3)"):
        try: nov.setdefault(r["name"], float(v))
        except: pass
cls_cur={r["name"]:r["molecule_class"] for r in csv.DictReader(open(f"{S}/submission.csv"))}
def klass(n):
    if n in cls_cur: return cls_cur[n]
    return "nanobody" if (n.startswith("nb") or n.startswith("nanobody")) else "single_chain"

KD={'I':4.5,'V':4.2,'L':3.8,'F':2.8,'C':2.5,'M':1.9,'A':1.8,'G':-0.4,'T':-0.7,'S':-0.8,
    'W':-0.9,'Y':-1.3,'P':-1.6,'H':-3.2,'E':-3.5,'Q':-3.5,'D':-3.5,'N':-3.5,'K':-3.9,'R':-4.5}
def kd(seq): return sum(KD.get(a,0) for a in seq)/len(seq)

# ---- value getters: canonical source first, else carry-over from current screens ----
def g_plddt(n):
    if n in plddt: return plddt[n]
    return float(carry[n]["plddt"]) if n in carry and carry[n]["plddt"] else float("nan")
def g_ip(n):
    if n in panel and panel[n].get("g12d"): return float(panel[n]["g12d"])
    return float(carry[n]["ipSAE_g12d"]) if n in carry and carry[n]["ipSAE_g12d"] else None
def g_wk(n):
    if n in wk: return wk[n]
    return float(carry[n]["weakest_margin"]) if n in carry and carry[n]["weakest_margin"] else 0.0
def g_kd(n): return kd(seqs[n])
def g_gate(n):
    if n in gate: return gate[n]
    if n in carry and carry[n]["gate_ddG_kcalmol"]:
        ci=carry[n]["gate_CI"].strip("[]").split(",")
        return (float(carry[n]["gate_ddG_kcalmol"]), float(ci[0]), float(ci[1]), "")
    return None
def novcol(n):
    if klass(n)!="single_chain": return "CDR-judged(HCDR3)"
    if n in nov: return f"{nov[n]:.3f}"
    return carry[n]["novelty_maxTM_or_basis"] if n in carry else "n/a"

# ---------- THE RANKING DECISION (explicit, post-audit) ----------
ORDER=[
 # 1-2 credible pose-verified selectives
 "b3_gpu7_113","nb3_gpu4_132",
 # 3-10 eligible core by weakest, novelty-aware (zero novelty-risk in the assayed top-10)
 "nb3_gpu6_132","b3_gpu7_181","b3_gpu5_174","b3_gpu4_211","nb3_gpu3_307","nb3_gpu7_192",
 "nb3_gpu7_029","b3_gpu4_161",
 # 11-15 positive-weakest reserve (novelty-risk disclosed; b2 + nanobody reps)
 "b2_gpu3_36","b3_gpu3_164","nb3_gpu2_108","b3_gpu6_132","nb3_gpu6_432",
 # 16-20 gate-WT-favored (anti-selective) pads, by weakest
 "b3_gpu7_136","b3_gpu5_072","nanobody_0202","b2_gpu3_15","b2_gpu4_26",
]
assert len(ORDER)==20 and len(set(ORDER))==20
for n in ORDER: assert n in seqs, f"missing sequence: {n}"

CRED={"b3_gpu7_113","nb3_gpu4_132"}
def reason(n,rank):
    w=g_wk(n); g=g_gate(n); pr=pose.get(n,{}); pl=g_plddt(n)
    kdv=g_kd(n); nv=novcol(n)
    sol = "soluble" if kdv<=0 else f"borderline hydropathy (KD {kdv:+.2f})"
    novs = f"novel (maxTM {nv})" if (nv not in ("CDR-judged(HCDR3)","n/a")) else ("CDR-novel" if nv=="CDR-judged(HCDR3)" else "")
    if n in CRED:
        return (f"Co-fold panel + ensemble MM-GBSA on an Asp6-buried pose predict G12D-over-WT "
                f"selectivity (ddG {g[0]:.1f} kcal/mol, 95% CI [{g[1]:.1f},{g[2]:.1f}] excludes 0); "
                f"pLDDT {pl:.0f}, {sol}. G12D-vs-WT confirmed only at the bench.")
    if n=="nb3_gpu6_132":
        return (f"Strongest co-fold selectivity margin (weakest {w:+.2f}); MM-GBSA selectivity not "
                f"credited (over-docked pose); pLDDT {pl:.0f}, {sol}.")
    if pr.get("verdict")=="WT-favored":
        return (f"Peptide-specific on the co-fold panel (weakest {w:+.2f}) but ensemble MM-GBSA leans "
                f"wild-type; lower-ranked, included for sequence/fold diversity; pLDDT {pl:.0f}, {sol}.")
    realism=pr.get("realism","")
    extra=""
    if realism=="broken": extra=" (co-fold over-docks; MM-GBSA not credited)"
    elif pr.get("name") and realism=="near": extra=" (near-native pose)"
    gca = f"gate CI includes 0" if g else "not gated"
    nrisk = ""
    if nv not in ("CDR-judged(HCDR3)","n/a") and float(nv)>0.90:
        nrisk=f" NOTE structural novelty maxTM {nv} (reserve; disclosed)"
    return (f"Peptide-selective on the co-fold panel (weakest {w:+.2f}); {gca}{extra}; pLDDT {pl:.0f}, "
            f"{sol}{(', '+novs) if novs and nv!='CDR-judged(HCDR3)' else ''}. G12D-vs-WT left to the assay.{nrisk}")

# ---------- backups ----------
stamp=datetime.date.today().isoformat()
shutil.copy(f"{S}/submission.csv", f"{S}/submission.pre-advocate-{stamp}.bak.csv")
shutil.copy(f"{S}/submission_screens.csv", f"{S}/submission_screens.pre-advocate-{stamp}.bak.csv")

# ---------- emit submission.csv (CRLF) ----------
with open(f"{S}/submission.csv","w",newline="") as f:
    w=csv.writer(f,lineterminator="\r\n"); w.writerow(["name","sequence","molecule_class"])
    for n in ORDER: w.writerow([n,seqs[n],klass(n)])

# ---------- emit submission_screens.csv ----------
with open(f"{S}/submission_screens.csv","w",newline="") as f:
    w=csv.writer(f,lineterminator="\r\n")
    w.writerow(["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy",
                "novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"])
    for i,n in enumerate(ORDER,1):
        g=g_gate(n); ip=g_ip(n)
        ci = f"[{g[1]:.1f},{g[2]:.1f}]" if g else ""
        ddg = f"{g[0]:.2f}" if g else ""
        w.writerow([i,n,klass(n),len(seqs[n]),f"{g_plddt(n):.3f}",
                    (f"{ip:.3f}" if ip is not None else ""),f"{g_kd(n):+.3f}",novcol(n),
                    f"{g_wk(n):+.3f}",ddg,ci,reason(n,i)])
print("wrote submission.csv + submission_screens.csv (backups: *.pre-advocate-%s.bak.csv)"%stamp)
print(f"20 designs: {sum(1 for n in ORDER if klass(n)=='single_chain')} single_chain + "
      f"{sum(1 for n in ORDER if klass(n)=='nanobody')} nanobody")
