#!/usr/bin/env python
"""Charge-sensor selectivity PRIOR for the KRAS-G12D pMHC campaign.

WHY: the co-fold "weakest-margin" ruler is BLIND to the single buried-residue G12D-vs-WT
discrimination (CLAUDE.md invariant). The MM-GBSA gate is the only in-silico judge that sees
that axis, but it is expensive (~1 design/hr on 6 H100s) and has only ever been run on the ~68
designs the blind ruler floated to the top. This script ranks the ~2000 paneled-but-ungated
designs by a mechanism-based prior -- through-space electrostatic complementarity to the buried
Asp6 carboxylate (the induced-electrostatics mechanism, lesson-pmhc-g12d-mechanism-induced-
electrostatic) -- so the gate can be applied BEST-FIRST across the untested pool.

This is a PRIOR ONLY. It never ranks the selectivity axis for the submission and is never
reported as evidence of selectivity. Credibility is decided solely by the gate's ddG CI.

Pose layout (verified): chain A=HLA, B=b2m, C=peptide VVVGADGVGK (resSeq 6 = ASP6), binder=any
other chain (e.g. P). Over-dock artifacts (Asp6 swung out of the groove) are flagged by low
burial so they are NOT prioritized.

Usage: <pepglad-python> charge_sensor_prior.py
Writes: runs/gate_prior/charge_sensor_prior.tsv  (full ranked table, all poses)
Prints: control check (known credibles + known over-dock) then top un-gated candidates.
"""
import os, glob, sys
import numpy as np

P = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
POSE_GLOBS = [
    f"{P}/runs/campaign/panel_fold/**/*__g12d/*__g12d_model_0.pdb",
    f"{P}/runs/genie3/funnel/panel_fold/**/*__g12d*model_0.pdb",
]
OUTDIR = f"{P}/runs/gate_prior"; os.makedirs(OUTDIR, exist_ok=True)
OUT = f"{OUTDIR}/charge_sensor_prior.tsv"

# --- atom chemistry (binder side) ---
CATION = {('ARG', 'NE'), ('ARG', 'NH1'), ('ARG', 'NH2'), ('LYS', 'NZ')}
HISN   = {('HIS', 'ND1'), ('HIS', 'NE2')}
DONOR  = {('SER', 'OG'), ('THR', 'OG1'), ('TYR', 'OH'), ('ASN', 'ND2'),
          ('GLN', 'NE2'), ('TRP', 'NE1')}
ANION  = {('ASP', 'OD1'), ('ASP', 'OD2'), ('GLU', 'OE1'), ('GLU', 'OE2')}
AA3 = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE',
       'PRO','SER','THR','TRP','TYR','VAL'}


def parse(path):
    """Return dicts of coords by role. None if peptide Asp6 carboxylate absent."""
    carb = []          # peptide Asp6 OD1/OD2 coords
    bind_pts = []      # (weight, xyz) binder polar atoms  (+cation/donor, -anion)
    bind_cat = []      # binder cation N xyz
    bind_don = []      # binder cation+His+donor xyz (H-bond donors)
    bind_ani = []      # binder anion O xyz
    bind_heavy = []    # all binder heavy-atom xyz
    env_heavy = []     # HLA(A)+b2m(B) heavy-atom xyz
    hla_cat = []       # chain A cation N xyz (native Arg114 bridge partner)
    for ln in open(path):
        if not ln.startswith(("ATOM", "HETATM")):
            continue
        alt = ln[16]
        if alt not in (' ', 'A'):
            continue
        res = ln[17:20].strip(); ch = ln[21]; atom = ln[12:16].strip()
        try:
            seq = int(ln[22:26]); x = float(ln[30:38]); y = float(ln[38:46]); z = float(ln[46:54])
        except ValueError:
            continue
        if ln[13] == 'H':
            continue
        xyz = (x, y, z)
        if ch == 'C':
            if seq == 6 and res == 'ASP' and atom in ('OD1', 'OD2'):
                carb.append(xyz)
            continue
        if ch in ('A', 'B'):
            env_heavy.append(xyz)
            if ch == 'A' and (res, atom) in CATION:
                hla_cat.append(xyz)
            continue
        # binder chain
        if res not in AA3:
            continue
        bind_heavy.append(xyz)
        w = 0.0
        if (res, atom) in CATION:
            w = 1.0; bind_cat.append(xyz); bind_don.append(xyz)
        elif (res, atom) in HISN:
            w = 0.5; bind_don.append(xyz)
        elif (res, atom) in DONOR:
            w = 0.25; bind_don.append(xyz)
        elif atom == 'N':                       # backbone amide donor
            w = 0.20; bind_don.append(xyz)
        elif (res, atom) in ANION:
            w = -1.0; bind_ani.append(xyz)
        if w != 0.0:
            bind_pts.append((w, xyz))
    if len(carb) < 2:
        return None
    return dict(carb=np.array(carb), bind_pts=bind_pts,
                bind_cat=np.array(bind_cat) if bind_cat else np.zeros((0, 3)),
                bind_don=np.array(bind_don) if bind_don else np.zeros((0, 3)),
                bind_ani=np.array(bind_ani) if bind_ani else np.zeros((0, 3)),
                bind_heavy=np.array(bind_heavy) if bind_heavy else np.zeros((0, 3)),
                env_heavy=np.array(env_heavy) if env_heavy else np.zeros((0, 3)),
                hla_cat=np.array(hla_cat) if hla_cat else np.zeros((0, 3)))


