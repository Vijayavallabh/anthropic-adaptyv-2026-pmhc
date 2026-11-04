#!/usr/bin/env python3
"""Orthogonal, NON-docking tier-1 selectivity probe -- ProteinMPNN differential peptide scoring.

Motivation (docs/RESEARCH_SOTA.md, finding #3 + the "verifier-dependent bias" caveat): our whole
ranking leans on ONE co-folder (Boltz-2 ipSAE); the Protenix cross-check turned out uninformative
(soft pocket, failed its own positive control). ProteinMPNN differential scoring is the one
orthogonal, non-docking selectivity signal the lit scan flagged as adoptable (Baker science.adv0185).
It is a WEAK prior on a BURIED discriminator -> ENRICHMENT, never a hard gate.

Method -- "what does this pocket want at the buried mutation site?":
  For a co-fold complex (A=HLA, B=b2m, C=peptide VVVGADGVGK with Asp6, binder=remaining chain(s)),
  run ProteinMPNN conditional_probs with ONLY peptide position 6 designable (every other residue
  fixed to its true identity). conditional_probs decodes that position LAST, conditioned on the
  full backbone + the TRUE sequence of everything else (binder in its pose, HLA, rest of peptide).
  Read logP(Asp) - logP(Gly) at P6 = does the pocket prefer the mutant (D) or the wild-type (G)?
    dDG_wb = that log-odds WITH the binder present.
    dDG_nb = the SAME structure with the binder chain(s) stripped (identical peptide+HLA coords).
    delta  = dDG_wb - dDG_nb  = the binder's OWN contribution to preferring Asp6 over Gly6.
  delta > 0  => the binder enriches the mutant identity at the buried site (orthogonal tier-1 signal).

FAIL-LOUD positive controls (crystals, CONTROLS ONLY -- never design seeds):
  7PB2 = JDI TCR  (therapeutic, >4000x G12D-selective)  -> STRONG positive, expect delta clearly > 0.
  7OW6 = Poole TCR (parental, binds G12D AND WT)         -> WEAK positive, expect smaller delta.
  If MPNN sees the buried discrimination at all, it must rank JDI > Poole. If both sit ~0, the metric
  is blind on this axis (like the Protenix check) and we report it UNINFORMATIVE, not disconfirming.

Run with the boltz venv python (has torch). Usage:
  mpnn_differential.py --designs all|<comma list> --out runs/mpnn_diff.tsv [--gpu 3] [--nsamp 5]
"""
import os, sys, json, glob, argparse, subprocess
import numpy as np

PMHC = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
MPNN_PY = "/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python"
MPNN_SRC = f"{PMHC}/tools/proteinmpnn/src"          # vendored in-repo (TFR third_party/ + weights/ vanished mid-session)
WEIGHTS = f"{PMHC}/tools/proteinmpnn/weights"        # byte-identical upstream v_48_020 (cache code == Proteina code; same checkpoint)
PARSE = f"{MPNN_SRC}/helper_scripts/parse_multiple_chains.py"
RUN = f"{MPNN_SRC}/protein_mpnn_run.py"
MODEL = "v_48_020"

AA3 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H',
       'ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W',
       'TYR':'Y','VAL':'V'}
ALPHABET = 'ACDEFGHIKLMNPQRSTVWYX'
iD, iG = ALPHABET.index('D'), ALPHABET.index('G')  # 2, 5

# submission design -> 5-sample re-validation fold root (the trusted panels the ranking used)
GENUINE = ["nanobody_0202","nanobody_0081","protein_0103","protein_0155","protein_0212",
           "protein_0073","protein_0092","protein_0025"]
BATCH2 = ["b2_gpu3_15","b2_gpu4_26","b2_gpu3_27","b2_gpu5_05","b2_gpu5_37","b2_gpu7_33",
          "b2_gpu5_13","b2_gpu3_36","b2_gpu5_19","b2_gpu5_27","b2_gpu7_02"]
RFD = ["rfd_des_173_m2"]
ROOT_OF = {**{d: f"{PMHC}/folds/reval_genuine" for d in GENUINE},
           **{d: f"{PMHC}/folds/batch2_reval" for d in BATCH2},
           **{d: f"{PMHC}/folds/rfd_val" for d in RFD}}
ALL_DESIGNS = GENUINE + BATCH2 + RFD


