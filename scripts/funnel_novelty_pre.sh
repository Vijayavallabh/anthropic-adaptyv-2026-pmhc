#!/bin/bash
# Gap-filler: precompute structural-novelty (single-seq ESMFold + foldseek max-TM vs PDB) for ALL
# foldable PROTEINS (b3_*), sharded across GPUs 2-7, while the CPU-bound triage tail finishes and the
# panel has not yet claimed the GPUs. Proteins only (nanobodies are CDR-novelty-exempt). Output lands
# at runs/campaign/novelty/b3_struct.csv -- exactly where assemble_final20 --with-campaign reads it, so
# funnel_score.sh's novelty step becomes redundant for these designs.
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
ESMPY=/home/prachh/v/sepiq-2026-challenge/.venv-esm/bin/python
GPUS=(2 3 4 5 6 7); NG=${#GPUS[@]}
R=$P/runs/campaign; PRE=$R/novelty_pre; mkdir -p "$PRE" "$R/novelty"
cd "$P"
say(){ echo "[nov-pre] $* $(date -u +%FT%TZ)"; }

# foldable proteins only (b3_*), name,sequence from foldable.csv
{ echo "name,sequence"; tail -n +2 "$R/foldable.csv" | awk -F, '$1 ~ /^b3_/ {print $1","$2}'; } > "$PRE/prot_seqs.csv"
NP=$(( $(wc -l < "$PRE/prot_seqs.csv") - 1 )); say "foldable proteins to fold: $NP"

# round-robin shard into NG chunks
tail -n +2 "$PRE/prot_seqs.csv" | awk -v ng=$NG -v dir="$PRE" 'BEGIN{for(i=0;i<ng;i++){f[i]=dir"/chunk"i".csv"; print "name,sequence" > f[i]}} {print >> f[NR%ng]}'

pids=()
for i in "${!GPUS[@]}"; do
  g=${GPUS[$i]}
  [ "$(wc -l < "$PRE/chunk$i.csv")" -gt 1 ] || continue
  CUDA_VISIBLE_DEVICES=$g $ESMPY -I "$TFR/scripts/novelty_struct.py" \
    --seqs "$PRE/chunk$i.csv" --out "$PRE/out$i.csv" --struct-dir "$PRE/esmfold$i" \
    > "$PRE/log$i.log" 2>&1 &
  pids+=($!); sleep 3
done
say "launched ${#pids[@]} shards on GPUs ${GPUS[*]}; waiting"
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
say "shards done rc=$rc"

# merge shard outputs -> the path assemble reads (header once)
$ESMPY - "$PRE" "$NG" "$R/novelty/b3_struct.csv" <<'PY'
import sys, os, csv
pre, ng, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rows, header = [], None
for i in range(ng):
    fp = f"{pre}/out{i}.csv"
    if not os.path.exists(fp): continue
    rd = list(csv.reader(open(fp)))
    if not rd: continue
    header = rd[0] if header is None else header
    rows += rd[1:]
with open(out, "w", newline="") as o:
    w = csv.writer(o)
    if header: w.writerow(header)
    w.writerows(rows)
print(f"[nov-pre] merged {len(rows)} proteins -> {out}")
PY
say "NOVELTY PRECOMPUTE DONE -> $R/novelty/b3_struct.csv"
