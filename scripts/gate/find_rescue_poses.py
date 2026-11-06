#!/usr/bin/env python
"""POSE-RESCUE finder. For each OVER-DOCKED gate-selective, scan ALL its g12d co-fold shards/models
and find any pose that is BOTH physically realistic (native Asp6<->HLA salt bridge preserved, sb<4A)
AND productively bound (binder engages the peptide, bind_pep<6A) AND near enough to sense Asp6
through-space (bind_p6<10A). If such a pose exists, re-gating on it tests whether the design's G12D
selectivity SURVIVES on a realistic pose (rescued/credible) or vanishes (artifact confirmed).
Writes gate/rescue_poses.tsv (design_r <TAB> chosen preserved pose). python -I find_rescue_poses.py"""
import math, glob, os, json, re
CAMP="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs/campaign"; os.chdir(CAMP)
OVERDOCKED=["nb3_gpu6_132","nb3_gpu6_432","protein_0103","nb3_gpu7_040","nb3_gpu4_093"]
def parse(path):
    ch={}
    for ln in open(path):
        if not ln.startswith(("ATOM","HETATM")): continue
        an=ln[12:16].strip(); cid=ln[21]
        try: resi=int(ln[22:26])
        except: continue
        el=(ln[76:78].strip() if len(ln)>=78 else "") or an[0]
        if el=="H": continue
        x=float(ln[30:38]); y=float(ln[38:46]); z=float(ln[46:54])
        ch.setdefault(cid,{}).setdefault(resi,[]).append((an,x,y,z))
    return ch
def dmin(A,B):
    m=1e9
    for _,ax,ay,az in A:
        for _,bx,by,bz in B:
            d=(ax-bx)**2+(ay-by)**2+(az-bz)**2
            if d<m:m=d
    return math.sqrt(m)
BN={"NE","NH1","NH2","NZ"}
def analyze(path):
    ch=parse(path)
    peps=[c for c in ch if 8<=len(ch[c])<=12]
    if not peps or "A" not in ch: return None
    pep=peps[0]; A=ch["A"]; r6=sorted(ch[pep])[5]; asp=ch[pep][r6]
    carb=[a for a in asp if a[0] in {"OD1","OD2"}]
    if not carb: return None
    sb=1e9
    for resi in A:
        # resname not stored; detect basic by sidechain-N atom names present
        bn=[a for a in A[resi] if a[0] in BN]
        if bn: sb=min(sb,dmin(bn,carb))
    binder="P" if "P" in ch else None
    if binder is None:
        o=[c for c in ch if c not in ("A","B",pep)]; binder=max(o,key=lambda c:len(ch[c])) if o else None
    if binder is None: return None
    bat=[a for r in ch[binder] for a in ch[binder][r]]
    pepat=[a for r in ch[pep] for a in ch[pep][r]]
    bind_p6=dmin(asp,bat); bind_pep=dmin(pepat,bat)
    return sb,bind_p6,bind_pep
def conf(pdb):
    m=re.search(r"model_(\d+)\.pdb$",pdb); k=m.group(1) if m else "0"
    nm=os.path.basename(pdb).split("__")[0]
    cj=os.path.join(os.path.dirname(pdb),f"confidence_{nm}__g12d_model_{k}.json")
    try: return float(json.load(open(cj)).get("confidence_score",-1.0))
    except Exception: return -1.0
rows=[]
print(f"{'design':14} {'poses':>5} {'preserv':>7} {'presBound':>9}  best-rescue(sb/bp6/bpep/conf)")
for n in OVERDOCKED:
    poses=[]
    for r in ("panel_fold","triage_fold","incumbent_g12d_fold"):
        poses+=glob.glob(f"{r}/pred*/boltz_results_sh*/predictions/{n}__g12d/{n}__g12d_model_*.pdb")
    stats=[]
    for p in poses:
        a=analyze(p)
        if a is None: continue
        sb,bp6,bpep=a; stats.append((sb,bp6,bpep,conf(p),p))
    npres=sum(1 for s in stats if s[0]<4)
    cand=[s for s in stats if s[0]<4 and s[2]<6 and s[1]<10]   # preserved + bound + near-Asp6
    best=max(cand,key=lambda s:s[3]) if cand else None
    if best:
        rows.append((n+"_r",best[4],best[0],best[1],best[2],best[3]))
        print(f"{n:14} {len(stats):>5} {npres:>7} {len(cand):>9}  sb={best[0]:.2f} bp6={best[1]:.2f} bpep={best[2]:.2f} conf={best[3]:.3f}")
    else:
        print(f"{n:14} {len(stats):>5} {npres:>7} {len(cand):>9}  NONE (no preserved+bound+near pose -> cannot rescue; over-dock is intrinsic)")
with open("gate/rescue_poses.tsv","w") as o:
    for dr,p,sb,bp6,bpep,c in rows: o.write(f"{dr}\t{p}\n")
print(f"\nrescue candidates: {len(rows)}/{len(OVERDOCKED)} -> wrote gate/rescue_poses.tsv")
for dr,p,sb,bp6,bpep,c in rows: print(f"  {dr}: {p}")
