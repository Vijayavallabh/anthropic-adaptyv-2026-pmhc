#!/usr/bin/env python
"""Build a Genie3 binder_design dataset for the G12D pMHC (orthogonal-generator run).
Mirrors the binderbench problem schema. Target = ordered G12D pMHC (A=HLA-A*11:01, B=b2m,
C=peptide VVVGADGVGK) from data/targets/g12d.pdb. Peptide-centric: hotspot = exposed bulge
C4,C5,C7,C8; extended INCLUDES the buried Asp6 (C6) to bias binders toward the discriminating
residue. Generation needs no MSA (single-seq a3m provided only to satisfy the schema). stdlib only."""
import os, json, shutil

ROOT="/home/prachh/v/anthropic-adaptyv-2026-pmhc"
SRC_PDB=f"{ROOT}/data/targets/g12d.pdb"
DS=f"{ROOT}/runs/genie3/pmhc_g12d_bench"
KEY="pmhc_g12d"
for sub in ["problems","targets/pdb","targets/fasta","targets/msa"]:
    os.makedirs(f"{DS}/{sub}", exist_ok=True)

AA3TO1={'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
 'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T',
 'TRP':'W','TYR':'Y','VAL':'V'}

# parse ATOM records -> per-chain ordered (resnum, resname)
chains={}
lines_by_chain={}
for ln in open(SRC_PDB):
    if not ln.startswith("ATOM"): continue
    ch=ln[21]; resn=ln[17:20].strip(); resi=int(ln[22:26])
    lines_by_chain.setdefault(ch,[]).append(ln)
    d=chains.setdefault(ch,{})
    if resi not in d: d[resi]=resn

def seq_of(ch):
    d=chains[ch]
    return "".join(AA3TO1.get(d[r],"X") for r in sorted(d))
def rng_of(ch):
    rs=sorted(chains[ch]); return f"{ch}{rs[0]}-{rs[-1]}"

order=[c for c in ("A","B","C") if c in chains]
print("chains:", {c:(len(chains[c]), rng_of(c)) for c in order})

# full complex pdb
shutil.copy(SRC_PDB, f"{DS}/targets/pdb/{KEY}.pdb")
# per-chain pdbs + fastas + single-seq a3m
by_chain_pdb=[]; by_chain_fa=[]; by_chain_msa=[]
for c in order:
    p=f"targets/pdb/{KEY}-chain_{c}.pdb"; fa=f"targets/fasta/{KEY}-chain_{c}.fasta"; a3=f"targets/msa/{KEY}-chain_{c}.a3m"
    with open(f"{DS}/{p}","w") as f: f.writelines(lines_by_chain[c]); f.write("TER\nEND\n")
    s=seq_of(c)
    open(f"{DS}/{fa}","w").write(f">{KEY}-chain_{c}\n{s}\n")
    open(f"{DS}/{a3}","w").write(f">{KEY}-chain_{c}\n{s}\n")   # single-seq a3m (generation ignores it)
    by_chain_pdb.append(p); by_chain_fa.append(fa); by_chain_msa.append(a3)
# full fasta + a3m (concatenated chains)
fullseq="".join(seq_of(c) for c in order)
open(f"{DS}/targets/fasta/{KEY}.fasta","w").write(f">{KEY}\n{fullseq}\n")
open(f"{DS}/targets/msa/{KEY}.a3m","w").write(f">{KEY}\n{fullseq}\n")

problem={
 "key":KEY,"name":"KRAS-G12D pMHC (HLA-A*11:01)",
 "target_pdb_filepath":f"{DS}/targets/pdb/{KEY}.pdb",
 "target_fasta_filepath":f"{DS}/targets/fasta/{KEY}.fasta",
 "target_msa_filepath":f"{DS}/targets/msa/{KEY}.a3m",
 "target_pdb_filepath_by_chain":[f"{DS}/{p}" for p in by_chain_pdb],
 "target_fasta_filepath_by_chain":[f"{DS}/{p}" for p in by_chain_fa],
 "target_msa_filepath_by_chain":[f"{DS}/{p}" for p in by_chain_msa],
 "target_chain_and_residues":[rng_of(c) for c in order],
 "target_interface_residues":{
   "hotspot":["C4","C5","C7","C8"],                       # exposed G12D bulge
   "extended":["C3","C4","C5","C6","C7","C8","C9"],        # incl buried Asp6 (C6) -> bias to discriminating residue
   "common":["C4","C5","C6","C7","C8"],
 },
 "binder_min_length":55,"binder_max_length":110,
 "tag":["orthogonal","genie3"],"pdb_id":"7OW6",
}
open(f"{DS}/problems/{KEY}.json","w").write(json.dumps(problem,indent=2))
print("wrote dataset at", DS)
print("problem:", json.dumps(problem["target_interface_residues"]), "chains_resid:", problem["target_chain_and_residues"])
print("peptide seq C:", seq_of("C"), "(Asp6 =", seq_of("C")[5], ")")
