#!/usr/bin/env python
"""Portfolio pose-realism scan. For every gated design's g12d co-fold pose, measure:
  sb_dist  = Asp6 carboxylate <-> nearest HLA basic-N  (native salt bridge; <4A = PRESERVED/realistic)
  bind_p6  = Asp6 <-> nearest binder atom              (how the binder relates to the mutation site)
Interpretation (challenge: Asp6 is BURIED, salt-bridged to HLA Arg114, ~8 A^2 SASA):
  PRESERVED + large bind_p6 + gate-selective = credible THROUGH-SPACE discriminator (intended mechanism)
  BROKEN (Asp6 swung ~8A to the binder)      = over-dock artifact; gate ddG inflated/suspect
Joins gate ddG/verdict + ruler weakest. Writes gate/pose_realism.tsv. python -I scan_saltbridge_all.py"""
import math, glob, os, csv, json
CAMP="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs/campaign"; os.chdir(CAMP)
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
def analyze(path):
    ch=parse(path)
    peps=[c for c in ch if 8<=len(ch[c])<=12]
    if not peps or "A" not in ch: return None
    pep=peps[0]; A=ch["A"]; asp=ch[pep][sorted(ch[pep])[5]]
    carb=[a for a in asp[1] if a[0] in {"OD1","OD2"}]
    if not carb: return None
    sb=1e9
    for resi in A:
        if A[resi][0] in ("ARG","LYS"):
            bn=[a for a in A[resi][1] if a[0] in BN]
            if bn: sb=min(sb,dmin(bn,carb))
    binder="P" if "P" in ch else None
    if binder is None:
        others=[c for c in ch if c not in ("A","B",pep)]
        binder=max(others,key=lambda c:len(ch[c])) if others else None
    bp6=None
    if binder and binder in ch:
        bat=[a for r in ch[binder] for a in ch[binder][r][1]]
        bp6=dmin(asp[1],bat)
    return sb,bp6
def best_pose(n):
    cands=[]
    for r in ("panel_fold","triage_fold","incumbent_g12d_fold"):
        for pdb in glob.glob(f"{r}/pred*/boltz_results_sh*/predictions/{n}__g12d/{n}__g12d_model_0.pdb"):
            cj=os.path.join(os.path.dirname(pdb),f"confidence_{n}__g12d_model_0.json")
            sc=-1.0
            try: sc=float(json.load(open(cj)).get("confidence_score",-1.0))
            except Exception: pass
            cands.append((sc,pdb))
    return max(cands)[1] if cands else None
gate={r["design"]:r for r in csv.DictReader(open("gate/gate_results_unified.tsv"),delimiter="\t")}
weak={r["name"]:r for r in csv.DictReader(open("weakest_objective.tsv"),delimiter="\t")}
names=[l.strip() for l in open("gate/all_designs.txt") if l.strip()]
rows=[]
for n in names:
    p=best_pose(n)
    if not p: continue
    r=analyze(p)
    if r is None: continue
    sb,bp6=r; g=gate.get(n,{}); w=weak.get(n,{})
    rows.append((sb,bp6,n,g.get("ddG","?"),g.get("verdict","?"),w.get("weakest","?")))
rows.sort()
with open("gate/pose_realism.tsv","w") as o:
    o.write("name\tsb_dist\tbind_p6\trealism\tgate_ddG\tverdict\truler_wk\n")
    for sb,bp6,n,ddg,v,wk in sorted(rows,key=lambda r:r[2]):
        rl="preserved" if sb<4 else ("near" if sb<6 else "broken")
        o.write(f"{n}\t{sb:.2f}\t{bp6:.2f}\t{rl}\t{ddg}\t{v}\t{wk}\n")
print(f"{'sb':>6} {'b-p6':>6}  {'design':16} {'ddG':>7}  {'verdict':22} {'wk':>7}  realism")
for sb,bp6,n,ddg,v,wk in rows:
    rl="PRESERVED" if sb<4 else ("near" if sb<6 else "BROKEN")
    print(f"{sb:6.2f} {bp6:6.2f}  {n:16} {str(ddg):>7}  {v:22} {str(wk):>7}  {rl}")
pres=[r for r in rows if r[0]<4]; brok=[r for r in rows if r[0]>=6]
selp=[r for r in pres if "SELECTIVE" in r[4]]
print(f"\nN={len(rows)}  PRESERVED={len(pres)}  BROKEN={len(brok)}")
print(f"PRESERVED & gate-selective (credible, incl ruler-neg): {[r[2] for r in selp]}")
print("  of those, ruler-OK (weakest>0) = credible 4-axis discriminators:",
      [r[2] for r in selp if (r[5] not in ('?','') and float(r[5])>0)])
