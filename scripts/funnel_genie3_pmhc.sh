#!/bin/bash
# Isolated funnel for the Genie3 ORTHOGONAL designs: fullbb -> SolubleMPNN -> ESMFold -> g12d triage ->
# 5-sample 6-state panel -> same weakest-margin ruler. ALL output under runs/genie3/funnel (NEVER clobbers
# runs/campaign, which backs the committed submission). Stages are resumable: funnel_genie3_pmhc.sh <START> <STOP>.
#   1 fullbb  2 mpnn  3 esmfold+foldable  4 g12d-triage  5 panel(5x6, long)  6 weakest-ruler
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
BPY=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
ESMPY=/home/prachh/v/sepiq-2026-challenge/.venv-esm/bin/python
PUL=/home/prachh/v/.claude-private/jobs/5045f83d/tmp/recon_venv/bin/pulchra
GPUS="2 3 4 5 6 7"; GARR=(2 3 4 5 6 7); NG=6
R=$P/runs/genie3/funnel; mkdir -p "$R"; cd "$P"
S1=${1:-1}; S2=${2:-6}
PLDDT_CUT=${PLDDT_CUT:-0.70}; TRIAGE_N=${TRIAGE_N:-150}
say(){ echo "[g3-funnel] $* $(date -u +%FT%TZ)"; }

if [ "$S1" -le 1 ] && [ "$S2" -ge 1 ]; then
  say "STAGE1 fullbb reconstruct (PULCHRA) all gen1 backbones"
  python3 scripts/build_genie3_fullbb_pmhc.py "$PUL" "$P/runs/genie3/gen1/shard_g*/pmhc_g12d/pdbs/*.pdb" "$R/fullbb"
fi

if [ "$S1" -le 2 ] && [ "$S2" -ge 2 ]; then
  say "STAGE2 SolubleMPNN (design binder chain D, fix target A/B/C, omit Cys), nseq 2"
  python3 scripts/mpnn_binder.py --pdbdir "$R/fullbb" --out "$R/genie3_mpnn.csv" --design-chain D --nseq 2 --temp 0.1
fi

if [ "$S1" -le 3 ] && [ "$S2" -ge 3 ]; then
  say "STAGE3 ESMFold monomer foldability (sharded) + filter pLDDT>=$PLDDT_CUT"
  mkdir -p "$R/esm"
  tail -n +2 "$R/genie3_mpnn.csv" | awk -v ng=$NG -v dir="$R/esm" 'BEGIN{for(i=0;i<ng;i++){f[i]=dir"/chunk"i".csv"; print "name,sequence" > f[i]}} {print >> f[NR%ng]}'
  pids=()
  for i in "${!GARR[@]}"; do g=${GARR[$i]}
    [ "$(wc -l < "$R/esm/chunk$i.csv")" -gt 1 ] || continue
    CUDA_VISIBLE_DEVICES=$g $ESMPY -I "$TFR/scripts/esmfold_monomer.py" "$R/esm/chunk$i.csv" "$R/esm/out$i" > "$R/esm/log$i.log" 2>&1 &
    pids+=($!); sleep 4
  done
  rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done; say "ESMFold done rc=$rc"
  $BPY - "$R" "$NG" "$PLDDT_CUT" <<'PY'
import sys, os, json, csv
R, NG, cut = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
pl={}
for i in range(NG):
    fp=f"{R}/esm/out{i}/plddt.json"
    if os.path.exists(fp): pl.update(json.load(open(fp)))
rows=list(csv.DictReader(open(f"{R}/genie3_mpnn.csv")))
nf=0
with open(f"{R}/genie3_plddt.csv","w") as a, open(f"{R}/genie3_foldable.csv","w") as b:
    a.write("name,sequence,plddt\n"); b.write("name,sequence\n")
    for r in rows:
        v=pl.get(r["name"])
        if v is None: continue
        a.write(f"{r['name']},{r['sequence']},{v}\n")
        if v>=cut: b.write(f"{r['name']},{r['sequence']}\n"); nf+=1
vals=sorted(v*100 for v in pl.values())
n=len(vals); import statistics as st
print(f"[g3-funnel] folded {n}; pLDDT min={vals[0] if vals else 0:.1f} med={st.median(vals) if vals else 0:.1f} max={vals[-1] if vals else 0:.1f}; foldable(>= {cut*100:.0f})={nf}")
for c in (60,65,70,75,80): print(f"   >= {c}: {sum(1 for v in vals if v>=c)}")
PY
fi

