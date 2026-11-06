#!/usr/bin/env python
"""Produce the final ranked submission order + a publishable per-design screen table, aligned to the
competition's published selection rubric (express+bind first; 3 screens pLDDT/ipSAE/hydropathy; evidence
for the hardest goal = selectivity; novelty 4>3; diversity + long shots). Cap is 10 designs/submission
taken in our order, so the TOP 10 is optimized: 2 credible MM-GBSA selectives first, then strongest
co-fold-ruler designs, with the 2 best soluble INDEPENDENT-lineage designs lifted into the assayed 10 to
hedge correlated model error; weak/hydrophobic designs kept below the cut. PURE REORDER (no add/drop/seed).
All shareable text is neutral and honest."""
import csv
CAMP="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs/campaign"
RUNS="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs"
KD={'I':4.5,'V':4.2,'L':3.8,'F':2.8,'C':2.5,'M':1.9,'A':1.8,'G':-0.4,'T':-0.7,'S':-0.8,
    'W':-0.9,'Y':-1.3,'P':-1.6,'H':-3.2,'E':-3.5,'Q':-3.5,'D':-3.5,'N':-3.5,'K':-3.9,'R':-4.5}
def coarse(l): return "b3" if "b3" in l else ("b2" if "b2" in l else "other")
comb={r["name"]:r for r in csv.DictReader(open(f"{CAMP}/combined_all_ranked.tsv"),delimiter="\t")}
rat ={r["name"]:r for r in csv.DictReader(open(f"{CAMP}/final20_two_axis_rationale.tsv"),delimiter="\t")}
seq={}; cls={}
for r in csv.DictReader(open(f"{RUNS}/submission.csv")): seq[r["name"]]=r["sequence"]; cls[r["name"]]=r["molecule_class"]
def f(x):
    try: return float(x)
    except: return None
D={}
for n in rat:
    c=comb.get(n,{})
    D[n]=dict(name=n,cls=cls[n],lin=rat[n]["lineage"],coarse=coarse(rat[n]["lineage"]),
        tier=rat[n]["tier"],realism=rat[n]["realism"],ddg=f(rat[n]["ddG_G12D-WT"]),ci=rat[n]["CI"],
        wk=f(rat[n]["weakest"]),lim=rat[n]["limiting"],pad=(rat[n]["core_or_pad"]!="CORE"),
        plddt=f(c.get("esm")),ipsae=f(c.get("bp")),maxtm=f(c.get("maxtm")),
        nov=c.get("novelty_risk","?"),kd=sum(KD[a] for a in seq[n])/len(seq[n]),ln=len(seq[n]))
# ---- order: credible selectives (most-negative ddG first) ----
cred=sorted([d for d in D.values() if d["tier"].startswith("1-CREDIBLE")],key=lambda d:d["ddg"])
rest=[d for d in D.values() if not d["tier"].startswith("1-CREDIBLE") and not d["pad"]]
pad =sorted([d for d in D.values() if d["pad"]],key=lambda d:-d["wk"])
b3   =sorted([d for d in rest if d["coarse"]=="b3"],key=lambda d:-d["wk"])
indep=sorted([d for d in rest if d["coarse"]!="b3" and d["kd"]<=0.0],key=lambda d:-d["wk"])  # soluble independents = hedges
hydro=[d for d in rest if d["coarse"]!="b3" and d["kd"]>0.0]                                  # non-soluble independents -> below cut
# top-10: cred(2) + b3 leader + hedge1 + next5 b3 + hedge2
top = cred + [b3[0], indep[0]] + b3[1:6] + [indep[1]]
remaining = sorted(b3[6:]+indep[2:]+hydro, key=lambda d:-d["wk"])
order = top + remaining + pad
assert len({d["name"] for d in order})==20, "lost a design"
# ---- emit reordered submission CSV (CRLF; sequences byte-identical) ----
with open(f"{CAMP}/final20_selected.csv","w",newline="") as o:
    w=csv.writer(o,lineterminator="\r\n"); w.writerow(["name","sequence","molecule_class"])
    for d in order: w.writerow([d["name"],seq[d["name"]],d["cls"]])
# ---- publishable per-design screen table (mirrors the selector's own CSV deliverable; neutral reasons) ----
def reason(d):
    sol = "soluble (KD %+.2f)"%d["kd"] if d["kd"]<=0 else "borderline hydropathy (KD %+.2f)"%d["kd"]
    fold= ("pLDDT %.2f"%d["plddt"]) if d["plddt"] is not None else "pLDDT n/a"
    if d["tier"].startswith("1-CREDIBLE"):
        return f"Co-fold panel + ensemble MM-GBSA on an Asp6-buried pose predict G12D-over-WT selectivity (ddG {d['ddg']:+.1f} kcal/mol, 95% CI {d['ci']} excludes 0); {fold}, {sol}. G12D-vs-WT confirmed only at the bench."
    if d["tier"].startswith("2-selective"):
        return f"Strongest co-fold selectivity margin (weakest {d['wk']:+.2f}); MM-GBSA selectivity not credited (over-docked pose); {fold}, {sol}."
    if d["pad"]:
        return f"Peptide-specific on the co-fold panel (weakest {d['wk']:+.2f}) but ensemble MM-GBSA leans wild-type; lower-ranked, included for sequence/fold diversity; {fold}, {sol}."
    tag = "rescue re-gate returned null (earlier over-docked)" if "realistic-pose" in d["tier"] else ("gate CI includes 0" if "lean" in d["tier"] else "gate neutral")
    return f"Peptide-selective on the co-fold panel (weakest {d['wk']:+.2f}); {tag}; {fold}, {sol}. G12D-vs-WT left to the assay."
def novcol(d):
    if d["cls"] in ("nanobody","scfv","fab_kappa","fab_lambda"): return "CDR-judged(HCDR3)"
    return f"{d['maxtm']:.3f}" if (d["maxtm"] is not None and d["maxtm"]>0) else "n/a"
with open(f"{RUNS}/submission_screens.csv","w",newline="") as o:
    w=csv.writer(o); w.writerow(["rank","name","class","length","plddt","ipSAE_g12d","mean_KD_hydropathy","novelty_maxTM_or_basis","weakest_margin","gate_ddG_kcalmol","gate_CI","reason"])
    for i,d in enumerate(order,1):
        w.writerow([i,d["name"],d["cls"],d["ln"],
            f"{d['plddt']:.3f}" if d["plddt"] is not None else "",
            f"{d['ipsae']:.3f}" if d["ipsae"] is not None else "",
            f"{d['kd']:+.3f}", novcol(d),
            f"{d['wk']:+.3f}", f"{d['ddg']:+.2f}" if d["ddg"] is not None else "", d["ci"], reason(d)])
print("order:")
for i,d in enumerate(order,1):
    star="<= top-10 cut" if i==10 else ""
    print(f"{i:>2} {d['name']:16}{d['cls']:12}{d['coarse']:6}wk{d['wk']:+.3f} pLDDT {str(round(d['plddt'],2)) if d['plddt'] else 'na':<5} ipSAE {str(round(d['ipsae'],2)) if d['ipsae'] else 'na':<5} KD{d['kd']:+.2f} {star}")
print("\ntop-10 lineages:", [d["coarse"] for d in order[:10]], "| distinct:", len({d["coarse"] for d in order[:10]}),"| independents:", sum(1 for d in order[:10] if d["coarse"]!="b3"))
print("wrote final20_selected.csv , submission_screens.csv")
