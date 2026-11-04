#!/usr/bin/env python3
"""Robust, BATCHED structural-novelty over pre-folded single-seq ESMFold structures.

Replaces the original per-protein easy-search (one foldseek process per pdb against a SHARED tmp dir,
which was slow and crashed the whole shard on a single foldseek error -> 0 output). Instead: stage all
query pdbs into one dir (foldseek names each query by basename-sans-.pdb, verified via .lookup), createdb
once, `search` all queries against the PDB DB in a single pass (TMalign, --alignment-type 1), convertalis,
then take the MAX alntmscore per query. One process, no per-call tmp race, no re-loading the DB 888x.

Emits name,singleseq_maxTM_pdb,top_hit,verdict (novel<0.80 | borderline<0.90 | risk>=0.90) -- exactly the
columns assemble_final20 reads from runs/campaign/novelty/b3_struct.csv.

Usage:
  robust_novelty.py --pdb-glob 'runs/campaign/novelty_pre/esmfold*/*.pdb' \
      --db tools/foldseek_pdb/pdb --fs tools/foldseek-env/bin/foldseek \
      --out runs/campaign/novelty/b3_struct.csv [--tmp tools/fs_nov_tmp] [--threads 32]
"""
import argparse, glob, os, subprocess, csv, shutil


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdb-glob", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--fs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tmp", default="tools/fs_nov_tmp")
    ap.add_argument("--threads", default="32")
    a = ap.parse_args()

    pdbs = sorted(glob.glob(a.pdb_glob))
    if not pdbs:
        raise SystemExit(f"no pdbs match {a.pdb_glob}")
    for suf in (".dbtype",):
        if not os.path.exists(a.db + suf):
            raise SystemExit(f"foldseek DB not found: {a.db} (missing {a.db + suf})")

    work = a.tmp
    if os.path.exists(work):
        shutil.rmtree(work)
    qdir = f"{work}/q"
    os.makedirs(qdir)
    names = []
    for p in pdbs:
        n = os.path.basename(p)[:-4]
        shutil.copy(p, f"{qdir}/{n}.pdb")
        names.append(n)
    print(f"[novelty] staged {len(names)} query structures", flush=True)

    FS = a.fs
    def run(cmd):
        subprocess.run(cmd, check=True)

    # easy-search handles createdb(query) + search(-a) + convertalis correctly in one call; decomposing it
    # by hand dropped the -a backtrace flag that `convertalis ... alntmscore` needs (-> segfault).
    run([FS, "easy-search", qdir, a.db, f"{work}/res.m8", f"{work}/t",
         "--alignment-type", "1", "--tmscore-threshold", "0.0",
         "--format-output", "query,target,alntmscore", "--threads", a.threads, "-v", "1"])

    best = {}
    for ln in open(f"{work}/res.m8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        q, t = p[0], p[1]
        try:
            tm = float(p[2])
        except ValueError:
            continue
        if q not in best or tm > best[q][0]:
            best[q] = (tm, t)

    rows = []
    for n in names:
        tm, hit = best.get(n, (0.0, ""))
        verdict = "novel" if tm < 0.80 else ("borderline" if tm < 0.90 else "risk")
        rows.append((n, round(tm, 3), hit, verdict))
    rows.sort(key=lambda r: r[1])

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="") as o:
        w = csv.writer(o)
        w.writerow(["name", "singleseq_maxTM_pdb", "top_hit", "verdict"])
        w.writerows(rows)

    nov = sum(1 for r in rows if r[1] < 0.80)
    bor = sum(1 for r in rows if 0.80 <= r[1] < 0.90)
    rsk = sum(1 for r in rows if r[1] >= 0.90)
    miss = sum(1 for r in rows if r[0] not in best)
    print(f"[novelty] {len(rows)} proteins -> {a.out}  novel={nov} borderline={bor} risk={rsk} "
          f"(no-hit={miss}, treated as maxTM=0=novel)")


if __name__ == "__main__":
    main()
