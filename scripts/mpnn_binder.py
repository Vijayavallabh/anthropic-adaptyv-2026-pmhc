#!/usr/bin/env python3
"""ProteinMPNN sequences for de-novo binder BACKBONES (RFd/Genie) co-folded against the pMHC target.
Designs the BINDER chain (default D = RFd1's diffused chain; target HLA/b2m/peptide = A/B/C are FIXED),
biases AWAY from Cys (0-Cys binders express better). The binder sub-sequence is pulled out of ProteinMPNN's
'/'-joined multi-chain record ROBUSTLY = the part that matches NONE of the known target sequences.
Emits a name,sequence CSV ready for build_design_cofold.py. Run with any python3 (subprocess to MPNN venv).

Usage: mpnn_binder.py --pdbdir <dir of des_*.pdb> --out <csv> [--design-chain D] [--nseq 2] [--temp 0.1]
"""
import argparse, csv, glob, json, os, re, subprocess, shutil
from pathlib import Path

MPNN_PY = Path("/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python")  # has torch
MPNN = Path("/home/prachh/v/anthropic-adaptyv-2026-tfr1/third_party/proteinmpnn/stock/src")
WEIGHTS = Path("/home/prachh/v/anthropic-adaptyv-2026-tfr1/weights/proteinmpnn/vanilla_model_weights")
ROOT = Path(__file__).resolve().parent.parent
_v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(ROOT / "configs/target.yaml").read(), re.M)
TARGET_SEQS = {s for s in _v}  # HLA, b2m, peptides -- the binder matches none of these

def run_mpnn(pdbdir, outdir, design_chain, nseq, temp, weights=WEIGHTS, omit="C"):
    outdir = Path(outdir).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    H = MPNN / "helper_scripts"
    parsed, chains = outdir / "parsed.jsonl", outdir / "chains.jsonl"
    sh = lambda *c: subprocess.run([str(MPNN_PY), *map(str, c)], check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    sh(H / "parse_multiple_chains.py", "--input_path", pdbdir, "--output_path", parsed)
    # assign_fixed_chains.py is absent in this opt-kit -> build chain_id_jsonl inline:
    # {name: [[design_chains],[fixed_chains]]}; design the binder chain, fix all target chains.
    cid = {}
    for ln in open(parsed):
        e = json.loads(ln); name = e["name"]
        all_ch = [k.split("_")[-1] for k in e if k.startswith("seq_chain_")]
        fixed = [c for c in all_ch if c != design_chain]
        cid[name] = [[design_chain], fixed]
    open(chains, "w").write(json.dumps(cid))
    subprocess.run([str(MPNN_PY), str(MPNN / "protein_mpnn_run.py"),
                    "--jsonl_path", str(parsed), "--chain_id_jsonl", str(chains),
                    "--path_to_model_weights", str(weights), "--model_name", "v_48_020",
                    "--out_folder", str(outdir), "--num_seq_per_target", str(nseq),
                    "--sampling_temp", str(temp), "--seed", "37", "--batch_size", "1",
                    "--omit_AAs", omit], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return outdir / "seqs"

def pick_binder(seq_line):
    """From a '/'-joined multi-chain ProteinMPNN record, return the binder part (matches no target seq)."""
    cands = [p.strip() for p in seq_line.strip().split("/") if p.strip()]
    for p in cands:
        if p not in TARGET_SEQS and 10 <= len(p) <= 250:
            return p
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdbdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default=None)
    ap.add_argument("--design-chain", default="D")
    ap.add_argument("--nseq", type=int, default=2)
    ap.add_argument("--temp", type=float, default=0.1)
    ap.add_argument("--weights", default=str(WEIGHTS))
    ap.add_argument("--omit", default="C")
    a = ap.parse_args()
    work = Path(a.work or (Path(a.out).parent / "mpnn_work"))
    stage = work / "pdb"; stage.mkdir(parents=True, exist_ok=True)
    pdbs = sorted(glob.glob(f"{a.pdbdir}/des_*.pdb"))
    for p in pdbs:
        shutil.copy(p, stage / Path(p).name)
    if not pdbs:
        print(f"no des_*.pdb in {a.pdbdir}"); return
    seqdir = run_mpnn(stage, work, a.design_chain, a.nseq, a.temp, a.weights, a.omit)
    rows, skip = [], 0
    for fa in sorted(glob.glob(f"{seqdir}/*.fa")):
        rec = list(open(fa)); base = Path(fa).stem; k = 0
        for i in range(2, len(rec), 2):  # skip native (rec 0); designs follow
            seq = pick_binder(rec[i + 1])
            if seq and all(c in "ACDEFGHIKLMNPQRSTVWY" for c in seq):
                rows.append((f"rfd_{base}_m{k}", seq)); k += 1
            else:
                skip += 1
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["name", "sequence"]); w.writerows(rows)
    print(f"[mpnn_binder] {len(pdbs)} backbones -> {len(rows)} seqs (skipped {skip}) -> {a.out}")
    if rows:
        import statistics
        print(f"  binder lengths: {min(len(s) for _,s in rows)}-{max(len(s) for _,s in rows)} (med {int(statistics.median(len(s) for _,s in rows))})")

if __name__ == "__main__":
    main()
