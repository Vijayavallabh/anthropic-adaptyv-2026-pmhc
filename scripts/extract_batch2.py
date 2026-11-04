#!/usr/bin/env python3
"""Extract + hard-filter BoltzGen batch-2 de-novo single-chain protein binders (chain A of each design cif;
target = B/C/D = HLA/b2m/peptide). Dedupe, then drop: non-standard AA, length outside [55,120], low-complexity
(poly-run>=5 or any AA>30%), and Ig-folds (protein-anything emits antibody V-domains -> not de-novo-eligible).
Emits runs/gen_batch2_clean.csv (name,sequence) for the ESMFold->cofold->5-sample-reval funnel.
Run with boltz venv python (Bio). Usage: extract_batch2.py [--gen folds/gen/prot_batch2] [--out runs/gen_batch2_clean.csv]
"""
import argparse, glob, os, re, csv, warnings
warnings.filterwarnings("ignore")
from Bio.PDB import MMCIFParser
_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I",
      "LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
jmotif = re.compile(r'[FW]G.G[TS]')
def is_ig(s):
    # ig_ss = immunoglobulin V-set topology (Cys -~13- conserved Trp -~40-60- 2nd Cys disulfide); catches de-novo
    # Ig V-domains whose motifs differ from the natural antibody consensus and evade the per-motif checks. x2.
    h = (s.count('C') >= 2) + bool(re.search(r'C.{8,20}W[VYFI][RQK]Q', s)) + bool(jmotif.search(s[-15:])) \
        + bool(re.search(r'(QVQL|EVQL|DIQ|DIV|EIV|QLQ|QVQ|GVQ|QSV|QVK)', s[:6])) + bool(re.search(r'Y[YFH]C[A-Z]{3,}', s)) \
        + 2 * bool(re.search(r'C.{8,18}W.{25,65}C', s))
    return h >= 3
def maxrun(s):
    m = c = 1
    for i in range(1, len(s)):
        c = c + 1 if s[i] == s[i-1] else 1; m = max(m, c)
    return m
def lowc(s): return (not s) or maxrun(s) >= 5 or max(s.count(a)/len(s) for a in set(s)) > 0.30

def chainA_seq(cif):
    m = MMCIFParser(QUIET=True).get_structure("s", cif)[0]
    if "A" not in m: return ""
    return "".join(_3[r.resname] for r in m["A"] if r.id[0] == " " and r.resname in _3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", default="folds/gen/prot_batch2")
    ap.add_argument("--out", default="runs/gen_batch2_clean.csv")
    a = ap.parse_args()
    cifs = sorted(glob.glob(f"{a.gen}/**/intermediate_designs/*_[0-9]*.cif", recursive=True))
    seen, rows, stats = {}, [], dict(total=0, ig=0, lowc=0, lenbad=0, dup=0, nonstd=0, kept=0)
    for cif in cifs:
        stats["total"] += 1
        g = re.search(r'/(gpu\d+)/', cif); gi = g.group(1) if g else "g"
        idx = re.search(r'_(\d+)\.cif$', cif).group(1)
        nm = f"b2_{gi}_{idx}"
        s = chainA_seq(cif)
        if not s or any(ch not in _3.values() for ch in s): stats["nonstd"] += 1; continue
        if not (55 <= len(s) <= 120): stats["lenbad"] += 1; continue
        if s in seen: stats["dup"] += 1; continue
        if lowc(s): stats["lowc"] += 1; continue
        if is_ig(s): stats["ig"] += 1; continue
        seen[s] = nm; rows.append((nm, s)); stats["kept"] += 1
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["name", "sequence"])
        for nm, s in rows: w.writerow([nm, s])
    print(f"batch2 extract: {stats}")
    print(f"wrote {len(rows)} clean de-novo single-chain candidates -> {a.out}")

if __name__ == "__main__":
    main()