def clean_pdb(src, dst, keep):
    """Write ATOM records for chains in `keep`, standard AAs, altloc ' '/'A', order preserved."""
    n = 0
    with open(src) as fh, open(dst, "w") as o:
        for ln in fh:
            if not ln.startswith("ATOM"):
                continue
            if ln[21] not in keep:
                continue
            if ln[17:20].strip() not in AA3:
                continue
            if ln[16] not in (' ', 'A'):
                continue
            o.write(ln); n += 1
        o.write("TER\nEND\n")
    return n


def chains_in(pdb):
    return sorted({ln[21] for ln in open(pdb) if ln.startswith("ATOM")})


def build_manifest(design_list, nsamp, root_of=None, with_controls=True):
    """-> list of dicts {tag, src, keep_wb(set), name_wb, name_nb, design, sample, kind}."""
    root_of = root_of or ROOT_OF
    man = []
    # crystals (CONTROLS): copy-1 chains A,B,C,D,E ; peptide C, binder D+E
    if with_controls:
        for tag, pdb in [("CTRL_JDI_7pb2", f"{PMHC}/data/pdb/7PB2.pdb"),
                         ("CTRL_Poole_7ow6", f"{PMHC}/data/pdb/7OW6.pdb")]:
            man.append(dict(tag=tag, src=pdb, keep_wb={'A','B','C','D','E'},
                            design=tag, sample=0, kind="control"))
    # designs: up to nsamp g12d co-folds; binder = chains present minus A,B,C
    for d in design_list:
        root = root_of[d]
        pdbs = sorted(glob.glob(f"{root}/**/{d}__g12d_model_*.pdb", recursive=True))
        # unique by model index, keep first occurrence
        seen = {}
        for p in pdbs:
            mi = os.path.basename(p).split("_model_")[1].split(".")[0]
            seen.setdefault(mi, p)
        for mi in sorted(seen)[:nsamp]:
            p = seen[mi]
            ch = set(chains_in(p))
            binder = ch - {'A', 'B', 'C'}
            if not binder:
                print(f"[warn] {d} model {mi}: no binder chain found ({ch})", file=sys.stderr)
                continue
            man.append(dict(tag=f"{d}__S{mi}", src=p, keep_wb={'A','B','C'} | binder,
                            design=d, sample=int(mi), kind="design"))
    return man


