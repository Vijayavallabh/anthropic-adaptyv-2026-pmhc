#!/bin/bash
# init.sh — environment check + verification entry points for the pMHC Challenge-5 repo.
# Non-destructive by default. Usage:
#   ./init.sh --check     # verify venv, GPUs, vendored tools, key result files (default)
#   ./init.sh --verify    # re-score the campaign panel fast-path (needs runs/campaign/panel_fold on disk)
#   ./init.sh --tools     # print how to rebuild the gitignored vendored tools (does NOT download anything)
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BPY=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/python
BOLTZ=/home/prachh/v/sepiq-2026-challenge/.venv-boltz/bin/boltz
MODE="${1:---check}"

ok(){ echo "  [ok] $*"; }
no(){ echo "  [--] $*"; }

check(){
  echo "== environment =="
  [ -x "$BPY" ] && ok "boltz venv python: $BPY" || no "MISSING boltz venv python: $BPY"
  [ -x "$BOLTZ" ] && ok "boltz CLI: $BOLTZ" || no "MISSING boltz CLI (co-fold will not run)"
  command -v nvidia-smi >/dev/null && {
    echo "== GPUs (0,1 are FOREIGN — never clobber; campaign uses 2-7) =="
    nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader | sed 's/^/  /'
  } || no "nvidia-smi not found"
  echo "== vendored tools (gitignored; rebuild with --tools) =="
  [ -x "$ROOT/tools/foldseek-env/bin/foldseek" ] && ok "foldseek binary" || no "foldseek missing (novelty screen)"
  [ -f "$ROOT/tools/foldseek_pdb/pdb.dbtype" ] && ok "foldseek PDB DB" || no "foldseek PDB DB missing"
  [ -f "$ROOT/tools/proteinmpnn/weights/v_48_020.pt" ] && ok "ProteinMPNN weights v_48_020" || no "ProteinMPNN weights missing (MPNN delta)"
  [ -f "$ROOT/scripts/ipsae.py" ] && ok "vendored ipsae.py" || no "ipsae.py missing (scorer)"
  echo "== key result files =="
  for f in runs/submission.csv runs/final20_ranked.tsv \
           runs/campaign/combined_submission.csv runs/campaign/panel_reval.tsv \
           runs/campaign/mpnn_diff_all.tsv runs/campaign/SWAP_PROPOSAL_mpnn.txt; do
    [ -f "$ROOT/$f" ] && ok "$f" || no "$f MISSING"
  done
}

case "$MODE" in
  --check) check ;;
  --verify)
    echo "Re-scoring the campaign panel (fast-path). Requires runs/campaign/panel_fold/ on disk."
    [ -d "$ROOT/runs/campaign/panel_fold" ] || { echo "  panel_fold not present (138 GB, gitignored) — regenerate via funnel_panel.sh"; exit 2; }
    "$BPY" "$ROOT/scripts/score_rfd_val_fast.py" "$ROOT/runs/campaign/panel_fold" \
        --out "$ROOT/runs/campaign/panel_reval.check.tsv" --nsamp 5
    echo "  wrote runs/campaign/panel_reval.check.tsv — diff against panel_reval.tsv to verify reproducibility."
    ;;
  --tools)
    cat <<'EOF'
Vendored tools are local-only (gitignored). Rebuild (owner-approved paths; conda/byte-identical copy, NOT curl|run):
  foldseek + PDB DB:
    ~/miniconda3/bin/conda create -y -p tools/foldseek-env -c conda-forge -c bioconda foldseek
    tools/foldseek-env/bin/foldseek databases PDB tools/foldseek_pdb/pdb /tmp/fsdl
  ProteinMPNN (code + v_48_020 weights): copy a byte-identical existing install into tools/proteinmpnn/{src,weights}
    (see memory env-novelty-foldseek-infra-gone-and-download-gated for the exact matched sources).
  ipsae.py / run_boltz.sh: already vendored byte-identical under scripts/.
EOF
    ;;
  *) echo "usage: ./init.sh [--check|--verify|--tools]"; exit 1 ;;
esac
