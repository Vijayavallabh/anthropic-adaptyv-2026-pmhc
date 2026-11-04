#!/bin/bash
# Boltz-2 single-seq cofold, sharded across GPUs (standalone .venv-boltz). binder=A : target=B, msa empty.
# Usage: run_boltz.sh <yaml_dir> <out_dir> "<gpus>"
set -uo pipefail
BOLTZ=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/boltz
IN=${1:?yaml dir}; OUT=${2:?out dir}; GPUS=${3:-1 2 3 4 5 6 7}
read -r -a G <<< "$GPUS"; NG=${#G[@]}
mkdir -p "$OUT"
yamls=( "$IN"/*.yaml ); [ ${#yamls[@]} -gt 0 ] || { echo "no yamls in $IN" >&2; exit 2; }
for i in "${!G[@]}"; do mkdir -p "$OUT/sh$i"; done
k=0; for y in "${yamls[@]}"; do s=$((k % NG)); cp "$y" "$OUT/sh$s/"; k=$((k+1)); done
export OMP_NUM_THREADS=8
echo "[boltz] ${#yamls[@]} designs across $NG gpus [$GPUS] $(date -u +%FT%TZ)"
pids=()
for i in "${!G[@]}"; do
  g=${G[$i]}; [ -n "$(ls -A "$OUT/sh$i"/*.yaml 2>/dev/null)" ] || continue
  CUDA_VISIBLE_DEVICES=$g "$BOLTZ" predict "$OUT/sh$i" --out_dir "$OUT/pred$i" --devices 1 \
    --recycling_steps 3 --sampling_steps 50 --diffusion_samples ${DIFF_SAMPLES:-1} --output_format pdb --override $([ "${NOMSA:-0}" = 1 ] || echo --use_msa_server) \
    > "$OUT/sh$i.log" 2>&1 &
  pids+=($!); sleep 6
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "BOLTZ_DONE rc=$rc confidence jsons: $(find "$OUT" -name 'confidence_*.json' 2>/dev/null | wc -l) $(date -u +%FT%TZ)"
