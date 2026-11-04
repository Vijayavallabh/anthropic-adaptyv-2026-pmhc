#!/usr/bin/env python3
"""FAST drop-in for score_rfd_val.py: byte-identical selectivity-axis TSV, but (1) one os.walk
index instead of a recursive glob per (design,pep,sample) pair, and (2) the ipSAE .txt files are
generated in a parallel process pool across many cores instead of one sequential subprocess at a
time. The scoring MATH (parse_ipsae, mean-over-samples, spec_scram, promisc_margin, sort, format)
is copied verbatim from score_rfd_val.py so output must match exactly.

Why: the panel scorer would otherwise spawn ~56k ipsae.py subprocesses sequentially (~31 h on the
511-res nanobody complexes). This runs them --jobs-wide (default 64 of 192 cores) -> ~30 min.
Verify against the original before trusting:  diff <(orig) <(fast)  must be empty.

Usage: score_rfd_val_fast.py <fold_root> --out <tsv> [--nsamp 5] [--binder-chain P] [--jobs 64]
"""
import os, glob, subprocess, argparse, re
import numpy as np
from multiprocessing import Pool
PY = "/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python"
IPSAE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ipsae.py")  # vendored in-repo (TFR tools/ vanished once mid-session); byte-identical copy
PEPS = ["g12d", "wt", "scram", "ebna4", "atic"]


def parse_ipsae(txt, want):
    # verbatim from score_rfd_val.py
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


def _run_ipsae(args):
    pae, pdb = args
    try:
        subprocess.run([PY, IPSAE, pae, pdb, "10", "10"], capture_output=True, timeout=300)
    except Exception:
        pass
    return None


def ipsae_pair_indexed(index, job, want, nsamp):
    """mean ipSAE for a chain pair over available samples of <job> -- same as score_rfd_val.ipsae_pair
    but file lookup is O(1) via the prebuilt basename index and the .txt is assumed pre-generated."""
    vals = []
    for mi in range(nsamp):
        pdb = index.get(f"{job}_model_{mi}.pdb")
        if not pdb: continue
        txt = pdb[:-4] + "_10_10.txt"
        v = parse_ipsae(txt, want)
        if v is not None: vals.append(v)
    return float(np.mean(vals)) if vals else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--nsamp", type=int, default=5)
    ap.add_argument("--binder-chain", default="P")
    ap.add_argument("--jobs", type=int, default=64)
    a = ap.parse_args()
    B = a.binder_chain

    # 1. ONE walk of the tree -> basename->fullpath index (unique basenames: design names are unique)
    index = {}
    for dp, _, fns in os.walk(a.root):
        for fn in fns:
            index.setdefault(fn, os.path.join(dp, fn))

    # 2. designs discovered exactly as the original (confidence_<name>__<pep>_model_0.json)
    designs = sorted({re.match(r"confidence_(.+)__\w+_model_0\.json", fn).group(1)
                      for fn in index if re.match(r"confidence_(.+)__\w+_model_0\.json", fn)})

    # 3. collect every (pae,pdb) the scoring loop will query whose .txt is missing -> generate in parallel
    work = []
    for d in designs:
        for pep in PEPS + ["empty"]:
            for mi in range(a.nsamp):
                pdb = index.get(f"{d}__{pep}_model_{mi}.pdb")
                if not pdb: continue
                txt = pdb[:-4] + "_10_10.txt"
                # pae path mirrors score_rfd_val.ipsae_pair: pae_<basename>.npz beside the pdb
                pae = os.path.join(os.path.dirname(pdb),
                                   f"pae_{os.path.basename(pdb)[:-4]}.npz")
                if not os.path.exists(txt) and os.path.exists(pae):
                    work.append((pae, pdb))
    if work:
        print(f"[fast] generating {len(work)} ipSAE txt in parallel (jobs={a.jobs})", flush=True)
        with Pool(a.jobs) as pool:
            for _ in pool.imap_unordered(_run_ipsae, work, chunksize=4):
                pass

    # 4. scoring loop -- verbatim logic from score_rfd_val.py, lookups via index
    rows = []
    for d in designs:
        r = {"name": d}
        for p in PEPS:
            r[p] = ipsae_pair_indexed(index, f"{d}__{p}", frozenset((B, "C")), a.nsamp)
        r["bh_e"] = ipsae_pair_indexed(index, f"{d}__empty", frozenset((B, "A")), a.nsamp)
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


if __name__ == "__main__":
    main()
