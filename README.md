# mulita-extractor-training

Training-side repository for the MulitaMiner embedded extraction model:
data engine (dataset verification, mapping, synthesis), fine-tuning
configs, and artifact publication. The MulitaMiner tool never depends on
this repo; this repo consumes the tool as a library (segmentation, PDF
reading) and ships only published model artifacts back.

Design notes live in the tool repo:
`MulitaMiner2/docs/superpowers/plans/2026-07-21-embedded-model-plan.md`.

## Contamination rule

The MulitaMiner evaluation baselines (everything under
`MulitaMiner2/resources/`) are the test set. They never enter training in
any form. Data in `data/` (vulnnet scans) is the training pool.

## Running

Scripts use the MulitaMiner2 environment (the `mulitaminer` package is
installed there in editable mode):

```
cd ../MulitaMiner2
uv run --no-sync python ../mulita-extractor-training/src/verify_pairing.py
```

## Layout

- `data/pdfs/` - 129 vulnnet OpenVAS PDF reports (local only, gitignored)
- `data/vulnnet_scans_openvas.csv` - OpenVAS CSV export of the same scans
- `src/verify_pairing.py` - 1:1 PDF vs CSV verification per host; nothing
  enters the dataset unless counts and names match exactly
