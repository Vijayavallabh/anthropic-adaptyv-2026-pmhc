#!/usr/bin/env python3
"""ORGANIZERS' outside judge for pMHC: BLIND co-fold of a binder with HLA-A*11:01 + b2m + G12D peptide
using Protenix (ByteDance AF3-class, open) -- a SECOND, independent co-folder. Purpose: give the nanobody
class a format-appropriate 2nd-method pose confirmation at PARITY with the proteins' af2ig (af2ig cannot
realise de-novo CDR loops), and give proteins a uniform organizer-aligned check. BLIND = no pocket restraint
(matches the organizers' regime); single-seq a3m everywhere (msa:empty analog, symmetric across designs).
Chains: P=binder, A=HLA, B=b2m, C=peptide (match the Boltz scorers). Reports per-pair ipTM via Protenix json.
Usage: fold_protenix_pmhc.py --seqs <name,sequence csv> --out DIR --gpu N [--names a,b] [--samples 10 --seeds 101]
Run with any python3 (subprocess to the protenix venv)."""
import argparse, csv, json, os, re, subprocess
from pathlib import Path
ROOT = Path("/home/prachh/v/anthropic-adaptyv-2026-pmhc")
PROT = Path("/home/prachh/v/sepiq-2026-challenge/.venv-protenix/bin/protenix")
_v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(ROOT / "configs/target.yaml").read(), re.M)
HLA = next(s for s in _v if s.startswith("GSHSMRY"))
B2M = next(s for s in _v if s.startswith("IQRTP"))
PEP = "VVVGADGVGK"  # G12D

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--seeds", default="101")
    ap.add_argument("--cycle", type=int, default=10)
    ap.add_argument("--step", type=int, default=200)
    ap.add_argument("--names", default="")
    a = ap.parse_args()
    od = ROOT / a.out; od.mkdir(parents=True, exist_ok=True)
    want = set(x for x in a.names.split(",") if x)
    rows = [(r["name"], (r.get("sequence") or r.get("seq")).strip())
            for r in csv.DictReader(open(a.seqs)) if (r.get("sequence") or r.get("seq"))]
    if want: rows = [r for r in rows if r[0] in want]
    def a3m(tag, seq):
        p = od / f"_{tag}_g{a.gpu}.a3m"; p.write_text(f">{tag}\n{seq}\n"); return str(p.resolve())
    hla_m, b2m_m, pep_m = a3m("hla", HLA), a3m("b2m", B2M), a3m("pep", PEP)
    jobs = []
    for nm, seq in rows:
        bm = od / f"{nm}_binder.a3m"; bm.write_text(f">{nm}\n{seq}\n")
        jobs.append({"name": nm, "sequences": [
            {"proteinChain": {"sequence": seq, "count": 1, "id": ["P"], "unpairedMsaPath": str(bm.resolve())}},
            {"proteinChain": {"sequence": HLA, "count": 1, "id": ["A"], "unpairedMsaPath": hla_m}},
            {"proteinChain": {"sequence": B2M, "count": 1, "id": ["B"], "unpairedMsaPath": b2m_m}},
            {"proteinChain": {"sequence": PEP, "count": 1, "id": ["C"], "unpairedMsaPath": pep_m}},
        ]})
    ijson = od / f"jobs_g{a.gpu}.json"; ijson.write_text(json.dumps(jobs, indent=2))
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=a.gpu, OMP_NUM_THREADS="4", MKL_NUM_THREADS="4")
    cmd = [str(PROT), "pred", "-i", str(ijson), "-o", str(od), "-s", a.seeds, "-e", str(a.samples),
           "-c", str(a.cycle), "-p", str(a.step), "-n", "protenix_base_default_v1.0.0",
           "--use_msa", "true", "--use_template", "false"]
    print(f"RUN protenix-pmhc gpu={a.gpu} {len(jobs)} job(s) samples={a.samples}", flush=True)
    raise SystemExit(subprocess.run(cmd, cwd=str(ROOT), env=env).returncode)

if __name__ == "__main__":
    main()
