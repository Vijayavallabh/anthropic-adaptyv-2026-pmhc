#!/usr/bin/env python
"""Diversity-aware re-ranking of the finalized 20 (deep-research 2026-11-06, Levers #1/#2/#5):
winning = P(>=1 assayed hit), so CAP within-lineage correlation at the TOP instead of stacking
correlated cousins. Keeps the 2 credible selectives at #1-2 (posterior-top + equilibrium-ceiling:
most-negative ddG first); then interleaves coarse lineages (b3/b2/other) by greedily picking the
design maximizing weakest_margin - LAM*(already-placed same-lineage), which for our pool equals a
lineage round-robin ordered within each lineage by the ruler. PURE REORDER of the finalized 20 -
no add/drop, no seeding, sequences byte-identical. Emits the reordered submission CSV + rationale."""
import csv
CAMP="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs/campaign"
RUNS="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs"
LAM=0.15
def coarse(lin): return "b3" if "b3" in lin else ("b2" if "b2" in lin else "other")
rat={}
for r in csv.DictReader(open(f"{CAMP}/final20_two_axis_rationale.tsv"),delimiter="\t"):
    rat[r["name"]]=r
seq={}; cls={}
for r in csv.DictReader(open(f"{RUNS}/submission.csv")):
    seq[r["name"]]=r["sequence"]; cls[r["name"]]=r["molecule_class"]
rows=[dict(name=n,cls=cls[n],lin=rat[n]["lineage"],coarse=coarse(rat[n]["lineage"]),
           tier=rat[n]["tier"],realism=rat[n]["realism"],ddg=float(rat[n]["ddG_G12D-WT"]),
           ci=rat[n]["CI"],wk=float(rat[n]["weakest"]),lim=rat[n]["limiting"],
           oldrank=int(rat[n]["rank"]),pad=(rat[n]["core_or_pad"]!="CORE")) for n in rat]
cred=sorted([r for r in rows if r["tier"].startswith("1-CREDIBLE")],key=lambda r:r["ddg"])
core_rest=[r for r in rows if not r["tier"].startswith("1-CREDIBLE") and not r["pad"]]
padd=[r for r in rows if r["pad"]]
def greedy(pool,placed):
    cnt={}; [cnt.__setitem__(r["coarse"],cnt.get(r["coarse"],0)+1) for r in placed]
    out=[]; pool=pool[:]
    while pool:
        b=max(pool,key=lambda r:r["wk"]-LAM*cnt.get(r["coarse"],0))
        out.append(b); pool.remove(b); cnt[b["coarse"]]=cnt.get(b["coarse"],0)+1
    return out
order=cred+greedy(core_rest,cred); order=order+greedy(padd,order)
# --- emit reordered submission CSV (CRLF, sequences byte-identical to source) ---
with open(f"{CAMP}/final20_diversity_recommended.csv","w",newline="") as o:
    w=csv.writer(o,lineterminator="\r\n"); w.writerow(["name","sequence","molecule_class"])
    for r in order: w.writerow([r["name"],seq[r["name"]],r["cls"]])
# --- rationale ---
with open(f"{CAMP}/final20_diversity_rationale.tsv","w") as o:
    o.write("new_rank\told_rank\tname\tcls\tlineage\ttier\trealism\tddG\tCI\tweakest\tlimiting\n")
    for i,r in enumerate(order,1):
        o.write(f'{i}\t{r["oldrank"]}\t{r["name"]}\t{r["cls"]}\t{r["coarse"]}\t{r["tier"]}\t{r["realism"]}\t{r["ddg"]:+.2f}\t{r["ci"]}\t{r["wk"]:+.3f}\t{r["lim"]}\n')
# --- markdown table for METHODS.md ---
print("MARKDOWN TABLE (METHODS.md):")
print("| # | design | class | lineage | tier | gate ΔΔG [95% CI] | weakest | was # |")
print("|--:|--------|-------|---------|------|------------------:|--------:|------:|")
tn={"1-CREDIBLE-SEL(preserved pose)":"credible G12D-selective","2-selective(OVER-DOCKED;suspect)":"ruler; gate over-docked (no credit)","3-lean(CI-incl-0;ranks-null)":"ruler (gate lean, CI incl 0)","4-clean-null":"ruler (gate null)","4-null-on-realistic-pose(rescue->artifact)":"ruler (rescue→null; was over-dock)","5-WT-favored(anti-sel)":"padding (anti-selective)"}
for i,r in enumerate(order,1):
    print(f'| {i} | {r["name"]} | {r["cls"]} | {r["coarse"]} | {tn.get(r["tier"],r["tier"])} | {r["ddg"]:+.2f} {r["ci"]} | {r["wk"]:+.3f} | {r["oldrank"]} |')
print(f"\ncoarse-lineage distinct in top-5 = {len({r['coarse'] for r in order[:5]})}, top-8 = {len({r['coarse'] for r in order[:8]})}")
print("order:", " ".join(r["name"] for r in order))
