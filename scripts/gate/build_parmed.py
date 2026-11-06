#!/usr/bin/env python
"""Build order-preserving dry com/rec/lig prmtops from a solvated prmtop via ParmEd.
mbondi3 radii for GBn2. Usage: python -I build_parmed.py <solv_prmtop> <ligmask> <recmask> <outdir> <tag>
ligmask = pMHC residues, recmask = TCR residues."""
import sys, os
import parmed as pmd
from parmed.tools import changeRadii
solv_prmtop, ligmask, recmask, outdir, tag = sys.argv[1:6]
os.makedirs(outdir, exist_ok=True)
solv = pmd.load_file(solv_prmtop)
com = solv['!(:WAT,Na+,Cl-)']
lig = com[ligmask]   # pMHC
rec = com[recmask]   # TCR
for name,st in [("com",com),("rec",rec),("lig",lig)]:
    changeRadii(st,'mbondi3').execute()
    st.box = None   # non-periodic for implicit-solvent GBSA
    p=os.path.join(outdir,f"{tag}_{name}.parm7")
    st.save(p, overwrite=True)
    print(f"{tag}_{name}: {len(st.atoms)} atoms, {len(st.residues)} res -> {p}")
# report the lig/rec atom split (lig first since res 1..N)
print(f"SPLIT {tag}: lig_atoms={len(lig.atoms)} rec_atoms={len(rec.atoms)} com_atoms={len(com.atoms)}")
