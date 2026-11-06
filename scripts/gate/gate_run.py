#!/usr/bin/env python
"""MM-GBSA selectivity gate: MD scheduler (6-GPU pool, GPUs 2-7 by default; NEVER 0,1).

Runs nrep replicas x {g12d, wtmut} x prod_ns ns per design, mirroring the validated calibration MD
(md_run.py: OpenMM CUDA, HMR 4 fs, min -> NVT 100 ps -> NPT equil -> production). Each design must be
prepped first (gate_prep.py -> designs/<d>/build_{g12d,wtmut}/*_solv.{prmtop,inpcrd}).

Resume-safe: legs whose *_prod.dcd already exists are skipped.
Usage: <pepglad-python> gate_run.py <outroot> <designs_file> [nrep=6] [prod_ns=5] [gpus=2,3,4,5,6,7]
"""
import sys, os, subprocess, time, threading, queue

HERE = os.path.dirname(os.path.abspath(__file__))
PYO = "/home/prachh/miniconda3/envs/pepglad/bin/python"
MDRUN = os.path.join(HERE, "md_run.py")


def main():
    outroot = sys.argv[1]
    dfile = sys.argv[2]
    nrep = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    prod_ns = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
    gpus = [int(x) for x in (sys.argv[5].split(",") if len(sys.argv) > 5 else ["2", "3", "4", "5", "6", "7"])]
    designs = [l.strip() for l in open(dfile) if l.strip() and not l.startswith("#")]

    legs = []
    for dez in designs:
        for syst, base in [("g12d", 100), ("wtmut", 200)]:
            bdir = os.path.join(outroot, dez, f"build_{syst}")
            prm = os.path.join(bdir, f"{syst}_solv.prmtop")
            crd = os.path.join(bdir, f"{syst}_solv.inpcrd")
            if not os.path.exists(prm):
                print(f"[gate_run] WARN missing {prm}; skip {dez}/{syst}", flush=True)
                continue
            mddir = os.path.join(outroot, dez, "md")
            os.makedirs(mddir, exist_ok=True)
            for r in range(1, nrep + 1):
                outpref = os.path.join(mddir, f"{syst}_r{r}")
                if os.path.exists(outpref + "_prod.dcd"):
                    continue
                legs.append((dez, syst, r, prm, crd, outpref, base + r))

    nlegs = len(legs)
    print(f"[gate_run] {len(designs)} designs, {nlegs} MD legs, {len(gpus)} GPUs {gpus}, {prod_ns} ns/leg", flush=True)
    if not nlegs:
        print("[gate_run] nothing to run"); return

    q = queue.Queue()
    for leg in legs:
        q.put(leg)
    logdir = os.path.join(HERE, "logs")
    os.makedirs(logdir, exist_ok=True)
    lock = threading.Lock()
    done = [0]

    def worker(gpu):
        while True:
            try:
                dez, syst, r, prm, crd, outpref, seed = q.get_nowait()
            except queue.Empty:
                return
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu),
                       OMP_NUM_THREADS="8", MKL_NUM_THREADS="8", OPENMM_CPU_THREADS="8")
            lg = open(os.path.join(logdir, f"md_{dez}_{syst}_r{r}.log"), "w")
            t0 = time.time()
            rc = subprocess.run([PYO, "-I", MDRUN, prm, crd, outpref, str(prod_ns), str(seed)],
                                stdout=lg, stderr=subprocess.STDOUT, env=env).returncode
            lg.close()
            with lock:
                done[0] += 1
                print(f"[gate_run] GPU{gpu} {dez}/{syst}_r{r} rc={rc} {time.time()-t0:.0f}s "
                      f"({done[0]}/{nlegs})", flush=True)

    threads = [threading.Thread(target=worker, args=(g,), daemon=True) for g in gpus]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"[gate_run] ALL MD DONE ({done[0]}/{nlegs} legs)", flush=True)


if __name__ == "__main__":
    main()
