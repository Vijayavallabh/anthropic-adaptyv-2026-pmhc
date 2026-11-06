#!/usr/bin/env python
"""Atom-level P6 contact: is the binder touching the Asp6 SIDECHAIN carboxylate (OD1/OD2/CG/CB
= direct readout of the mutated residue) or only the BACKBONE (N/CA/C/O, same in G12D & WT ->
discrimination would be through-space field)? Pure stdlib. python -I analyze_p6.py <name=path> ..."""
import sys, math
def parse(path):
    ch={}
    with open(path) as f:
        for ln in f:
            if not ln.startswith(("ATOM","HETATM")): continue
            an=ln[12:16].strip(); cid=ln[21]
            try: resi=int(ln[22:26])
            except: continue
            el=(ln[76:78].strip() if len(ln)>=78 else "") or an[0]
            if el=="H": continue
            x=float(ln[30:38]); y=float(ln[38:46]); z=float(ln[46:54])
            ch.setdefault(cid,{}).setdefault(resi,[]).append((an,x,y,z))
    return ch
def mind(A,B):
    m=1e9; best=None
    for an,ax,ay,az in A:
        for bn,bx,by,bz in B:
            d=(ax-bx)**2+(ay-by)**2+(az-bz)**2
            if d<m: m=d; best=(an,bn)
    return math.sqrt(m),best
BB={"N","CA","C","O","OXT"}
for arg in sys.argv[1:]:
    name,path=arg.split("=",1); ch=parse(path)
    # peptide = chain with 8-12 residues; binder = chain 'P' else largest non-A/B/C
    pep=[c for c in ch if 8<=len(ch[c])<=12][0]
    binder="P" if "P" in ch else max([c for c in ch if c not in ("A","B",pep)],key=lambda c:len(ch[c]))
    p6=ch[pep][sorted(ch[pep])[5]]  # 6th residue
    bat=[a for r in ch[binder] for a in ch[binder][r]]
    bb=[a for a in p6 if a[0] in BB]; sc=[a for a in p6 if a[0] not in BB]
    dall,pair=mind(p6,bat); dbb,_=mind(bb,bat) if bb else (float('nan'),None); dsc,scp=mind(sc,bat) if sc else (float('nan'),None)
    print(f"\n{name}:  binder={binder}  P6 atoms={[a[0] for a in p6]}")
    print(f"  P6 overall closest : {dall:5.2f} A   (peptide {pair[0]} <-> binder {pair[1]})")
    print(f"  P6 BACKBONE closest: {dbb:5.2f} A")
    print(f"  P6 SIDECHAIN close : {dsc:5.2f} A" + (f"   (Asp {scp[0]} <-> binder {scp[1]})" if scp else "  (no sidechain = GLY)"))
    tag = "SIDECHAIN carboxylate (DIRECT mutation readout)" if (sc and dsc<3.6 and scp[0] in {"OD1","OD2","CG"}) else \
          ("sidechain-ish" if sc and dsc<4 else "BACKBONE-only (field/through-space compatible)")
    print(f"  -> dominant contact: {tag}")
