#!/usr/bin/env python3
"""Sequence-level developability liabilities for binder candidates (expression/solubility risk).
Flags: free Cys (0 best; vicinal worst), longest CONTIGUOUS single-aa run>=4, a 5-residue all-hydrophobic
patch (SAP proxy), N-glyc sequon N-[^P]-[ST] (minor for bacterial/cell-free), GRAVY>0.2 (hydrophobic),
|net charge|>=10. Keeps structural Pro in mind (instability-index proline FP). Input = any TSV/CSV with
name + sequence columns. Run with any python3 (stdlib only).
Usage: developability.py <tsv/csv> [--name-col name] [--seq-col seq|sequence] [--out tsv]
"""
import argparse, csv, re
HYD = set("AILMFWVY"); ARO = set("FWY"); POS = set("KR"); NEG = set("DE")
KD = {'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'Q':-3.5,'E':-3.5,'G':-0.4,'H':-3.2,'I':4.5,'L':3.8,
      'K':-3.9,'M':1.9,'F':2.8,'P':-1.6,'S':-0.8,'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2}

def longest_run(s):
    return max((len(m.group(0)) for m in re.finditer(r'(.)\1*', s)), default=0)

def flags(s):
    f = []
    c = s.count('C')
    if c > 0: f.append(f"Cys{c}")
    if longest_run(s) >= 4: f.append(f"run{longest_run(s)}")
    if any(all(x in HYD for x in s[i:i+5]) for i in range(len(s)-4)): f.append("patch5")
    if re.search(r'N[^P][ST]', s): f.append("glyc" + str(len(re.findall(r'N[^P][ST]', s))))
    g = sum(KD[x] for x in s) / len(s)
    if g > 0.2: f.append("hydrophobic")
    net = sum(x in POS for x in s) - sum(x in NEG for x in s)
    if abs(net) >= 10: f.append(f"charge{net:+d}")
    return f, round(g, 2), net

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("--name-col", default="name")
    ap.add_argument("--seq-col", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    delim = "\t" if a.inp.endswith((".tsv", ".txt")) else ","
    rdr = list(csv.DictReader(open(a.inp), delimiter=delim))
    seqcol = a.seq_col or ("seq" if "seq" in rdr[0] else "sequence")
    out = a.out or (a.inp.rsplit(".", 1)[0] + "_dev.tsv")
    w = open(out, "w")
    w.write("name\tlen\tCys\trun\tpatch5\tnet\tgravy\tnglyc\tnflag\tflags\n")
    clean = 0
    for r in rdr:
        n = r[a.name_col]; s = r[seqcol].strip().upper()
        if not s or any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in s): continue
        f, g, net = flags(s)
        nglyc = len(re.findall(r'N[^P][ST]', s))
        if not f: clean += 1
        w.write(f"{n}\t{len(s)}\t{s.count('C')}\t{longest_run(s)}\t{int(any(all(x in HYD for x in s[i:i+5]) for i in range(len(s)-4)))}\t{net}\t{g}\t{nglyc}\t{len(f)}\t{','.join(f) or 'clean'}\n")
    w.close()
    print(f"[developability] {len(rdr)} seqs -> {out} ; {clean} fully clean")

if __name__ == "__main__":
    main()
