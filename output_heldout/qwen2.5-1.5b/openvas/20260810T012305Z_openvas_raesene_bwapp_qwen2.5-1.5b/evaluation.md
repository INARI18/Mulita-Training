# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\qwen2.5-1.5b\openvas\20260810T012305Z_openvas_raesene_bwapp_qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\openvas\openvas_raesene_bwapp.xlsx`
- source: OPENVAS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 214
- extracted records: 223
- matched: 158  (recall 0.738, precision 0.709)

## block_id drops

- 120 dropped (unknown_id=57, duplicate_id=42, validation_error=0, unrecovered=21)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 34 retried (bad_json=34, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field                     exact  set_f1  set_f1_ids  rouge_l  token_f1
-----                     -----  ------  ----------  -------  --------
name                      -      -       -           0.946    0.946   
description               -      -       -           0.441    0.454   
solution                  -      -       -           0.003    0.004   
impact                    -      -       -           0.000    0.000   
references                -      0.000   0.007       -        -       
severity                  0.823  -       -           -        -       
port                      0.937  -       -           -        -       
protocol                  0.962  -       -           -        -       
cvss                      0.247  -       -           -        -       
insight                   -      -       -           0.001    0.001   
detection_result          -      -       -           0.407    0.407   
detection_method          -      -       -           0.014    0.014   
product_detection_result  -      -       -           0.263    0.265   
log_method                -      -       -           0.000    0.000   
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: PHP < 5.6.12 Multiple DoS Vulnerabilities - Linux (0.429); Oracle MySQL Server <= 5.7.34 / 8.0 <= 8.0.25 Security Update (cpujul2021) - Linux (0.444); PHP < 5.5.37, 5.6.x < 5.6.23, 7.x < 7.0.8 Multiple Vulnerabilities (Aug 2016) - Linux (0.5); Oracle MySQL Server <= 5.7.41, 8.x <= 8.0.32 Security Update (cpuapr2023) - Linux (0.529); Oracle MySQL Server <= 5.5.51 Security Update (cpuoct2016) - Linux (0.6)
- **description**: Oracle Mysql Security Update (cpuoct2018 - 02) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); PHP < 5.4.40, 5.5.x < 5.5.24, 5.6.x < 5.6.8 Multiple Vulnerabilities - Linux (0.0); Oracle MySQL Server <= 5.7.35 / 8.0 <= 8.0.26 Security Update (cpuoct2021) - Linux (0.0)
- **solution**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **impact**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); PHP < 5.5.27, 5.6.x < 5.6.11 Arbitrary Code Execution Vulnerability (Aug 2016) - Linux (0.0); PHP < 5.6.27, 7.x < 7.0.12 Multiple DoS Vulnerabilities (Oct 2016) - Linux (0.0)
- **references**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **severity**: PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); PHP < 5.6.30, 7.x < 7.0.15, 7.1.x < 7.1.1 Multiple Vulnerabilities (Jan 2017) - Linux (0.0); PHP < 5.4.45, 5.5.x < 5.5.29, 5.6.x < 5.6.13 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); PHP < 5.4.40, 5.5.x < 5.5.24, 5.6.x < 5.6.8 Multiple Vulnerabilities - Linux (0.0)
- **port**: Oracle MySQL Server <= 5.7.42, 8.x <= 8.0.33 Security Update (cpuoct2023) - Linux (0.0); Oracle MySQL Server <= 5.5.48 / 5.6 <= 5.6.29 / 5.7 <= 5.7.10 Security Update (cpujul2016) - Linux (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Traceroute (0.0); CPE Inventory (0.0)
- **protocol**: Traceroute (0.0); PHP Detection Consolidation (0.0); Hostname Determination Reporting (0.0); OS Detection Consolidation and Reporting (0.0); IP Forwarding Enabled - Active Check (0.0)
- **cvss**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **insight**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **detection_result**: PHP < 5.5.37, 5.6.x < 5.6.23, 7.x < 7.0.8 Multiple Vulnerabilities (Aug 2016) - Linux (0.0); Oracle Mysql Security Update (cpuoct2018 - 02) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0); PHP < 5.4.40, 5.5.x < 5.5.24, 5.6.x < 5.6.8 Multiple Vulnerabilities - Linux (0.0)
- **detection_method**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **product_detection_result**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **log_method**: Oracle MySQL Server <= 5.7.41, 8.x <= 8.0.31 Security Update (cpuapr2023) - Linux (0.0); PHP < 5.5.37, 5.6.x < 5.6.23, 7.x < 7.0.8 Multiple Vulnerabilities (Aug 2016) - Linux (0.0); Oracle Mysql Security Update (cpuoct2018 - 02) - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability - Linux (0.0); Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux (0.0)

## False negatives (in baseline, not extracted)

