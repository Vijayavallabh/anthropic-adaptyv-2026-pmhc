#!/usr/bin/env python
"""Bootstrap ΔΔG(G12D − WTmut) per design for the MM-GBSA selectivity gate.

ΔΔG < 0  => design binds the G12D neoantigen tighter than WT (selective on the deciding axis).
Replica-level bootstrap CI (replica = the unit, as in calibration). Calibration anchors:
clean positive ΔΔG = -4.36 [-7.0,-1.6] (G12D tighter); null WT-vs-WT CI includes 0; noise floor
≈1.9 kcal/mol -> trust a selective call only when CI excludes 0 AND |ΔΔG| clears ~4 kcal/mol.

Usage: <any-python> gate_analyze.py <outroot> <designs_file> [out_tsv]
"""
import sys, os, glob, csv, json
import numpy as np

np.random.seed(42)
EQ = 50   # drop frames with index < 50 (first 0.5 ns), matching calibration


def load_sys(drydir, prefix):
    reps = []
    for f in sorted(glob.glob(os.path.join(drydir, f"{prefix}_r*_scores.csv"))):
        dg = [float(r['dG_bind']) for r in csv.DictReader(open(f)) if int(r['frame']) >= EQ]
        if dg:
            reps.append(np.array(dg))
    return reps


def sysmean(reps):
    return float(np.mean([r.mean() for r in reps])) if reps else float('nan')


def boot_rep(A, B, n=20000):
    a = np.array([r.mean() for r in A])
    b = np.array([r.mean() for r in B])
    out = np.empty(n)
    for i in range(n):
        out[i] = a[np.random.randint(0, len(a), len(a))].mean() - b[np.random.randint(0, len(b), len(b))].mean()
    return out


def main():
    outroot, dfile = sys.argv[1], sys.argv[2]
    out_tsv = sys.argv[3] if len(sys.argv) > 3 else os.path.join(outroot, "gate_results.tsv")
    designs = [l.strip() for l in open(dfile) if l.strip() and not l.startswith("#")]
    rows = []
    for d in designs:
        dry = os.path.join(outroot, d, "gbsa_dry")
        G, W = load_sys(dry, "g12d"), load_sys(dry, "wtmut")
        if not G or not W:
            rows.append(dict(design=d, nG=len(G), nW=len(W), ddG=float('nan'), verdict="NO_DATA"))
            continue
        ddG = sysmean(G) - sysmean(W)
        bl = boot_rep(G, W)
        ci = np.percentile(bl, [2.5, 97.5])
        p = 2 * min((bl < 0).mean(), (bl > 0).mean())
        excl = ci[1] < 0 or ci[0] > 0
        if excl and ddG < 0 and abs(ddG) >= 4.0:
            verd = "G12D-SELECTIVE"
        elif excl and ddG < 0:
            verd = "g12d-favored(sub-floor)"
        elif excl and ddG > 0:
            verd = "WT-favored"
        else:
            verd = "null(CI-incl-0)"
        rows.append(dict(design=d, nG=len(G), nW=len(W),
                         gmean=round(sysmean(G), 2), wmean=round(sysmean(W), 2),
                         ddG=round(float(ddG), 2), ci_lo=round(float(ci[0]), 2),
                         ci_hi=round(float(ci[1]), 2), p=round(float(p), 3), verdict=verd))
    rows.sort(key=lambda r: (r['ddG'] if r['ddG'] == r['ddG'] else 1e9))
    cols = ["design", "nG", "nW", "gmean", "wmean", "ddG", "ci_lo", "ci_hi", "p", "verdict"]
    with open(out_tsv, "w") as o:
        o.write("\t".join(cols) + "\n")
        for r in rows:
            o.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    json.dump(rows, open(out_tsv.replace(".tsv", ".json"), "w"), indent=2)
    print("\t".join(cols))
    for r in rows:
        print("\t".join(str(r.get(c, "")) for c in cols))
    print(f"\n[gate_analyze] wrote {out_tsv}")
    print("Anchor: calibration clean ΔΔG=-4.36 [-7.0,-1.6] (G12D tighter); null CI incl 0; noise floor ~1.9 kcal/mol")


if __name__ == "__main__":
    main()
