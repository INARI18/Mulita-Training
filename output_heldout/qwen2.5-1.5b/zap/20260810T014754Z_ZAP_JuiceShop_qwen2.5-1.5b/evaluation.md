# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\zap\20260810T014754Z_ZAP_JuiceShop_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\zap\ZAP_JuiceShop.xlsx`
- source: ZAP — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 10
- extracted records: 10
- matched: 9  (recall 0.900, precision 0.900)

## block_id drops

- 0 (clean): unknown_id=0, duplicate_id=0, validation_error=0, unrecovered=0
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 1 retried (bad_json=1, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field        exact  set_f1  set_f1_ids  structural  rouge_l  token_f1
-----        -----  ------  ----------  ----------  -------  --------
name         -      -       -           -           0.984    0.984   
description  -      -       -           -           0.667    0.667   
solution     -      -       -           -           0.000    0.000   
impact       -      -       -           -           n/a      n/a     
references   -      0.222   0.222       -           -        -       
severity     1.000  -       -           -           -        -       
port         n/a    -       -           -           -        -       
protocol     n/a    -       -           -           -        -       
plugin       0.889  -       -           -           -        -       
instances    -      -       -           0.585       -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Timestamp Disclosure - Unix (0.857)
- **description**: Private IP Disclosure (0.0); Timestamp Disclosure - Unix (0.0); User Agent Fuzzer (0.0)
- **solution**: SQL Injection (0.0); Content Security Policy (CSP) Header Not Set (0.0); Cross-Domain Misconfiguration (0.0); Missing Anti-clickjacking Header (0.0); Session ID in URL Rewrite (0.0)
- **references**: SQL Injection (0.0); Content Security Policy (CSP) Header Not Set (0.0); Cross-Domain Misconfiguration (0.0); Missing Anti-clickjacking Header (0.0); Private IP Disclosure (0.0)
- **plugin**: Timestamp Disclosure - Unix (0.0)
- **instances**: Session ID in URL Rewrite (0.18); User Agent Fuzzer (0.267); Content Security Policy (CSP) Header Not Set (0.414); X-Content-Type-Options Header Missing (0.533); Timestamp Disclosure - Unix (0.673)

## False negatives (in baseline, not extracted)

- Modern Web Application

## False positives (extracted, not in baseline)

- Informational Modern Web Application

## Notes

- baseline never fills `impact`, `port`, `protocol` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