if [ "$S1" -le 4 ] && [ "$S2" -ge 4 ]; then
  say "STAGE4 g12d-only triage co-fold (2 samples), keep top $TRIAGE_N by binder<->peptide ipSAE"
  $BPY scripts/build_pepswap_cofold.py --csv "$R/genie3_foldable.csv" --out "$R/triage_yaml" --peptides g12d=VVVGADGVGK
  NOMSA=1 DIFF_SAMPLES=2 bash "$TFR/scripts/run_boltz.sh" "$R/triage_yaml" "$R/triage_fold" "$GPUS"
  $BPY scripts/score_rfd_val.py "$R/triage_fold" --out "$R/triage_g12d.tsv" --nsamp 2 --binder-chain P
  $BPY - "$R/triage_g12d.tsv" "$R/triage_top.txt" "$TRIAGE_N" <<'PY'
import sys, csv, statistics as st
tsv,out,topn=sys.argv[1],sys.argv[2],int(sys.argv[3])
rows=[r for r in csv.DictReader(open(tsv),delimiter='\t') if r.get('g12d') not in (None,'','None')]
rows.sort(key=lambda r: float(r['g12d']), reverse=True)
open(out,'w').write("\n".join(r['name'] for r in rows[:topn])+"\n")
v=[float(r['g12d']) for r in rows]
print(f"[g3-funnel] triage ranked {len(rows)} by g12d ipSAE; max={max(v):.3f} med={st.median(v):.3f}; kept top {min(topn,len(rows))}")
PY
fi

if [ "$S1" -le 5 ] && [ "$S2" -ge 5 ]; then
  say "STAGE5 TRUSTED 5-sample 6-state panel on triage survivors (the long one)"
  $BPY - "$R/genie3_foldable.csv" "$R/triage_top.txt" "$R/panel_pool.csv" <<'PY'
import sys, csv
pool,names,out=sys.argv[1],sys.argv[2],sys.argv[3]
keep=set(l.strip() for l in open(names) if l.strip())
rows=[r for r in csv.DictReader(open(pool)) if r['name'] in keep]
open(out,'w').write("name,sequence\n"+"".join(f"{r['name']},{r['sequence']}\n" for r in rows))
print(f"[g3-funnel] panel pool = {len(rows)}")
PY
  $BPY scripts/build_pepswap_cofold.py --csv "$R/panel_pool.csv" --out "$R/panel_yaml"
  $BPY scripts/build_design_cofold.py  --csv "$R/panel_pool.csv" --out "$R/panel_yaml" --states empty
  NY=$(ls "$R/panel_yaml"/*.yaml | wc -l); say "panel yamls=$NY (expect 6/design)"
  NOMSA=1 DIFF_SAMPLES=5 bash "$TFR/scripts/run_boltz.sh" "$R/panel_yaml" "$R/panel_fold" "$GPUS"
  $BPY scripts/score_rfd_val_fast.py "$R/panel_fold" --out "$R/panel_reval.tsv" --nsamp 5 --binder-chain P
  say "panel scored -> $R/panel_reval.tsv"
fi

if [ "$S1" -le 6 ] && [ "$S2" -ge 6 ]; then
  say "STAGE6 weakest-margin ruler (same as submission)"
  $BPY - "$R/panel_reval.tsv" "$R/panel_ranked.tsv" <<'PY'
import sys, csv
src,out=sys.argv[1],sys.argv[2]
rows=list(csv.DictReader(open(src),delimiter='\t'))
cols=["name","lineage","bp","spec_scram","promisc_margin","bh_e","sel"]
with open(out,'w') as o:
    o.write("\t".join(cols)+"\n")
    for r in rows:
        bp=r.get("g12d","0")
        o.write("\t".join([r["name"],"genie3",bp,r.get("spec_scram","0"),r.get("promisc_margin","0"),r.get("bh_e","0"),"0"])+"\n")
print(f"[g3-funnel] wrote ranked tsv ({len(rows)} rows)")
PY
  python3 scripts/weakest_objective.py --ranked "$R/panel_ranked.tsv" --names "$R/panel_pool.csv" --out "$R/weakest.tsv"
  say "DONE -> $R/weakest.tsv (top by weakest margin):"
  head -12 "$R/weakest.tsv"
fi
say "stages $S1..$S2 complete"
