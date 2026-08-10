# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\mulita-qwen2.5-1.5b\openvas\20260809T212852Z_openvas_bkimminich_juice-shop_mulita-qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\openvas\openvas_bkimminich_juice-shop.xlsx`
- source: OPENVAS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 18
- extracted records: 18
- matched: 18  (recall 1.000, precision 1.000)

## block_id drops

- 1 dropped (unknown_id=1, duplicate_id=0, validation_error=0, unrecovered=0)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 1 retried (bad_json=1, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field                     exact  set_f1  set_f1_ids  rouge_l  token_f1
-----                     -----  ------  ----------  -------  --------
name                      -      -       -           1.000    1.000   
description               -      -       -           0.974    0.974   
solution                  -      -       -           0.667    0.667   
impact                    -      -       -           1.000    1.000   
references                -      0.417   0.483       -        -       
severity                  0.833  -       -           -        -       
port                      0.556  -       -           -        -       
protocol                  0.625  -       -           -        -       
cvss                      0.389  -       -           -        -       
insight                   -      -       -           0.200    0.200   
detection_result          -      -       -           0.665    0.665   
detection_method          -      -       -           0.784    0.784   
product_detection_result  -      -       -           n/a      n/a     
log_method                -      -       -           0.000    0.000   
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **description**: Allowed HTTP Methods Enumeration (0.706); security.txt Detection (HTTP) (0.894); Response Time / No 404 Error Code Check (0.927)
- **solution**: security.txt Detection (HTTP) (0.0); robot.txt / robots.txt exists on the Web Server (HTTP) (0.0)
- **references**: TCP Timestamps Information Disclosure (0.0); IP Forwarding Enabled - Active Check (0.0); HTTP Security Headers Detection (0.0); Web Application Scanning Consolidation / Info Reporting (0.0); CPE Inventory (0.0)
- **severity**: OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0)
- **port**: TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0)
- **protocol**: TCP Timestamps Information Disclosure (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0); jQuery Detection Consolidation (0.0)
- **cvss**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); Response Time / No 404 Error Code Check (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0)
- **insight**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Response Time / No 404 Error Code Check (0.0); Traceroute (0.0)
- **detection_result**: Backup File Scanner (HTTP) - Unreliable Detection Reporting (0.0); TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Web Application Scanning Consolidation / Info Reporting (0.0); robot.txt / robots.txt exists on the Web Server (HTTP) (0.0)
- **detection_method**: Backup File Scanner (HTTP) - Unreliable Detection Reporting (0.0); TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Traceroute (0.588); robot.txt / robots.txt exists on the Web Server (HTTP) (0.716)
- **log_method**: HTTP Security Headers Detection (0.0); Web Application Scanning Consolidation / Info Reporting (0.0); jQuery Detection Consolidation (0.0)

## Notes

- baseline never fills `product_detection_result`, `log_method` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
