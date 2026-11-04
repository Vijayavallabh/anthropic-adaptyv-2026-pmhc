#!/usr/bin/env python3
"""Clean BOUND pMHC-TCR complexes for the selectivity-RANKER CALIBRATION (does physics recover the
TCRs' known G12D>WT?). Keep chains A,B,C,D,E = HLA, b2m, peptide, TCRalpha, TCRbeta (copy 1 only).

  parental_g12d  = 7OW6  (parental TCR + G12D, real crystal)
  parental_wt    = 7OW5  (parental TCR + WT, real crystal)
  parental_wtins = 7OW6 with peptide C6 ASP->GLY (CONTROLLED single-residue swap, identical pose)
  jdi_g12d       = 7PB2  copy 1 (JDI high-affinity *selective* TCR + G12D)
  jdi_wtins      = 7PB2 with peptide C6 ASP->GLY (no JDI-WT crystal exists -> controlled model)

TCR kept (this is the calibration, not a design). waters/ions/altloc-B+ dropped. Run with ambertools py -I.
"""
import os
from Bio.PDB import PDBParser, PDBIO, Select
STD = {"ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS",
       "MET","PHE","PRO","SER","THR","TRP","TYR","VAL"}
BB = {"N", "CA", "C", "O"}
KEEP = {"A", "B", "C", "D", "E"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDB = os.path.join(ROOT, "data/pdb")
OUT = os.path.join(ROOT, "data/targets/bound"); os.makedirs(OUT, exist_ok=True)

class K(Select):
    def accept_chain(self, c): return 1 if c.id in KEEP else 0
    def accept_residue(self, r): return 1 if (r.id[0] == " " and r.resname in STD) else 0
    def accept_atom(self, a): return 1 if a.get_altloc() in (" ", "A") else 0

def load(p): return PDBParser(QUIET=True).get_structure("s", p)[0]
def write_clean(src, out):
    io = PDBIO(); io.set_structure(load(f"{PDB}/{src}")); io.save(out, K())
def mutate_d6g(clean_in, out):
    m = load(clean_in)  # already A-E, altlocs resolved
    r6 = m["C"][(" ", 6, " ")]; assert r6.resname == "ASP", r6.resname
    for an in [a.name for a in list(r6)]:
        if an not in BB: r6.detach_child(an)
    r6.resname = "GLY"
    io = PDBIO(); io.set_structure(m); io.save(out)

write_clean("7OW6.pdb", f"{OUT}/parental_g12d.pdb")
write_clean("7OW5.pdb", f"{OUT}/parental_wt.pdb")
mutate_d6g(f"{OUT}/parental_g12d.pdb", f"{OUT}/parental_wtins.pdb")
write_clean("7PB2.pdb", f"{OUT}/jdi_g12d.pdb")
mutate_d6g(f"{OUT}/jdi_g12d.pdb", f"{OUT}/jdi_wtins.pdb")

_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H",
      "ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
for f in sorted(os.listdir(OUT)):
    m = load(f"{OUT}/{f}")
    chains = {c.id: sum(1 for r in c if r.id[0] == " ") for c in m}
    pep = "".join(_3.get(r.resname, "X") for r in m["C"] if r.id[0] == " ")
    print(f"{f:22s} chains={chains}  pep(C)={pep}")