- PHP < 5.5.33, 5.6.x < 5.6.19 Multiple Vulnerabilities (Apr 2016) - Linux
- PHP < 8.1.32, 8.2.x < 8.2.28 Multiple Vulnerabilities - Linux
- PHP < 8.1.29, 8.2.x < 8.2.20, 8.3.x < 8.3.8 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.49 Multiple Vulnerabilities - Linux
- PHP < 5.6.28, 7.x < 7.0.13 Multiple Vulnerabilities (Nov 2016) - Linux
- PHP < 5.6.26, 7.x < 7.0.11 Multiple Vulnerabilities (Sep 2016) - Linux
- PHP < 5.6.26 DoS Vulnerability - Linux
- PHP < 7.4.33, 8.0.x < 8.0.25, 8.1.x < 8.1.12 Security Update - Linux
- PHP < 5.5.38, 5.6.x < 5.6.24, 7.0.x < 7.0.9 Multiple Vulnerabilities (Jul 2016) - Linux
- PHP < 5.5.37, 5.6.x < 5.6.23 Multiple Vulnerabilities (Aug 2016) - Linux
- Apache HTTP Server < 2.4.60 Multiple Vulnerabilities - Linux
- PHP < 5.4.43, 5.5.x < 5.5.27, 5.6.x < 5.6.11 Multiple Vulnerabilities (Mar 2016) - Linux
- PHP < 5.4.44, 5.5.x < 5.5.28, 5.6.x < 5.6.12 Multiple Vulnerabilities (Jul 2016) - Linux
- PHP < 5.5.34, 5.6.x < 5.6.20, 7.x < 7.0.5 Multiple Vulnerabilities (Jul 2016) - Linux
- PHP < 5.6.7 DoS Vulnerability - Linux
- PHP < 8.0.30, 8.1.x < 8.1.22, 8.2.x < 8.2.9 Security Update - Linux
- Apache HTTP Server Multiple Vulnerabilities (Apr 2018) - Linux
- PHP Multiple Vulnerabilities (Feb 2019) - Linux
- PHP < 7.1.33, 7.2.x < 7.2.24, 7.3.x < 7.3.11 RCE Vulnerability - Version Check
- PHP CVE-2019-13224 Use-After-Free Vulnerability - Linux
- PHP < 7.0.12 RCE / DoS Vulnerability - Linux
- PHP < 5.6.31, 7.0.x < 7.0.21, 7.1.x < 7.1.7 Multiple Vulnerabilities (Jul 2017) - Linux
- PHP < 5.5.31, 5.6.x < 5.6.17, 7.x < 7.0.2 DoS Vulnerability (Aug 2016) - Linux
- PHP < 7.2.27, 7.3.x < 7.3.14, 7.4.x < 7.4.2 Multiple Vulnerabilities (Jan 2020) - Linux
- Apache HTTP Server mod_auth_digest Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.55 Multiple Vulnerabilities - Linux
- PHP < 8.1.30, 8.2.x < 8.2.24, 8.3.x < 8.3.12 Multiple Vulnerabilities - Linux
- PHP < 5.6.18, 7.x < 7.0.3 DoS Vulnerability (Jul 2016) - Linux
- PHP < 5.4.41, 5.5.x < 5.5.25, 5.6.x < 5.6.9 Multiple Vulnerabilities - Linux
- PHP < 7.2.28 Multiple Vulnerabilities (Feb 2020) - Linux
- Oracle Mysql Security Updates (apr2017-3236618) 01 - Linux
- PHP 5.x < 5.6.39, 7.x < 7.0.33, 7.1.x < 7.1.26, 7.2.x < 7.2.14 DoS Vulnerability - Linux
- Apache HTTP Server < 2.4.59 Multiple Vulnerabilities - Linux
- PHP 5.4.x < 5.4.40, 5.5.x < 5.5.22, 5.6.x < 5.6.6 RCE Vulnerability (Jul 2015) - Linux
- Apache HTTP Server Denial of Service Vulnerability-02 (Apr 2018) - Linux
- Apache HTTP Server mod_session_crypto Vulnerability (Dec 2016) - Linux
- Apache HTTP Server Multiple Vulnerabilities (Sep 2014) - Linux
- PHP < 5.5.30, 5.6.x < 5.6.14 Multiple DoS Vulnerabilities - Linux
- PHP 5.4.x < 5.4.32, 5.5.x < 5.5.15 Multiple Vulnerabilities (Aug 2014)
- PHP < 7.4.31, 8.0.x < 8.0.24, 8.1.x < 8.1.11 Security Update - Linux
- PHP < 7.2.26 Multiple Vulnerabilities (Dec 2019) - Linux
- Apache HTTP Server 2.4.0 < 2.4.42 Multiple Vulnerabilities - Linux
- PHP < 7.3.29 Multiple Vulnerabilities (Jul 2021) - Linux
- Apache HTTP Server 2.4.7 - 2.4.65 Authentication Bypass Vulnerability - Linux
- PHP < 8.0.22, 8.1.x < 8.1.9 Security Update - Linux
- PHP < 7.2.29 Multiple Vulnerabilities (Mar 2020) - Linux
- Apache HTTP Server 2.4.1 < 2.4.24 IP Spoofing Vulnerability - Linux
- Oracle MySQL Server <= 5.6.45 / 5.7 <= 5.7.27 Security Update (cpuoct2019) - Linux
- phpinfo() Output Reporting (HTTP)
- PHP < 7.3.33, 7.4.x < 7.4.26, 8.0.x < 8.0.13 Security Update (Nov 2021) - Linux
- PHP < 7.3.30, 7.4.x < 7.4.23, 8.0.x < 8.0.10 Security Update (Aug 2021) - Linux
- Apache HTTP Server Multiple Vulnerabilities (Mar 2014) - Linux
- PHP 5.5.x < 5.5.15 Multiple Use After Free Vulnerabilities (Jul 2014)
- TCP Timestamps Information Disclosure
- robot.txt / robots.txt exists on the Web Server (HTTP)
- HTTP Security Headers Detection

