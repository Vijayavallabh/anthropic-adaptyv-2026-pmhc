#!/usr/bin/env python
"""Regenerate the two-axis decision artifacts using the DEEPENED (12-replica) gate verdicts
for the 8-design core, falling back to 6-replica for the other 24. Writes an audit column
(nrep) so every row says how much MD backs it. Selection+upload remain USER-GATED.

Policy unchanged from emit_artifacts.py:
  HARD FILTER : ruler weakest > 0 (peptide-specific on the co-fold axes).
  RANK KEY    : gate_bonus + ruler_weakest ; gate_bonus = +3 selective (ddG<=-4 & ci_hi<0),
                +1 lean (ddG<0, CI incl 0), -3 WT-favored (ddG>=4 & ci_lo>0), else 0 null.
  CORE        = ruler_ok AND not gate-WT-favored. PAD = ruler_ok AND gate-WT-favored (optional).
"""
import csv
CAMP="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs/campaign"; RUNS="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs"
G=f"{CAMP}/gate"
def ltsv(p,k="name"): return {r[k]:r for r in csv.DictReader(open(p),delimiter="\t")}
def mem(p): return {r["name"] for r in csv.DictReader(open(p))}
def fnum(x):
    try:return float(x)
    except:return None

gate6=ltsv(f"{G}/gate_results_all.tsv",k="design")      # 6-rep, all 32
deep =ltsv(f"{G}/core8_deep_results.tsv",k="design")     # 12-rep, the core 8
weak =ltsv(f"{CAMP}/weakest_objective.tsv"); comb=ltsv(f"{CAMP}/combined_all_ranked.tsv")
try: realm={r["name"]:r["realism"] for r in csv.DictReader(open(f"{G}/pose_realism.tsv"),delimiter="\t")}
except FileNotFoundError: realm={}
locked=mem(f"{RUNS}/submission.csv"); proposed=mem(f"{CAMP}/combined_submission.csv")
seqs={}; cls={}
for src in [f"{CAMP}/combined_submission.csv",f"{RUNS}/submission.csv"]:
    for r in csv.DictReader(open(src)):
        seqs.setdefault(r["name"],r["sequence"]); cls.setdefault(r["name"],r["molecule_class"])

# ---- merged gate table: prefer 12-rep where present ----
merged={}
for n,g in gate6.items():
    if n in deep:
        d=deep[n]; merged[n]=dict(ddG=d["ddG"],ci_lo=d["ci_lo"],ci_hi=d["ci_hi"],p=d["p"],verdict=d["verdict"],nrep=int(d["nG"]))
    else:
        merged[n]=dict(ddG=g["ddG"],ci_lo=g["ci_lo"],ci_hi=g["ci_hi"],p=g["p"],verdict=g["verdict"],nrep=6)
# ---- POSE-RESCUE overlay: an over-docked selective re-gated on its PRESERVED (Asp6-buried) pose.
# The rescue (keyed design+"_r") is the AUTHORITATIVE gate call: override the broken-pose ddG/CI and
# force realism "preserved" so the normal tier logic promotes it IFF it is STILL selective on the real
# pose; if it goes null the design is correctly re-labelled null-on-realistic-pose (artifact confirmed).
rescued=set()
try:
    for r in csv.DictReader(open(f"{G}/gate_results_rescue.tsv"),delimiter="\t"):
        base=r["design"][:-2] if r["design"].endswith("_r") else r["design"]
        merged[base]=dict(ddG=r["ddG"],ci_lo=r["ci_lo"],ci_hi=r["ci_hi"],p=r["p"],verdict=r["verdict"],nrep=int(r["nG"]))
        realm[base]="preserved"; rescued.add(base)
except FileNotFoundError: pass
with open(f"{G}/gate_results_merged.tsv","w") as o:
    o.write("design\tnrep\tddG\tci_lo\tci_hi\tp\tverdict\n")
    for n in sorted(merged,key=lambda n:fnum(merged[n]["ddG"]) if fnum(merged[n]["ddG"]) is not None else 1e9):
        m=merged[n]; o.write(f'{n}\t{m["nrep"]}\t{m["ddG"]}\t{m["ci_lo"]}\t{m["ci_hi"]}\t{m["p"]}\t{m["verdict"]}\n')

