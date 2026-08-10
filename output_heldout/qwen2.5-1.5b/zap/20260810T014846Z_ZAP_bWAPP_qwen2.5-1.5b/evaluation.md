# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\zap\20260810T014846Z_ZAP_bWAPP_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\zap\ZAP_bWAPP.xlsx`
- source: ZAP — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 6
- extracted records: 6
- matched: 6  (recall 1.000, precision 1.000)

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
name         -      -       -           -           1.000    1.000   
description  -      -       -           -           0.816    0.816   
solution     -      -       -           -           0.000    0.000   
impact       -      -       -           -           n/a      n/a     
references   -      0.347   0.347       -           -        -       
severity     1.000  -       -           -           -        -       
port         n/a    -       -           -           -        -       
protocol     n/a    -       -           -           -        -       
plugin       1.000  -       -           -           -        -       
instances    -      -       -           0.800       -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **description**: Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.407); Server Leaks Version Information via "Server" HTTP Response Header Field (0.488)
- **solution**: Application Error Disclosure (0.0); Content Security Policy (CSP) Header Not Set (0.0); Missing Anti-clickjacking Header (0.0); Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.0); Server Leaks Version Information via "Server" HTTP Response Header Field (0.0)
- **references**: Application Error Disclosure (0.0); Content Security Policy (CSP) Header Not Set (0.0); Missing Anti-clickjacking Header (0.0); Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.333); Server Leaks Version Information via "Server" HTTP Response Header Field (0.75)
- **instances**: Missing Anti-clickjacking Header (0.7); Application Error Disclosure (0.8); Content Security Policy (CSP) Header Not Set (0.8); Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.8); X-Content-Type-Options Header Missing (0.8)

## Notes

- baseline never fills `impact`, `port`, `protocol` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
