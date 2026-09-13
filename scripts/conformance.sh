#!/usr/bin/env bash
# Does THIS environment reproduce the recorded behaviour of the served model?
#
#   ./scripts/conformance.sh [model-key]
#   MULITAMINER='docker run --rm --network host -v $HOME/repo:$HOME/repo img' \
#     ./scripts/conformance.sh
#
# Run it after registering the model, after changing Ollama, and on any new
# machine. It catches the silent-empty failure of TRAINING.md 6f, which the
# pipeline itself cannot: constrained decoding guarantees shape, never content,
# and an empty array is a legal value.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
MM=${MULITAMINER:-mulitaminer}
CFG="$REPO/serving/conformance.json"
# python3 on Linux, python on Git Bash; the checks are stdlib-only.
PY=${PYTHON:-$(command -v python3 || command -v python)}

eval "$("$PY" - "$CFG" <<'PY'
import json, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))
for k in ("report", "scanner", "baseline", "model"):
    print(f"CFG_{k.upper()}={c[k]}")
PY
)"
MODEL="${1:-$CFG_MODEL}"
OUT="$REPO/output_heldout/_conformance"
rm -rf "$OUT"

echo "conformance: $MODEL on $(basename "$CFG_REPORT")"
$MM extract "$REPO/$CFG_REPORT" -s "$CFG_SCANNER" -m "$MODEL" --output-dir "$OUT" >/dev/null
RUN="$(dirname "$(find "$OUT" -name results.json | head -1)")"
$MM evaluate "$RUN" -b "$REPO/$CFG_BASELINE" --metrics token_f1 >/dev/null

"$PY" - "$CFG" "$RUN/evaluation.json" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1], encoding="utf-8"))
ev = json.load(open(sys.argv[2], encoding="utf-8"))

def measured(key):
    if key == "recall":
        return ev["coverage"]["recall"]
    field, metric = key.split(".")
    entry = ev["fields"].get(field, {}).get(metric)
    return entry.get("measured_mean") if isinstance(entry, dict) else entry

failed = []
for key, floor in cfg["floors"].items():
    value = measured(key)
    ok = value is not None and value >= floor
    shown = "none" if value is None else f"{value:.3f}"
    print(f"  {'PASS' if ok else 'FAIL'}  {key:<22} {shown:>6}  floor {floor}")
    if not ok:
        failed.append(key)

if failed:
    print(f"\nFAILED: {', '.join(failed)}")
    print("Most likely the model was registered without serving/Modelfile "
          "(a bare FROM falls back to the GGUF's Jinja template). TRAINING.md 6f.")
    raise SystemExit(1)
print("\nOK: this environment reproduces the recorded behaviour.")
PY
