#!/usr/bin/env python3
"""REAL tier-2 (red-team fix): instead of trusting loaded-vs-empty ipTM (confounded by groove
destabilization), measure how CONSISTENTLY and SUBSTANTIALLY the binder grips the PEPTIDE across all
co-fold diffusion samples. A genuine peptide-dependent binder makes many direct peptide contacts in
EVERY sample; a groove-destabilization / empty-HLA confound contacts mostly the a1/a2 helices and
contacts the peptide weakly/variably. Reports, over the g12d samples of each design:
  f_pep  = fraction of binder heavy-atom contacts (<4.5A) on the peptide (chain C), mean & MIN over samples
  npep   = raw peptide contacts, mean
  core   = fraction of samples that contact the G12D-adjacent core (peptide res 6,7,8) with >=3 binder atoms
Run with ambertools python (Bio). Usage: pep_contact_consistency.py <name1> <name2> ... [--root folds/cofold2]
"""
import sys, glob, os
from collections import defaultdict
from Bio.PDB import PDBParser, NeighborSearch
import numpy as np
_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I",
      "LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
HELIX = set(range(57, 86)) | set(range(138, 181))
CORE = {6, 7, 8}  # G12D (res6) + the exposed P7/P8 apex it perturbs

def sq(res): return "".join(_3.get(r.resname, "X") for r in res)

def classify(chains):
    hla = b2m = pep = binder = None
    for cid, res in chains.items():
        s = sq(res)
        if s.startswith("GSHSMRY"): hla = cid
        elif s.startswith("IQRTP"): b2m = cid
        elif s.startswith("VVVGA") and len(s) <= 12: pep = cid
    for cid in chains:
        if cid not in (hla, b2m, pep): binder = cid
    return hla, b2m, pep, binder

def one(path):
    m = PDBParser(QUIET=True).get_structure("s", path)[0]
    chains = {c.id: [r for r in c if r.id[0] == " "] for c in m}
    hla, b2m, pep, binder = classify(chains)
    if not (hla and pep and binder): return None
    tgt = [a for cid in (hla, b2m, pep) if cid for r in chains[cid] for a in r]
    ns = NeighborSearch(tgt)
    cc = defaultdict(int)
    for r in chains[binder]:
        for a in r:
            for nb in ns.search(a.coord, 4.5):
                pr = nb.get_parent(); cc[(pr.get_parent().id, pr.id[1])] += 1
    tot = sum(cc.values()) or 1
    pep_c = sum(v for (c, ri), v in cc.items() if c == pep)
    core_c = sum(v for (c, ri), v in cc.items() if c == pep and ri in CORE)
    return dict(tot=tot, f_pep=pep_c / tot, npep=pep_c, core=core_c)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = "folds/cofold2"
    if "--root" in sys.argv: root = sys.argv[sys.argv.index("--root") + 1]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    print(f"{'design':26s} {'ns':>2} {'fpep_mean':>9} {'fpep_min':>8} {'npep_mean':>9} {'core_frac':>9}  per_sample_fpep")
    recs = []
    for nm in args:
        pdbs = sorted(glob.glob(f"{root}/**/{nm}__g12d_model_*.pdb", recursive=True))
        rs = [one(p) for p in pdbs]; rs = [r for r in rs if r]
        if not rs: print(f"{nm:26s}  no g12d samples"); continue
        fp = [r["f_pep"] for r in rs]; cf = sum(1 for r in rs if r["core"] >= 3) / len(rs)
        recs.append((nm, len(rs), round(float(np.mean(fp)), 3), round(min(fp), 3),
                     round(float(np.mean([r['npep'] for r in rs]))), round(cf, 2)))
        print(f"{nm:26s} {len(rs):>2} {np.mean(fp):>9.2f} {min(fp):>8.2f} {np.mean([r['npep'] for r in rs]):>9.0f} {cf:>9.2f}  {[round(x,2) for x in fp]}")
    if out:
        with open(out, "w") as f:
            f.write("name\tns\tfpep_mean\tfpep_min\tnpep\tcore_frac\n")
            for r in recs: f.write("\t".join(str(x) for x in r) + "\n")
        print(f"\nwrote {len(recs)} -> {out}")

if __name__ == "__main__":
    main()