def mindist(A, B):
    if len(A) == 0 or len(B) == 0:
        return 99.0
    return float(np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)).min())


def count_within(A, cen, r):
    if len(A) == 0:
        return 0
    return int((np.sqrt(((A - cen) ** 2).sum(-1)) <= r).sum())


def descriptor(d):
    carb = d['carb']; cen = carb.mean(0)
    # through-space electrostatic complementarity: sum w/dist over binder polar atoms <12A
    esp = 0.0
    for w, xyz in d['bind_pts']:
        dd = np.sqrt(((np.array(xyz) - cen) ** 2).sum())
        if dd <= 12.0:
            esp += w / max(dd, 2.0)
    d_min_cat = mindist(d['bind_cat'], carb)
    n_don4 = sum(count_within(d['bind_don'], o, 4.0) for o in carb)
    n_env5 = count_within(d['env_heavy'], cen, 5.0) + count_within(d['bind_heavy'], cen, 5.0)
    binder_near6 = count_within(d['bind_heavy'], cen, 6.0)
    native_bridge = mindist(d['hla_cat'], carb)
    anion_near = 0.0
    if len(d['bind_ani']):
        dd = np.sqrt(((d['bind_ani'] - cen) ** 2).sum(-1))
        anion_near = float((1.0 / np.clip(dd[dd <= 8.0], 2.0, None)).sum())
    return dict(esp=esp, d_min_cat=d_min_cat, n_don4=n_don4, n_env5=n_env5,
                binder_near6=binder_near6, native_bridge=native_bridge, anion_near=anion_near)


def design_name(path):
    base = os.path.basename(path)
    return base.split('__g12d')[0]


def load_weakest():
    w = {}
    for f, lin in [(f"{P}/runs/campaign/weakest_objective.tsv", None),
                   (f"{P}/runs/genie3/funnel/weakest.tsv", None)]:
        if not os.path.exists(f):
            continue
        with open(f) as fh:
            hdr = fh.readline().rstrip("\n").split("\t")
            iname = hdr.index("name"); iwk = hdr.index("weakest")
            ilin = hdr.index("lineage") if "lineage" in hdr else None
            for ln in fh:
                c = ln.rstrip("\n").split("\t")
                if len(c) <= max(iname, iwk):
                    continue
                try:
                    w[c[iname]] = (float(c[iwk]), c[ilin] if ilin is not None else "?")
                except ValueError:
                    pass
    return w


def load_gated():
    g = set()
    for f in glob.glob(f"{P}/runs/campaign/gate/gate_results*.tsv") + \
             glob.glob(f"{P}/runs/genie3/gate/gate_results*.tsv"):
        with open(f) as fh:
            next(fh, None)
            for ln in fh:
                g.add(ln.split("\t")[0].strip())
    return g


