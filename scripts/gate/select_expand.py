#!/usr/bin/env python
"""Select the expansion-gate screen set from the realistic-pose un-gated pool.

Realistic pose = native Asp6-Arg114 bridge intact (<=4.5A; validated: both known credibles
intact at 2.6-3.0A, the over-dock artifact broken at 7.5A) AND non-promiscuous (weakest>=0)
AND un-gated. The geometric charge-sensor score is NOT used to rank (control check showed it
anti-correlates with true credibility); we only use the pose-realism filter, then diversify.

Diversity weighting: take ALL realistic genie3 designs (orthogonal generator = maximal
decorrelation from our two BoltzGen credibles), plus a BoltzGen spread (vhh + protein) chosen
by weakest-margin as a mild cleanliness tiebreak. Output a screen list for cheap MD triage.

Usage: <pepglad-python> select_expand.py [N_boltzgen=42]
Writes: runs/gate_expand/screen_cands.tsv (name, lineage, class, weakest, native_bridge, pose)
        runs/gate_expand/screen_list.txt (design names, one per line)
"""
import csv, sys, os
P = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
PRIOR = f"{P}/runs/gate_prior/charge_sensor_prior.tsv"
OUT = f"{P}/runs/gate_expand"; os.makedirs(OUT, exist_ok=True)
N_BG = int(sys.argv[1]) if len(sys.argv) > 1 else 42


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def cls(r):
    if r["name"].startswith("rfd_des"):
        return "genie3"
    if r["name"].startswith("nb") or "vhh" in r["lineage"]:
        return "vhh"
    return "protein"


rows = list(csv.DictReader(open(PRIOR), delimiter="\t"))
real = [r for r in rows if r["gated"] == "0" and f(r["native_bridge"]) is not None
        and f(r["native_bridge"]) <= 4.5 and (r["weakest"] == "" or f(r["weakest"]) >= 0.0)]
for r in real:
    r["_cls"] = cls(r)
    r["_wk"] = f(r["weakest"]) or 0.0

genie3 = [r for r in real if r["_cls"] == "genie3"]
vhh = sorted([r for r in real if r["_cls"] == "vhh"], key=lambda r: -r["_wk"])
prot = sorted([r for r in real if r["_cls"] == "protein"], key=lambda r: -r["_wk"])

n_vhh = (N_BG + 1) // 2
n_prot = N_BG - n_vhh
sel = genie3 + vhh[:n_vhh] + prot[:n_prot]

with open(f"{OUT}/screen_cands.tsv", "w") as fh:
    fh.write("name\tlineage\tclass\tweakest\tnative_bridge\tpose\n")
    for r in sel:
        fh.write(f"{r['name']}\t{r['lineage']}\t{r['_cls']}\t{r['weakest']}\t{r['native_bridge']}\t{r['pose']}\n")
with open(f"{OUT}/screen_list.txt", "w") as fh:
    for r in sel:
        fh.write(r["name"] + "\n")

from collections import Counter
print(f"selected {len(sel)} for screen: {dict(Counter(r['_cls'] for r in sel))}")
print(f"  genie3={len(genie3)} (all realistic) vhh={n_vhh} protein={n_prot}")
print(f"wrote {OUT}/screen_cands.tsv and screen_list.txt")
