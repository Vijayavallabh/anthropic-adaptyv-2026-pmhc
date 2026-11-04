#!/usr/bin/env python
"""Print FASTA for given <pdb>:<chain> args (resolved standard residues only).
Run:  /home/prachh/miniconda3/envs/ambertools/bin/python -I scripts/extract_seqs.py data/pdb/7PB2.pdb:D ...
"""
import sys
from Bio.PDB import PDBParser
_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H",
      "ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W",
      "TYR":"Y","VAL":"V"}

def seq(path, chain):
    m = PDBParser(QUIET=True).get_structure("s", path)[0]
    return "".join(_3.get(r.resname, "X") for r in m[chain] if r.id[0] == " " and r.resname in _3)

for arg in sys.argv[1:]:
    path, chain = arg.rsplit(":", 1)
    s = seq(path, chain)
    tag = path.split("/")[-1].split(".")[0]
    print(f">{tag}_{chain} len={len(s)}")
    print(s)
