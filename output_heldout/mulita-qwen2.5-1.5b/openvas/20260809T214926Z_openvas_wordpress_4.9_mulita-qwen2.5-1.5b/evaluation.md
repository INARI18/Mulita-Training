# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\mulita-qwen2.5-1.5b\openvas\20260809T214926Z_openvas_wordpress_4.9_mulita-qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\openvas\openvas_wordpress_4.9.xlsx`
- source: OPENVAS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 52
- extracted records: 54
- matched: 45  (recall 0.865, precision 0.833)

## block_id drops

- 3 dropped (unknown_id=3, duplicate_id=0, validation_error=0, unrecovered=0)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 4 retried (bad_json=4, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field                     exact  set_f1  set_f1_ids  rouge_l  token_f1
-----                     -----  ------  ----------  -------  --------
name                      -      -       -           1.000    1.000   
description               -      -       -           0.733    0.733   
solution                  -      -       -           0.529    0.529   
impact                    -      -       -           0.429    0.429   
references                -      0.624   0.624       -        -       
severity                  0.933  -       -           -        -       
port                      0.800  -       -           -        -       
protocol                  0.818  -       -           -        -       
cvss                      0.444  -       -           -        -       
insight                   -      -       -           0.207    0.207   
detection_result          -      -       -           0.733    0.733   
detection_method          -      -       -           0.634    0.634   
product_detection_result  -      -       -           0.984    0.984   
log_method                -      -       -           0.000    0.000   
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **description**: Apache HTTP Server HTTP/2 connection DoS Vulnerability (0.0); Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial-Of-Service Vulnerability (Jun 2017) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.40 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0)
- **solution**: Apache HTTP Server < 2.4.55 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.20 - 2.4.39 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.20 < 2.4.44 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server HTTP/2 connection DoS Vulnerability (0.0); Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux (0.0)
- **impact**: Apache HTTP Server HTTP/2 connection DoS Vulnerability (0.0); Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux (0.0); Apache HTTP Server < 2.4.38 mod_session_cookie Vulnerability - Linux (0.0); Apache HTTP Server Denial-Of-Service Vulnerability (Jun 2017) - Linux (0.0); Apache HTTP Server 2.4.0 < 2.4.42 Multiple Vulnerabilities - Linux (0.0)
- **references**: Apache HTTP Server HTTP/2 connection DoS Vulnerability (0.0); Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial-Of-Service Vulnerability (Jun 2017) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.40 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0)
- **severity**: Apache HTTP Server Detection Consolidation (0.0); Traceroute (0.0); OS Detection Consolidation and Reporting (0.0)
- **port**: Operating System (OS) End of Life (EOL) Detection (0.0); TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Hostname Determination Reporting (0.0); IP Forwarding Enabled - Active Check (0.0)
- **protocol**: Operating System (OS) End of Life (EOL) Detection (0.0); TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Hostname Determination Reporting (0.0); IP Forwarding Enabled - Active Check (0.0)
- **cvss**: Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0); Apache HTTP Server mod_auth_digest Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server Memory Access Vulnerability - Linux (0.0); Apache HTTP Server < 2.4.55 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.7 - 2.4.51 Multiple Vulnerabilities - Linux (0.0)
- **insight**: Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server Memory Access Vulnerability - Linux (0.0); Apache HTTP Server < 2.4.55 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.7 - 2.4.51 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.59 Multiple Vulnerabilities - Linux (0.0)
- **detection_result**: Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0); Apache HTTP Server mod_auth_digest Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server HTTP/2 connection DoS Vulnerability (0.0); Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial-Of-Service Vulnerability (Jun 2017) - Linux (0.0)
- **detection_method**: Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0); Apache HTTP Server mod_auth_digest Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.6 - 2.4.46 Tunneling Misconfiguration Vulnerability - Linux (0.0); Apache HTTP Server < 2.4.38 HTTP/2 DoS Vulnerability - Linux (0.0); Apache HTTP Server < 2.4.39 URL Normalization Vulnerability - Linux (0.0)
- **product_detection_result**: Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.743); Apache HTTP Server Denial of Service Vulnerability (Apr 2018) - Linux (0.754)
- **log_method**: Apache HTTP Server HTTP/2 connection DoS Vulnerability (0.0); Apache HTTP Server mod_http2 null pointer dereference DoS Vulnerability - Linux (0.0); Apache HTTP Server Denial-Of-Service Vulnerability (Jun 2017) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.40 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server 2.4.17 - 2.4.57 DoS Vulnerability - Linux (0.0)

## False negatives (in baseline, not extracted)

- Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux
- Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux
- Apache HTTP Server <= 2.4.52 Multiple Vulnerabilities - Linux
- Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux
- Apache HTTP Server < 2.4.60 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.49 Multiple Vulnerabilities - Linux

## False positives (extracted, not in baseline)

- BLOCK 1 (host: 172.31.1.83, port: 80/tcp)
- BLOCK 2 (host: 172.31.1.83, port: 80/tcp)
- BLOCK 3 (host: 172.31.1.83, port: 80/tcp)
- BLOCK 4 (host: 172.31.1.83, port: 80/tcp)
- BLOCK 5 (host: 172.31.1.83, port: 80/tcp)
- BLOCK 6 (host: 172.31.1.83, port: 80/tcp)
- BLOCK 7 (host: 172.31.1.83, port: 80/tcp)
- Apache HTTP Server OPTIONS Memory Leak Vulnerability (Optionsbleed) - Version C. →..
- Apache HTTP Server < 2.4.39 mod_auth_digest Access Control Bypass Vulnerability - Linux

## Notes

- baseline never fills `log_method` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
