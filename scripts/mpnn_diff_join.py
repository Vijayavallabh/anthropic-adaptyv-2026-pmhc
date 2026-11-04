#!/usr/bin/env python3
"""Join the orthogonal MPNN differential (runs/mpnn_diff.tsv) onto the committed ranking
(runs/final20_ranked.tsv) and quantify whether the orthogonal signal CORROBORATES the
Boltz-based ranking. ENRICHMENT read-out only -- never used to gate or reorder.

Reference lines from the fail-loud positive control (seed-averaged):
  JDI/7PB2  delta ~0.83  = a >4000x G12D-SELECTIVE therapeutic TCR (ceiling)
  Poole/7OW6 delta ~0.44 = a NON-selective TCR that binds G12D AND WT (floor for 'real binder')
A design delta above the Poole line has orthogonal tier-1 support; near/below 0 has none
(not disconfirming -- the lit scan rates this a WEAK prior on a buried axis).
"""
import sys

def load_tsv(path):
    rows = []
    with open(path) as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            rows.append(dict(zip(hdr, p)))
    return rows

def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    return num / (dx * dy) if dx and dy else None

def main():
    diff = {r["design"]: r for r in load_tsv("runs/mpnn_diff.tsv")}
    rank = load_tsv("runs/final20_ranked.tsv")
    ctrl = {k: diff[k] for k in diff if diff[k]["kind"] == "control"}
    jdi = float(ctrl.get("CTRL_JDI_7pb2", {}).get("delta", "nan"))
    poole = float(ctrl.get("CTRL_Poole_7ow6", {}).get("delta", "nan"))
    print(f"CONTROLS (seed-avg):  JDI/7PB2 selective delta={jdi:+.3f}   Poole/7OW6 non-sel delta={poole:+.3f}\n")
    cols = ["rk", "name", "cls", "sel", "spec_scram", "bh_e", "promisc_margin", "mpnn_delta", "sd", "fD", "vs_Poole"]
    print("\t".join(cols))
    xs_sel, ys, xs_spec = [], [], []
    for r in rank:
        nm = r["name"]
        d = diff.get(nm)
        if not d:
            continue
        dl = float(d["delta"])
        tag = "OK" if dl >= poole else ("low" if dl >= 0 else "NEG")
        print("\t".join([r["rank"], nm, r["cls"], r["sel"], r["spec_scram"], r["bh_e"],
                          r["promisc_margin"], f"{dl:+.3f}", d["delta_sd"], d["argmax_frac_D"], tag]))
        xs_sel.append(float(r["sel"])); xs_spec.append(float(r["spec_scram"])); ys.append(dl)
    rs = spearman(xs_sel, ys); rp = spearman(xs_spec, ys)
    print(f"\nSpearman rho(mpnn_delta, sel_score)   = {rs:+.3f}  (n={len(ys)})" if rs is not None else "n/a")
    print(f"Spearman rho(mpnn_delta, spec_scram)  = {rp:+.3f}  (n={len(ys)})" if rp is not None else "n/a")
    above = sum(1 for y in ys if y >= poole); nonneg = sum(1 for y in ys if y >= 0)
    print(f"\n{above}/{len(ys)} designs >= Poole floor ({poole:+.3f});  {nonneg}/{len(ys)} non-negative.")

if __name__ == "__main__":
    main()