## False positives (extracted, not in baseline)

- BLOCK 1
- BLOCK 2
- BLOCK 3
- Critical (CVSS: 9.8)
- Block 7
- Critical (CVSS: 9.8)
- BLOCK 14
- BLOCK 15
- PHP 5.x < 5.6.34, 7.x < 7.0.28, 7.1.x < 7.1.15, 7.2.x < 7.2.3 Stack Buffer Overflow
- BLOCK 22
- Block 23
- Critical (CVSS: 9.8)
- Critical (CVSS: 9.8)
- Critical (CVSS: 9.8)
- Apache HTTP Server 2.4.0 - 2.4.55 HTTP Request Smuggling Vulnerability
- Block 36
- Block 37
- Block 38
- Block 39
- Block 40
- Block 41
- BLOCK 42
- BLOCK 43
- BLOCK 45 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 46 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 47 (host: 172.30.9.2, port: 80/tcp)
- PHP < 5.5.31, 5.6.x < 5.6.17, 7.x < 7.0.2 Out of Bounds Read Memory Corruption
- BLOCK 50
- BLOCK 51
- BLOCK 58 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 59 (host: 172.30.9.2, port: 80/tcp)
- High (CVSS: 7.5)
- PHP < 5.6.32, 7.x < 7.0.24, 7.1.x < 7.1.11 Heap Based Buffer Overflow Vulnerability - Linux
- BLOCK 94
- Apache HTTP Server < 2.4.39 mod_auth_digest Access Control Bypass Vulnerability - Linux
- BLOCK 98 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 99 (host: 172.30.9.2, port: 80/tcp)
- Apache HTTP Server OPTIONS Memory Leak Vulnerability (Optionsbleed) - Version Check
- PHP < 5.4.44, 5.5.x < 5.5.28, 5.6.x < 5.6.12, 7.x < 7.0.4 DoS and Information Disclosure Vulnerability - Linux
- Oracle MySQL
- Block 131
- Medium (CVSS: 6.8)
- BLOCK 138
- BLOCK 139
- Multiple Vulnerabilities (Jul 2021)
- PHP < 8.1.28, 8.2.x < 8.2.18, 8.3.x < 8.3.6 Security Update (GHSA-h746-cjrr-wfmr) - Linux
- BLOCK 149 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 150 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 151 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 154
- BLOCK 155
- PHP < 7.3.26, 7.x < 7.0.28, 7.1.x < 7.1.15, 7.2.x < 7.2.3 Filter Vulnerability (Jan 2021) - Linux
- PHP Heap Based Buffer Overflow Vulnerability
- PHP Security Update Vulnerability
- BLOCK 169 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 170 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 171 (host: 172.30.9.2, port: 80/tcp)
- Oracle MySQL Server <= 5.6.44 / 5.7 <= 5.7.26 / 8.0 <= 8.0.16 Security Update
- Oracle MySQL Server <= 5.5.47 / 5.6 <= 5.6.28 / 5.7 <= 5.7.10 Security Update
- Oracle MySQL Server <= 8.0.43
- Oracle MySQL Server <= 5.6.45 / 5.7 <= 5.7.27
- Oracle MySQL Server <= 8.0.39, 8.1 <= 8.4.1, 9.0 <= 9.0.1 Security Update (cpuoct2024)
- Oracle MySQL Server <= 8.0.38, 8.1 <= 8.4.1, 9.0 <= 9.0.1 Security Update (cpuoct2024)
- Block 234
- Block 235

## Notes

- baseline never fills `log_method` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
