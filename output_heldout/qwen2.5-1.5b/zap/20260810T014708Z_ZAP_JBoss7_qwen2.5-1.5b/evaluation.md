# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\zap\20260810T014708Z_ZAP_JBoss7_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\zap\ZAP_JBoss7.xlsx`
- source: ZAP — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 7
- extracted records: 7
- matched: 7  (recall 1.000, precision 1.000)

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
description  -      -       -           -           0.355    0.355   
solution     -      -       -           -           0.000    0.000   
impact       -      -       -           -           n/a      n/a     
references   -      0.662   0.662       -           -        -       
severity     1.000  -       -           -           -        -       
port         n/a    -       -           -           -        -       
protocol     n/a    -       -           -           -        -       
plugin       0.571  -       -           -           -        -       
instances    -      -       -           0.376       -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Information Disclosure - Suspicious Comments (0.889)
- **description**: Content Security Policy (CSP) Header Not Set (0.0); Missing Anti-clickjacking Header (0.0); Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.0); User Agent Fuzzer (0.0); Server Leaks Version Information via "Server" HTTP Response Header Field (0.488)
- **solution**: Content Security Policy (CSP) Header Not Set (0.0); Missing Anti-clickjacking Header (0.0); Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.0); Server Leaks Version Information via "Server" HTTP Response Header Field (0.0); X-Content-Type-Options Header Missing (0.0)
- **references**: Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.222); Missing Anti-clickjacking Header (0.286); User Agent Fuzzer (0.5); Server Leaks Version Information via "Server" HTTP Response Header Field (0.75); Content Security Policy (CSP) Header Not Set (0.875)
- **plugin**: Content Security Policy (CSP) Header Not Set (0.0); Missing Anti-clickjacking Header (0.0); Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.0)
- **instances**: Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s) (0.0); Content Security Policy (CSP) Header Not Set (0.14); Missing Anti-clickjacking Header (0.15); User Agent Fuzzer (0.267); X-Content-Type-Options Header Missing (0.583)

## Notes

- baseline never fills `impact`, `port`, `protocol` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
