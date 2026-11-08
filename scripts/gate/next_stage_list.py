#!/usr/bin/env python
"""Pick the next expansion-gate stage's design set from a results TSV, per the pre-registered
bar in docs/EXPANSION_GATE_PREREG.md. Gate TSV columns: design nG nW gmean wmean ddG ci_lo ci_hi p verdict.

Usage:
  next_stage_list.py confirm <screen_results.tsv>    # C2: <=24 most-negative ddG<0 -> confirm_cands.tsv
  next_stage_list.py deepen  <confirm_results.tsv>   # C3: ddG<=-4 & ci_hi<0        -> deepen_list.txt
  next_stage_list.py promote <deepen_results.tsv> <confirm_results.tsv>  # C4 hold @12-rep + C6 BH-FDR(m=all confirm) -> report
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
    elif mode == "promote":  # C4 hold @12-rep (this TSV) + C6 BH-FDR across the FULL confirm family
        confirm_tsv = sys.argv[3]
        conf = load(confirm_tsv)
        # C4: hold at 12-rep (ddG<=-4 AND CI excludes 0 on the negative side)
        held = {r["design"] for r in rows if r["_ddg"] <= -4.0 and r["_hi"] < 0.0}
        # C6: Benjamini-Hochberg across ALL confirm tests (the look-elsewhere family), q=0.05
        ps = sorted([(r["_p"], r["design"]) for r in conf], key=lambda x: x[0])
        m = len(ps); q = 0.05; kmax = 0
        for i, (p, d) in enumerate(ps, 1):
            if p <= q * i / m:
                kmax = i
        fdr_pass = {d for _, d in ps[:kmax]}
        promote = sorted([r for r in rows if r["design"] in held and r["design"] in fdr_pass],
                         key=lambda r: r["_ddg"])
        print(f"C4 (12-rep HOLD, ddG<=-4 & CI excl 0): {sorted(held)}")
        print(f"C6 (BH-FDR q=0.05 across m={m} CONFIRM tests): rejects {sorted(fdr_pass)}")
        print("PROMOTE candidates (C4-hold AND C6-FDR-pass; still need C5 bridge + C7 read):")
        for r in promote:
            print(f"  {r['design']:<26} 12rep ddG={r['_ddg']:+.2f} CI[{r['_lo']:+.1f},{r['_hi']:+.1f}] p={r['_p']:.3g}")
        if not promote:
            print("  (none survive — honest null; credible count stays 2)")
        # also report what each candidate did at 12-rep for transparency
        print("\nall deepened designs at 12-rep:")
        for r in sorted(rows, key=lambda r: r["_ddg"]):
            tag = []
            if r["design"] in held: tag.append("C4-hold")
            if r["design"] in fdr_pass: tag.append("C6-FDR")
            print(f"  {r['design']:<26} ddG={r['_ddg']:+.2f} CI[{r['_lo']:+.1f},{r['_hi']:+.1f}] p={r['_p']:.3g}  {' '.join(tag)}")
    else:
        sys.exit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