def process(man, workdir, gpu, nseeds=1):
    pdbdir = f"{workdir}/pdbs"
    os.makedirs(pdbdir, exist_ok=True)
    meta = {}  # mpnn-name -> (role, entry)
    for e in man:
        wb, nb = f"{e['tag']}_wb", f"{e['tag']}_nb"
        n1 = clean_pdb(e['src'], f"{pdbdir}/{wb}.pdb", e['keep_wb'])
        n2 = clean_pdb(e['src'], f"{pdbdir}/{nb}.pdb", {'A', 'B', 'C'})
        if n1 == 0 or n2 == 0:
            raise RuntimeError(f"empty clean for {e['tag']} ({n1},{n2})")
        meta[wb] = ("wb", e); meta[nb] = ("nb", e)
    parsed = f"{workdir}/parsed.jsonl"
    r = subprocess.run([MPNN_PY, PARSE, "--input_path", pdbdir, "--output_path", parsed],
                       capture_output=True, text=True)
    if r.returncode or not os.path.exists(parsed):
        raise RuntimeError(f"parse failed:\n{r.stdout}\n{r.stderr}")
    cid, fixp = {}, {}
    for ln in open(parsed):
        ent = json.loads(ln); name = ent['name']
        allch = [k.split("_")[-1] for k in ent if k.startswith("seq_chain_")]
        assert 'C' in allch, (name, allch)
        cid[name] = [['C'], [c for c in allch if c != 'C']]
        Lc = len(ent['seq_chain_C'])
        assert Lc == 10, f"{name}: peptide C len {Lc} != 10"
        fixp[name] = {'C': [i for i in range(1, Lc + 1) if i != 6]}  # fix all but P6
    json.dump(cid, open(f"{workdir}/chains.jsonl", "w"))
    json.dump(fixp, open(f"{workdir}/fixed.jsonl", "w"))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu))
    # Monte-Carlo-average the C6 conditional log-probs over `nseeds` random decoding orders
    # (ProteinMPNN's autoregressive decode order is randn-seeded and injects ~0.3 noise on a single
    # masked position; averaging is the standard correct way to use conditional_probs for scoring).
    acc = {}  # name -> (sum_row[21], count)
    for k in range(nseeds):
        out = f"{workdir}/out_s{k}"
        r = subprocess.run([MPNN_PY, RUN, "--jsonl_path", parsed,
                            "--chain_id_jsonl", f"{workdir}/chains.jsonl",
                            "--fixed_positions_jsonl", f"{workdir}/fixed.jsonl",
                            "--conditional_probs_only", "1",
                            "--path_to_model_weights", WEIGHTS, "--model_name", MODEL,
                            "--out_folder", out, "--seed", str(101 + k), "--batch_size", "1"],
                           capture_output=True, text=True, env=env)
        if r.returncode:
            raise RuntimeError(f"mpnn run failed (seed {k}):\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        for name in meta:
            d = np.load(f"{out}/conditional_probs_only/{name}.npz")
            lp, S, dm = d['log_p'], d['S'], d['design_mask']
            pos = np.argwhere(dm == 1).flatten()
            assert len(pos) == 1, f"{name}: {len(pos)} designable positions (expected 1)"
            p = int(pos[0])
            assert int(S[p]) == iD, f"{name}: masked position is not Asp (S={int(S[p])})"
            row = lp[0, p, :] if lp.ndim == 3 else lp[p, :]
            if name not in acc:
                acc[name] = [np.zeros(21), 0]
            acc[name][0] += row; acc[name][1] += 1
    res = {}
    for name in meta:
        row = acc[name][0] / acc[name][1]
        res[name] = dict(logD=float(row[iD]), logG=float(row[iG]),
                         dDG=float(row[iD] - row[iG]), argmax=ALPHABET[int(np.argmax(row))])
    return res, meta


def aggregate(res, meta):
    """-> per-design {design, kind, n, dDG_wb, dDG_nb, delta, delta_sd, argmax_wb}."""
    by = {}
    for name, (role, e) in meta.items():
        by.setdefault(e['design'], dict(kind=e['kind'], wb={}, nb={}))
        by[e['design']][role][e['sample']] = res[name]
    rows = []
    for d, v in by.items():
        samples = sorted(set(v['wb']) & set(v['nb']))
        deltas = [v['wb'][s]['dDG'] - v['nb'][s]['dDG'] for s in samples]
        wb = [v['wb'][s]['dDG'] for s in samples]
        nb = [v['nb'][s]['dDG'] for s in samples]
        amax = [v['wb'][s]['argmax'] for s in samples]
        rows.append(dict(design=d, kind=v['kind'], n=len(samples),
                         dDG_wb=round(float(np.mean(wb)), 3),
                         dDG_nb=round(float(np.mean(nb)), 3),
                         delta=round(float(np.mean(deltas)), 3),
                         delta_sd=round(float(np.std(deltas)), 3) if len(deltas) > 1 else 0.0,
                         argmax_frac_D=round(sum(a == 'D' for a in amax) / len(amax), 2)))
    rows.sort(key=lambda r: (r['kind'] != 'control', -r['delta']))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--designs", default="all")
    ap.add_argument("--designs-file", default=None, help="file with one design name per line (overrides --designs)")
    ap.add_argument("--foldroot", default=None, help="fold root holding {design}__g12d_model_*.pdb for ALL designs")
    ap.add_argument("--no-controls", action="store_true", help="skip the crystal positive controls")
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu", default="3")
    ap.add_argument("--nsamp", type=int, default=5)
    ap.add_argument("--seeds", type=int, default=1, help="MC-average C6 logits over this many decoding-order seeds")
    ap.add_argument("--workdir", default=None)
    a = ap.parse_args()
    if a.designs_file:
        dl = [x.strip() for x in open(a.designs_file) if x.strip()]
    else:
        dl = ALL_DESIGNS if a.designs == "all" else [x for x in a.designs.split(",") if x]
    root_of = {d: a.foldroot for d in dl} if a.foldroot else None
    wd = a.workdir or os.path.join(os.environ.get("SCRATCH", "/tmp"), "mpnn_diff")
    os.makedirs(wd, exist_ok=True)
    man = build_manifest(dl, a.nsamp, root_of=root_of, with_controls=not a.no_controls)
    print(f"[info] {len(man)} structures ({len(dl)} designs + controls), seeds={a.seeds}, workdir={wd}", file=sys.stderr)
    res, meta = process(man, wd, a.gpu, a.seeds)
    rows = aggregate(res, meta)
    cols = ["design", "kind", "n", "dDG_wb", "dDG_nb", "delta", "delta_sd", "argmax_frac_D"]
    with open(a.out, "w") as o:
        o.write("\t".join(cols) + "\n")
        for r in rows:
            o.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"[done] wrote {a.out}", file=sys.stderr)
    # echo to stdout
    print("\t".join(cols))
    for r in rows:
        print("\t".join(str(r[c]) for c in cols))


if __name__ == "__main__":
    main()
