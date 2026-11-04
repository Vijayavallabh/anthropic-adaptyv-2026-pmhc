#!/bin/bash
# Campaign funnel stage F: score the 5-sample 6-state PANEL on ALL axes, into runs/campaign/.
# The cheap selectivity scorer runs on EVERY panel design; the expensive/secondary axes (grip, MPNN
# delta, novelty) run only on a GENEROUS selectivity-survivor set (campaign_survivors.py) -- a design
# that is not plausibly selective cannot be a top-20 selective binder regardless of grip/delta, and
# this keeps grip (Bio.PDB/sample) and MPNN (24 decode orders/GPU) from running on all ~1888.
#   panel_reval.tsv       score_rfd_val_fast: g12d/wt/scram/ebna4/atic + bh_e + spec_scram + promisc_margin
#   survivors.txt         generous selectivity gate for the expensive axes
#   panel_grip.tsv        pep_contact_consistency: f_pep peptide-contact fraction (grip) -- survivors
#   mpnn_diff.tsv         orthogonal MPNN delta (24 decode orders) + JDI/Poole controls -- survivors
#   novelty/b3_struct.csv single-seq ESMFold + foldseek max-TM vs PDB (PROTEIN survivors; IF foldseek present)
# Then: assemble_final20.py --with-campaign --out-prefix runs/campaign/combined_  +  campaign_select.py
# Usage: funnel_score.sh   (reads runs/campaign/panel_pool.csv + runs/campaign/panel_fold)
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
BPY=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
ESMPY=/home/prachh/v/sepiq-2026-challenge/.venv-esm/bin/python
R=$P/runs/campaign; cd "$P"
POOL=$R/panel_pool.csv; FOLD=$R/panel_fold
say(){ echo "[score] $* $(date -u +%FT%TZ)"; }
mkdir -p "$R/novelty"
[ -f "$POOL" ] || { echo "missing $POOL (run funnel_panel.sh first)"; exit 1; }

ALL=$R/panel_names.txt
tail -n +2 "$POOL" | cut -d, -f1 > "$ALL"
say "panel designs=$(wc -l < "$ALL")"

# 1. selectivity axes (5-sample, chain P) -- CPU, PARALLEL ipsae across cores, on ALL panel designs.
#    score_rfd_val_fast == score_rfd_val byte-for-byte (verified on folds/rfd_val, both code paths);
#    the sequential original would spawn ~56k ipsae subprocesses serially ~= 31h on the panel.
say "score_rfd_val_fast 5-sample panel (parallel ipsae)"
$BPY scripts/score_rfd_val_fast.py "$FOLD" --out "$R/panel_reval.tsv" --nsamp 5 --binder-chain P --jobs 64

# 2. GENEROUS selectivity survivor gate -- expensive axes run only on these
say "select survivors"
$BPY scripts/campaign_survivors.py "$R/panel_reval.tsv" --out "$R/survivors.txt" --topn 500
SURV=$R/survivors.txt
# protein survivors (name,sequence) for the optional novelty axis
$BPY - "$POOL" "$SURV" "$R/panel_protein_seqs.csv" <<'PY'
import sys, csv
pool, surv, out = sys.argv[1:4]
keep = set(l.strip() for l in open(surv) if l.strip())
rows = [r for r in csv.DictReader(open(pool)) if r['name'] in keep and not r['name'].startswith('nb3')]
with open(out, 'w') as o:
    o.write("name,sequence\n")
    for r in rows: o.write(f"{r['name']},{r['sequence']}\n")
print(f"[score] protein survivors for novelty: {len(rows)}")
PY
say "survivors=$(wc -l < "$SURV")"

# 3. grip peptide-contact fraction -- CPU (Bio.PDB) -- survivors only
say "grip (pep_contact_consistency) on survivors"
$BPY scripts/pep_contact_consistency.py $(cat "$SURV") --root "$FOLD" --out "$R/panel_grip.tsv" > "$R/panel_grip.log" 2>&1

# 4. orthogonal MPNN delta (24 decode orders, + JDI/Poole controls) -- GPU 2 -- survivors only
say "mpnn differential delta (24 seeds) on GPU 2 (survivors)"
$BPY scripts/mpnn_differential.py --foldroot "$FOLD" --designs-file "$SURV" \
     --out "$R/mpnn_diff.tsv" --gpu 2 --nsamp 5 --seeds 24 > "$R/mpnn_diff.log" 2>&1 &
MPID=$!

# 5. structural novelty: foldseek TM vs PDB over the PRE-FOLDED single-seq ESMFold structures. In-repo
#    foldseek + PDB DB under tools/ (tfr1/tools vanished mid-campaign); reuses the precompute folds -- no
#    re-fold. Batched (one search, not per-protein easy-search). CPU -> fine alongside the panel GPUs.
FS=tools/foldseek-env/bin/foldseek; DB=tools/foldseek_pdb/pdb; NPID=""
if [ -s "$R/novelty/b3_struct.csv" ]; then
  say "novelty already computed ($R/novelty/b3_struct.csv) -- skipping"
elif [ -x "$FS" ] && [ -f "$DB.dbtype" ] && ls runs/campaign/novelty_pre/esmfold*/*.pdb >/dev/null 2>&1; then
  say "robust_novelty (foldseek TM over precomputed folds)"
  $BPY scripts/robust_novelty.py --pdb-glob 'runs/campaign/novelty_pre/esmfold*/*.pdb' \
       --db "$DB" --fs "$FS" --out "$R/novelty/b3_struct.csv" > "$R/novelty.log" 2>&1 &
  NPID=$!
else
  say "SKIP novelty: need foldseek+DB+precomputed folds (FS=$FS DB=$DB)"
fi

rc=0
wait $MPID || rc=1; say "mpnn done"
[ -n "$NPID" ] && { wait $NPID || rc=1; say "novelty done"; }
say "AXES SCORED rc=$rc -> $R"
echo "NEXT: python3 scripts/assemble_final20.py --with-campaign --out-prefix $R/combined_  &&  python3 scripts/campaign_select.py"
