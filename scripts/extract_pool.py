#!/usr/bin/env python3
"""Mode-aware extraction + hard-filter of a BoltzGen generation pool (chain A = de-novo binder;
chains B/C/D = target HLA/b2m/peptide). Dedupe + drop junk. Emits name,sequence CSV.

  protein  mode: de-novo single_chain -- length 55-120, DROP Ig-folds (protein-anything emits antibody
                 V-domains that are not de-novo-eligible), drop low-complexity (poly-run>=5 / any AA>30%).
  nanobody mode: VHH -- length 105-140, KEEP the Ig framework (CDR-judged + novelty-exempt), still drop
                 low-complexity + dedup; require a plausible VHH C..C pair.

Run with the boltz venv python (Bio.PDB). Usage:
  extract_pool.py --gen <gen_dir> --out <csv> --prefix <tag> --mode protein|nanobody
"""
import argparse, glob, re, warnings
warnings.filterwarnings("ignore")
from Bio.PDB import MMCIFParser

_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I",
      "LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
jmotif = re.compile(r'[FW]G.G[TS]')

def is_ig(s):
    h = (s.count('C') >= 2) + bool(re.search(r'C.{8,20}W[VYFI][RQK]Q', s)) + bool(jmotif.search(s[-15:])) \
        + bool(re.search(r'(QVQL|EVQL|DIQ|DIV|EIV|QLQ|QVQ|GVQ|QSV|QVK)', s[:6])) + bool(re.search(r'Y[YFH]C[A-Z]{3,}', s)) \
        + 2 * bool(re.search(r'C.{8,18}W.{25,65}C', s))
    return h >= 3

def maxrun(s):
    m = c = 1
    for i in range(1, len(s)):
        c = c + 1 if s[i] == s[i-1] else 1; m = max(m, c)
    return m

def lowc(s):
    return (not s) or maxrun(s) >= 5 or max(s.count(a)/len(s) for a in set(s)) > 0.30

def _chain_seq(chain):
    return "".join(_3[r.resname] for r in chain if r.id[0] == " " and r.resname in _3)

def binder_seq(cif):
    """Return the de-novo BINDER chain, identified by EXCLUSION of the fixed target chains (HLA
    'GSHSMRY...', b2m 'IQRTP...', peptide 'VVVGA...' len<=12). Robust to chain order: protein-anything
    emits the binder as chain A; nanobody-anything emits the target as A/B/C and the binder as chain D."""
    m = MMCIFParser(QUIET=True).get_structure("s", cif)[0]
    seqs = [s for s in (_chain_seq(c) for c in m) if s]
    def is_target(s):
        return s.startswith("GSHSMRY") or s.startswith("IQRTP") or (s.startswith("VVVGA") and len(s) <= 12)
    binders = [s for s in seqs if not is_target(s)]
    return binders[0] if len(binders) == 1 else ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--mode", choices=["protein", "nanobody"], required=True)
    a = ap.parse_args()
    lo, hi = (55, 120) if a.mode == "protein" else (105, 140)
    cifs = sorted(glob.glob(f"{a.gen}/**/intermediate_designs/*_[0-9]*.cif", recursive=True))
    seen, rows = {}, []
    stats = dict(total=0, ig=0, lowc=0, lenbad=0, dup=0, nonstd=0, novhh=0, kept=0)
    for cif in cifs:
        stats["total"] += 1
        g = re.search(r'/(gpu\d+)/', cif); gi = g.group(1) if g else "g"
        mi = re.search(r'_(\d+)\.cif$', cif)
        if not mi:
            continue
        nm = f"{a.prefix}_{gi}_{mi.group(1)}"
        s = binder_seq(cif)
        if not s or any(c not in _3.values() for c in s):
            stats["nonstd"] += 1; continue
        if not (lo <= len(s) <= hi):
            stats["lenbad"] += 1; continue
        if lowc(s):
            stats["lowc"] += 1; continue
        if a.mode == "protein" and is_ig(s):
            stats["ig"] += 1; continue
        if a.mode == "nanobody" and s.count("C") < 2:
            stats["novhh"] += 1; continue
        if s in seen:
            stats["dup"] += 1; continue
        seen[s] = nm; rows.append((nm, s)); stats["kept"] += 1
    with open(a.out, "w") as o:
        o.write("name,sequence\n")
        for nm, s in rows:
            o.write(f"{nm},{s}\n")
    print(f"[extract_pool {a.mode}] {stats}  -> {a.out} ({len(rows)} designs)")

if __name__ == "__main__":
    main()
