# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\qualys\20260810T013953Z_Qualys_VulnLab_scan-b_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\qualys\Qualys_VulnLab_scan-b.xlsx`
- source: QUALYS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 419
- extracted records: 402
- matched: 381  (recall 0.909, precision 0.948)

## block_id drops

- 158 dropped (unknown_id=64, duplicate_id=78, validation_error=0, unrecovered=16)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 8 retried (bad_json=8, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field        exact  set_f1  set_f1_ids  rouge_l  token_f1
-----        -----  ------  ----------  -------  --------
name         -      -       -           0.963    0.963   
description  -      -       -           0.598    0.608   
solution     -      -       -           0.011    0.011   
impact       -      -       -           0.705    0.707   
references   -      0.250   0.257       -        -       
severity     0.580  -       -           -        -       
port         0.000  -       -           -        -       
protocol     0.000  -       -           -        -       
category     -      -       -           0.037    0.037   
plugin       0.724  -       -           -        -       
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: cAdvisor (Container Advisor) Detected (0.727); PhpMyAdmin SQL Injection Vulnerability (PMASA-2019-2) (0.727); Nginx Web Server Detected (0.727); SSL Server default Diffie-Hellman prime information (0.737); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2025-23048) (0.759)
- **description**: Content-Security-Policy HTTP Security Header Not Detected (0.0); Apache httpd Server ap_get_basic_auth_pw() Authentication Bypass Vulnerability (0.0); Hypertext Preprocessor (PHP) Security Update (0.0); PHP Server Detected (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2024-47252) (0.0)
- **solution**: Session Cookie Does Not Contain the "Secure" Attribute (0.0); AutoComplete Attribute Not Disabled for Password in Form Based Authentication (0.0); Open TCP Services List (0.0); Referrer-Policy HTTP Security Header Not Detected (0.0); Web Server Uses Plain-Text Form Based Authentication (0.0)
- **impact**: Open TCP Services List (0.0); HTTP Response Method and Header Information Collected (0.0); URLScan Security Tool Detected (0.0); Apache httpd Server Uninitialized memory reflection in mod_auth_digest Information Disclosure Vulnerability (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0)
- **references**: Web Server Supports HTTP Request Pipelining (0.0); Hypertext Preprocessor (PHP) Multiple Security Vulnerabilities (81738, 81739) (0.0); Apache httpd Server Uninitialized memory reflection in mod_auth_digest Information Disclosure Vulnerability (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) mod_proxy X-Forwarded-For dropped by hop-by-hop mechanism Vulnerability (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0)
- **severity**: Content-Security-Policy HTTP Security Header Not Detected (0.0); Web Server HTTP Protocol Versions (0.0); HTTP Methods Returned by OPTIONS Request (0.0); Web Server Supports HTTP Request Pipelining (0.0); Hypertext Preprocessor (PHP) Multiple Security Vulnerabilities (81738, 81739) (0.0)
- **port**: Session Cookie Does Not Contain the "Secure" Attribute (0.0); AutoComplete Attribute Not Disabled for Password in Form Based Authentication (0.0); Content-Security-Policy HTTP Security Header Not Detected (0.0); Web Server HTTP Protocol Versions (0.0); Default Web Page ( Follow HTTP Redirection) (0.0)
- **protocol**: Session Cookie Does Not Contain the "Secure" Attribute (0.0); AutoComplete Attribute Not Disabled for Password in Form Based Authentication (0.0); Content-Security-Policy HTTP Security Header Not Detected (0.0); Web Server HTTP Protocol Versions (0.0); Default Web Page ( Follow HTTP Redirection) (0.0)
- **category**: Session Cookie Does Not Contain the "Secure" Attribute (0.0); AutoComplete Attribute Not Disabled for Password in Form Based Authentication (0.0); Content-Security-Policy HTTP Security Header Not Detected (0.0); Web Server HTTP Protocol Versions (0.0); DNS Host Name (0.0)
- **plugin**: Apache httpd Server Uninitialized memory reflection in mod_auth_digest Information Disclosure Vulnerability (0.0); Apache HTTP Server Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Vulnerabilities (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Buffer Overflow Vulnerability (0.0); Apache Hypertext Transfer Protocol (HTTP) Server Out-of-bounds Write Vulnerability (0.0)

## False negatives (in baseline, not extracted)

- Default Web Page
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Security Vulnerabilities (CVE-2022-28330, CVE-2022-28614, CVE-2022-28615, CVE-2022-29404, CVE-2022-30556)
- Apache httpd Server Information Disclosure Vulnerability (OptionsBleed)
- Apache HTTP Server Privilege Escalation From Modules Scripts
- Apache Hypertext Transfer Protocol (HTTP) Server Request Smuggling Vulnerability
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2024-47252)
- TCP Sequence Number Approximation Based Denial of Service
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Security Vulnerabilities (CVE-2023-38709, CVE-2024-24795)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2025-49812)
- TCP Sequence Number Approximation Based Denial of Service
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2024-43204)
- Default Web Page
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.60 Multiple Security Vulnerabilities
- TCP Sequence Number Approximation Based Denial of Service
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Security Vulnerabilities (CVE-2023-38709, CVE-2024-24795)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2025-49812)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-44186)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-49975)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-48913)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-34356)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-44631)
- Web Server Version
- Secure Sockets Layer/Transport Layer Security (SSL/TLS) Key Exchange Methods
- Default Web Page
- Apache Hypertext Transfer Protocol Server (HTTP Server) mod_proxy X-Forwarded-For dropped by hop-by-hop mechanism Vulnerability
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Security Vulnerabilities (CVE-2022-28330, CVE-2022-28614, CVE-2022-28615, CVE-2022-29404, CVE-2022-30556)
- PHP 7 Remote Code Execution Vulnerability
- TCP Sequence Number Approximation Based Denial of Service
- Apache Hypertext Transfer Protocol Server (HTTP Server) Multiple Security Vulnerabilities (CVE-2023-38709, CVE-2024-24795)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2024-43204)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.64 Security Vulnerabilities (CVE-2025-49630)
- Apache Hypertext Transfer Protocol Server (HTTP Server) Prior to 2.4.68 Security Vulnerabilities (CVE-2026-44631)
- Default Web Page
- PhpMyAdmin Multiple Vulnerabilities (PMASA-2018-3,PMASA-2018-4)
- PhpMyAdmin Cross-Site Scripting Vulnerability (PMASA-2018-5)
- AutoComplete Attribute Not Disabled for Password in Form Based Authentication
- Default Web Page
- Default Web Page ( Follow HTTP Redirection)

