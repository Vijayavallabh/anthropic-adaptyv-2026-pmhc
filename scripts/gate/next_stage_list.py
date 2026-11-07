#!/usr/bin/env python
"""Pick the next expansion-gate stage's design set from a results TSV, per the pre-registered
bar in docs/EXPANSION_GATE_PREREG.md. Gate TSV columns: design nG nW gmean wmean ddG ci_lo ci_hi p verdict.

Usage:
  next_stage_list.py confirm <screen_results.tsv>    # C2: <=24 most-negative ddG<0 -> confirm_cands.tsv
  next_stage_list.py deepen  <confirm_results.tsv>   # C3: ddG<=-4 & ci_hi<0        -> deepen_list.txt
  next_stage_list.py promote <deepen_results.tsv>    # C4+C6: hold at 12-rep + BH-FDR q=0.05 -> report
"""
import sys, csv, os
P = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
EXP = f"{P}/runs/gate_expand"
PRIOR = f"{P}/runs/gate_prior/charge_sensor_prior.tsv"


def load(tsv):
    rows = []
    with open(tsv) as fh:
        r = csv.DictReader(fh, delimiter="\t")
        for d in r:
            try:
                d["_ddg"] = float(d["ddG"]); d["_hi"] = float(d["ci_hi"])
                d["_lo"] = float(d["ci_lo"]); d["_p"] = float(d.get("p", "nan"))
            except Exception:
                continue
            rows.append(d)
    return rows


def pose_map():
    m = {}
    for d in csv.DictReader(open(PRIOR), delimiter="\t"):
        m[d["name"]] = d["pose"]
    return m


def main():
    mode, tsv = sys.argv[1], sys.argv[2]
    rows = load(tsv)
    if mode == "confirm":  # C2: rank-based, cap 24, ddG<0
        cand = sorted([r for r in rows if r["_ddg"] < 0], key=lambda r: r["_ddg"])[:24]
        pm = pose_map()
        with open(f"{EXP}/confirm_cands.tsv", "w") as fh:
            fh.write("name\tddG_screen\tpose\n")
            for r in cand:
                fh.write(f"{r['design']}\t{r['_ddg']:.2f}\t{pm.get(r['design'],'')}\n")
        print(f"C2: {len(cand)} designs -> confirm (most-negative screen ddG):")
        for r in cand:
            print(f"  {r['design']:<26} screen ddG={r['_ddg']:+.2f}")
    elif mode == "deepen":  # C3: ddG<=-4 AND ci_hi<0
        cand = sorted([r for r in rows if r["_ddg"] <= -4.0 and r["_hi"] < 0.0], key=lambda r: r["_ddg"])
        with open(f"{EXP}/deepen_list.txt", "w") as fh:
            for r in cand:
                fh.write(r["design"] + "\n")
        print(f"C3: {len(cand)}/{len(rows)} designs pass confirm (ddG<=-4 & CI excludes 0) -> deepen:")
        for r in cand:
            print(f"  {r['design']:<26} ddG={r['_ddg']:+.2f} CI[{r['_lo']:+.1f},{r['_hi']:+.1f}] p={r['_p']:.3g}")
        if not cand:
            print("  (none — honest null at confirm; credible count stays 2)")
    elif mode == "promote":  # C4 hold + C6 BH-FDR
        held = [r for r in rows if r["_ddg"] <= -4.0 and r["_hi"] < 0.0]
        # Benjamini-Hochberg across everything deepened
        ps = sorted([(r["_p"], r) for r in rows], key=lambda x: x[0])
        m = len(ps); q = 0.05; passed = set()
        for i, (p, r) in enumerate(ps, 1):
            if p <= q * i / m:
                passed = set(id(rr) for _, rr in ps[:i])
        promote = [r for r in held if id(r) in passed]
        print(f"C4: {len(held)}/{len(rows)} HOLD at 12-rep (ddG<=-4 & CI excludes 0)")
        print(f"C6: BH-FDR q=0.05 across m={m} deepened; adjusted-pass set size {len(passed)}")
        print("PROMOTE (hold AND FDR-pass):")
        for r in sorted(promote, key=lambda r: r["_ddg"]):
            print(f"  {r['design']:<26} ddG={r['_ddg']:+.2f} CI[{r['_lo']:+.1f},{r['_hi']:+.1f}] p={r['_p']:.3g}")
        if not promote:
            print("  (none survive — honest null; credible count stays 2)")
    else:
        sys.exit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
