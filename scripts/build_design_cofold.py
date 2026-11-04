#!/usr/bin/env python3
"""From passing.csv (name,sequence) of de-novo binders, write 3-state Boltz-2 co-fold YAMLs per design:
binder(P) + HLA(A) + b2m(B) + peptide(C) in states {g12d, wt, empty}. Pocket restraint binder->peptide
bulge [C4,C6,C7,C8] identical across g12d/wt (clean mutation differential); empty restrains binder to the
HLA groove floor. msa:empty (symmetric, no network). Emits <out>/<name>__<state>.yaml.
Then: run_boltz.sh <out> <foldout> "<gpus>" (NOMSA=1 DIFF_SAMPLES=5); score_pmhc.py <foldout> --binder-chains P.
"""
import argparse, csv, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(os.path.join(ROOT, "configs/target.yaml")).read(), re.M)
HLA = next(s for s in _v if s.startswith("GSHSMRY"))
B2M = next(s for s in _v if s.startswith("IQRTP"))
STATES = {"g12d": "VVVGADGVGK", "wt": "VVVGAGGVGK", "empty": None}

def prot(cid, seq): return f"  - protein:\n      id: {cid}\n      sequence: {seq}\n      msa: empty\n"
def yaml_for(binder_seq, pepseq):
    s = "version: 1\nsequences:\n" + prot("A", HLA) + prot("B", B2M)
    if pepseq:
        s += prot("C", pepseq)
    s += prot("P", binder_seq)
    contacts = "[[C, 4], [C, 6], [C, 7], [C, 8]]" if pepseq else "[[A, 66], [A, 69], [A, 146], [A, 150], [A, 155]]"
    s += f"constraints:\n  - pocket:\n      binder: P\n      contacts: {contacts}\n      max_distance: 8.0\n"
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--states", default="g12d,wt,empty")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    n = 0
    for row in csv.DictReader(open(a.csv)):
        nm = row["name"]; seq = row["sequence"].strip().upper()
        if not (10 <= len(seq) <= 250) or any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in seq):
            continue
        for st in a.states.split(","):
            open(f"{a.out}/{nm}__{st}.yaml", "w").write(yaml_for(seq, STATES[st]))
            n += 1
    print(f"wrote {n} yamls to {a.out} ({a.states})")

if __name__ == "__main__":
    main()
