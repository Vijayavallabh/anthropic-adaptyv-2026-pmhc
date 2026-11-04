#!/usr/bin/env python3
"""Design-level gate from the 3-state co-fold. Pairs each design's <name>__g12d and <name>__empty jobs:
  BINDING (loaded g12d): bp_iptm/bp_ipsae = binder(P)<->peptide(C); bh_iptm = binder<->HLA(A); global iptm
  PEPTIDE-DEPENDENCE   : pep_dep_iptm = bh_iptm(g12d) - bh_iptm(empty); pep_dep_glob = iptm(g12d)-iptm(empty)
                         (the proven tier-2 signal: loaded >> empty; TCR pos-control was +0.20)
Ranks by a composite (peptide-interface confidence gated on positive peptide-dependence) and writes
scored.tsv + top<N>.csv for the refined pass (more samples + WT + Chai + af2ig). Run with boltz venv python.
Usage: score_designs.py <fold_root> [--topn 80]
"""
import sys, os, glob, json, re, subprocess, argparse
import numpy as np
PY = "/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python"
IPSAE = "/home/prachh/v/anthropic-adaptyv-2026-tfr1/scripts/ipsae.py"

def chain_order(pdb):
    order, seen = [], set()
    for ln in open(pdb):
        if ln.startswith(("ATOM", "HETATM")):
            c = ln[21]
            if c not in seen: seen.add(c); order.append(c)
    return order

def pair_iptm(pair, i, j):
    a = pair.get(str(i), {}).get(str(j)); b = pair.get(str(j), {}).get(str(i))
    vals = [v for v in (a, b) if isinstance(v, (int, float))]
    return max(vals) if vals else None

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

def job_metrics(d, job):
    """One job dir -> metrics using model_0."""
    cj = glob.glob(f"{d}/confidence_{job}_model_0.json")
    pdb = glob.glob(f"{d}/{job}_model_0.pdb")
    if not (cj and pdb): return None
    conf = json.load(open(cj[0])); pair = conf.get("pair_chains_iptm", {})
    order = chain_order(pdb[0]); idx = {c: k for k, c in enumerate(order)}
    m = {"iptm": conf.get("iptm")}
    if "P" in idx and "A" in idx:
        m["bh_iptm"] = pair_iptm(pair, idx["P"], idx["A"])
    if "P" in idx and "C" in idx:
        m["bp_iptm"] = pair_iptm(pair, idx["P"], idx["C"])
        pae = glob.glob(f"{d}/pae_{job}_model_0.npz")
        txt = pdb[0][:-4] + "_10_10.txt"
        if not os.path.exists(txt) and pae:
            subprocess.run([PY, IPSAE, pae[0], pdb[0], "10", "10"], capture_output=True, timeout=600)
        m["bp_ipsae"] = parse_ipsae(txt, frozenset(("P", "C")))
        m["bh_ipsae"] = parse_ipsae(txt, frozenset(("P", "A")))
    return m

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--topn", type=int, default=80)
    a = ap.parse_args()
    cjs = glob.glob(f"{a.root}/**/confidence_*__g12d_model_0.json", recursive=True)
    designs = {}
    for cj in cjs:
        name = re.match(r"confidence_(.+)__g12d_model_0\.json", os.path.basename(cj)).group(1)
        designs[name] = os.path.dirname(cj)
    rows = []
    for name, gdir in sorted(designs.items()):
        g = job_metrics(gdir, f"{name}__g12d")
        edir_cands = glob.glob(f"{a.root}/**/confidence_{name}__empty_model_0.json", recursive=True)
        e = job_metrics(os.path.dirname(edir_cands[0]), f"{name}__empty") if edir_cands else None
        if not g: continue
        def gv(d, k): return d.get(k) if d else None
        bp_ipsae = gv(g, "bp_ipsae") or 0.0; bp_iptm = gv(g, "bp_iptm") or 0.0
        bh_iptm = gv(g, "bh_iptm") or 0.0; bh_iptm_e = gv(e, "bh_iptm") or 0.0
        pep_dep_iptm = bh_iptm - bh_iptm_e
        pep_dep_glob = (gv(g, "iptm") or 0.0) - (gv(e, "iptm") or 0.0)
        rows.append(dict(name=name, g_iptm=round(gv(g, "iptm") or 0, 3), bp_iptm=round(bp_iptm, 3),
                         bp_ipsae=round(bp_ipsae, 3), bh_iptm=round(bh_iptm, 3), bh_iptm_e=round(bh_iptm_e, 3),
                         pep_dep_iptm=round(pep_dep_iptm, 3), pep_dep_glob=round(pep_dep_glob, 3)))
    # composite: peptide-interface confidence, gated on positive peptide-dependence
    for r in rows:
        r["score"] = round(r["bp_ipsae"] + 0.5 * r["bp_iptm"] + 0.5 * max(0.0, r["pep_dep_iptm"]), 3)
    rows.sort(key=lambda r: -r["score"])
    cols = ["name", "score", "bp_ipsae", "bp_iptm", "g_iptm", "bh_iptm", "bh_iptm_e", "pep_dep_iptm", "pep_dep_glob"]
    with open(f"{a.root}/scored.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows: f.write("\t".join(str(r[c]) for c in cols) + "\n")
    top = rows[:a.topn]
    print(f"scored {len(rows)} designs -> {a.root}/scored.tsv ; top {len(top)}:")
    print(f"{'name':16s} {'score':>6} {'bp_ipsae':>8} {'bp_iptm':>7} {'pep_dep':>7} {'bh_g/e':>12}")
    for r in top[:25]:
        print(f"{r['name']:16s} {r['score']:>6} {r['bp_ipsae']:>8} {r['bp_iptm']:>7} {r['pep_dep_iptm']:>7}  {r['bh_iptm']}/{r['bh_iptm_e']}")
    if rows:
        import statistics as st
        print(f"\ndistribution: bp_ipsae med {st.median(r['bp_ipsae'] for r in rows):.2f} max {max(r['bp_ipsae'] for r in rows):.2f}; "
              f"pep_dep_iptm med {st.median(r['pep_dep_iptm'] for r in rows):+.2f} (>0 in {sum(r['pep_dep_iptm']>0 for r in rows)}/{len(rows)})")
    import csv as _c
    with open(f"{a.root}/top{a.topn}.csv", "w", newline="") as f:
        w = _c.writer(f); w.writerow(["name"]); [w.writerow([r["name"]]) for r in top]

if __name__ == "__main__":
    main()