def main():
    weak = load_weakest()
    gated = load_gated()
    poses = []
    for g in POSE_GLOBS:
        poses += glob.glob(g, recursive=True)
    # one pose per design (model_0)
    seen = {}
    for p in poses:
        seen.setdefault(design_name(p), p)
    rows = []
    for name, path in seen.items():
        d = parse(path)
        if d is None:
            continue
        desc = descriptor(d)
        wk, lin = weak.get(name, (None, "?"))
        lineage = "genie3" if name.startswith("rfd_des") else ("boltzgen" if lin == "?" else lin)
        buried = desc['n_env5'] >= 10
        at_site = desc['binder_near6'] >= 3
        promisc_ok = (wk is None) or (wk >= 0.0)
        # priority: through-space complementarity, bonus for a direct cation bridge / donors
        score = desc['esp'] + (1.5 if desc['d_min_cat'] < 4.0 else 0.0) + 0.25 * min(desc['n_don4'], 4)
        eligible = buried and at_site and promisc_ok and (name not in gated)
        rows.append((name, lineage, wk, desc, score, buried, at_site, promisc_ok,
                     name in gated, eligible, path))

    rows.sort(key=lambda r: r[4], reverse=True)
    with open(OUT, "w") as fh:
        fh.write("name\tlineage\tweakest\tesp\td_min_cat\tn_don4\tn_env5\tbinder_near6\t"
                 "native_bridge\tanion_near\tprior_score\tburied\tat_site\tpromisc_ok\tgated\teligible\tpose\n")
        for (name, lin, wk, de, sc, bu, at, po, gd, el, path) in rows:
            fh.write(f"{name}\t{lin}\t{'' if wk is None else f'{wk:.3f}'}\t{de['esp']:.3f}\t"
                     f"{de['d_min_cat']:.2f}\t{de['n_don4']}\t{de['n_env5']}\t{de['binder_near6']}\t"
                     f"{de['native_bridge']:.2f}\t{de['anion_near']:.3f}\t{sc:.3f}\t{int(bu)}\t{int(at)}\t"
                     f"{int(po)}\t{int(gd)}\t{int(el)}\t{path}\n")

    byname = {r[0]: r for r in rows}
    print(f"# scored {len(rows)} designs; wrote {OUT}")
    print("\n=== CONTROL CHECK: descriptor on KNOWN-answer designs (validates the prior) ===")
    print(f"{'design':<22}{'lineage':<10}{'esp':>7}{'dcat':>7}{'ndon4':>6}{'env5':>6}{'near6':>6}{'natbr':>7}{'score':>8}  note")
    controls = [("b3_gpu7_113", "CREDIBLE selective (gate -9.29)"),
                ("nb3_gpu4_132", "CREDIBLE selective (gate -7.27)"),
                ("nb3_gpu6_132", "OVER-DOCK artifact (gate -11.72 not credited)"),
                ("b3_gpu7_181", "co-fold top, gate +4.22 (WT-lean)"),
                ("b3_gpu4_211", "co-fold top, gate +4.88 (WT-lean)")]
    for cn, note in controls:
        r = byname.get(cn)
        if not r:
            print(f"{cn:<22} (no pose found)"); continue
        de = r[3]
        print(f"{cn:<22}{r[1]:<10}{de['esp']:>7.2f}{de['d_min_cat']:>7.2f}{de['n_don4']:>6}"
              f"{de['n_env5']:>6}{de['binder_near6']:>6}{de['native_bridge']:>7.2f}{r[4]:>8.2f}  {note}")
        rank = [i for i, rr in enumerate(rows) if rr[0] == cn][0] + 1
        print(f"{'':22}-> prior rank {rank}/{len(rows)}")

    elig = [r for r in rows if r[9]]
    print(f"\n=== TOP 50 UN-GATED ELIGIBLE candidates (buried, at-site, non-promiscuous) ===")
    print(f"total eligible un-gated = {len(elig)}")
    print(f"{'rank':>4} {'design':<24}{'lineage':<10}{'weakest':>8}{'esp':>7}{'dcat':>7}{'ndon4':>6}{'env5':>6}{'score':>8}")
    for i, r in enumerate(elig[:50]):
        de = r[3]
        wk = '' if r[2] is None else f'{r[2]:.3f}'
        print(f"{i+1:>4} {r[0]:<24}{r[1]:<10}{wk:>8}{de['esp']:>7.2f}{de['d_min_cat']:>7.2f}"
              f"{de['n_don4']:>6}{de['n_env5']:>6}{r[4]:>8.2f}")


if __name__ == "__main__":
    main()
