#!/usr/bin/env python
"""Adversarial self-audit: run the published selection prompt's checks on our own 20.
Hard rules (length 10-250/chain, valid class, no duplicates, no tag-aimed), the 3 within-class screens,
Ig-V-domain misclassification (single_chain), near-duplicate detection, and the set-aside flags. Read-only."""
import csv, difflib
RUNS="/home/prachh/v/anthropic-adaptyv-2026-pmhc/runs"
rows=list(csv.DictReader(open(f"{RUNS}/submission.csv")))
scr={r["name"]:r for r in csv.DictReader(open(f"{RUNS}/submission_screens.csv"))}
TAGS=["HHHHHH","WSHPQFEK","DYKDDDDK","EQKLISEEDL","GGGGSGGGGS"]  # His6, Strep, FLAG, myc, long GS-linker
print("=== HARD RULES: length (10-250), class, tag scan ===")
for i,r in enumerate(rows,1):
    s=r["sequence"]; n=r["name"]; L=len(s)
    oklen = 10<=L<=250
    tag = [t for t in TAGS if t in s]
    cls_ok = r["molecule_class"] in ("single_chain","nanobody","scfv","fab_kappa","fab_lambda")
    flags=[]
    if not oklen: flags.append(f"LEN {L}")
    if tag: flags.append(f"TAG {tag}")
    if not cls_ok: flags.append("CLASS")
    if flags: print(f"  #{i:<2} {n:16} FLAG: {flags}")
print("  (no lines above = all pass length/class/tag)")

print("\n=== Ig V-domain misclassification risk (single_chain only; Ig VH/VHH ~110-125 aa) ===")
for i,r in enumerate(rows,1):
    if r["molecule_class"]!="single_chain": continue
    s=r["sequence"]; L=len(s)
    # Ig V-domain hallmarks: length ~110-130, two Cys ~ (positions), framework motifs WGQG/WGxG near C-term
    cys=s.count("C"); wg = ("WGQG" in s or "WGRG" in s or "WGKG" in s)
    risk = (L>=105) and wg and cys>=2
    tag = "IG-RISK" if risk else ("short(%d aa) - not an Ig V-domain"%L if L<105 else "len ok, no Ig motif")
    print(f"  #{i:<2} {r['name']:16} len {L:>3}  Cys {cys}  WGxG {wg}  -> {tag}")

print("\n=== NEAR-DUPLICATE scan (difflib ratio; flag >0.85) ===")
def cdr3(seq):  # crude VHH HCDR3: between last 'C' and the 'WG.G'
    import re
    m=re.search(r"C([A-Z]{3,40}?)WG[QRK]G", seq)
    return m.group(1) if m else None
pairs=[]
for a in range(len(rows)):
    for b in range(a+1,len(rows)):
        na,nb=rows[a]["name"],rows[b]["name"]; sa,sb=rows[a]["sequence"],rows[b]["sequence"]
        rt=difflib.SequenceMatcher(None,sa,sb).ratio()
        if rt>0.85:
            note=""
            if rows[a]["molecule_class"]=="nanobody" and rows[b]["molecule_class"]=="nanobody":
                ca,cb=cdr3(sa),cdr3(sb)
                if ca and cb:
                    cr=difflib.SequenceMatcher(None,ca,cb).ratio()
                    note=f"(shared VHH framework; CDR3 identity {cr:.2f}: {'DISTINCT CDR3' if cr<0.7 else 'SIMILAR CDR3'})"
            pairs.append((rt,na,nb,rows[a]["molecule_class"],note))
pairs.sort(reverse=True)
top10={rows[i]["name"] for i in range(10)}
for rt,na,nb,cl,note in pairs:
    both = "BOTH in top-10" if (na in top10 and nb in top10) else ("one in top-10" if (na in top10 or nb in top10) else "neither in top-10")
    print(f"  {rt:.2f} {na:15}~{nb:15} {cl:11} [{both}] {note}")
print("  (pairs >0.85 only; VHH framework sharing is expected and not a true duplicate if CDR3 differs)")

print("\n=== 3 SCREENS within-class: flag outliers (pLDDT low / KD>0 / low ipSAE) ===")
for i,r in enumerate(rows,1):
    if i>10: break
    sc=scr[r["name"]]; cls=r["molecule_class"]
    pl=float(sc["plddt"]); kd=float(sc["mean_KD_hydropathy"]); ip=float(sc["ipSAE_g12d"])
    fl=[]
    floor = 70 if cls=="nanobody" else 80   # within-class pLDDT floor (nanobodies scored lower by single-seq)
    if pl<floor: fl.append(f"pLDDT {pl:.0f}<{floor}")
    if kd>0: fl.append(f"KD {kd:+.2f}>0")
    if ip<0.45: fl.append(f"ipSAE {ip:.2f} low")
    print(f"  #{i:<2} {r['name']:16}{cls:11} pLDDT {pl:>4.0f} ipSAE {ip:.2f} KD {kd:+.2f}  {'FLAG: '+', '.join(fl) if fl else 'ok'}")
