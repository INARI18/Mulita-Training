# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\openvas\20260810T013711Z_openvas_wordpress_4.9_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\openvas\openvas_wordpress_4.9.xlsx`
- source: OPENVAS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 52
- extracted records: 52
- matched: 36  (recall 0.692, precision 0.692)

## block_id drops

- 6 dropped (unknown_id=1, duplicate_id=3, validation_error=0, unrecovered=2)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 6 retried (bad_json=6, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field                     exact  set_f1  set_f1_ids  rouge_l  token_f1
-----                     -----  ------  ----------  -------  --------
name                      -      -       -           0.995    0.995   
description               -      -       -           0.583    0.598   
solution                  -      -       -           0.000    0.000   
impact                    -      -       -           0.000    0.000   
references                -      0.000   0.000       -        -       
severity                  0.917  -       -           -        -       
port                      0.750  -       -           -        -       
protocol                  0.794  -       -           -        -       
cvss                      0.056  -       -           -        -       
insight                   -      -       -           0.000    0.000   
detection_result          -      -       -           0.675    0.675   
detection_method          -      -       -           0.048    0.048   
product_detection_result  -      -       -           0.041    0.041   
log_method                -      -       -           0.000    0.000   
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Apache HTTP Server Denial of Service Vulnerability (Apr 2018) - Linux (0.947); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.957); Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.957); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.963)
- **description**: Apache HTTP Server 2.4.20 < 2.4.44 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.38 mod_session_cookie Vulnerability - Linux (0.0); Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial of Service Vulnerability (Apr 2018) - Linux (0.0); Apache HTTP Server 2.4.7 - 2.4.51 Multiple Vulnerabilities - Linux (0.055)
- **solution**: Operating System (OS) End of Life (EOL) Detection (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0)
- **impact**: Operating System (OS) End of Life (EOL) Detection (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0)
- **references**: Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0)
- **severity**: Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial of Service Vulnerability (Apr 2018) - Linux (0.0); Apache HTTP Server 2.4.x < 2.4.66 Improper Neutralization Vulnerability - Linux (0.0)
- **port**: Operating System (OS) End of Life (EOL) Detection (0.0); TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Hostname Determination Reporting (0.0); IP Forwarding Enabled - Active Check (0.0)
- **protocol**: Operating System (OS) End of Life (EOL) Detection (0.0); TCP Timestamps Information Disclosure (0.0); Hostname Determination Reporting (0.0); IP Forwarding Enabled - Active Check (0.0); Apache HTTP Server Detection Consolidation (0.0)
- **cvss**: Operating System (OS) End of Life (EOL) Detection (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0)
- **insight**: Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0)
- **detection_result**: Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial of Service Vulnerability (Apr 2018) - Linux (0.0); HTTP Server type and version (0.0); HTTP Security Headers Detection (0.0); Web Application Scanning Consolidation / Info Reporting (0.0)
- **detection_method**: Operating System (OS) End of Life (EOL) Detection (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0)
- **product_detection_result**: Operating System (OS) End of Life (EOL) Detection (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0)
- **log_method**: Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); Apache HTTP Server 2.4.20 < 2.4.44 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.38 mod_session_cookie Vulnerability - Linux (0.0); Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial of Service Vulnerability (Apr 2018) - Linux (0.0)

## False negatives (in baseline, not extracted)

- Apache HTTP Server <= 2.4.52 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.60 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.49 Multiple Vulnerabilities - Linux
- Apache HTTP Server 2.4.20 - 2.4.39 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.58 mod_macro Out-of-bounds Read Vulnerability - Linux
- Apache HTTP Server HTTP/2 connection DoS Vulnerability
- Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux
- Apache HTTP Server Denial-Of-Service Vulnerability (Jun 2017) - Linux
- Apache HTTP Server 2.4.7 - 2.4.65 Authentication Bypass Vulnerability - Linux
- Apache HTTP Server 2.4.6 - 2.4.46 Tunneling Misconfiguration Vulnerability - Linux
- Apache HTTP Server < 2.4.38 HTTP/2 DoS Vulnerability - Linux
- Apache HTTP Server < 2.4.39 URL Normalization Vulnerability - Linux
- Apache HTTP Server < 2.4.64 Multiple Vulnerabilities - Linux
- Apache HTTP Server 2.4.17 < 2.4.64 DoS Vulnerability - Linux
- Apache HTTP Server < 2.4.66 SSI Vulnerability - Linux

## False positives (extracted, not in baseline)

- Critical (CVSS: 9.8)
- BLOCK 6
- Critical (CVSS: 9.8)
- Apache HTTP Server OPTIONS Memory Leak Vulnerability (Optionsbleed) - Version
- BLOCK 18
- BLOCK 19
- BLOCK 21
- BLOCK 22
- BLOCK 23
- BLOCK 26
- BLOCK 33
- BLOCK 34
- BLOCK 35
- BLOCK 37
- BLOCK 38
- BLOCK 39

## Notes

- baseline never fills `log_method` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
