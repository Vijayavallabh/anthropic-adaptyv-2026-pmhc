#!/bin/bash
# Campaign funnel stage E: the TRUSTED 5-sample, 6-state co-fold panel on triage survivors.
# States: g12d/wt/scram/ebna4/atic (build_pepswap_cofold) + empty (build_design_cofold --states empty).
# binder=P, same pocket restraint (peptide bulge C4,6,7,8; empty->HLA floor). run_boltz NOMSA=1 DIFF_SAMPLES=5.
# Usage: funnel_panel.sh <names_file> <pool_csv>
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
BPY=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
GPUS="2 3 4 5 6 7"
NAMES=${1:?names file}; POOL=${2:?pool csv}
R=$P/runs/campaign; cd "$P"
say(){ echo "[panel] $* $(date -u +%FT%TZ)"; }

$BPY - "$POOL" "$NAMES" "$R/panel_pool.csv" <<'PY'
import sys, csv
pool, names, out = sys.argv[1], sys.argv[2], sys.argv[3]
keep = set(l.strip() for l in open(names) if l.strip())
rows = [r for r in csv.DictReader(open(pool)) if r['name'] in keep]
with open(out, 'w') as o:
    o.write("name,sequence\n")
    for r in rows:
        o.write(f"{r['name']},{r['sequence']}\n")
print(f"[panel] pool = {len(rows)} designs")
PY
say "build 6-state panel yamls"
$BPY scripts/build_pepswap_cofold.py --csv "$R/panel_pool.csv" --out "$R/panel_yaml"
$BPY scripts/build_design_cofold.py  --csv "$R/panel_pool.csv" --out "$R/panel_yaml" --states empty
NY=$(ls "$R/panel_yaml"/*.yaml | wc -l); say "yamls=$NY (expect 6/design)"
say "5-sample co-fold across [$GPUS] (this is the long one)"
NOMSA=1 DIFF_SAMPLES=5 bash "$TFR/scripts/run_boltz.sh" "$R/panel_yaml" "$R/panel_fold" "$GPUS"
say "PANEL FOLD DONE -> $R/panel_fold"
