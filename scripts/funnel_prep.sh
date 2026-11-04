#!/bin/bash
# Campaign funnel, stage A-B: extract protein+nanobody pools -> sharded ESMFold monomer foldability.
# Foldability (monomer pLDDT) is the best single de-novo success predictor (Rocklin 2026) and the cheapest
# strong filter, so it runs before any co-fold. Emits runs/campaign/pool_plddt.csv (name,sequence,plddt)
# + a pLDDT histogram so the foldable cut is chosen from the data, not guessed.
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
ESMPY=/home/prachh/v/sepiq-2026-challenge/.venv-esm/bin/python
BPY=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
GPUS=(2 3 4 5 6 7); NG=${#GPUS[@]}
R=$P/runs/campaign; ESM=$R/esm; mkdir -p "$ESM"
cd "$P"
say(){ echo "[funnel] $* $(date -u +%FT%TZ)"; }

# A. extract + hard-filter both arms
say "extract protein"
$BPY scripts/extract_pool.py --gen folds/gen/b3_protein --out "$R/pool_protein.csv" --prefix b3  --mode protein
say "extract nanobody"
$BPY scripts/extract_pool.py --gen folds/gen/b3_nb      --out "$R/pool_nb.csv"      --prefix nb3 --mode nanobody
{ echo "name,sequence"; tail -n +2 "$R/pool_protein.csv"; tail -n +2 "$R/pool_nb.csv"; } > "$R/pool_all.csv"
N=$(( $(wc -l < "$R/pool_all.csv") - 1 )); say "pool_all=$N designs"

# B. sharded ESMFold monomer foldability (one GPU per chunk, round-robin)
tail -n +2 "$R/pool_all.csv" | awk -v ng=$NG -v dir="$ESM" 'BEGIN{for(i=0;i<ng;i++){f[i]=dir"/chunk"i".csv"; print "name,sequence" > f[i]}} {print >> f[NR%ng]}'
pids=()
for i in "${!GPUS[@]}"; do
  g=${GPUS[$i]}
  [ "$(wc -l < "$ESM/chunk$i.csv")" -gt 1 ] || continue
  CUDA_VISIBLE_DEVICES=$g $ESMPY -I "$TFR/scripts/esmfold_monomer.py" "$ESM/chunk$i.csv" "$ESM/out$i" > "$ESM/log$i.log" 2>&1 &
  pids+=($!); sleep 4
done
say "ESMFold launched on ${#pids[@]} gpus; waiting"
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
say "ESMFold done rc=$rc"

# merge plddt + attach to sequences; print histogram
$BPY - "$R" "$NG" <<'PY'
import sys, os, json, csv
R, NG = sys.argv[1], int(sys.argv[2])
pl = {}
for i in range(NG):
    fp = f"{R}/esm/out{i}/plddt.json"
    if os.path.exists(fp):
        pl.update(json.load(open(fp)))
rows = list(csv.DictReader(open(f"{R}/pool_all.csv")))
with open(f"{R}/pool_plddt.csv", "w") as o:
    o.write("name,sequence,plddt\n")
    for r in rows:
        v = pl.get(r["name"])
        if v is None:
            continue
        o.write(f"{r['name']},{r['sequence']},{v}\n")
vals = sorted(v * 100 for v in pl.values())   # pLDDT stored 0-1; display/cuts in 0-100 percent
n = len(vals)
print(f"[funnel] folded {n} designs; pLDDT min={vals[0] if vals else 0:.1f} "
      f"median={vals[n//2] if vals else 0:.1f} max={vals[-1] if vals else 0:.1f}")
import collections
h = collections.Counter(int(v // 5) * 5 for v in vals)
for b in sorted(h):
    print(f"   pLDDT [{b:3d},{b+5:3d}): {h[b]:5d}  " + "#" * (h[b] * 60 // max(h.values())))
for cut in (65, 70, 72, 75, 80):
    print(f"   >= {cut}: {sum(1 for v in vals if v >= cut)}")
PY
say "STAGE A-B DONE -> runs/campaign/pool_plddt.csv"
