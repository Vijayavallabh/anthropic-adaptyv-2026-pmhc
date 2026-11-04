#!/usr/bin/env python3
"""POCKET-RESTRAINED Protenix cross-check (2nd independent AF3-class co-folder) for the top front-load picks.
Mirrors the Boltz pocket restraint (binder->peptide C4,6,7,8 for loaded states; binder->HLA groove floor
66,69,146,150,155 for empty) so Protenix and Boltz are scored in the SAME regime -- a genuine 2-folder
consensus, not a blind run (blind co-fold drifts even positive controls). States g12d/scram/empty give
binding + specificity + tier-2. Chains P=binder(entity1), A=HLA(2), B=b2m(3), C=peptide(4); single-seq a3m
(msa:empty analog, symmetric). Builds per-GPU job shards, launches one Protenix process per GPU, waits.
Score with score_protenix_restrained.py (chain_pair_iptm: P-C loaded, P-A empty).
Usage: fold_protenix_restrained.py --csv <name,seq> --out DIR --gpus "3 4 5 6 7" [--samples 5 --seeds 101]
Run with any python3 (subprocesses the protenix venv)."""
import argparse, csv, json, os, re, subprocess
from pathlib import Path
ROOT = Path("/home/prachh/v/anthropic-adaptyv-2026-pmhc")
PROT = Path("/home/prachh/v/sepiq-2026-challenge/.venv-protenix/bin/protenix")
_v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(ROOT / "configs/target.yaml").read(), re.M)
HLA = next(s for s in _v if s.startswith("GSHSMRY"))
B2M = next(s for s in _v if s.startswith("IQRTP"))
PEP = {"g12d": "VVVGADGVGK", "scram": "VVGAVGDGVK"}          # loaded states (scram = pepswap control)
PEP_CONTACTS = [4, 6, 7, 8]                                  # peptide bulge (entity 4)
HLA_FLOOR = [66, 69, 146, 150, 155]                          # empty-state groove floor (entity 2)

def a3m(od, tag, seq):
    p = od / f"_{tag}.a3m"; p.write_text(f">{tag}\n{seq}\n"); return str(p.resolve())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--gpus", default="3 4 5 6 7"); ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--seeds", default="101"); ap.add_argument("--cycle", type=int, default=10)
    ap.add_argument("--step", type=int, default=200); ap.add_argument("--states", default="g12d,scram,empty")
    a = ap.parse_args()
    od = ROOT / a.out; od.mkdir(parents=True, exist_ok=True)
    rows = [(r["name"], (r.get("sequence") or r.get("seq")).strip())
            for r in csv.DictReader(open(a.csv)) if (r.get("sequence") or r.get("seq"))]
    hla_m, b2m_m = a3m(od, "hla", HLA), a3m(od, "b2m", B2M)
    pep_m = {k: a3m(od, f"pep_{k}", v) for k, v in PEP.items()}
    states = a.states.split(",")
    jobs = []
    BIDS = ["P", "Q"]  # binder chain ids (2nd used for a paired binder e.g. TCR Va:Vb positive control)
    for nm, seq in rows:
        bchains = [s.strip() for s in seq.split(":") if s.strip()]   # "Va:Vb" -> 2 binder chains
        nb = len(bchains)
        for st in states:
            seqs = []
            for i, bc in enumerate(bchains):
                bm = od / f"{nm}_{BIDS[i]}.a3m"; bm.write_text(f">{nm}_{BIDS[i]}\n{bc}\n")
                seqs.append({"proteinChain": {"sequence": bc, "count": 1, "id": [BIDS[i]], "unpairedMsaPath": str(bm.resolve())}})
            seqs.append({"proteinChain": {"sequence": HLA, "count": 1, "id": ["A"], "unpairedMsaPath": hla_m}})
            seqs.append({"proteinChain": {"sequence": B2M, "count": 1, "id": ["B"], "unpairedMsaPath": b2m_m}})
            hla_ent, pep_ent = nb + 1, nb + 3   # entities are 1-based positional: [binders..., HLA, b2m, (pep)]
            if st in PEP:   # loaded: add peptide, restrain binder chain P -> peptide bulge
                seqs.append({"proteinChain": {"sequence": PEP[st], "count": 1, "id": ["C"], "unpairedMsaPath": pep_m[st]}})
                res = [{"entity": pep_ent, "copy": 1, "position": p} for p in PEP_CONTACTS]
            else:           # empty: restrain binder chain P -> HLA groove floor
                res = [{"entity": hla_ent, "copy": 1, "position": p} for p in HLA_FLOOR]
            constraint = {"pocket": {"max_distance": 8.0, "binder_chain": {"entity": 1, "copy": 1},
                                     "contact_residues": res}}
            jobs.append({"name": f"{nm}__{st}", "sequences": seqs, "constraint": constraint})
    # shard across gpus
    G = a.gpus.split(); shards = {g: [] for g in G}
    for i, j in enumerate(jobs): shards[G[i % len(G)]].append(j)
    procs = []
    for g, js in shards.items():
        if not js: continue
        ij = od / f"jobs_g{g}.json"; ij.write_text(json.dumps(js, indent=1))
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=g, OMP_NUM_THREADS="4", MKL_NUM_THREADS="4")
        cmd = [str(PROT), "pred", "-i", str(ij), "-o", str(od), "-s", a.seeds, "-e", str(a.samples),
               "-c", str(a.cycle), "-p", str(a.step), "-n", "protenix_base_default_v1.0.0",
               "--use_msa", "true", "--use_template", "false"]
        lg = open(od / f"protenix_g{g}.log", "w")
        procs.append(subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=lg, stderr=subprocess.STDOUT))
        print(f"launched gpu {g}: {len(js)} jobs", flush=True)
    rc = 0
    for p in procs: rc |= p.wait()
    njson = len(list(od.rglob("*_summary_confidence_sample_0.json")))
    print(f"PROTENIX_RESTRAINED_DONE rc={rc} jobs={len(jobs)} summaries={njson}")

if __name__ == "__main__":
    main()
