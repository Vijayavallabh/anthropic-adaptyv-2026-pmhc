#!/bin/bash
# Genie3 de-novo binder generation vs the ORDERED G12D pMHC, peptide-centric (hotspot C4,5,7,8;
# extended incl buried Asp6). Orthogonal to BoltzGen (correlated-failure hedge). Shards across GPUs,
# 1 proc/GPU, distinct seeds, per-GPU triton cache. NEVER GPUs 0/1 (foreign). Weights via GENIE3_WEIGHTS.
# Usage: gen_genie3_pmhc.sh "<gpu space-list>" [N_total=600] [seedbase=7000] [tag=gen]
set -uo pipefail
REPO=/home/prachh/v/anthropic-adaptyv-2026-pmhc
G3="$REPO/third_party/uplifting-biomolecular-modeling/genie3"
PY="$G3/venv_g3/bin/python"
BATCH="$G3/opt/genie3_opt/g3batch.py"
DS="$REPO/runs/genie3/pmhc_g12d_bench"
export GENIE3_WEIGHTS="$REPO/weights/genie3/pretrained/v1"
CKPT="$GENIE3_WEIGHTS/checkpoints/step=600000.ckpt"
[ -f "$CKPT" ] || { echo "no checkpoint $CKPT"; exit 3; }
[ -x "$PY" ] || { echo "no venv python $PY"; exit 3; }

IFS=' ' read -ra GPUS <<< "${1:-}"; NG=${#GPUS[@]}
[ "$NG" -ge 1 ] || { echo "usage: gen_genie3_pmhc.sh \"<gpus>\" [N] [seedbase] [tag]"; exit 2; }
TOTAL="${2:-600}"; SEEDBASE="${3:-7000}"; TAG="${4:-gen}"
PERSHARD=$(( (TOTAL + NG - 1) / NG ))
echo "[gen-pmhc] $TOTAL designs across ${NG} GPU(s) (${GPUS[*]}) ~$PERSHARD/shard seedbase $SEEDBASE tag=$TAG $(date -u +%FT%TZ)"
cd "$G3" || exit 4

pids=(); i=0
for g in "${GPUS[@]}"; do
  SH="$REPO/runs/genie3/${TAG}/shard_g${g}"; mkdir -p "$SH" "$REPO/.jit/g3_triton_g${g}"
  REQ="$SH/request.yaml"; SEED=$((SEEDBASE + i))
  cat > "$REQ" <<YAML
experiment:
  name: ${TAG}_g${SEED}
  seed: ${SEED}
paths:
  rootdir: ${SH}
  dataset: ${DS}
generation:
  dataset:
    source: target
    selections: pmhc_g12d
    n_sample: ${PERSHARD}
  sampler:
    sampler:
      direction_scale: 0.0
  base:
    checkpoint: ${CKPT}
    config: ${GENIE3_WEIGHTS}/config.yaml
YAML
  echo "[gen-pmhc] shard g${g} seed ${SEED} n=${PERSHARD} -> $SH/gen.log"
  CUDA_VISIBLE_DEVICES=$g TRITON_CACHE_DIR="$REPO/.jit/g3_triton_g${g}" OMP_NUM_THREADS=8 \
    nohup "$PY" "$BATCH" --config "$REQ" --outdir "$SH" --batch-size 1 --seed "$SEED" \
    > "$SH/gen.log" 2>&1 &
  pids+=($!); i=$((i+1))
done
echo "[gen-pmhc] launched pids: ${pids[*]} ; waiting..."
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=$?; done
echo "[gen-pmhc] all shards done rc=$rc $(date -u +%FT%TZ)"
echo "[gen-pmhc] backbones produced:"; find "$REPO/runs/genie3/${TAG}" -name "*.pdb" 2>/dev/null | wc -l
