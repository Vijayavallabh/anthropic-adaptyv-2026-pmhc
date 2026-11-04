#!/bin/bash
# Campaign funnel stage C-D: cheap g12d-only triage co-fold to cut the foldable pool before the
# expensive 5-sample 6-state panel. Ranks by binder(P)<->peptide(C) ipSAE (2 samples) and keeps top-N.
# Triage is deliberately LENIENT (single-state, low-sample OVER-estimates -> keep a generous top-N; the
# 5-sample multi-state panel is the real gate). Usage: funnel_triage.sh <foldable_csv> <topN> [nsamp]
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
BPY=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
GPUS="2 3 4 5 6 7"
CSV=${1:?foldable csv}; TOPN=${2:-800}; NS=${3:-2}
R=$P/runs/campaign; cd "$P"
say(){ echo "[triage] $* $(date -u +%FT%TZ)"; }

say "build g12d-only yamls from $CSV"
$BPY scripts/build_pepswap_cofold.py --csv "$CSV" --out "$R/triage_yaml" --peptides g12d=VVVGADGVGK
say "cofold g12d ($NS samples) across [$GPUS]"
NOMSA=1 DIFF_SAMPLES=$NS bash "$TFR/scripts/run_boltz.sh" "$R/triage_yaml" "$R/triage_fold" "$GPUS"
say "score g12d binder<->peptide ipSAE"
$BPY scripts/score_rfd_val.py "$R/triage_fold" --out "$R/triage_g12d.tsv" --nsamp "$NS" --binder-chain P
$BPY - "$R/triage_g12d.tsv" "$R/triage_top.txt" "$TOPN" <<'PY'
import sys, csv
tsv, out, topn = sys.argv[1], sys.argv[2], int(sys.argv[3])
rows = [r for r in csv.DictReader(open(tsv), delimiter='\t') if r.get('g12d') not in (None, '', 'None')]
rows.sort(key=lambda r: float(r['g12d']), reverse=True)
open(out, 'w').write("\n".join(r['name'] for r in rows[:topn]) + "\n")
vals = [float(r['g12d']) for r in rows]
import statistics as st
print(f"[triage] ranked {len(rows)} by g12d ipSAE; "
      f"max={max(vals):.3f} median={st.median(vals):.3f}; kept top {min(topn,len(rows))} -> {out}")
for c in (0.3, 0.4, 0.5, 0.6):
    print(f"   g12d>={c}: {sum(1 for v in vals if v>=c)}")
PY
say "TRIAGE DONE -> $R/triage_top.txt"
