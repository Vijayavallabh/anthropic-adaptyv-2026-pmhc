#!/usr/bin/env python3
"""Score pMHC co-folds: per (job, model) interface metrics + the G12D/WT/empty DIFFERENTIAL.

Reads Boltz-2 outputs under <fold_root> (confidence_*.json + pae_*.npz + *_model_*.pdb).
Generalizes the hardcoded A-B scorers to the 5-chain pMHC+TCR/binder complex by reading the chain
order + lengths from the model_0 pdb, so it handles loaded [A,B,C,D,E] and empty [A,B,D,E] alike.

Interfaces reported (TCR / binder = chains D,E if present, else the last chain):
  * binder<->peptide  (C): ipTM (pair_chains_iptm), ipSAE (ipsae.py), iPAE (mean cross-block PAE)
  * binder<->HLA      (A): ipTM, ipSAE  -- high here w/ low pep = the 'reads the helices' failure
  * peptide<->HLA     (A): ipTM         -- presentation sanity

Prints per-job means +/- SD over models and the DIFFERENTIALS g12d-wt and loaded-empty.
Usage: score_pmhc.py <fold_root> [--binder-chains D,E]
Run with the boltz venv python (numpy): /home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
"""
import sys, os, glob, json, re, subprocess, argparse, statistics as st
from collections import defaultdict
import numpy as np

PY = "/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python"
IPSAE = "/home/prachh/v/anthropic-adaptyv-2026-tfr1/scripts/ipsae.py"

def chain_order_and_lengths(pdb):
    """Ordered chain ids (first appearance) + residue count per chain from a pdb."""
    order, seen = [], {}
    for ln in open(pdb):
        if ln.startswith(("ATOM", "HETATM")):
            c = ln[21]; rs = ln[22:27]
            if c not in seen:
                seen[c] = set(); order.append(c)
            seen[c].add(rs)
    return order, {c: len(seen[c]) for c in order}

def pair_iptm(pair, i, j):
    """pair_chains_iptm is index-keyed + may be stored one-directional; try both."""
    a = pair.get(str(i), {}).get(str(j))
    b = pair.get(str(j), {}).get(str(i))
    vals = [v for v in (a, b) if isinstance(v, (int, float))]
    return max(vals) if vals else None

def parse_ipsae(txt, want_pairs):
    """Max symmetric ipSAE over the requested chain-letter pairs from a *_10_10.txt."""
    if not os.path.exists(txt):
        return None
    best = None
    for ln in open(txt):
        p = ln.split()
        if len(p) < 6 or p[0] in ("Chn1", "#"):
            continue
        if p[4] != "max":
            continue
        if frozenset((p[0], p[1])) not in want_pairs:
            continue
        try:
            v = float(p[5])
        except ValueError:
            continue
        best = v if best is None else max(best, v)
    return best

