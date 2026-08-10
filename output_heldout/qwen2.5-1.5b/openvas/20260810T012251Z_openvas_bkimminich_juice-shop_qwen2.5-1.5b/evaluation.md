# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\openvas\20260810T012251Z_openvas_bkimminich_juice-shop_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\openvas\openvas_bkimminich_juice-shop.xlsx`
- source: OPENVAS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 18
- extracted records: 18
- matched: 15  (recall 0.833, precision 0.833)

## block_id drops

- 1 dropped (unknown_id=1, duplicate_id=0, validation_error=0, unrecovered=0)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 0 (clean): bad_json=0, bad_shape=0
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field                     exact  set_f1  set_f1_ids  rouge_l  token_f1
-----                     -----  ------  ----------  -------  --------
name                      -      -       -           1.000    1.000   
description               -      -       -           0.756    0.756   
solution                  -      -       -           0.000    0.000   
impact                    -      -       -           0.000    0.000   
references                -      0.000   0.000       -        -       
severity                  0.933  -       -           -        -       
port                      0.600  -       -           -        -       
protocol                  0.643  -       -           -        -       
cvss                      0.000  -       -           -        -       
insight                   -      -       -           0.000    0.000   
detection_result          -      -       -           0.405    0.405   
detection_method          -      -       -           0.000    0.000   
product_detection_result  -      -       -           n/a      n/a     
log_method                -      -       -           0.000    0.000   
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **description**: Allowed HTTP Methods Enumeration (0.0); Check open ports (0.279); robot.txt / robots.txt exists on the Web Server (HTTP) (0.341); CPE Inventory (0.438); TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.526)
- **solution**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); security.txt Detection (HTTP) (0.0); robot.txt / robots.txt exists on the Web Server (HTTP) (0.0)
- **impact**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0)
- **references**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); security.txt Detection (HTTP) (0.0); HTTP Security Headers Detection (0.0)
- **severity**: OS Detection Consolidation and Reporting (0.0)
- **port**: OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0); jQuery Detection Consolidation (0.0); CPE Inventory (0.0)
- **protocol**: OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0); jQuery Detection Consolidation (0.0); Hostname Determination Reporting (0.0)
- **cvss**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); Response Time / No 404 Error Code Check (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0)
- **insight**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); Response Time / No 404 Error Code Check (0.0); Traceroute (0.0); security.txt Detection (HTTP) (0.0); Allowed HTTP Methods Enumeration (0.0)
- **detection_result**: Web Application Scanning Consolidation / Info Reporting (0.0); CPE Inventory (0.0); robot.txt / robots.txt exists on the Web Server (HTTP) (0.0); Hostname Determination Reporting (0.0); Check open ports (0.0)
- **detection_method**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); Response Time / No 404 Error Code Check (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0)
- **log_method**: TCP Sequence Number Approximation Reset DoS Vulnerability (Apr 2004) (0.0); Response Time / No 404 Error Code Check (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Traceroute (0.0)

## False negatives (in baseline, not extracted)

- Backup File Scanner (HTTP) - Unreliable Detection Reporting
- TCP Timestamps Information Disclosure
- ICMP Timestamp Reply Information Disclosure

## False positives (extracted, not in baseline)

- Block 1 (host: 172.30.7.1, port: general/icmp)
- Block 2 (host: 172.30.7.1, port: general/icmp)
- Block 3 (host: 172.30.7.1, port: general/tcp)

## Notes

- baseline never fills `product_detection_result`, `log_method` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