R=[]
for n,m in merged.items():
    w=weak.get(n,{}); c=comb.get(n,{})
    ddg=fnum(m["ddG"]); cilo=fnum(m["ci_lo"]); cihi=fnum(m["ci_hi"]); wk=fnum(w.get("weakest"))
    sel=ddg is not None and ddg<=-4 and cihi is not None and cihi<0
    wt =ddg is not None and ddg>=4 and cilo is not None and cilo>0
    leans=(ddg is not None and ddg<0 and not sel)
    ruler_ok=wk is not None and wk>0
    # Gate confirms G12D-vs-WT ONLY from a PHYSICALLY REALISTIC pose. pose_realism.tsv: "preserved"
    # = native Asp6<->HLA salt bridge intact (<4A) -> Asp6 stays buried, binder discriminates
    # THROUGH-SPACE = the intended non-mimetic mechanism. "broken" = Asp6 swung ~8A out to H-bond the
    # binder = over-dock artifact (co-fold reaching a buried residue), so its selective call is suspect.
    # Only a preserved + CI-excludes-0 selective earns promotion (+3). A broken-pose selective gets 0
    # credit (ranked on the pre-registered ruler, flagged). Anti-selective (CI>0) demoted (-3).
    preserved = realm.get(n)=="preserved"
    resc = n in rescued
    credible  = sel and preserved
    gb=3.0 if credible else (-3.0 if wt else 0.0)
    if credible and ruler_ok: tier="1-CREDIBLE-SEL"+("(RESCUED preserved pose)" if resc else "(preserved pose)")
    elif wt and ruler_ok: tier="5-WT-favored(anti-sel)"
    elif resc and ruler_ok: tier="4-null-on-realistic-pose(rescue->artifact)"
    elif sel and ruler_ok: tier="2-selective(OVER-DOCKED;suspect)"
    elif leans and ruler_ok: tier="3-lean(CI-incl-0;ranks-null)"
    elif (not wt) and ruler_ok: tier="4-clean-null"
    else: tier="X-platform-binder(ruler<=0)"
    R.append(dict(name=n,cls=cls.get(n,c.get("cls","?")),lin=w.get("lineage") or c.get("lineage","?"),
        locked=n in locked,prop=n in proposed,ddg=ddg,cilo=cilo,cihi=cihi,p=m["p"],verdict=m["verdict"],nrep=m["nrep"],
        m_scram=fnum(w.get("m_scram")),m_promisc=fnum(w.get("m_promisc")),m_empty=fnum(w.get("m_empty")),
        wk=wk,lim=w.get("limiting","?"),nov=c.get("novelty_risk","?"),tier=tier,
        realism=realm.get(n,"?"),preserved=preserved,credible=credible,rescued=resc,
        key=gb+(wk if wk is not None else -1),sel=sel,wt=wt,leans=leans,ruler_ok=ruler_ok))

core=sorted([r for r in R if r["ruler_ok"] and not r["wt"]],key=lambda r:-r["key"])
pad =sorted([r for r in R if r["ruler_ok"] and r["wt"]],key=lambda r:-r["key"])
rec=core+pad
for i,r in enumerate(rec,1): r["rank"]=i
# ---- SENSITIVITY: ruler-primary alternative (gate as FILTER-ONLY, not ranker) ----
# Rank the same ruler-ok, non-anti-selective core PURELY by the pre-registered ruler (weakest
# margin); confirmed anti-selectives stay demoted. Shows how much each design's rank depends on
# trusting the gate as a *ranker* vs. a *filter for the clear winners* -- the open question.
core_rp=sorted([r for r in R if r["ruler_ok"] and not r["wt"]],
               key=lambda r:-(r["wk"] if r["wk"] is not None else -1))
for i,r in enumerate(core_rp,1): r["rp_rank"]=i
for r in pad: r["rp_rank"]=None
for r in R:
    gp=r.get("rank"); rp=r.get("rp_rank")
    r["robust_top5"]=(gp is not None and rp is not None and gp<=5 and rp<=5)
    r["gate_promoted"]=(r["credible"] and rp is not None and gp is not None and (rp-gp)>=3)