def ipae_block(pae, order, lens, rows_chains, col_chain):
    """Mean PAE between residues of rows_chains and residues of col_chain (both directions)."""
    off, cur = {}, 0
    for c in order:
        off[c] = (cur, cur + lens[c]); cur += lens[c]
    if col_chain not in off or any(c not in off for c in rows_chains):
        return None
    cs, ce = off[col_chain]
    blocks = []
    for rc in rows_chains:
        rs, re_ = off[rc]
        blocks.append(pae[rs:re_, cs:ce].ravel())
        blocks.append(pae[cs:ce, rs:re_].ravel())
    return float(np.mean(np.concatenate(blocks))) if blocks else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--binder-chains", default="D,E")
    a = ap.parse_args()
    binder_pref = a.binder_chains.split(",")

    confs = glob.glob(f"{a.root}/**/confidence_*_model_*.json", recursive=True)
    per = defaultdict(lambda: defaultdict(list))  # job -> metric -> [per-model]
    for cj in sorted(confs):
        d = os.path.dirname(cj)
        m = re.match(r"confidence_(.+)_model_(\d+)\.json", os.path.basename(cj))
        if not m:
            continue
        job, mi = m.group(1), m.group(2)
        pdb = os.path.join(d, f"{job}_model_{mi}.pdb")
        pae_npz = os.path.join(d, f"pae_{job}_model_{mi}.npz")
        if not (os.path.exists(pdb) and os.path.exists(pae_npz)):
            continue
        order, lens = chain_order_and_lengths(pdb)
        idx = {c: k for k, c in enumerate(order)}
        tcr = [c for c in binder_pref if c in idx]
        hla = "A"
        pep = "C" if "C" in idx else None
        conf = json.load(open(cj))
        pair = conf.get("pair_chains_iptm", {})
        per[job]["iptm"].append(conf.get("iptm"))
        if pep:
            v = max((x for t in tcr if (x := pair_iptm(pair, idx[t], idx[pep])) is not None), default=None)
            if v is not None: per[job]["tcr_pep_iptm"].append(v)
            vp = pair_iptm(pair, idx[pep], idx[hla])
            if vp is not None: per[job]["pep_hla_iptm"].append(vp)
        vh = max((x for t in tcr if (x := pair_iptm(pair, idx[t], idx[hla])) is not None), default=None)
        if vh is not None: per[job]["tcr_hla_iptm"].append(vh)
        # ipSAE via reference script (cached by the _10_10.txt)
        stem = pdb[:-4]
        txt = f"{stem}_10_10.txt"
        if not os.path.exists(txt):
            subprocess.run([PY, IPSAE, pae_npz, pdb, "10", "10"], capture_output=True, timeout=600)
        if pep:
            s = parse_ipsae(txt, {frozenset((t, pep)) for t in tcr})
            if s is not None: per[job]["tcr_pep_ipsae"].append(s)
        sh = parse_ipsae(txt, {frozenset((t, hla)) for t in tcr})
        if sh is not None: per[job]["tcr_hla_ipsae"].append(sh)
        # iPAE binder<->peptide
        try:
            P = np.load(pae_npz); pae = P[P.files[0]]
            if pep:
                ip = ipae_block(pae, order, lens, tcr, pep)
                if ip is not None: per[job]["tcr_pep_ipae"].append(ip)
        except Exception as e:
            print("iPAE fail", job, mi, e, file=sys.stderr)

    def agg(job, metric):
        xs = [x for x in per[job][metric] if isinstance(x, (int, float))]
        if not xs: return (float("nan"), float("nan"), 0)
        return (st.mean(xs), st.pstdev(xs) if len(xs) > 1 else 0.0, len(xs))

    metrics = ["tcr_pep_iptm", "tcr_pep_ipsae", "tcr_pep_ipae", "tcr_hla_iptm", "tcr_hla_ipsae", "pep_hla_iptm", "iptm"]
    jobs = sorted(per)
    print(f"\n=== per-job (mean +/- SD over n models) :: {a.root} ===")
    hdr = f"{'job':12s} " + " ".join(f"{m.replace('tcr_','').replace('_',''):>12s}" for m in metrics)
    print(hdr)
    table = {}
    for job in jobs:
        table[job] = {m: agg(job, m) for m in metrics}
        row = f"{job:12s} " + " ".join(f"{table[job][m][0]:12.3f}" for m in metrics)
        print(row)
        print(f"{'  +/-SD':12s} " + " ".join(f"{table[job][m][1]:12.3f}" for m in metrics))

    # DIFFERENTIALS
    def diff(hi, lo, metric):
        a_, sa, na = table.get(hi, {}).get(metric, (float('nan'),0,0))
        b_, sb, nb = table.get(lo, {}).get(metric, (float('nan'),0,0))
        pooled = (sa**2 + sb**2) ** 0.5
        return a_ - b_, pooled
    print("\n=== DIFFERENTIALS (want > 0; z = delta / pooledSD) ===")
    for tag, hi, lo in [("JDI  g12d-wt", "jdi_g12d", "jdi_wt"),
                        ("JDI  load-empty(pepIPTMvsHLA)", "jdi_g12d", "jdi_empty"),
                        ("Poole g12d-wt", "poole_g12d", "poole_wt")]:
        if hi in table and lo in table:
            for m in ["tcr_pep_iptm", "tcr_pep_ipsae", "tcr_pep_ipae", "tcr_hla_iptm"]:
                dv, ps = diff(hi, lo, m)
                z = dv / ps if ps > 1e-9 else float("inf") if abs(dv) > 1e-9 else 0.0
                arrow = "" if m == "tcr_pep_ipae" else ""  # ipae: lower=better so sign flips meaning
                print(f"  {tag:34s} {m:16s} delta={dv:+.3f}  z={z:+.2f}")
    print("\nNOTE: tcr_pep_ipae is an ERROR (lower=better) -> for it a NEGATIVE delta(g12d-wt) is good.")

if __name__ == "__main__":
    main()
