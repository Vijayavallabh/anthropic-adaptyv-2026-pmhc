#!/usr/bin/env python3
"""Score the multi-sample RFd re-validation panel (folds/rfd_val/out) into ONE clean TSV with the
corrected, robust (5-sample) selectivity axes -- the single-sample rfd_pepswap was noise
([[lesson-cofold-pepdep-single-sample-is-noise-use-consistency]]). Per design:
  g12d/wt/scram/ebna4/atic = mean binder<->peptide ipSAE(P,C) over samples
  bh_e                      = mean binder<->HLA ipSAE(P,A) in the EMPTY state (real tier-2, LOWER=better)
  spec_scram = g12d-scram (sequence-order specificity, PRIMARY), promisc_margin = g12d-max(atic,ebna4)
A clean selective binder: g12d high, scram/atic/ebna4 low (promisc_margin>0), bh_e low.
Run with boltz venv python. Usage: score_rfd_val.py <fold_root> --out <tsv> [--nsamp 5]
"""
import os, glob, subprocess, argparse, re
import numpy as np
PY = "/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python"
IPSAE = "/home/prachh/v/anthropic-adaptyv-2026-tfr1/scripts/ipsae.py"
PEPS = ["g12d", "wt", "scram", "ebna4", "atic"]

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

def ipsae_pair(root, job, want, nsamp):
    """mean ipSAE for a chain pair over available samples of <job>."""
    vals = []
    for mi in range(nsamp):
        cand = glob.glob(f"{root}/**/{job}_model_{mi}.pdb", recursive=True)
        if not cand: continue
        pdb = cand[0]; pae = pdb.replace(f"{job}_model_{mi}.pdb", f"pae_{job}_model_{mi}.npz")
        txt = pdb[:-4] + "_10_10.txt"
        if not os.path.exists(txt) and os.path.exists(pae):
            subprocess.run([PY, IPSAE, pae, pdb, "10", "10"], capture_output=True, timeout=300)
        v = parse_ipsae(txt, want)
        if v is not None: vals.append(v)
    return float(np.mean(vals)) if vals else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--nsamp", type=int, default=5)
    ap.add_argument("--binder-chain", default="P", help="binder chain id for interface pairs (P single-chain; H for fab VH)")
    a = ap.parse_args()
    B = a.binder_chain
    designs = sorted({re.match(r"confidence_(.+)__\w+_model_0\.json", os.path.basename(j)).group(1)
                      for j in glob.glob(f"{a.root}/**/confidence_*__*_model_0.json", recursive=True)})
    rows = []
    for d in designs:
        r = {"name": d}
        for p in PEPS:
            r[p] = ipsae_pair(a.root, f"{d}__{p}", frozenset((B, "C")), a.nsamp)
        r["bh_e"] = ipsae_pair(a.root, f"{d}__empty", frozenset((B, "A")), a.nsamp)
        g, sc = r.get("g12d"), r.get("scram")
        r["spec_scram"] = round(g - sc, 3) if (g is not None and sc is not None) else None
        od = [r[p] for p in ("atic", "ebna4") if r.get(p) is not None]
        r["promisc_margin"] = round(g - max(od), 3) if (g is not None and od) else None
        rows.append(r)
    rows.sort(key=lambda x: (x["spec_scram"] is not None, x["spec_scram"] or -9), reverse=True)
    cols = ["name"] + PEPS + ["bh_e", "spec_scram", "promisc_margin"]
    with open(a.out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(f"{r.get(c):.3f}" if isinstance(r.get(c), float) else str(r.get(c)) for c in cols) + "\n")
    print(f"scored {len(rows)} designs -> {a.out}")
    print(f"{'design':16s}" + "".join(f"{p:>7}" for p in PEPS) + f"{'bh_e':>7}{'spcS':>7}{'pmarg':>7}")
    for r in rows:
        print(f"{r['name']:16s}" + "".join(f"{(r.get(p) if r.get(p) is not None else float('nan')):7.2f}" for p in PEPS)
              + f"{(r['bh_e'] if r.get('bh_e') is not None else float('nan')):7.2f}"
              + f"{(r['spec_scram'] if r['spec_scram'] is not None else float('nan')):7.2f}"
              + f"{(r['promisc_margin'] if r['promisc_margin'] is not None else float('nan')):7.2f}")

if __name__ == "__main__":
    main()
