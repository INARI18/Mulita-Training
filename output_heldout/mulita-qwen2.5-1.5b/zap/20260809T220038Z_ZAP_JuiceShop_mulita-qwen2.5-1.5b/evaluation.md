# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\mulita-qwen2.5-1.5b\zap\20260809T220038Z_ZAP_JuiceShop_mulita-qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\zap\ZAP_JuiceShop.xlsx`
- source: ZAP — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 10
- extracted records: 9
- matched: 9  (recall 0.900, precision 1.000)

## block_id drops

- 1 dropped (unknown_id=0, duplicate_id=0, validation_error=0, unrecovered=1)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 3 retried (bad_json=3, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field        exact  set_f1  set_f1_ids  structural  rouge_l  token_f1
-----        -----  ------  ----------  ----------  -------  --------
name         -      -       -           -           1.000    1.000   
description  -      -       -           -           0.778    0.778   
solution     -      -       -           -           0.953    0.953   
impact       -      -       -           -           n/a      n/a     
references   -      0.741   0.741       -           -        -       
severity     1.000  -       -           -           -        -       
port         n/a    -       -           -           -        -       
protocol     n/a    -       -           -           -        -       
plugin       1.000  -       -           -           -        -       
instances    -      -       -           0.311       -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **description**: Content Security Policy (CSP) Header Not Set (0.0); Cross-Domain Misconfiguration (0.0)
- **solution**: Session ID in URL Rewrite (0.793); Private IP Disclosure (0.829)
- **references**: Session ID in URL Rewrite (0.0); Private IP Disclosure (0.0); Cross-Domain Misconfiguration (0.667)
- **instances**: SQL Injection (0.0); Content Security Policy (CSP) Header Not Set (0.0); Cross-Domain Misconfiguration (0.0); Missing Anti-clickjacking Header (0.0); Session ID in URL Rewrite (0.0)

## False negatives (in baseline, not extracted)

- Modern Web Application

## Notes

- baseline never fills `impact`, `port`, `protocol` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
