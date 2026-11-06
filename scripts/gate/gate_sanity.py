#!/usr/bin/env python
"""Single-frame ΔG_bind SANITY on a prepped system (NO MD) — validates masks/atom-order/split
before committing full MD. Strips the solvated inpcrd to a 1-frame dry NetCDF, builds the dry
com/rec/lig parmtops, and scores one frame. Expect a SANE negative ΔG_bind (the calibration crystal
single-frame was -17.6 kcal/mol; equilibrated frames -60..-74). A large positive value = a bug.

Usage: <any-python> gate_sanity.py <outroot> <design> [syst=g12d]
"""
import sys, os, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
AMBER = "/home/prachh/miniconda3/envs/ambertools"
AMBER_PY = f"{AMBER}/bin/python"
CPPTRAJ = f"{AMBER}/bin/cpptraj"
PEPGLAD = "/home/prachh/miniconda3/envs/pepglad/bin/python"


def sh(c, **k):
    return subprocess.run(c, capture_output=True, text=True, **k)


def main():
    outroot, d = sys.argv[1], sys.argv[2]
    syst = sys.argv[3] if len(sys.argv) > 3 else "g12d"
    dd = os.path.join(outroot, d)
    masks = json.load(open(os.path.join(dd, "masks.json")))
    solv = os.path.join(dd, f"build_{syst}", f"{syst}_solv.prmtop")
    inp = os.path.join(dd, f"build_{syst}", f"{syst}_solv.inpcrd")
    san = os.path.join(dd, "sanity")
    os.makedirs(san, exist_ok=True)
    nc = os.path.join(san, f"{syst}_1frame_dry.nc")
    scr = f"parm {solv}\ntrajin {inp}\nautoimage\nstrip :WAT,Na+,Cl-\ntrajout {nc}\nrun\nquit\n"
    r = sh([CPPTRAJ], input=scr)
    assert os.path.exists(nc) and os.path.getsize(nc) > 0, f"cpptraj failed:\n{r.stdout[-1200:]}\n{r.stderr[-1200:]}"
    r = sh([AMBER_PY, "-I", os.path.join(HERE, "build_parmed.py"),
            solv, masks["ligmask"], masks["recmask"], san, syst])
    print(r.stdout.strip())
    m = re.search(r"lig_atoms=(\d+)", r.stdout)
    assert m, f"build_parmed failed:\n{r.stderr[-1500:]}"
    nlig = m.group(1)
    com = os.path.join(san, f"{syst}_com.parm7")
    rec = os.path.join(san, f"{syst}_rec.parm7")
    lig = os.path.join(san, f"{syst}_lig.parm7")
    r = sh([PEPGLAD, "-I", os.path.join(HERE, "score_gbsa.py"),
            com, rec, lig, nlig, "1", "CUDA", os.path.join(san, f"{syst}_sanity.csv"), nc])
    print(r.stdout.strip() or r.stderr[-1800:])
    print("\nSANE if ΔG_bind is NEGATIVE and roughly -10..-80 kcal/mol (calibration crystal 1-frame = -17.6).")


if __name__ == "__main__":
    main()
