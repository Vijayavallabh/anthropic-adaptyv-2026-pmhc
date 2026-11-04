#!/usr/bin/env python3
"""Score the pocket-restrained Protenix cross-check and put it beside the Boltz 5-sample numbers.
Protenix reports per-pair ipTM in *_summary_confidence_sample_*.json (chain_pair_iptm, chain order = the
sequences order P=0,A=1,B=2,C=3). We read, per design, the binder-peptide ipTM (P-C=[0][3]) for g12d and
scram and the binder-HLA ipTM (P-A=[0][1]) for empty, averaged over samples. Derived: prot_spec = g12d-scram
(sequence specificity), prot_bh = empty P-A (tier-2, LOWER=better). A design is CORROBORATED if Protenix,
independently and restrained the same way, reproduces the Boltz directionality (g12d binds, g12d>scram,
empty low). ipTM != ipSAE in scale, so the DIRECTION is the consensus signal, not the absolute value.
Usage: score_protenix_restrained.py <out_dir> [--boltz runs/reval_genuine.tsv,runs/batch2_reval.tsv]
Run with any python3."""
import sys, os, glob, json, argparse
import numpy as np

def pair_iptm(summary_json, i, j):
    try:
        m = json.load(open(summary_json)).get("chain_pair_iptm")
        return float(m[i][j]) if m and len(m) > max(i, j) else None
    except Exception:
        return None

def mean_pair(out, job, i, j):
    vals = []
    for s in glob.glob(f"{out}/**/{job}_summary_confidence_sample_*.json", recursive=True):
        v = pair_iptm(s, i, j)
        if v is not None: vals.append(v)
    return (round(float(np.mean(vals)), 3), len(vals)) if vals else (None, 0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--boltz", default="runs/reval_genuine.tsv,runs/batch2_reval.tsv")
    a = ap.parse_args()
    R = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
    # Boltz reference (g12d / scram / bh_e), merged from the reval tables
    import csv
    bz = {}
    for p in a.boltz.split(","):
        pp = p if os.path.isabs(p) else f"{R}/{p}"
        if not os.path.exists(pp): continue
        for r in csv.DictReader(open(pp), delimiter="\t"):
            try:
                bz[r["name"]] = dict(g=float(r["g12d"]), sc=float(r["scram"]), bh=float(r["bh_e"]),
                                     spec=float(r["spec_scram"]))
            except Exception: pass
    designs = sorted({os.path.basename(d).rsplit("__", 1)[0]
                      for d in glob.glob(f"{a.out}/*__*") if os.path.isdir(d)})
    if not designs:
        designs = sorted({os.path.basename(j).split("__")[0] + "__" + os.path.basename(j).split("__")[1].split("_summary")[0]
                          for j in glob.glob(f"{a.out}/**/*_summary_confidence_sample_0.json", recursive=True)})
        designs = sorted({d.rsplit("__", 1)[0] for d in designs})
    print(f"{'design':14s}| {'PROTENIX (restrained, ipTM)':34s}| {'BOLTZ (ipSAE)':26s}| consensus")
    print(f"{'':14s}| {'g12d  scram  empty  spec  bh':34s}| {'g12d  scram  bh    spec':26s}|")
    rows = []
    for d in designs:
        pg, ng = mean_pair(a.out, f"{d}__g12d", 0, 3)
        ps, ns = mean_pair(a.out, f"{d}__scram", 0, 3)
        pe, ne = mean_pair(a.out, f"{d}__empty", 0, 1)
        pspec = round(pg - ps, 3) if (pg is not None and ps is not None) else None
        b = bz.get(d, {})
        # consensus: Protenix agrees on (a) g12d binds (P-C ipTM>=0.5), (b) spec same sign, (c) empty lower than g12d
        tags = []
        if pg is not None and pg >= 0.50: tags.append("binds")
        elif pg is not None: tags.append("weak-bind")
        if pspec is not None and b.get("spec") is not None:
            tags.append("spec-AGREE" if (pspec > 0.05) == (b["spec"] > 0.05) else "spec-DISAGREE")
        if pe is not None and pg is not None:
            tags.append("tier2-ok" if pe < pg else "tier2-FAIL(empty>=g12d)")
        def f(x): return f"{x:.2f}" if isinstance(x, float) else "  . "
        print(f"{d:14s}| {f(pg):5s} {f(ps):5s} {f(pe):5s} {f(pspec):5s} {'':4s}| "
              f"{f(b.get('g')):5s} {f(b.get('sc')):5s} {f(b.get('bh')):5s} {f(b.get('spec')):5s}| {','.join(tags)}")
        rows.append(dict(name=d, prot_g12d=pg, prot_scram=ps, prot_empty=pe, prot_spec=pspec,
                         boltz_g12d=b.get("g"), boltz_spec=b.get("spec"), boltz_bh=b.get("bh"),
                         consensus=",".join(tags), n_samp=ng))
    out_tsv = f"{a.out}/protenix_consensus.tsv"
    with open(out_tsv, "w") as fo:
        cols = ["name", "prot_g12d", "prot_scram", "prot_empty", "prot_spec", "boltz_g12d", "boltz_spec",
                "boltz_bh", "consensus", "n_samp"]
        fo.write("\t".join(cols) + "\n")
        for r in rows: fo.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    print(f"\nwrote {out_tsv}")

if __name__ == "__main__":
    main()
