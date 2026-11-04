#!/usr/bin/env python3
"""Corrected, selectivity-FIRST integrated scorecard for the de-novo protein arm (red-team overhaul).
Fixes: (1) drop antibody V-domain folds mislabeled as 'protein' (novelty/de-novo-rule DQ); (2) PRIMARY
specificity = spec_scram = bp_ipsae(g12d) - bp_ipsae(scram) (composition-matched; not the old dissimilar
axis); (3) real peptide-grip = f_pep vs the should-fail decoy ceiling (~0.28); (4) affinity (bp_ipsae) is
a MINOR term, not the front-load driver (co-fold is tier-1-blind, so ranking by affinity front-loads the
pan-KRAS phenotype). Transparent multi-axis table; the human-style pick reasons over it afterwards.
Run with any python3. Writes runs/protein_scorecard_v2.tsv."""
import csv, re
R = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
DECOY_CEIL = 0.28  # max f_pep among should-fail helix decoys (helixdecoy_0037=0.28)

def load(path, key="name"):
    d = {}
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"): d[r[key]] = r
    return d

jmotif = re.compile(r'[FW]G.G[TS]')
def is_ig(s):
    h = 0
    if s.count('C') >= 2: h += 1
    if re.search(r'C.{8,20}W[VYFI][RQK]Q', s): h += 1
    if jmotif.search(s[-15:]): h += 1
    if re.search(r'(QVQL|EVQL|DIQ|DIV|EIV|QLQ|QVQ|GVQ|QSV|QVK)', s[:6]): h += 1
    if re.search(r'Y[YFH]C[A-Z]{3,}', s): h += 1
    return h >= 3

def maxrun(s):
    m = c = 1
    for i in range(1, len(s)):
        c = c + 1 if s[i] == s[i-1] else 1; m = max(m, c)
    return m

def fnum(x, d=0.0):
    try: return float(x)
    except Exception: return d

pep = load(f"{R}/runs/pepswap_full_3samp.tsv")
grip = load(f"{R}/runs/pep_grip.tsv")
sc = load(f"{R}/runs/protein_scorecard.tsv")
fp = load(f"{R}/runs/final_protein.tsv")

rows = []
for nm, pr in sc.items():
    seq = fp.get(nm, {}).get("seq", "")
    ig = is_ig(seq) if seq else False
    lowc = maxrun(seq) >= 5 or (seq and max(seq.count(a)/len(seq) for a in set(seq)) > 0.30)
    g = fnum(pep.get(nm, {}).get("g12d")); scram = fnum(pep.get(nm, {}).get("scram"))
    eb = fnum(pep.get(nm, {}).get("ebna4")); at = fnum(pep.get(nm, {}).get("atic"))
    spec_scram = round(g - scram, 3) if (g and nm in pep) else None
    off = round(max(scram, eb, at), 3) if nm in pep else None
    fpep = fnum(grip.get(nm, {}).get("fpep_mean"))
    fpmin = fnum(grip.get(nm, {}).get("fpep_min"))
    bp = fnum(pr.get("bp")); pepdep = fnum(fp.get(nm, {}).get("pep_dep"))
    bh_e = fnum(fp.get(nm, {}).get("bh_e")); esm = fnum(pr.get("esm")); maxtm = fnum(pr.get("maxTM"))
    afr = fnum(pr.get("af_rmsd"), 9); afpl = fnum(pr.get("af_plddt")); nli = fnum(pr.get("nliab"))
    grip_strong = fpmin > DECOY_CEIL
    spec_strong = spec_scram is not None and spec_scram >= 0.30
    platform = spec_scram is not None and spec_scram < 0.10   # binds scram ~ g12d (red flag, not proof)
    # selectivity-first composite (affinity minor; esm on 0-1). grip bonus only ABOVE decoy ceiling.
    sel = (max(0.0, spec_scram or 0) + 0.6*max(0.0, fpep - DECOY_CEIL)
           + 0.25*bp + 0.3*(esm/100.0) + 0.1*min(pepdep, 0.4)
           - 0.4*max(0.0, (off or 0) - 0.55) - (0.2 if bh_e > 0.80 else 0)
           - (0.5 if platform else 0))   # soft-demote platform readers
    # hard disqualifiers (Ig-fold / low-complexity / fold-fail); platform is a SOFT flag below
    dq = []
    if ig: dq.append("IG-FOLD")
    if lowc: dq.append("low-complexity")
    if afr >= 2.0: dq.append("af2ig-fail")
    flag = "platform" if platform else ("grip" if grip_strong else ("spec" if spec_strong else "-"))
    rows.append(dict(name=nm, sel=round(sel, 3), spec_scram=spec_scram, fpep=round(fpep, 2),
                     fpmin=round(fpmin, 2), grip=("Y" if grip_strong else "."),
                     specS=("Y" if spec_strong else "."), off=off, bp=round(bp, 2),
                     pepdep=round(pepdep, 2), bh_e=round(bh_e, 2), esm=round(esm, 2),
                     afr=round(afr, 2), maxtm=round(maxtm, 2), nli=int(nli), dq=",".join(dq) or "-"))

clean = [r for r in rows if r["dq"] == "-"]
clean.sort(key=lambda r: -r["sel"])
cols = ["name","sel","spec_scram","fpep","fpmin","grip","specS","off","bp","pepdep","bh_e","esm","afr","maxtm","nli","dq"]
with open(f"{R}/runs/protein_scorecard_v2.tsv", "w") as f:
    f.write("\t".join(cols) + "\n")
    for r in sorted(rows, key=lambda r: (r["dq"] != "-", -r["sel"])):
        f.write("\t".join(str(r[c]) for c in cols) + "\n")

print("=== CLEAN de-novo protein candidates, selectivity-first (sel desc) ===")
print(f"{'name':14s} {'sel':>5} {'specScr':>7} {'fpep':>4} {'grip':>4} {'specS':>5} {'off':>4} {'bp':>4} {'pepdep':>6} {'bh_e':>4} {'esm':>4} {'afr':>4} {'maxtm':>5} {'nli':>3}")
for r in clean:
    print(f"{r['name']:14s} {r['sel']:>5} {str(r['spec_scram']):>7} {r['fpep']:>4} {r['grip']:>4} {r['specS']:>5} {str(r['off']):>4} {r['bp']:>4} {r['pepdep']:>6} {r['bh_e']:>4} {r['esm']:>4} {r['afr']:>4} {r['maxtm']:>5} {r['nli']:>3}")
print(f"\nclean={len(clean)}  dropped:")
for r in sorted(rows, key=lambda r: r["name"]):
    if r["dq"] != "-": print(f"  {r['name']}: {r['dq']}")
