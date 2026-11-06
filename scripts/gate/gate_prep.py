#!/usr/bin/env python
"""Prep a design:pMHC co-fold pose for the MM-GBSA G12D-vs-WT selectivity gate.

Mirrors the VALIDATED calibration pipeline (runs/campaign/calibration, Task 2): from ONE co-fold
pose it builds TWO matched solvated Amber systems --
  * design:G12D   = peptide VVVGADGVGK (Asp6), the co-folded state
  * design:WTmut  = identical scaffold with Asp6 -> Gly6 (backbone kept, sidechain dropped)
so that  ddG = dG_bind(design:G12D) - dG_bind(design:WTmut)  is the EXACT clean same-scaffold
single-residue contrast that passed calibration (clean ddG = -4.36 kcal/mol, 95% CI [-7.0,-1.6],
p=0.002; null WT-vs-WT CI includes 0; noise floor ~1.9 kcal/mol).

Ligand = pMHC (chains A,B,C; written FIRST so it occupies topology residues 1..npMHC -> score_gbsa
splits ligand = first NLIG atoms). Receptor = binder (every other chain, e.g. P).

Usage:  <pepglad-python> gate_prep.py <design> <g12d_pose.pdb> <outroot>
Writes: <outroot>/<design>/{g12d,wtmut}_{raw,clean}.pdb, build_{g12d,wtmut}/*_solv.{prmtop,inpcrd},
        masks.json {npMHC_res,nbinder_res,binder_chains,ligmask,recmask}.
"""
import sys, os, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
AMBER = "/home/prachh/miniconda3/envs/ambertools"
PDB4AMBER = f"{AMBER}/bin/pdb4amber"
PYO = "/home/prachh/miniconda3/envs/pepglad/bin/python"
BUILD_MD = os.path.join(HERE, "build_md.py")
AA3 = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE',
       'PRO','SER','THR','TRP','TYR','VAL'}
PMHC = ['A', 'B', 'C']           # HLA, b2m, peptide (co-fold chain order)


def atoms_by_chain(src):
    by = {}
    for ln in open(src):
        if not ln.startswith("ATOM"):
            continue
        if ln[17:20].strip() not in AA3:
            continue
        if ln[16] not in (' ', 'A'):          # keep blank/altloc-A only
            continue
        by.setdefault(ln[21], []).append(ln)
    return by


def nres(lines):
    return len({int(ln[22:26]) for ln in lines})


def mutate_C6_D2G(c_lines):
    """Peptide chain C residue 6: ASP -> GLY. Keep backbone N,CA,C,O; drop sidechain; rename."""
    KEEP = {'N', 'CA', 'C', 'O'}
    out, seen6 = [], False
    for ln in c_lines:
        if int(ln[22:26]) == 6:
            assert ln[17:20].strip() == 'ASP', f"C res6 = {ln[17:20]} (expected ASP = G12D peptide)"
            seen6 = True
            if ln[12:16].strip() not in KEEP:
                continue
            ln = ln[:17] + 'GLY' + ln[20:]
        out.append(ln)
    assert seen6, "peptide chain C has no residue 6"
    return out


def write_pdb(blocks, path):
    """Each block = one chain's ATOM lines; TER between chains (prevents cross-chain bonding)."""
    with open(path, 'w') as o:
        for blk in blocks:
            o.writelines(blk)
            o.write("TER\n")
        o.write("END\n")


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def pdb4amber(raw, clean):
    r = sh([PDB4AMBER, "-i", raw, "-o", clean])
    if (not os.path.exists(clean)) or os.path.getsize(clean) == 0:
        print(r.stdout[-2000:]); print(r.stderr[-2000:]); sys.exit(f"pdb4amber failed: {raw}")


def build_md(tag, clean, outdir):
    os.makedirs(outdir, exist_ok=True)
    r = sh([PYO, "-I", BUILD_MD, tag, clean, "", outdir])
    print(r.stdout[-1800:])
    prm = os.path.join(outdir, f"{tag}_solv.prmtop")
    if (not os.path.exists(prm)) or os.path.getsize(prm) == 0:
        print(r.stderr[-2500:]); sys.exit(f"build_md failed: {tag}")
    return prm


def main():
    design, pose, outroot = sys.argv[1], sys.argv[2], sys.argv[3]
    d = os.path.join(outroot, design)
    os.makedirs(d, exist_ok=True)
    by = atoms_by_chain(pose)
    for c in PMHC:
        assert c in by, f"{design}: missing pMHC chain {c} in {pose} (chains={sorted(by)})"
    binder_ch = sorted(c for c in by if c not in PMHC)
    assert binder_ch, f"{design}: no binder chain (chains={sorted(by)})"
    npMHC = sum(nres(by[c]) for c in PMHC)
    nbind = sum(nres(by[c]) for c in binder_ch)

    pmhc_g_blocks = [by['A'], by['B'], by['C']]
    pmhc_w_blocks = [by['A'], by['B'], mutate_C6_D2G(by['C'])]
    binder_blocks = [by[c] for c in binder_ch]

    g_raw, w_raw = os.path.join(d, "g12d_raw.pdb"), os.path.join(d, "wtmut_raw.pdb")
    g_cln, w_cln = os.path.join(d, "g12d_clean.pdb"), os.path.join(d, "wtmut_clean.pdb")
    write_pdb(pmhc_g_blocks + binder_blocks, g_raw)
    write_pdb(pmhc_w_blocks + binder_blocks, w_raw)
    pdb4amber(g_raw, g_cln)
    pdb4amber(w_raw, w_cln)
    build_md("g12d", g_cln, os.path.join(d, "build_g12d"))
    build_md("wtmut", w_cln, os.path.join(d, "build_wtmut"))

    masks = dict(design=design, pose=pose, binder_chains=binder_ch,
                 npMHC_res=npMHC, nbinder_res=nbind,
                 ligmask=f":1-{npMHC}", recmask=f":{npMHC + 1}-{npMHC + nbind}")
    json.dump(masks, open(os.path.join(d, "masks.json"), "w"), indent=2)
    print(f"[gate_prep] {design}: pMHC {npMHC} res / binder {nbind} res (chains {binder_ch}) -> {d}")
    print(f"  ligmask {masks['ligmask']}  recmask {masks['recmask']}")


if __name__ == "__main__":
    main()
