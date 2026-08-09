#!/usr/bin/env bash
# Held-out evaluation runbook (extract on the GPU box, evaluate on the dev box).
#
#   extract:  ./scripts/eval_heldout.sh extract <model-key> [out_root]
#             runs `mulitaminer extract` on every data/heldout/*/*.pdf
#   evaluate: ./scripts/eval_heldout.sh evaluate <out_root>
#             scores every run dir against its data/heldout xlsx
#
# Model keys: mulita-qwen2.5-1.5b, mulita-qwen3-1.7b (tuned, served via
# Ollama), qwen2.5-1.5b, qwen3-1.7b-nothink (bases), deepseek.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
# override when the tool is not on PATH, e.g. inside the mulita image:
#   MULITAMINER='uv run --no-sync mulitaminer'
MM=${MULITAMINER:-mulitaminer}

case "${1:?extract|evaluate}" in
extract)
  model="${2:?model key}"
  out="${3:-$REPO/output_heldout/$model}"
  for pdf in "$REPO"/data/heldout/*/*.pdf; do
    scanner="$(basename "$(dirname "$pdf")")"
    $MM extract "$pdf" -s "$scanner" -m "$model" \
      --output-dir "$out/$scanner"
  done
  ;;
evaluate)
  out="${2:?out_root}"
  for pdf in "$REPO"/data/heldout/*/*.pdf; do
    stem="$(basename "$pdf" .pdf)"
    run="$(find "$out" -type f -name results.json -path "*${stem}*" \
           | sort | tail -1)"
    if [ -z "$run" ]; then
      echo "SKIP $stem: no run found under $out" >&2
      continue
    fi
    $MM evaluate "$(dirname "$run")" -b "${pdf%.pdf}.xlsx"
  done
  ;;
*)
  echo "usage: $0 extract <model-key> [out_root] | evaluate <out_root>" >&2
  exit 1
  ;;
esac
