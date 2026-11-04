#!/usr/bin/env python3
"""Robust tier-2 (peptide-dependence) metric from a 3-state co-fold, calibrated on a should-fail decoy.

WHY (decoy control result, 2026-10-27): single-sample pep_dep = bh_iptm(g12d) - bh_iptm(empty) is a WEAK
tier-2 discriminator (AUC 0.84 design-vs-helix-decoy) with a fat false-positive tail -- 27/48 peptide-
INDEPENDENT helix-reader decoys pass pep_dep>0. The confound: removing the peptide destabilises the whole
pMHC, so ANY binder tends to score higher binder-HLA ipTM loaded-vs-empty. The RIGHT statistic is the
WITHIN-DESIGN CONSISTENCY across the diffusion samples: a true peptide-gripper loses binder-HLA confidence
EVERY sample when the peptide is removed (sign-consistency 1.0, large Cohen's d); a wall-gripper's sign
wobbles (decoy median signC 0.40, Cohen-d ~0). That lifts AUC to 0.95. Decoy null p95 Cohen-d = 4.0.

TIER-2 GATE (decoy-calibrated, VARIANCE-ROBUST): signC == 1.0 (loaded>empty in ALL samples) AND
pep_dep >= 0.05. NB: raw Cohen's d is NOT used as the gate -- it EXPLODES when the diffusion samples are
near-identical (nanobody co-folds gave cohenD 5e5 at ~0 variance), so it is not comparable across runs.
We report a FLOORED cohenD (sd floored at 0.02 = realistic Boltz-ipTM sample noise) as a tiebreaker only.
Decoy null (48 helix-readers): signC==1 reaches pep_dep 0.37 -> the gate is a ~90%-specific ENRICHER
(12% irreducible FP from helix-readers that are consistently peptide-STABILISED), NOT a perfect classifier;
residual FP is handled by the conjunction with bp_ipsae (decoy median 0.21) + ESM monomer + orthogonal checks.
Run with ambertools python (numpy). Usage: robust_pepdep.py <cofold_out_dir> [--out tsv] [--pepfloor 0.05]
"""
import argparse, glob, json, re, os
import numpy as np

def chain_order(pdb):
    o, s = [], set()
    for ln in open(pdb):
        if ln.startswith(("ATOM", "HETATM")):
            c = ln[21]
            if c not in s: s.add(c); o.append(c)
    return o

def pair_iptm(pair, i, j):
    a = pair.get(str(i), {}).get(str(j)); b = pair.get(str(j), {}).get(str(i))
    v = [x for x in (a, b) if isinstance(x, (int, float))]
    return max(v) if v else None

def bh_series(name, state, d):
    """binder(P)<->HLA(A) ipTM across all available diffusion samples of one state."""
    xs = []
    for m in range(8):
        c = f"{d}/confidence_{name}__{state}_model_{m}.json"; p = f"{d}/{name}__{state}_model_{m}.pdb"
        if not (os.path.exists(c) and os.path.exists(p)): continue
        idx = {ch: k for k, ch in enumerate(chain_order(p))}
        if {"P", "A"} <= set(idx):
            v = pair_iptm(json.load(open(c)).get("pair_chains_iptm", {}), idx["P"], idx["A"])
            if v is not None: xs.append(v)
    return np.array(xs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default=None)
    ap.add_argument("--pepfloor", type=float, default=0.05)
    ap.add_argument("--sd-floor", type=float, default=0.02)
    a = ap.parse_args()
    cjs = glob.glob(f"{a.root}/**/confidence_*__g12d_model_0.json", recursive=True)
    rows = []
    for cj in cjs:
        name = re.match(r"confidence_(.+)__g12d_model_0\.json", os.path.basename(cj)).group(1)
        g = bh_series(name, "g12d", os.path.dirname(cj))
        ej = glob.glob(f"{a.root}/**/confidence_{name}__empty_model_0.json", recursive=True)
        if not ej or not len(g): continue
        e = bh_series(name, "empty", os.path.dirname(ej[0]))
        if not len(e): continue
        sd = max(float(np.sqrt((g.var() + e.var()) / 2)), a.sd_floor)  # FLOOR sd -> cohenD can't explode
        signC = float((g > e.mean()).mean())
        pep = float(g.mean() - e.mean())
        cohenD = pep / sd  # floored-sd diagnostic/tiebreaker, NOT the gate
        rows.append(dict(name=name, nsg=len(g), nse=len(e), bh_g=round(float(g.mean()), 3),
                         bh_e=round(float(e.mean()), 3), pep_dep=round(pep, 3),
                         signC=round(signC, 2), cohenD=round(cohenD, 2),
                         t2pass=bool(signC == 1.0 and pep >= a.pepfloor)))
    rows.sort(key=lambda r: (-r["t2pass"], -r["pep_dep"]))
    out = a.out or f"{a.root}/robust_t2.tsv"
    cols = ["name", "nsg", "nse", "bh_g", "bh_e", "pep_dep", "signC", "cohenD", "t2pass"]
    with open(out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows: f.write("\t".join(str(r[c]) for c in cols) + "\n")
    cd = [r["cohenD"] for r in rows]
    npass = sum(r["t2pass"] for r in rows)
    print(f"robust tier-2: {len(rows)} designs -> {out} ; T2-PASS {npass} (signC==1 & pep_dep>={a.pepfloor})")
    if rows:
        print(f"cohenD dist: med {np.median(cd):+.1f} p90 {np.percentile(cd,90):+.1f} p95 {np.percentile(cd,95):+.1f} max {max(cd):+.1f}")
        print(f"{'name':16s} {'signC':>5} {'cohenD':>6} {'pep_dep':>7} {'bh_g/e':>11} {'t2':>4}")
        for r in rows[:25]:
            print(f"{r['name']:16s} {r['signC']:>5} {r['cohenD']:>6} {r['pep_dep']:>7} {r['bh_g']}/{r['bh_e']:<5} {str(r['t2pass']):>4}")

if __name__ == "__main__":
    main()
