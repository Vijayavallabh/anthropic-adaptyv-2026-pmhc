#!/usr/bin/env python
"""C5 dynamic pose-realism: is the native Asp6<->HLA-Arg114 salt bridge maintained THROUGH the
G12D MD, or does the binder pull Asp6 out of the groove during dynamics (systematic over-dock bias
that replication cannot fix)? Measures the min carboxylate(Asp6 386 OD1/OD2)-to-guanidinium
(Arg114 114 NH1/NH2/NE) distance per frame across all g12d replica trajectories and reports the
fraction of frames with the bridge intact (<= cutoff). Pre-registered C5 bar: >= 80% intact.

Residue map (constant across designs; pMHC block = 390 residues, written first): Asp6 = resid 386,
Arg114 = resid 114 (verified: g12d_clean.pdb res 386=ASP, 114=ARG). WTmut has Gly6 (no carboxylate)
so C5 is measured on the G12D state only.

Usage: <python> c5_dynamic_bridge.py <design> <confirm_outroot> [cutoff=4.5]
"""
import sys, os, subprocess, glob, tempfile

CPPTRAJ = "/home/prachh/miniconda3/envs/ambertools/bin/cpptraj"
PAIRS = [("OD1", "NH1"), ("OD1", "NH2"), ("OD1", "NE"),
         ("OD2", "NH1"), ("OD2", "NH2"), ("OD2", "NE")]


def main():
    design = sys.argv[1]
    outroot = sys.argv[2]
    cutoff = float(sys.argv[3]) if len(sys.argv) > 3 else 4.5
    dd = os.path.join(outroot, design)
    parm = os.path.join(dd, "gbsa_parm", "g12d_com.parm7")
    trajs = sorted(glob.glob(os.path.join(dd, "gbsa_dry", "g12d_r*_dry.nc")))
    if not os.path.exists(parm) or not trajs:
        print(f"{design}: MISSING parm/trajs (parm={os.path.exists(parm)}, ntraj={len(trajs)})")
        sys.exit(1)
    datf = tempfile.NamedTemporaryFile(suffix=".dat", delete=False).name
    lines = [f"parm {parm}"]
    for t in trajs:
        lines.append(f"trajin {t}")
    for i, (o, n) in enumerate(PAIRS, 1):
        lines.append(f"distance d{i} :386@{o} :114@{n} noimage")
    lines.append("run")
    lines.append(f"writedata {datf} " + " ".join(f"d{i}" for i in range(1, len(PAIRS) + 1)))
    inp = "\n".join(lines) + "\n"
    r = subprocess.run([CPPTRAJ], input=inp, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{design}: cpptraj failed\n{r.stderr[-800:]}")
        sys.exit(1)
    # parse: col0 = frame, cols1..6 = the 6 pair distances; per-frame min = bridge distance
    nframes = 0; intact = 0; mind_all = []
    with open(datf) as fh:
        for ln in fh:
            if ln.startswith("#") or not ln.strip():
                continue
            vals = ln.split()
            try:
                dists = [float(x) for x in vals[1:1 + len(PAIRS)]]
            except ValueError:
                continue
            m = min(dists)
            mind_all.append(m); nframes += 1
            if m <= cutoff:
                intact += 1
    os.unlink(datf)
    if nframes == 0:
        print(f"{design}: no frames parsed"); sys.exit(1)
    frac = intact / nframes
    import statistics as st
    print(f"{design}: frames={nframes} (over {len(trajs)} g12d replicas)  "
          f"bridge min-dist median={st.median(mind_all):.2f}A mean={st.mean(mind_all):.2f}A  "
          f"intact(<= {cutoff}A)={frac*100:.1f}%  -> C5 {'PASS' if frac>=0.80 else 'FAIL'} (bar 80%)")
    return frac


if __name__ == "__main__":
    main()
