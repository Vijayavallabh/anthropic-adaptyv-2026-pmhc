#!/usr/bin/env python3
"""Score a peptide-SWAP panel: per (design, peptide) binder<->peptide interface (bp_ipsae), then the
SPECIFICITY metric spec = bp_ipsae(g12d) - mean(bp_ipsae over DISSIMILAR peptides). A peptide-shape-specific
binder has spec>0 (binds the KRAS peptide, rejects dissimilar A*11:01 peptides); a PAN-PEPTIDE platform-reader
has spec~0 (binds everything) -> DEMOTE. Co-fold is blind to g12d-vs-wt and the composition-matched scramble
(so those are NOT in the dissimilar set). Uses model_0 ipSAE for speed. Run with boltz venv python.
Usage: score_pepswap.py <panel_out_dir> [--dissimilar ebna4,atic] [--out tsv]
"""
import sys, os, glob, json, re, subprocess, argparse
import numpy as np
PY = "/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python"
IPSAE = "/home/prachh/v/anthropic-adaptyv-2026-tfr1/scripts/ipsae.py"

def chain_order(pdb):
    o, s = [], set()
    for ln in open(pdb):
        if ln.startswith(("ATOM", "HETATM")):
            c = ln[21]
            if c not in s: s.add(c); o.append(c)
    return o

def parse_ipsae(txt, want):
    if not os.path.exists(txt): return None
    best = None
    for ln in open(txt):
        p = ln.split()
        if len(p) < 6 or p[4] != "max": continue
        if frozenset((p[0], p[1])) != want: continue
        try: v = float(p[5])
        except ValueError: continue
        best = v if best is None else max(best, v)
    return best

def bp_ipsae(root, design, pep, nsamp=3):
    """mean bp_ipsae(P,C) over available samples for design__pep."""
    job = f"{design}__{pep}"
    vals = []
    for mi in range(nsamp):
        cand = glob.glob(f"{root}/**/{job}_model_{mi}.pdb", recursive=True)
        if not cand: continue
        pdb = cand[0]; pae = pdb.replace(f"{job}_model_{mi}.pdb", f"pae_{job}_model_{mi}.npz")
        txt = pdb[:-4] + "_10_10.txt"
        if not os.path.exists(txt) and os.path.exists(pae):
            subprocess.run([PY, IPSAE, pae, pdb, "10", "10"], capture_output=True, timeout=300)
        v = parse_ipsae(txt, frozenset(("P", "C")))
        if v is not None: vals.append(v)
    return float(np.mean(vals)) if vals else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--dissimilar", default="ebna4,atic")
    ap.add_argument("--nsamp", type=int, default=3)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    dissim = a.dissimilar.split(",")
    # discover designs and peptides
    jobs = set()
    for cj in glob.glob(f"{a.root}/**/confidence_*__*_model_0.json", recursive=True):
        m = re.match(r"confidence_(.+)__(\w+)_model_0\.json", os.path.basename(cj))
        if m: jobs.add((m.group(1), m.group(2)))
    designs = sorted({d for d, _ in jobs}); peps = sorted({p for _, p in jobs})
    rows = []
    for d in designs:
        r = {"name": d}
        for p in peps:
            r[p] = bp_ipsae(a.root, d, p, a.nsamp)
        g = r.get("g12d")
        ds = [r[p] for p in dissim if r.get(p) is not None]
        r["spec"] = round(g - np.mean(ds), 3) if (g is not None and ds) else None
        rows.append(r)
    rows.sort(key=lambda x: (x["spec"] is not None, x["spec"] or -9), reverse=True)
    out = a.out or f"{a.root}/pepswap_spec.tsv"
    cols = ["name"] + peps + ["spec"]
    with open(out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(f"{r.get(c):.2f}" if isinstance(r.get(c), float) else str(r.get(c)) for c in cols) + "\n")
    print(f"peptide-swap: {len(rows)} designs -> {out} ; dissimilar={dissim}")
    print(f"{'design':16s} " + " ".join(f"{p:>6}" for p in peps) + f" {'spec':>6}")
    for r in rows:
        print(f"{r['name']:16s} " + " ".join(f"{(r.get(p) if r.get(p) is not None else float('nan')):6.2f}" for p in peps) + f" {(r['spec'] if r['spec'] is not None else float('nan')):6.2f}")
    sp = [r["spec"] for r in rows if r["spec"] is not None]
    if sp:
        print(f"\nspec>0.20 (peptide-specific): {sum(s>0.20 for s in sp)}/{len(sp)} ; spec<0.10 (pan-peptide, DEMOTE): {sum(s<0.10 for s in sp)}")

if __name__ == "__main__":
    main()
