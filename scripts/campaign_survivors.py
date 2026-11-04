#!/usr/bin/env python3
"""Pick a GENEROUS survivor set from the cheap selectivity scorer (panel_reval.tsv) so the
expensive/secondary axes -- peptide-contact grip (Bio.PDB per sample) and MPNN delta (24 decode
orders/GPU) -- run only on designs that could plausibly be selective, not all ~1888 panel designs.

The gate mirrors the dominant selectivity terms of assemble_final20.sel_score MINUS grip/esm/novelty
(which we have not computed yet), kept deliberately generous: a design is a survivor if it is in the
top-N by this partial sel OR clears spec_scram>=0.10 (the sel_score hard floor) OR g12d>=0.60 (a strong
binder worth the orthogonal checks). Per-lineage floors guarantee neither arm is starved. This never
decides the final ranking -- assemble does that on the full ruler; it only decides who gets the
expensive axes. Usage: campaign_survivors.py <panel_reval.tsv> --out survivors.txt [--topn 500]
"""
import argparse, csv


def fnum(v):
    try: return float(v)
    except (TypeError, ValueError): return None


def partial_sel(r):
    ss = fnum(r.get("spec_scram")) or 0.0
    pm = fnum(r.get("promisc_margin")) or 0.0
    bh = fnum(r.get("bh_e"));  bh = 1.0 if bh is None else max(0.0, min(1.0, bh))
    g = fnum(r.get("g12d")) or 0.0
    return max(0.0, ss) + 0.4 * max(0.0, pm) + 0.6 * (1.0 - bh) + 0.2 * g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("--out", default="runs/campaign/survivors.txt")
    ap.add_argument("--topn", type=int, default=500, help="top-N by partial sel (union with the floors)")
    ap.add_argument("--min-per-lineage", type=int, default=60)
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.tsv), delimiter="\t"))
    for r in rows:
        r["_ps"] = partial_sel(r)
    rows.sort(key=lambda r: r["_ps"], reverse=True)

    keep = set()
    # top-N by partial sel
    for r in rows[:a.topn]:
        keep.add(r["name"])
    # union: hard-floor clearers (never drop a genuinely selective design)
    for r in rows:
        ss = fnum(r.get("spec_scram")); g = fnum(r.get("g12d"))
        if (ss is not None and ss >= 0.10) or (g is not None and g >= 0.60):
            keep.add(r["name"])
    # per-lineage floor so neither arm is starved
    for pref in ("b3_", "nb3_"):
        lin = [r for r in rows if r["name"].startswith(pref)]
        for r in lin[:a.min_per_lineage]:
            keep.add(r["name"])

    ordered = [r["name"] for r in rows if r["name"] in keep]
    with open(a.out, "w") as o:
        o.write("\n".join(ordered) + "\n")
    nprot = sum(1 for n in ordered if n.startswith("b3_"))
    nnb = sum(1 for n in ordered if n.startswith("nb3_"))
    sstop = [fnum(r.get("spec_scram")) for r in rows if fnum(r.get("spec_scram")) is not None]
    print(f"[survivors] {len(ordered)} survivors ({nprot} protein + {nnb} nanobody) of {len(rows)} panel "
          f"-> {a.out}")
    print(f"[survivors] panel spec_scram: >=0.10: {sum(1 for v in sstop if v>=0.10)}  "
          f">=0.20: {sum(1 for v in sstop if v>=0.20)}  >=0.30: {sum(1 for v in sstop if v>=0.30)}  "
          f"max: {max(sstop) if sstop else float('nan'):.3f}")


if __name__ == "__main__":
    main()
