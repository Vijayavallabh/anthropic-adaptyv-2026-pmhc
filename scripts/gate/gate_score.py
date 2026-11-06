#!/usr/bin/env python
"""Post-MD MM-GBSA scoring for the design selectivity gate.
Per design/system {g12d,wtmut}: build dry com/rec/lig parmtops once (ParmEd, mbondi3), cpptraj-strip
each replica production DCD to a dry NetCDF, then OpenMM GBn2 single-trajectory score each replica ->
gbsa_dry/<syst>_r<r>_scores.csv. Resume-safe (skips existing *_scores.csv).
Usage: <any-python> gate_score.py <outroot> <designs_file> [stride=5] [plat=CUDA]
"""
import sys, os, subprocess, json, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
AMBER = "/home/prachh/miniconda3/envs/ambertools"
AMBER_PY = f"{AMBER}/bin/python"
CPPTRAJ = f"{AMBER}/bin/cpptraj"
PEPGLAD_PY = "/home/prachh/miniconda3/envs/pepglad/bin/python"
BUILD_PARMED = os.path.join(HERE, "build_parmed.py")
SCORE = os.path.join(HERE, "score_gbsa.py")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def strip_dry(solv_prm, dcd, outnc):
    scr = f"parm {solv_prm}\ntrajin {dcd}\nautoimage\nstrip :WAT,Na+,Cl-\ntrajout {outnc}\nrun\nquit\n"
    r = sh([CPPTRAJ], input=scr)
    if (not os.path.exists(outnc)) or os.path.getsize(outnc) == 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:])
        raise RuntimeError(f"cpptraj strip failed: {dcd}")


def build_parmed(solv_prm, ligmask, recmask, parmdir, tag):
    os.makedirs(parmdir, exist_ok=True)
    r = sh([AMBER_PY, "-I", BUILD_PARMED, solv_prm, ligmask, recmask, parmdir, tag])
    m = re.search(r"lig_atoms=(\d+)", r.stdout)
    if not m:
        print(r.stdout[-1500:]); print(r.stderr[-1500:])
        raise RuntimeError(f"build_parmed failed: {tag}")
    return int(m.group(1))


def main():
    outroot, dfile = sys.argv[1], sys.argv[2]
    stride = sys.argv[3] if len(sys.argv) > 3 else "5"
    plat = sys.argv[4] if len(sys.argv) > 4 else "CUDA"
    designs = [l.strip() for l in open(dfile) if l.strip() and not l.startswith("#")]
    for d in designs:
        dd = os.path.join(outroot, d)
        masks = json.load(open(os.path.join(dd, "masks.json")))
        lig, rec = masks["ligmask"], masks["recmask"]
        dry = os.path.join(dd, "gbsa_dry")
        parm = os.path.join(dd, "gbsa_parm")
        os.makedirs(dry, exist_ok=True)
        for syst in ("g12d", "wtmut"):
            solv = os.path.join(dd, f"build_{syst}", f"{syst}_solv.prmtop")
            if not os.path.exists(solv):
                print(f"[score] skip {d}/{syst} (no solv prmtop)"); continue
            dcds = sorted(glob.glob(os.path.join(dd, "md", f"{syst}_r*_prod.dcd")))
            if not dcds:
                print(f"[score] skip {d}/{syst} (no DCDs yet)"); continue
            nlig = build_parmed(solv, lig, rec, parm, syst)
            com = os.path.join(parm, f"{syst}_com.parm7")
            recp = os.path.join(parm, f"{syst}_rec.parm7")
            ligp = os.path.join(parm, f"{syst}_lig.parm7")
            for dcd in dcds:
                rn = re.search(rf"{syst}_r(\d+)_prod\.dcd", dcd).group(1)
                outnc = os.path.join(dry, f"{syst}_r{rn}_dry.nc")
                outcsv = os.path.join(dry, f"{syst}_r{rn}_scores.csv")
                if os.path.exists(outcsv) and os.path.getsize(outcsv) > 0:
                    continue
                strip_dry(solv, dcd, outnc)
                rr = sh([PEPGLAD_PY, "-I", SCORE, com, recp, ligp, str(nlig), stride, plat, outcsv, outnc])
                last = rr.stdout.strip().splitlines()[-1] if rr.stdout.strip() else rr.stderr[-300:]
                print(f"[score] {d}/{syst}_r{rn}: {last}", flush=True)
        print(f"[score] {d} DONE", flush=True)


if __name__ == "__main__":
    main()
