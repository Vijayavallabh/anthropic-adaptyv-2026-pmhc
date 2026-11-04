#!/usr/bin/env python3
"""Convert design BoltzGen cifs -> af2ig input PDBs. af2ig (predict_pdb.py) convention: FILE chain order
= chain 1 binder, all following chains target; input coords ARE the initial guess. pae_interaction is
mean PAE over ALL binder x target pairs, so a big target (full 385-res pMHC) dilutes it -> we CROP the
target (HLA/b2m) to residues within RADIUS of the binder, ALWAYS keeping the full peptide, so the honest
gate (pae_interaction<10, plddt_binder>80, binder_aligned_rmsd<2) reflects the real interface.
Output chains: A=binder (full), B=HLA(cropped), C=b2m(cropped, usually empty), D=peptide(full).
Usage: prep_af2ig_pmhc.py --names <csv name col> --triage <triage.tsv> --out <dir> [--radius 10]
Run with gemmi+numpy python (ambertools).
"""
import argparse, csv, os, gemmi
import numpy as np
_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I",
      "LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}

def seqof(chain): return "".join(_3.get(r.name, "X") for r in chain)
def heavy(res): return [[a.pos.x, a.pos.y, a.pos.z] for a in res if a.element.name != "H"]

def convert(cif, out, radius):
    m = gemmi.read_structure(cif)[0]
    chains = {c.name: c for c in m}
    seqs = {cid: seqof(c) for cid, c in chains.items()}
    hla = b2m = pep = binder = None
    for cid, s in seqs.items():
        if s.startswith("GSHSMRY"): hla = cid
        elif s.startswith("IQRTP"): b2m = cid
        elif s.startswith("VVVGA") and len(s) <= 12: pep = cid
    for cid in chains:
        if cid not in (hla, b2m, pep): binder = cid
    if not (binder and hla and pep): return False
    bxyz = np.array([p for r in chains[binder] for p in heavy(r)])
    def near(res):
        pts = heavy(res)
        if not pts: return False
        return float(np.sqrt(((np.array(pts)[:, None, :] - bxyz[None, :, :]) ** 2).sum(-1)).min()) <= radius
    ns = gemmi.Structure(); mo = gemmi.Model("1")
    cb = gemmi.Chain("A")
    for r in chains[binder]: cb.add_residue(r)
    mo.add_chain(cb)
    for cid, lab, crop in [(hla, "B", True), (b2m, "C", True), (pep, "D", False)]:
        if cid is None: continue
        nc = gemmi.Chain(lab)
        for r in chains[cid]:
            if (not crop) or near(r): nc.add_residue(r)
        if len(nc) > 0: mo.add_chain(nc)
    ns.add_model(mo); ns.setup_entities(); ns.write_pdb(out)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", required=True)
    ap.add_argument("--triage", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--radius", type=float, default=10.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cif_of = {r["name"]: r["cif"] for r in csv.DictReader(open(a.triage), delimiter="\t")}
    names = [l.strip() for l in open(a.names).read().splitlines()[1:] if l.strip()]
    ok = miss = 0
    for n in names:
        c = cif_of.get(n)
        if not c or not os.path.exists(c): miss += 1; continue
        try:
            if convert(c, f"{a.out}/{n}.pdb", a.radius): ok += 1
            else: miss += 1
        except Exception as e:
            print("fail", n, e); miss += 1
    print(f"[prep_af2ig] wrote {ok} cropped PDBs (radius {a.radius}) to {a.out} (missing/failed {miss})")

if __name__ == "__main__":
    main()
