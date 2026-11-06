#!/usr/bin/env python3
"""Genie3 CA-trace -> full-backbone complex for the pMHC funnel.
Each Genie3 output: binder = chain A (CA-only, UNK); target = chains B(HLA 276)+C(b2m 99)+D(pep 10), CA-only.
  1. binder CA -> UNK->ALA -> PULCHRA -> N/CA/C/O
  2. Kabsch-superpose the REAL full-atom target (data/targets/g12d.pdb, chains A/B/C) onto Genie3's B/C/D CA frame
  3. write full complex: binder as chain D + real target as A(HLA)/B(b2m)/C(peptide)
Output feeds STANDARD SolubleMPNN (scripts/mpnn_binder.py --design-chain D) then the co-fold panel.
Usage: build_genie3_fullbb_pmhc.py <pulchra_bin> <backbone_glob> <out_dir> [target_pdb]
"""
import sys, os, glob, subprocess, tempfile, re
import numpy as np

PULCHRA=sys.argv[1]
GLOB=sys.argv[2]
OUT=sys.argv[3]
TARGET=sys.argv[4] if len(sys.argv)>4 else "/home/prachh/v/anthropic-adaptyv-2026-pmhc/data/targets/g12d.pdb"
os.makedirs(OUT, exist_ok=True)

def atom_lines(path, chains=None):
    out=[]
    for ln in open(path):
        if ln.startswith(("ATOM","HETATM")) and (chains is None or ln[21] in chains):
            out.append(ln)
    return out
def ca_xyz(lines):
    return np.array([[float(l[30:38]),float(l[38:46]),float(l[46:54])]
                     for l in lines if l[12:16].strip()=="CA"])
def set_xyz(ln, xyz):
    return f"{ln[:30]}{xyz[0]:8.3f}{xyz[1]:8.3f}{xyz[2]:8.3f}{ln[54:]}"
def kabsch(P, Q):
    Pc=P.mean(0); Qc=Q.mean(0)
    H=(P-Pc).T@(Q-Qc); U,S,Vt=np.linalg.svd(H)
    d=np.sign(np.linalg.det(Vt.T@U.T)); D=np.diag([1.0,1.0,d])
    return Vt.T@D@U.T, Pc, Qc

# real full-atom target, ordered chains A(HLA)/B(b2m)/C(peptide)
TGT_LINES=[]
for c in ("A","B","C"): TGT_LINES += atom_lines(TARGET, c)
TGT_CA=ca_xyz(TGT_LINES)
TGT_ALL=np.array([[float(l[30:38]),float(l[38:46]),float(l[46:54])] for l in TGT_LINES])

files=[]
for pat in GLOB.split(): files+=glob.glob(pat)
n_ok=n_fail=0
for p in sorted(files):
    m=re.search(r'shard_(g\d+)', p); shard=m.group(1) if m else "gX"
    name=f"{shard}_"+os.path.basename(p).replace(".pdb","")   # shard-unique (basenames repeat across shards)
    binderA=atom_lines(p,"A")                       # generated binder = chain A
    gen_tgt=[]
    for c in ("B","C","D"): gen_tgt += atom_lines(p, c)   # genie3 target copy = B/C/D
    b_ca=ca_xyz(binderA); t_ca=ca_xyz(gen_tgt)
    if len(b_ca)==0 or len(t_ca)!=len(TGT_CA):
        n_fail+=1; continue
    with tempfile.TemporaryDirectory() as td:
        bca=os.path.join(td,"b.pdb")
        with open(bca,"w") as fh:
            for l in binderA:
                if l[12:16].strip()=="CA": fh.write(f"{l[:17]}ALA{l[20:]}")
            fh.write("END\n")
        subprocess.run([PULCHRA,bca],capture_output=True,text=True,cwd=td)
        reb=os.path.join(td,"b.rebuilt.pdb")
        if not os.path.exists(reb): n_fail+=1; continue
        binder_bb=[l for l in atom_lines(reb) if l[12:16].strip() in ("N","CA","C","O")]
    # superpose real target (P) onto genie3 target CA frame (Q)
    R,Pc,Qc=kabsch(TGT_CA, t_ca)
    moved=(TGT_ALL-Pc)@R.T+Qc
    tgt_moved=[set_xyz(TGT_LINES[i], moved[i]) for i in range(len(TGT_LINES))]
    with open(os.path.join(OUT,f"des_{name}.pdb"),"w") as fh:
        for l in binder_bb: fh.write(f"{l[:21]}D{l[22:]}")   # binder -> chain D
        fh.write("TER\n")
        prev=None
        for l in tgt_moved:
            if prev and l[21]!=prev: fh.write("TER\n")
            fh.write(l); prev=l[21]
        fh.write("TER\nEND\n")
    n_ok+=1
print(f"built {n_ok} full-backbone complexes -> {OUT}  (failed {n_fail})")
