#!/usr/bin/env python3
"""Final per-design gate/rank: merge af2ig honest gate + 3-state co-fold + triage.

af2ig pae_interaction is pMHC-MISCALIBRATED (0/80 reach the de-novo <10 even where af2ig realizes the fold
at plddt_b>80 & rmsd<2; the organizers score by co-fold ipSAE, not af2ig pae -- reference-adaptyv-binder-
protocol). So TRUST (lesson-af2ig-positive-control-must-be-denovo): af2ig plddt_binder>80 & binder_rmsd<2
= the designed fold is REALIZED. Primary binding/selectivity = co-fold bp_ipsae + peptide-dependence
(loaded>>empty, proven z=5.9). pae_int = relative tiebreaker only.

GATE: af_rmsd<2 AND af_plddt_b>80 AND bp_ipsae>=IPSAE_THR AND ROBUST-TIER-2 AND on-platform(>=0.80).
ROBUST-TIER-2 (decoy-calibrated 2026-10-27, replaces the discredited pep_dep>0): signC==1 & cohenD>4.0,
from robust_pepdep.py -- single-sample pep_dep let 56% of peptide-INDEPENDENT helix-decoys through; the
WITHIN-DESIGN consistency (loaded>empty in every diffusion sample) cut the decoy false-positive rate to 6%.
RANK: composite = bp_ipsae (interface quality / affinity proxy) + a clipped tier-2 bonus, af gates realism.
Usage: merge_gate.py --af2ig <dir> --cofold <scored.tsv> --triage <triage.tsv> --robust-t2 <t2.tsv> --out <tsv> [--ipsae-thr 0.5]
"""
import argparse, glob, csv

def read_af2ig(d):
    rows = {}
    for sc in glob.glob(f"{d}/**/*.sc", recursive=True):
        for ln in open(sc):
            if not ln.startswith("SCORE:") or "binder_aligned" in ln: continue
            p = ln.split()
            try:
                rmsd, pae, plb = float(p[1]), float(p[3]), float(p[5])
            except (ValueError, IndexError):
                continue
            rows[p[10].replace("_af2pred", "")] = {"af_rmsd": rmsd, "af_pae_int": pae, "af_plddt_b": plb}
    return rows

def read_tsv(f, keymap):
    rows = {}
    for r in csv.DictReader(open(f), delimiter="\t"):
        rows[r["name"]] = {k: (float(r[v]) if t == "f" else int(r[v]) if t == "i" else r[v]) for k, (v, t) in keymap.items()}
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--af2ig", required=True)
    ap.add_argument("--cofold", required=True)
    ap.add_argument("--triage", required=True)
    ap.add_argument("--robust-t2", required=True, dest="robust_t2")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ipsae-thr", type=float, default=0.5)
    a = ap.parse_args()
    af = read_af2ig(a.af2ig)
    co = read_tsv(a.cofold, {"bp_ipsae": ("bp_ipsae", "f")})
    t2 = read_tsv(a.robust_t2, {"pep_dep": ("pep_dep", "f"), "signC": ("signC", "f"), "cohenD": ("cohenD", "f"),
                                "bh_g": ("bh_g", "f"), "bh_e": ("bh_e", "f"), "t2pass": ("t2pass", "s")})
    tr = read_tsv(a.triage, {"seq": ("seq", "s"), "blen": ("blen", "i"), "fpep": ("fpep", "f"),
                             "onplat": ("onplat", "f"), "id_b2m": ("id_b2m", "f"), "id_hla": ("id_hla", "f")})
    rows = []
    for name, c in co.items():
        if name not in af or name not in tr or name not in t2: continue
        r = {"name": name, **af[name], **c, **t2[name], **tr[name]}
        r["t2pass"] = (r["t2pass"] == "True")
        r["gate"] = (r["af_rmsd"] < 2 and r["af_plddt_b"] > 80 and r["bp_ipsae"] >= a.ipsae_thr
                     and r["t2pass"] and r["onplat"] >= 0.80 and r["id_b2m"] < 0.5 and r["id_hla"] < 0.5)
        r["score"] = round(r["bp_ipsae"] + 0.3 * min(r["pep_dep"], 0.4) + 0.002 * r["af_plddt_b"] - 0.005 * r["af_pae_int"], 3)
        rows.append(r)
    rows.sort(key=lambda r: (-r["gate"], -r["score"]))
    cols = ["name", "gate", "score", "bp_ipsae", "cohenD", "signC", "pep_dep", "bh_g", "bh_e", "af_rmsd", "af_plddt_b", "af_pae_int", "fpep", "blen", "id_b2m", "id_hla", "seq"]
    with open(a.out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows: f.write("\t".join(str(r[c]) for c in cols) + "\n")
    npass = sum(r["gate"] for r in rows)
    print(f"merged {len(rows)} -> {a.out} ; GATE-PASS {npass}")
    print(f"{'name':16s} {'gate':>4} {'score':>6} {'bp_ipsae':>8} {'cohenD':>6} {'signC':>5} {'af_rmsd':>7} {'af_plddt':>8} {'bh_g/e':>11}")
    for r in rows[:30]:
        print(f"{r['name']:16s} {str(r['gate']):>4} {r['score']:>6} {r['bp_ipsae']:>8} {r['cohenD']:>6} {r['signC']:>5} {r['af_rmsd']:>7} {r['af_plddt_b']:>8}  {r['bh_g']}/{r['bh_e']}")

if __name__ == "__main__":
    main()