## False positives (extracted, not in baseline)

- Block 11
- Web server
- Default Web Page port 80/tcp
- Default Web Page port 8200/tcp
- Apache HTTP Server Prior to 2.4.68 Security Vulnerabilities
- Web Server Version port 80/tcp
- Apache HTTP Server Prior to 2.4.64 Security Vulnerabilities
- Apache HTTP Server Prior to 2.4.64 Security Vulnerabilities
- Apache HTTP Server Prior to 2.4.64 Security Vulnerabilities
- Scan Results page 431
- Apache HTTP Server Prior to 2.4.68 Security Vulnerabilities
- Default Web Page port 80/tcp
- Apache HTTP Server mod_proxy X-Forwarded-For dropped by hop port 80/tcp
- Apache HTTP Server Multiple Security Vulnerabilities
- Apache HTTP Server Request Smuggling Vulnerability
- Apache HTTP Server Multiple Security Vulnerabilities
- Apache HTTP Server Prior to 2.4.64 Security Vulnerabilities
- Apache HTTP Server Prior to 2.4.68 Security Vulnerabilities
- Apache HTTP Server Prior to 2.4.68 Security Vulnerabilities
- Apache HTTP Server Prior to 2.4.68 Security Vulnerabilities
- Default Web Page port 3000/tcp
