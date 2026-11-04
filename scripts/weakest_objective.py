#!/usr/bin/env python3
"""Weakest-objective (minimax) selectivity lens — the organizers' north star made operational:
"improve the weakest objective rather than worship the highest score."

A G12D-selective binder must discriminate the neoantigen from everything the targets SHARE. There are three
independent "reject what they share" margins, all on the same ipSAE scale (g12d binding minus a decoy binding):

  m_scram   = spec_scram            = ipSAE(g12d) - ipSAE(scramble)        # reads sequence order, not anchors
  m_promisc = promisc_margin        = ipSAE(g12d) - max(ipSAE(atic,ebna4)) # rejects other A*11:01 peptides
  m_empty   = bp - bh_e             = ipSAE(g12d) - ipSAE(empty HLA)       # peptide-DEPENDENCE (not platform)

A design's discrimination is only as good as its WEAKEST margin:  weakest = min(m_scram, m_promisc, m_empty).
Rank by `weakest`, not by the composite `sel`. A "spiker" (high sel but low weakest) leans on one objective and
is a weak discriminator; a balanced design is robustly positive on all three. This does NOT rank G12D-vs-WT (the
buried P6, un-rankable in silico and left to the bench) — it ranks how well a design rejects what the targets share.

Usage: weakest_objective.py [--ranked runs/campaign/combined_all_ranked.tsv]
                            [--names runs/campaign/combined_submission.csv] [--out runs/campaign/weakest_objective.tsv]
"""
import argparse, csv, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def f(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranked", default=f"{R}/runs/campaign/combined_all_ranked.tsv")
    ap.add_argument("--names", default=f"{R}/runs/campaign/combined_submission.csv",
                    help="CSV/txt of names to spotlight (the proposed portfolio); first column = name")
    ap.add_argument("--out", default=f"{R}/runs/campaign/weakest_objective.tsv")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.ranked), delimiter="\t"))
    out = []
    for r in rows:
        g12d = f(r.get("bp"))
        m_scram = f(r.get("spec_scram"))
        m_promisc = f(r.get("promisc_margin"))
        m_empty = round(g12d - f(r.get("bh_e")), 3)
        margins = {"scram": m_scram, "promisc": m_promisc, "empty": m_empty}
        weakest = min(margins.values())
        limiting = min(margins, key=margins.get)
        out.append({"name": r["name"], "lineage": r.get("lineage", ""), "sel": f(r.get("sel")),
                    "m_scram": m_scram, "m_promisc": m_promisc, "m_empty": m_empty,
                    "weakest": round(weakest, 3), "limiting": limiting})
    out.sort(key=lambda x: x["weakest"], reverse=True)

    cols = ["name", "lineage", "sel", "m_scram", "m_promisc", "m_empty", "weakest", "limiting"]
    with open(a.out, "w") as o:
        o.write("\t".join(cols) + "\n")
        for r in out:
            o.write("\t".join(str(r[c]) for c in cols) + "\n")

    spot = set()
    if a.names and os.path.exists(a.names):
        for ln in open(a.names):
            nm = ln.split(",")[0].strip()
            if nm and nm.lower() != "name":
                spot.add(nm)

    idx = {r["name"]: i for i, r in enumerate(out)}  # rank by weakest (0-based)
    print(f"ranked {len(out)} candidates by WEAKEST discrimination margin -> {a.out}")
    if spot:
        sub = sorted((r for r in out if r["name"] in spot), key=lambda x: x["weakest"], reverse=True)
        print(f"\nSpotlight portfolio ({len(sub)} designs) ordered by weakest margin (minimax lens):")
        print(f"  {'name':16s} {'lineage':20s} {'sel':>5} {'m_scram':>8} {'m_promisc':>9} {'m_empty':>8} {'WEAKEST':>8} {'limiting':>8}  selRank")
        for r in sub:
            print(f"  {r['name']:16s} {r['lineage']:20s} {r['sel']:>5.2f} {r['m_scram']:>8.3f} "
                  f"{r['m_promisc']:>9.3f} {r['m_empty']:>8.3f} {r['weakest']:>8.3f} {r['limiting']:>8s}  "
                  f"(weakest-rank {idx[r['name']]+1}/{len(out)})")
        bad = [r for r in sub if r["weakest"] <= 0]
        print(f"\n  designs with a NEGATIVE weakest margin (fail a shared-target rejection): "
              f"{', '.join(r['name']+'('+r['limiting']+')' for r in bad) or 'none'}")


if __name__ == "__main__":
    main()
