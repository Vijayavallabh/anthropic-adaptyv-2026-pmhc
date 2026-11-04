#!/usr/bin/env python3
"""Peptide-SWAP co-fold panel: test binder PEPTIDE-SEQUENCE specificity (the neoantigen crux).
For each design, co-fold binder(P)+HLA(A)+b2m(B)+peptide(C) with the SAME pocket restraint, swapping only
the peptide across a panel: the G12D target, WT (1-residue, co-fold tier-1 blind by prior finding), a
SCRAMBLE (same composition + A*11:01 anchors P2=V/PΩ=K, interior shuffled -> tests sequence-reading vs
anchor/platform-reading), and dissimilar REAL A*11:01 epitopes. A sequence-specific binder: bp_ipsae(G12D)
>> bp_ipsae(scramble/dissimilar). If equal, it reads the platform (pan-peptide risk) or co-fold is
sequence-blind. Run: build -> run_boltz.sh (NOMSA=1 DIFF_SAMPLES=5) -> score_designs.py / robust per peptide.
Usage: build_pepswap_cofold.py --csv <name,sequence> --out <dir> [--peptides name=SEQ,...]
"""
import argparse, csv, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(os.path.join(ROOT, "configs/target.yaml")).read(), re.M)
HLA = next(s for s in _v if s.startswith("GSHSMRY"))
B2M = next(s for s in _v if s.startswith("IQRTP"))
# panel: target, 1-res WT, composition+anchor-matched scramble, two dissimilar real A*11:01 10mer epitopes
PANEL = {
    "g12d":   "VVVGADGVGK",   # target neoantigen (KRAS 7-16, P6=D)
    "wt":     "VVVGAGGVGK",   # 1-residue WT (co-fold blind -> prior finding)
    "scram":  "VVGAVGDGVK",   # same composition, anchors P2=V/PΩ=K kept, interior shuffled
    "ebna4":  "AVFDRKSDAK",   # EBV EBNA3B/EBNA4 -- canonical dissimilar A*11:01 10mer (A2=V, PΩ=K)
    "atic":   "ASFKHWPFLK",   # dissimilar A*11:01-anchored 10mer control (A2=S, PΩ=K)
}

def prot(cid, seq): return f"  - protein:\n      id: {cid}\n      sequence: {seq}\n      msa: empty\n"
def yaml_for(binder, pep):
    s = "version: 1\nsequences:\n" + prot("A", HLA) + prot("B", B2M) + prot("C", pep) + prot("P", binder)
    s += "constraints:\n  - pocket:\n      binder: P\n      contacts: [[C, 4], [C, 6], [C, 7], [C, 8]]\n      max_distance: 8.0\n"
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--peptides", default=None, help="override panel: name=SEQ,name=SEQ")
    a = ap.parse_args()
    panel = PANEL if not a.peptides else {kv.split("=")[0]: kv.split("=")[1] for kv in a.peptides.split(",")}
    os.makedirs(a.out, exist_ok=True)
    n = 0
    for row in csv.DictReader(open(a.csv)):
        nm = row["name"]; seq = row["sequence"].strip().upper()
        if not (10 <= len(seq) <= 250): continue
        for pn, ps in panel.items():
            open(f"{a.out}/{nm}__{pn}.yaml", "w").write(yaml_for(seq, ps))
            n += 1
    print(f"wrote {n} yamls to {a.out}; panel={list(panel)}")

if __name__ == "__main__":
    main()
