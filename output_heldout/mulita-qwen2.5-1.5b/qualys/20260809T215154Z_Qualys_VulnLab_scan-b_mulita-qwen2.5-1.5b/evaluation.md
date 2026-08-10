# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\mulita-qwen2.5-1.5b\qualys\20260809T215154Z_Qualys_VulnLab_scan-b_mulita-qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\qualys\Qualys_VulnLab_scan-b.xlsx`
- source: QUALYS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 419
- extracted records: 402
- matched: 399  (recall 0.952, precision 0.993)

## block_id drops

- 74 dropped (unknown_id=55, duplicate_id=3, validation_error=0, unrecovered=16)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 11 retried (bad_json=11, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field        exact  set_f1  set_f1_ids  rouge_l  token_f1
-----        -----  ------  ----------  -------  --------
name         -      -       -           0.991    0.991   
description  -      -       -           0.923    0.924   
solution     -      -       -           0.898    0.898   
impact       -      -       -           0.887    0.887   
references   -      0.725   0.725       -        -       
severity     0.855  -       -           -        -       
port         0.897  -       -           -        -       
protocol     0.890  -       -           -        -       
category     -      -       -           0.501    0.501   
plugin       0.744  -       -           -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Apache HTTP Server multiple vulnerabilities (0.769); Web Server HTTP Protocol Versions (0.769); Secure Sockets Layer/Transport Layer Security (SSL/TLS) Server Supports Transport Layer Security (TLSv1.1) (0.778); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2024-43394) (0.824); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2024-42516) (0.824)
- **description**: Content-Security-Policy HTTP Security Header Not Detected (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.55 Multiple Security Vulnerabilities (0.0); Apache httpd Server ap_get_basic_auth_pw() Authentication Bypass Vulnerability (0.0); Hypertext Preprocessor (PHP) Multiple Vulnerabilities (Unauthenticated) (0.0); Content-Security-Policy HTTP Security Header Not Detected (0.0)
- **solution**: Apache HTTP Server Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.55 Multiple Security Vulnerabilities (0.0); Open TCP Services List (0.0); Hypertext Preprocessor (PHP) Multiple Vulnerabilities (Unauthenticated) (0.0); jQuery Cross-Site Scripting Vulnerability (0.0)
- **impact**: Session Cookie Does Not Contain the "Secure" Attribute (0.0); AutoComplete Attribute Not Disabled for Password in Form Based Authentication (0.0); HTTP Response Method and Header Information Collected (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.55 Multiple Security Vulnerabilities (0.0)
- **references**: Apache Hypertext Transfer Protocol (HTTP) Server Buffer Overflow Vulnerability (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.55 Multiple Security Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.67 Security Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.67 Security Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-42535) (0.0)
- **severity**: Content-Security-Policy HTTP Security Header Not Detected (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.55 Multiple Security Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.67 Security Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.67 Security Vulnerabilities (0.0)
- **port**: Hypertext Preprocessor (PHP) Multiple Security Vulnerabilities (81738, 81739) (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Buffer Overflow Vulnerability (0.0); Apache Hypertext Transfer Protocol (HTTP) Server NULL Pointer Dereference and Server Side Request Forgery (SSRF) Vulnerability (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Out-of-bounds Write Vulnerability (0.0)
- **protocol**: Hypertext Preprocessor (PHP) Multiple Security Vulnerabilities (81738, 81739) (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Buffer Overflow Vulnerability (0.0); Apache Hypertext Transfer Protocol (HTTP) Server NULL Pointer Dereference and Server Side Request Forgery (SSRF) Vulnerability (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Out-of-bounds Write Vulnerability (0.0)
- **category**: Web Server HTTP Protocol Versions (0.0); DNS Host Name (0.0); Host Scan Time - Scanner (0.0); Host Names Found (0.0); Scan Activity per Port (0.0)
- **plugin**: Web Server HTTP Protocol Versions (0.0); DNS Host Name (0.0); Host Scan Time - Scanner (0.0); Apache httpd Server Uninitialized memory reflection in mod_auth_digest Information Disclosure Vulnerability (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Buffer Overflow Vulnerability (0.0)

## False negatives (in baseline, not extracted)

- Apache httpd Server Information Disclosure Vulnerability (OptionsBleed)
- Apache HTTP Server Privilege Escalation From Modules Scripts
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Vulnerabilities
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.60 Multiple Security Vulnerabilities
- TCP Sequence Number Approximation Based Denial of Service
- TCP Sequence Number Approximation Based Denial of Service
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.60 Multiple Security Vulnerabilities
- TCP Sequence Number Approximation Based Denial of Service
- Secure Sockets Layer/Transport Layer Security (SSL/TLS) Key Exchange Methods
- PHP 7 Remote Code Execution Vulnerability
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Vulnerabilities
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.60 Multiple Security Vulnerabilities
- TCP Sequence Number Approximation Based Denial of Service
- Hypertext Preprocessor (PHP) Multiple Security Vulnerabilities (81726, 81727)
- PhpMyAdmin Multiple Vulnerabilities (PMASA-2018-3,PMASA-2018-4)
- Web Server Uses Plain-Text Form Based Authentication
- Session Cookie Does Not Contain the "Secure" Attribute
- AutoComplete Attribute Not Disabled for Password in Form Based Authentication
- Default Web Page
- Default Web Page ( Follow HTTP Redirection)

## False positives (extracted, not in baseline)

- Un-authenticated Access via Unencrypted Channel
- Web server
- Apache Partial HTTP Request Denial of Service Vulnerability - Zero Day
