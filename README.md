# mulita-extractor-training

Training-side repository for the MulitaMiner embedded extraction model: data
engine (verification, labeling, dataset assembly), fine-tuning configs, and
artifact publication. The MulitaMiner tool never depends on this repo; this
repo consumes the tool as a library (segmentation, PDF reading, prompts) and
ships only published model artifacts back.

Design note: `MulitaMiner2/docs/superpowers/plans/2026-07-21-embedded-model-plan.md`.

## Contamination rule

The tool's evaluation baselines (everything under `MulitaMiner2/resources/`)
are the test set and never enter training. `build_dataset` enforces this and
aborts if any source example overlaps a baseline host or report.

## Layout

```
src/
  common.py                shared text helpers (norm_key, tokens, containment)
  build_dataset.py         scanner-agnostic assembler (CLI)
  sources/
    base.py                Example + LabelSource protocol
    openvas_csv.py         OpenVAS vulnnet CSV as gold labels
    openvas_references.py  OpenVAS References-section parser
  verify/
    pairing.py             1:1 PDF vs CSV pairing check
    content.py             field-content containment check
tests/                     unit tests for the data engine
data/                      inputs + generated dataset (gitignored)
```

Add a training-data source by implementing `sources.base.LabelSource` and
registering it in `sources/__init__.py`; the assembler is unchanged.

## Running

Scripts use the MulitaMiner2 environment (the `mulitaminer` package is there):

```
cd ../MulitaMiner2
uv run --no-sync python ../mulita-extractor-training/src/build_dataset.py
uv run --no-sync python ../mulita-extractor-training/src/verify/pairing.py
uv run --no-sync python -m pytest ../mulita-extractor-training/tests
```

Output (`data/dataset/`): `train.jsonl`, `val.jsonl`, `prompts/<scanner>.txt`
(the exact prompt each example was built against), `dataset_report.md`.
