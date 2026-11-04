#!/bin/bash
# Campaign generation orchestrator: wait for the running protein arm, then run the nanobody arm.
# High-yield arms only (protein + nanobody); RFd historically converted 0 front-loaders and its
# contigs are unlogged, so it is excluded to spend the scarce co-fold budget on productive lineages.
# Usage: gen_campaign.sh <protein_gen_pid>   (launch tracked/background)
set -uo pipefail
P=/home/prachh/v/anthropic-adaptyv-2026-pmhc
TFR=/home/prachh/v/anthropic-adaptyv-2026-tfr1
export BG=$TFR/third_party/boltzgen
GPUS="2 3 4 5 6 7"
LOG=$P/folds/gen/campaign.log
WAITPID=${1:-}
say(){ echo "[campaign] $* $(date -u +%FT%TZ)" | tee -a "$LOG"; }

say "START waitpid=$WAITPID"
if [ -n "$WAITPID" ]; then
  say "waiting for protein arm pid $WAITPID"
  while kill -0 "$WAITPID" 2>/dev/null; do sleep 30; done
  say "protein arm done; protein cifs=$(find $P/folds/gen/b3_protein -path '*intermediate_designs*_[0-9]*.cif' 2>/dev/null | wc -l)"
fi

say "nanobody arm start (nb_pep_centric, nanobody-anything, N=3000)"
bash $TFR/scripts/gen_boltzgen.sh $P/specs/boltzgen/nb_pep_centric.yaml $P/folds/gen/b3_nb 3000 "$GPUS" nanobody-anything 2 >> "$LOG" 2>&1
say "nanobody cifs=$(find $P/folds/gen/b3_nb -path '*intermediate_designs*_[0-9]*.cif' 2>/dev/null | wc -l)"
say "ALL GEN DONE"
