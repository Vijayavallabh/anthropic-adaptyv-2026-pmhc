#!/bin/bash
# MM-GBSA G12D-vs-WT gate on the top orthogonal Genie3 candidates (same pipeline/params as the
# submission's expansion set: nrep=6, prod 5ns). Isolated outroot runs/genie3/gate (never clobbers
# runs/campaign/gate). Prep uses the best g12d co-fold pose (model_0). GPUs 2-7 only.
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
PEPG=/home/prachh/miniconda3/envs/pepglad/bin/python
OUT=$P/runs/genie3/gate; mkdir -p "$OUT"; cd "$P"
CANDS=(
  rfd_des_g5_pmhc_g12d_176_m1 rfd_des_pmhc_g12d_8_m0 rfd_des_g4_pmhc_g12d_121_m1
  rfd_des_g2_pmhc_g12d_169_m0 rfd_des_g6_pmhc_g12d_142_m1 rfd_des_g5_pmhc_g12d_72_m0
  rfd_des_g2_pmhc_g12d_87_m0 rfd_des_g6_pmhc_g12d_148_m1
)
say(){ echo "[gate-g3] $* $(date -u +%FT%TZ)"; }

say "STAGE prep (${#CANDS[@]} candidates)"
: > "$OUT/genie3_list.txt"
for d in "${CANDS[@]}"; do
  if [ -f "$OUT/$d/build_g12d/g12d_solv.prmtop" ] && [ -f "$OUT/$d/build_wtmut/wtmut_solv.prmtop" ]; then
    say "prep $d already done"; echo "$d" >> "$OUT/genie3_list.txt"; continue
  fi
  POSE=$(find "$P/runs/genie3/funnel/panel_fold" -path "*${d}__g12d*model_0.pdb" 2>/dev/null | head -1)
  [ -n "$POSE" ] || { say "NO g12d pose for $d - skipping"; continue; }
  say "prep $d <- $(basename "$POSE")"
  if $PEPG scripts/gate/gate_prep.py "$d" "$POSE" "$OUT" > "$OUT/prep_$d.log" 2>&1; then
    echo "$d" >> "$OUT/genie3_list.txt"
  else
    say "prep FAILED $d (see prep_$d.log)"; tail -3 "$OUT/prep_$d.log"
  fi
done
N=$(wc -l < "$OUT/genie3_list.txt"); say "prepped $N designs"
[ "$N" -ge 1 ] || { say "no designs prepped; abort"; exit 1; }

say "STAGE run MD (nrep=6, prod 5ns, GPUs 2-7) - the long one"
$PEPG scripts/gate/gate_run.py "$OUT" "$OUT/genie3_list.txt" 6 5 2,3,4,5,6,7 2>&1 | tail -8
say "STAGE score MM-GBSA (OpenMM GBn2)"
$PEPG scripts/gate/gate_score.py "$OUT" "$OUT/genie3_list.txt" 2>&1 | tail -4
say "STAGE analyze ddG + CI"
$PEPG scripts/gate/gate_analyze.py "$OUT" "$OUT/genie3_list.txt" "$OUT/gate_results_genie3.tsv" 2>&1 | tail -4
say "DONE -> $OUT/gate_results_genie3.tsv"
column -t "$OUT/gate_results_genie3.tsv" 2>/dev/null || cat "$OUT/gate_results_genie3.tsv"
