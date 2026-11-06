#!/usr/bin/env python
"""Is the native Asp6<->HLA-Arg114 salt bridge PRESERVED in the co-fold pose, or did the
co-folder BREAK it to swing Asp6 up to the binder (over-docking artifact)? Reports the HLA
basic residue closest to Asp6 carboxylate + the resi-114 distance specifically. python -I ..."""
import sys, math
def parse(path):
    ch={}
    with open(path) as f:
        for ln in f:
            if not ln.startswith(("ATOM","HETATM")): continue
            an=ln[12:16].strip(); rn=ln[17:20].strip(); cid=ln[21]
            try: resi=int(ln[22:26])
            except: continue
            el=(ln[76:78].strip() if len(ln)>=78 else "") or an[0]
            if el=="H": continue
            x=float(ln[30:38]); y=float(ln[38:46]); z=float(ln[46:54])
            ch.setdefault(cid,{}).setdefault(resi,[rn,[]]); ch[cid][resi][1].append((an,x,y,z))
    return ch
def dmin(A,B):
    m=1e9
    for _,ax,ay,az in A:
        for _,bx,by,bz in B:
            d=(ax-bx)**2+(ay-by)**2+(az-bz)**2
            if d<m:m=d
    return math.sqrt(m)
BN={"NE","NH1","NH2","NZ"}
for arg in sys.argv[1:]:
    name,path=arg.split("=",1); ch=parse(path)
    pep=[c for c in ch if 8<=len(ch[c])<=12][0]; A=ch["A"]
    asp=ch[pep][sorted(ch[pep])[5]]; carb=[a for a in asp[1] if a[0] in {"OD1","OD2"}]
    if not carb: print(f"\n{name}: P6 is {asp[0]} (no carboxylate)"); continue
    cand=[]
    for resi in A:
        rn=A[resi][0]
        if rn in ("ARG","LYS"):
            bn=[a for a in A[resi][1] if a[0] in BN]
            if bn: cand.append((dmin(bn,carb),resi,rn))
    cand.sort()
    print(f"\n{name}:")
    print(f"  closest HLA basic residue to Asp6 carboxylate: {cand[0][2]}{cand[0][1]} at {cand[0][0]:.2f} A")
    r114=A.get(114)
    if r114:
        bn=[a for a in r114[1] if a[0] in BN]
        d114=dmin(bn,carb) if bn else float('nan')
        print(f"  HLA chain-A resi 114 = {r114[0]}  (Asp6 carboxylate <-> its basic-N: {d114:.2f} A)")
    print(f"  top-3 basic neighbours: " + ", ".join(f"{rn}{ri}:{d:.1f}A" for d,ri,rn in cand[:3]))
    sb=cand[0][0]
    print(f"  -> native salt bridge {'INTACT (<4A; binder reads other face)' if sb<4 else 'BROKEN (>4A; co-fold swung Asp6 to binder = OVER-DOCK artifact)' }")
