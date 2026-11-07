#!/bin/bash
# Expansion gate: apply the MM-GBSA G12D-vs-WT selectivity judge across the realistic-pose,
# un-gated paneled pool, staged per docs/EXPANSION_GATE_PREREG.md. Isolated outroots under
# runs/gate_expand (NEVER clobbers runs/campaign/gate or runs/genie3/gate). GPUs 2-7 only.
# Usage: gate_expand.sh <stage>   stage in {prep_screen, screen, confirm, deepen}
#   screen   -> runs/gate_expand/screen   2-rep/2ns  (prioritizer)
#   confirm  -> runs/gate_expand/confirm  6-rep/5ns  (fresh, calibrated bar)
#   deepen   -> runs/gate_expand/confirm 12-rep/5ns  (appends reps 7-12; must hold)
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
PEPG=/home/prachh/miniconda3/envs/pepglad/bin/python
GPUS=2,3,4,5,6,7
cd "$P"
STAGE="${1:?stage required}"
say(){ echo "[gate-exp:$STAGE] $* $(date -u +%FT%TZ)"; }

prep_one(){  # $1=name $2=pose $3=outroot
  local d="$1" pose="$2" out="$3"
  if [ -f "$out/$d/build_g12d/g12d_solv.prmtop" ] && [ -f "$out/$d/build_wtmut/wtmut_solv.prmtop" ]; then
    return 0
  fi
  $PEPG scripts/gate/gate_prep.py "$d" "$pose" "$out" > "$out/prep_$d.log" 2>&1
}
export -f prep_one; export PEPG P

do_prep(){  # $1=cands.tsv (name\t...\tpose) $2=outroot  -> writes $2/list.txt of prepped names
  local cands="$1" out="$2"; mkdir -p "$out"
  say "prep from $cands -> $out (parallel 6)"
  # columns: name is $1, pose is last column
  tail -n +2 "$cands" | awk -F'\t' '{print $1"\t"$NF}' | \
    xargs -P 6 -d '\n' -I{} bash -c 'IFS=$'"'"'\t'"'"' read -r n p <<<"{}"; prep_one "$n" "$p" "'"$out"'"'
  : > "$out/list.txt"
  tail -n +2 "$cands" | cut -f1 | while read -r d; do
    [ -f "$out/$d/build_g12d/g12d_solv.prmtop" ] && [ -f "$out/$d/build_wtmut/wtmut_solv.prmtop" ] && echo "$d" >> "$out/list.txt"
  done
  say "prepped $(wc -l < "$out/list.txt") designs"
}

run_md(){  # $1=outroot $2=list $3=nrep $4=ns $5=tag
  local out="$1" lst="$2" nrep="$3" ns="$4" tag="$5"
  say "MD nrep=$nrep ns=$ns on $(wc -l < "$lst") designs (GPUs $GPUS) - the long one"
  $PEPG scripts/gate/gate_run.py "$out" "$lst" "$nrep" "$ns" "$GPUS" 2>&1 | tail -4
  say "score MM-GBSA (GBn2)"
  $PEPG scripts/gate/gate_score.py "$out" "$lst" 2>&1 | tail -3
  say "analyze ddG + CI -> $out/gate_results_$tag.tsv"
  $PEPG scripts/gate/gate_analyze.py "$out" "$lst" "$out/gate_results_$tag.tsv" 2>&1 | tail -3
  column -t "$out/gate_results_$tag.tsv" 2>/dev/null || cat "$out/gate_results_$tag.tsv"
}

case "$STAGE" in
  prep_screen) do_prep "$P/runs/gate_expand/screen_cands.tsv" "$P/runs/gate_expand/screen" ;;
  screen)      run_md "$P/runs/gate_expand/screen"  "$P/runs/gate_expand/screen/list.txt"   2 2 screen ;;
  confirm)     do_prep "$P/runs/gate_expand/confirm_cands.tsv" "$P/runs/gate_expand/confirm"
               run_md "$P/runs/gate_expand/confirm" "$P/runs/gate_expand/confirm/list.txt"  6 5 confirm ;;
  deepen)      run_md "$P/runs/gate_expand/confirm" "$P/runs/gate_expand/deepen_list.txt"  12 5 deepen ;;
  *) echo "unknown stage $STAGE"; exit 2 ;;
esac
say "STAGE DONE"
