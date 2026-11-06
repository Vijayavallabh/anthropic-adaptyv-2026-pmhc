#!/usr/bin/env python
"""Devil's-advocate pose geometry: does the binder DIRECTLY contact the buried peptide
P6 (Asp6 in G12D) -- the known co-fold-reaches-a-buried-residue artifact -- or does it
discriminate THROUGH-SPACE (no P6 contact; the validated non-mimetic mechanism)?
Pure-stdlib PDB parse. Run with: python -I analyze_pose.py <name=path> [<name=path> ...]"""
import sys, math
AA3={'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H',
     'ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W',
     'TYR':'Y','VAL':'V','HIE':'H','HID':'H','HIP':'H'}
B2M_PREFIX="IQRTPKIQVY"
def parse(path):
    ch={}
    with open(path) as f:
        for ln in f:
            if not ln.startswith(("ATOM","HETATM")): continue
            atom=ln[12:16].strip(); resn=ln[17:20].strip(); cid=ln[21]
            try: resi=int(ln[22:26])
            except: continue
            el=(ln[76:78].strip() if len(ln)>=78 else "") or atom[0]
            if el=="H": continue
            x=float(ln[30:38]); y=float(ln[38:46]); z=float(ln[46:54])
            ch.setdefault(cid,{}).setdefault(resi,[resn,[]])
            ch[cid][resi][1].append((x,y,z))
    return ch
def seqof(cd): return "".join(AA3.get(cd[r][0],"X") for r in sorted(cd))
def atoms(cd):
    out=[]
    for r in cd: out+= [(r,)+t for t in cd[r][1]]
    return out
def mind(A,B):
    m=1e9
    for _,ax,ay,az in A:
        for _,bx,by,bz in B:
            d=(ax-bx)**2+(ay-by)**2+(az-bz)**2
            if d<m: m=d
    return math.sqrt(m)
def roles(ch):
    sizes={c:len(ch[c]) for c in ch}
    pep=[c for c in ch if 8<=sizes[c]<=12]
    pep=pep[0] if pep else min(ch,key=lambda c:sizes[c])
    b2m=[c for c in ch if c!=pep and seqof(ch[c]).startswith(B2M_PREFIX[:6])]
    b2m=b2m[0] if b2m else None
    if b2m is None:
        b2m=sorted([c for c in ch if c!=pep],key=lambda c:abs(sizes[c]-99))[0]
    hla=max([c for c in ch if c not in (pep,b2m)],key=lambda c:sizes[c])
    binder=[c for c in ch if c not in (pep,b2m,hla)]
    binder=binder[0] if binder else None
    return pep,b2m,hla,binder
for arg in sys.argv[1:]:
    name,path=arg.split("=",1)
    ch=parse(path)
    pep,b2m,hla,binder=roles(ch)
    print(f"\n===== {name} =====")
    print("chains (id:nres):", {c:len(ch[c]) for c in ch})
    print(f"roles -> peptide={pep} ({seqof(ch[pep])})  b2m={b2m}  HLA={hla}  binder={binder}({len(ch[binder]) if binder else '?'})")
    if binder is None: print("  !! could not isolate binder chain"); continue
    bat=atoms(ch[binder])
    pres=sorted(ch[pep]); first=pres[0]
    print(f"  binder->peptide per-residue min heavy-atom distance (A):")
    prof=[]
    for i,r in enumerate(pres,1):
        d=mind(atoms({0:ch[pep][r]} and [ (r,)+t for t in ch[pep][r][1] ]),bat) if False else mind([(r,)+t for t in ch[pep][r][1]],bat)
        prof.append((i,ch[pep][r][0],d));
    for i,rn,d in prof:
        star=" <== P6 (mutation site; BURIED in HLA)" if i==6 else (" (contact<4A)" if d<4 else "")
        print(f"    P{i:<2} {rn:<3} {d:6.2f}{star}")
    p6=[d for i,_,d in prof if i==6][0]
    nearest=min(prof,key=lambda t:t[2])
    contacts=[i for i,_,d in prof if d<4.0]
    print(f"  SUMMARY {name}: P6 min-dist={p6:.2f} A | nearest residue=P{nearest[0]}({nearest[1]}) {nearest[2]:.2f} A | <4A contacts at P{contacts}")
    verdict=("DIRECT-P6-CONTACT (suspect: buried-residue reach)" if p6<4.0 else
             "near-P6 (<6A, watch)" if p6<6.0 else "THROUGH-SPACE (no P6 contact; consistent with validated mechanism)")
    print(f"  MECHANISM VERDICT: P6={p6:.2f}A -> {verdict}")
