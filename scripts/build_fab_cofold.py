#!/usr/bin/env python3
"""Fab 2-chain co-fold YAMLs: VH(H)+VL(L) + HLA(A)+b2m(B)+peptide(C), states {g12d,empty}.
Pocket restraint on VH (carries HCDR3, the main paratope) -> peptide bulge [C4,C6,C7,C8]; empty -> groove floor.
msa:empty. Reads name,sequence csv where sequence is "VH:VL". Emits <out>/<name>__<state>.yaml.
Then: run_boltz.sh <out> <foldout> "<gpus>"; score_pmhc.py <foldout> --binder-chains H,L.
Usage: build_fab_cofold.py --csv runs/fab_candidates.csv --out DIR [--states g12d,empty] [--sample N]
"""
import argparse, csv, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(os.path.join(ROOT, "configs/target.yaml")).read(), re.M)
HLA = next(s for s in _v if s.startswith("GSHSMRY"))
B2M = next(s for s in _v if s.startswith("IQRTP"))
STATES = {"g12d": "VVVGADGVGK", "empty": None, "wt": "VVVGAGGVGK", "scram": "VVGAVGDGVK",
          "ebna4": "AVFDRKSDAK", "atic": "ASFKHWPFLK"}  # ebna4/atic = unrelated A*11:01 peptides (promiscuity)

def prot(cid, seq): return f"  - protein:\n      id: {cid}\n      sequence: {seq}\n      msa: empty\n"
def yaml_for(vh, vl, pepseq):
    s = "version: 1\nsequences:\n" + prot("A", HLA) + prot("B", B2M)
    if pepseq: s += prot("C", pepseq)
    s += prot("H", vh) + prot("L", vl)
    contacts = "[[C, 4], [C, 6], [C, 7], [C, 8]]" if pepseq else "[[A, 66], [A, 69], [A, 146], [A, 150], [A, 155]]"
    s += f"constraints:\n  - pocket:\n      binder: H\n      contacts: {contacts}\n      max_distance: 8.0\n"
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--states", default="g12d,empty"); ap.add_argument("--sample", type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows = [r for r in csv.DictReader(open(a.csv)) if ":" in (r.get("sequence") or "")]
    if a.sample and a.sample < len(rows):
        stride = len(rows) / a.sample
        rows = [rows[int(i * stride)] for i in range(a.sample)]
    n = 0
    for r in rows:
        nm = r["name"]; vh, vl = r["sequence"].split(":")
        vh, vl = vh.strip().upper(), vl.strip().upper()
        if not (80 <= len(vh) <= 140 and 80 <= len(vl) <= 140): continue
        if any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in vh + vl): continue
        for st in a.states.split(","):
            open(f"{a.out}/{nm}__{st}.yaml", "w").write(yaml_for(vh, vl, STATES[st]))
            n += 1
    print(f"wrote {n} yamls to {a.out} ({a.states}) from {len(rows)} fabs")

if __name__ == "__main__":
    main()
