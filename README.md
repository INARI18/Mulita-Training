# mulita-extractor-training

Training-side repository for the MulitaMiner embedded extraction model: data
engine (verification, labeling, dataset assembly), fine-tuning configs, and
artifact publication. The MulitaMiner tool never depends on this repo; this
repo consumes the tool as a library (segmentation, PDF reading, prompts) and
ships only published model artifacts back.

Design note: `MulitaMiner2/docs/superpowers/plans/2026-07-21-embedded-model-plan.md`.

## Contamination rule

`heldout.json` is the train/eval separation contract: per-scanner held-out
reports (evaluated with scanner-export baselines), denied stems (app duplicates
of held-outs; eval-only scanners), and eval-only hosts (the held-out apps'
hosts, denied across ALL scanners so those apps stay eval-only everywhere).
Cross-scanner overlap on other hosts is allowed by design (matched hosts carry
largely distinct finding sets). `build_dataset` skips and reports denied
examples.

## Layout

```
heldout.json               train/eval separation (held-outs, denied stems/hosts)
src/
  common.py                shared text helpers (norm_key, tokens, containment)
  build_dataset.py         scanner-agnostic assembler (CLI, --sources all)
  make_heldout_baselines.py  held-out OpenVAS xlsx from the campaign CSV
  sources/
    base.py                Example + LabelSource protocol (scanner-agnostic)
    openvas/               vulnnet CSV as gold labels (+ References parser)
    qualys/                scan CSV export as gold labels
    nessus/                "Vulnerabilities by Host" HTML export as gold labels
    zap/                   ZAP XML report as gold labels
  verify/
    pairing.py             1:1 PDF vs CSV pairing check
    content.py             field-content containment check
    source_vs_baseline.py  source targets vs the derived eval xlsx (mapping check)
  train/
    sft.py                 QLoRA SFT (Unsloth), loss masked to the assistant turn
    configs/               per-model training configs (qwen3-1.7b, qwen2.5-1.5b)
tests/                     unit tests for the data engine
data/                      inputs + generated dataset + heldout/ (gitignored)
```

## Training (on the GPU box, Docker)

The dataset is never committed; copy it to the box (`scp -r data/dataset ...`),
then run inside the official Unsloth image (Blackwell/RTX 50xx ready):

```
docker run --gpus all -v ~/mulita-extractor-training:/w -w /w -d \
  unsloth/unsloth python src/train/sft.py --config src/train/configs/qwen3-1.7b.json
```

Outputs land in `outputs/<name>/`: `adapter/`, `merged/` (fp16) and, with
`--gguf`, `gguf/` (q4_k_m) for Ollama/llama.cpp serving. Evaluation of the
tuned model runs in the tool repo against `data/heldout/` baselines.

Add a scanner by creating `sources/<scanner>/`, implementing
`sources.base.LabelSource`, and registering it in `sources/__init__.py`; the
assembler is unchanged.

## Metrics ownership

Extraction quality (BERTScore/ROUGE-L/F1/coverage) is measured by the tool's
`mulitaminer evaluate` against the baselines — never reimplemented here. This
repo owns only dataset metrics (verify/) and, later, training-process metrics
(loss curves, dataset-size learning curve) that orchestrate train -> the
tool's eval.

## Running

Scripts use the MulitaMiner2 environment (the `mulitaminer` package is there):

```
cd ../MulitaMiner2
uv run --no-sync python ../mulita-extractor-training/src/build_dataset.py --sources all
uv run --no-sync python ../mulita-extractor-training/src/make_heldout_baselines.py
uv run --no-sync python ../mulita-extractor-training/src/verify/source_vs_baseline.py qualys-csv
uv run --no-sync python -m pytest ../mulita-extractor-training/tests
```

Output (`data/dataset/`): `train.jsonl`, `val.jsonl`, `prompts/<scanner>.txt`
(the exact prompt each example was built against), `dataset_report.md`.
