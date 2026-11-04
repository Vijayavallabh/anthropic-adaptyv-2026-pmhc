#!/usr/bin/env python3
"""Stage D->E glue: from triage_g12d.tsv (lenient single-state g12d ipSAE ranking), build the
per-lineage panel name list for the expensive 5-sample 6-state panel (funnel_panel.sh).

Proteins (b3_*) and nanobodies (nb3_*) are ranked and capped SEPARATELY so the scarcer protein
arm is not crowded out: assemble_final20 caps 6/lineage, proteins are the novelty-friendly lineage,
and they are the most vulnerable to single-state triage noise. Triage OVER-estimates (lesson:
cofold-pepdep-single-sample-is-noise) so the cut here is deliberately generous -- the 6-state panel
is the real gate. Default keeps ALL foldable proteins and a generous nanobody top-K.

Usage:
  funnel_select_panel.py [--tsv runs/campaign/triage_g12d.tsv] [--out runs/campaign/panel_select.txt]
                         [--kprot N] [--knb N] [--min-g12d X]
"""
import argparse, csv, statistics as st


def dist(label, vals):
    if not vals:
        print(f"  {label}: (none)"); return
    vals = sorted(vals, reverse=True)
    n = len(vals)
    print(f"  {label}: n={n} max={vals[0]:.3f} median={st.median(vals):.3f} "
          f"p90={vals[int(n*0.10)]:.3f} min={vals[-1]:.3f}")
    for c in (0.3, 0.4, 0.5, 0.6, 0.7):
        print(f"       g12d>={c}: {sum(1 for v in vals if v >= c)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default="runs/campaign/triage_g12d.tsv")
    ap.add_argument("--out", default="runs/campaign/panel_select.txt")
    ap.add_argument("--kprot", type=int, default=888, help="max proteins (default: all foldable)")
    ap.add_argument("--knb", type=int, default=1000, help="max nanobodies")
    ap.add_argument("--min-g12d", type=float, default=0.0, help="drop below this triage g12d ipSAE")
    a = ap.parse_args()

    rows = [r for r in csv.DictReader(open(a.tsv), delimiter="\t")
            if r.get("g12d") not in (None, "", "None")]
    for r in rows:
        r["_g"] = float(r["g12d"])
    prot = sorted([r for r in rows if not r["name"].startswith("nb3")], key=lambda r: r["_g"], reverse=True)
    nb = sorted([r for r in rows if r["name"].startswith("nb3")], key=lambda r: r["_g"], reverse=True)

    print(f"[select] triage rows={len(rows)}  proteins={len(prot)}  nanobodies={len(nb)}")
    dist("protein  (b3_) ", [r["_g"] for r in prot])
    dist("nanobody (nb3_)", [r["_g"] for r in nb])

    psel = [r for r in prot if r["_g"] >= a.min_g12d][:a.kprot]
    nsel = [r for r in nb if r["_g"] >= a.min_g12d][:a.knb]
    names = [r["name"] for r in psel] + [r["name"] for r in nsel]
    with open(a.out, "w") as o:
        o.write("\n".join(names) + "\n")

    pc = f"{psel[-1]['_g']:.3f}" if psel else "n/a"
    nc = f"{nsel[-1]['_g']:.3f}" if nsel else "n/a"
    print(f"[select] PANEL SET: {len(psel)} protein (cut g12d>={pc}) + "
          f"{len(nsel)} nanobody (cut g12d>={nc}) = {len(names)} designs -> {a.out}")
    print(f"[select] est panel cofold ~{0.269*len(names)/60:.1f}h "
          f"(6 states x 5 samples @ ~112 samples/min on 6 GPUs)")
    print(f"[select] NEXT: bash scripts/funnel_panel.sh {a.out} runs/campaign/foldable.csv")


if __name__ == "__main__":
    main()