with open(f"{G}/two_axis_sensitivity.tsv","w") as o:
    o.write("gate_rank\truler_rank\tdelta\tname\tcls\tgate_status\trealism\twk\tddG\tCI\trobust_top5\tnote\n")
    for r in sorted(core,key=lambda r:r["rank"]):
        gp=r["rank"]; rp=r["rp_rank"]
        st=("CRED-SEL" if r["credible"] else ("od-sel" if r["sel"] else ("lean" if r["leans"] else "null")))
        note=("ROBUST(top5 both axes)" if r["robust_top5"] else ("gate-promoted" if r["gate_promoted"] else ("over-docked-sel(no gate credit)" if r["sel"] and not r["credible"] else "")))
        o.write(f'{gp}\t{rp}\t{rp-gp:+d}\t{r["name"]}\t{r["cls"]}\t{st}\t{r["realism"]}\t{r["wk"]:+.3f}\t{r["ddg"]:+.2f}\t[{r["cilo"]:+.1f},{r["cihi"]:+.1f}]\t{r["robust_top5"]}\t{note}\n')

cols=["name","cls","lin","locked","prop","nrep","ddg","cilo","cihi","p","wk","m_scram","m_promisc","m_empty","lim","nov","realism","tier"]
with open(f"{G}/two_axis_decision.tsv","w") as o:
    o.write("\t".join(cols)+"\n")
    for r in sorted(R,key=lambda r:(r["ddg"] if r["ddg"] is not None else 1e9)):
        o.write("\t".join(str(r.get(c,"")) for c in cols)+"\n")

with open(f"{CAMP}/final20_two_axis_recommended.csv","w",newline="") as o:
    wtr=csv.writer(o); wtr.writerow(["name","sequence","molecule_class"])
    for r in rec[:20]:
        wtr.writerow([r["name"],seqs.get(r["name"],"SEQ_MISSING"),r["cls"]])
with open(f"{CAMP}/final20_two_axis_rationale.tsv","w") as o:
    o.write("rank\truler_rank\tname\tcls\tlineage\tnrep\ttier\trealism\tddG_G12D-WT\tCI\tweakest\tlimiting\tcore_or_pad\n")
    for r in rec[:20]:
        cp="CORE" if r["rank"]<=len(core) else "pad(optional)"
        rp=r.get("rp_rank"); rps=str(rp) if rp else "-"
        o.write(f'{r["rank"]}\t{rps}\t{r["name"]}\t{r["cls"]}\t{r["lin"]}\t{r["nrep"]}\t{r["tier"]}\t{r["realism"]}\t{r["ddg"]:+.2f}\t[{r["cilo"]:+.1f},{r["cihi"]:+.1f}]\t{r["wk"]:+.3f}\t{r["lim"]}\t{cp}\n')

print(f"core(clean)={len(core)}  padding(optional)={len(pad)}  selectives(12rep)={sum(1 for r in R if r['sel'])}")
print(f"wrote {G}/gate_results_merged.tsv , {G}/two_axis_decision.tsv")
print(f"wrote {CAMP}/final20_two_axis_recommended.csv , final20_two_axis_rationale.tsv\n")
print("GP RP  TIER                             DESIGN            CLS         NREP POSE       ddG     CI                 wk")
for r in rec[:20]:
    cp="CORE" if r["rank"]<=len(core) else "PAD "
    rp=r.get("rp_rank"); rps=f'{rp:>2}' if rp else ' -'
    print(f'{r["rank"]:2} {rps} {cp} {r["tier"]:33} {r["name"]:16} {r["cls"]:11} {r["nrep"]:>3} {r["realism"]:9} {r["ddg"]:+6.2f} [{r["cilo"]:+6.1f},{r["cihi"]:+6.1f}]  {r["wk"]:+.3f}')
print(f'\nCREDIBLE (preserved-pose) selectives in core:', [r["name"] for r in core if r["credible"]])
print(f'OVER-DOCKED selectives (gate credit withheld, ranked on ruler):', [r["name"] for r in core if r["sel"] and not r["credible"]])
print(f'RESCUED (now credible on realistic pose):', [r["name"] for r in R if r.get("rescued") and r["credible"]])
print(f'Rescue FAILED (null on realistic pose -> artifact confirmed):', [r["name"] for r in R if r.get("rescued") and not r["credible"]])
print(f'\nCORE class mix: ', {k:sum(1 for r in core if r["cls"]==k) for k in sorted(set(r["cls"] for r in core))})
print(f'CORE lineage mix:', {k:sum(1 for r in core if r["lin"]==k) for k in sorted(set(r["lin"] for r in core))})
