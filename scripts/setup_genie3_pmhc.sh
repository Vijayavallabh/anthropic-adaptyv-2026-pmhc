#!/bin/bash
# Rebuild Genie3 (anthropics/uplifting-biomolecular-modeling) for the pMHC orthogonal-generator run.
# The TNF/TfR1 installs were cleaned, so clone fresh + build the pinned venv + fetch weights.
# Self-contained under the pmhc repo (third_party is gitignored). GPU-touching steps pinned to a free GPU.
set -uo pipefail
export CUDA_VISIBLE_DEVICES=2            # free GPU; NEVER 0/1 (foreign jobs)
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
REPO=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TP=$REPO/third_party
UP=$TP/uplifting-biomolecular-modeling
G=$UP/genie3
W=$REPO/weights/genie3
mkdir -p "$TP" "$W"
echo "[g3-build] $(date -u +%FT%TZ) start"

if [ ! -d "$UP/.git" ]; then
  echo "[g3-build] cloning anthropics/uplifting-biomolecular-modeling"
  git clone --depth 1 https://github.com/anthropics/uplifting-biomolecular-modeling "$UP" 2>&1 | tail -8 \
    || { echo "G3_BUILD_FAIL clone rc=$?"; exit 11; }
fi
[ -d "$G" ] || { echo "G3_BUILD_FAIL no genie3 subdir at $G"; ls "$UP" | head; exit 12; }
cd "$G"
echo "[g3-build] repo layout:"; ls | head -30

echo "[g3-build] uv venv py3.10"
uv venv --seed --managed-python --python 3.10 venv_g3 2>&1 | tail -3 || { echo "G3_BUILD_FAIL venv"; exit 13; }
. venv_g3/bin/activate

if [ -f environment/requirements.lock ]; then
  echo "[g3-build] pip install pinned lock (long pole)"
  pip install -q -r environment/requirements.lock --src "$G/stock_src" 2>&1 | tail -15
  echo "[g3-build] rc_lock=$?"
else
  echo "[g3-build] NO environment/requirements.lock — listing environment/:"; ls environment 2>/dev/null | head
fi

if [ -f run.sh ]; then
  echo "[g3-build] run.sh install --weights $W"
  bash run.sh install --weights "$W" 2>&1 | tail -25
  echo "[g3-build] rc_install=$?"
  echo "[g3-build] run.sh check (fast)"
  bash run.sh check --config h100 --mode fast 2>&1 | tail -20
  echo "[g3-build] rc_check=$?"
else
  echo "[g3-build] NO run.sh — repo layout differs; listing:"; ls
fi
echo "[g3-build] checkpoints present:"; find "$W" -name "*.ckpt" 2>/dev/null | head
echo "G3_BUILD_DONE $(date -u +%FT%TZ)"
