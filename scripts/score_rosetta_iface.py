#!/usr/bin/env python3
"""RANKER CALIBRATION (rung 1, Rosetta endpoint): quantify the G12D-vs-WT physics signal on the bound
TCR complexes. Since only peptide P6 differs, the G12D-WT differential of ANY peptide-partner energy
reduces to P6's differential, so we score P6's ref2015 2-body interaction energies (relaxed, N replicas):
  E_P6_TCR  = P6 <-> all TCR residues (chains D,E)      [direct TCR contact -- expected WEAK: D6 points IN]
  E_P6_HLA  = P6 <-> all HLA residues (chain A)         [incl the D6-Arg114 salt bridge]
  E_P6_R114 = P6 <-> HLA Arg114                         [the buried salt bridge -- expected STRONG for Asp]
reported as weighted total + fa_elec component. Compares parental TCR (real 7OW6 vs 7OW5; controlled
7OW6->Gly6) and JDI TCR (7PB2 vs controlled Gly6). Lesson from the smoke test: the selectivity is an
intra-pMHC ordering effect, not a TCR-contact effect -> endpoint interface dG is weak; two-state FEP is
the rigorous ranker (reserved for the final handful). Run: /home/prachh/v/.venv-rosetta/bin/python <this>
"""
import glob, os, statistics as st
import pyrosetta
from pyrosetta.rosetta.protocols.relax import FastRelax
from pyrosetta.rosetta.core.scoring import EMapVector, fa_elec

pyrosetta.init("-mute all -ignore_unrecognized_res -ignore_zero_occupancy false "
               "-relax:constrain_relax_to_start_coords -relax:coord_constrain_sidechains "
               "-relax:ramp_constraints false -ex1 -ex2 -default_repeats 1")
SF = pyrosetta.create_score_function("ref2015")
NREP = 3
BOUND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/targets/bound")

def interaction(pose, i, j):
    e = EMapVector()
    SF.eval_ci_2b(pose.residue(i), pose.residue(j), pose, e)
    SF.eval_cd_2b(pose.residue(i), pose.residue(j), pose, e)
    w = SF.weights()
    return e.dot(w), e[fa_elec] * w[fa_elec]

def measure(pose):
    SF(pose); pi = pose.pdb_info()
    c6 = pi.pdb2pose("C", 6); r114 = pi.pdb2pose("A", 114)
    tcr = [i for i in range(1, pose.total_residue() + 1) if pi.chain(i) in ("D", "E")]
    hla = [i for i in range(1, pose.total_residue() + 1) if pi.chain(i) == "A"]
    def s(group):
        t = e = 0.0
        for j in group:
            a, b = interaction(pose, c6, j); t += a; e += b
        return t, e
    tt, te = s(tcr); ht, he = s(hla)
    rt, re_ = interaction(pose, c6, r114) if r114 else (float("nan"), float("nan"))
    return dict(E_P6_TCR=tt, E_P6_TCR_elec=te, E_P6_HLA=ht, E_P6_HLA_elec=he, E_P6_R114=rt, E_P6_R114_elec=re_)

def run(pdb):
    base = pyrosetta.pose_from_file(pdb); fr = FastRelax(SF, 1); reps = []
    for _ in range(NREP):
        p = base.clone(); fr.apply(p); reps.append(measure(p))
    return {k: (st.mean([r[k] for r in reps]), st.pstdev([r[k] for r in reps]) if NREP > 1 else 0.0) for k in reps[0]}

rows = {}
for pdb in sorted(glob.glob(f"{BOUND}/*.pdb")):
    nm = os.path.basename(pdb)[:-4]
    try:
        rows[nm] = run(pdb); a = rows[nm]
        print(f"[{nm}] P6-TCR={a['E_P6_TCR'][0]:.2f}(elec {a['E_P6_TCR_elec'][0]:.2f})  "
              f"P6-HLA={a['E_P6_HLA'][0]:.2f}(elec {a['E_P6_HLA_elec'][0]:.2f})  "
              f"P6-R114={a['E_P6_R114'][0]:.2f}(elec {a['E_P6_R114_elec'][0]:.2f})", flush=True)
    except Exception as e:
        print(f"[{nm}] FAIL {e}", flush=True)

def delta(hi, lo, key):
    if hi in rows and lo in rows:
        d = rows[lo][key][0] - rows[hi][key][0]   # energy lower=better -> (wt - g12d)>0 means G12D favored
        ps = (rows[hi][key][1] ** 2 + rows[lo][key][1] ** 2) ** 0.5
        return d, (d / ps if ps > 1e-9 else float("inf"))
    return float("nan"), float("nan")

print("\n=== DIFFERENTIALS (G12D-favored if >0; z=delta/pooledSD) ===")
for tag, hi, lo in [("parental g12d vs wt(7OW5 crystal)", "parental_g12d", "parental_wt"),
                    ("parental g12d vs wt(controlled Gly6)", "parental_g12d", "parental_wtins"),
                    ("JDI g12d vs wt(controlled Gly6)", "jdi_g12d", "jdi_wtins")]:
    for key in ["E_P6_TCR", "E_P6_TCR_elec", "E_P6_HLA", "E_P6_HLA_elec", "E_P6_R114", "E_P6_R114_elec"]:
        d, z = delta(hi, lo, key)
        print(f"  {tag:38s} {key:16s} dG12D-fav={d:+.2f}  z={z:+.2f}")
