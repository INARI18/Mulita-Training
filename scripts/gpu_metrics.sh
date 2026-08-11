#!/usr/bin/env bash
# Full-metrics recalculation on the GPU box (token_f1 + rouge_l + bertscore,
# no nli). Runs inside the unsloth image (CUDA torch available):
#
#   docker run -d --name gpu-metrics --gpus all \
#     -v ~/mulita:/mulita -v ~/mulita-extractor-training:/training \
#     --entrypoint bash unsloth/unsloth /training/scripts/gpu_metrics.sh
#
# Scores (1) the SLM-study copies in /mulita/output_slm_metrics against the
# trimmed resources/ baselines, and (2) base + tuned qwen2.5 series in
# /training/output_heldout against data/heldout (latest run per report, via
# the eval runbook). Progress in /mulita/gpu_metrics.log.
set -uo pipefail
cd /mulita || exit 1
LOG=/mulita/gpu_metrics.log
: > "$LOG"

echo "=== uv sync (eval group) $(date +%H:%M:%S)" >> "$LOG"
uv sync --group eval >> "$LOG" 2>&1 || { echo "SYNC FAILED" >> "$LOG"; exit 1; }
uv run --no-sync python -c "import torch; print('cuda:', torch.cuda.is_available())" >> "$LOG" 2>&1

export MULITAMINER='uv run --no-sync mulitaminer'
export METRICS=token_f1,rouge_l,bertscore

i=0
find output_slm_metrics -name results.json | sort | while read -r r; do
  i=$((i+1))
  echo "=== [slm $i/216] $(date +%H:%M:%S) $(dirname "$r")" >> "$LOG"
  $MULITAMINER evaluate "$(dirname "$r")" --metrics "$METRICS" >> "$LOG" 2>&1
done

for model in qwen2.5-1.5b mulita-qwen2.5-1.5b mulita-qwen2.5-1.5b-v2 \
             mulita-qwen2.5-1.5b-v3 mulita-qwen2.5-1.5b-v4; do
  echo "=== [heldout] $(date +%H:%M:%S) $model" >> "$LOG"
  bash /training/scripts/eval_heldout.sh evaluate \
    "/training/output_heldout/$model" >> "$LOG" 2>&1
done

echo "=== ALL DONE $(date +%H:%M:%S)" >> "$LOG"
