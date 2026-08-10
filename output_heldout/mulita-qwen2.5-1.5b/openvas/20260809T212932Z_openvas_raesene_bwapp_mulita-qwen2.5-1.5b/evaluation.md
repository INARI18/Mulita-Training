# Evaluation report

- results: `..\mulita-extractor-training\output_heldout\mulita-qwen2.5-1.5b\openvas\20260809T212932Z_openvas_raesene_bwapp_mulita-qwen2.5-1.5b\results.json`
- baseline: `C:\Users\Bia\Documents\GitHub\Projetos\mulita-extractor-training\data\heldout\openvas\openvas_raesene_bwapp.xlsx`
- source: OPENVAS — threshold 0.7 — text metrics: token_f1, rouge_l

## Coverage

- baseline findings: 214
- extracted records: 242
- matched: 200  (recall 0.935, precision 0.826)

## block_id drops

- 273 dropped (unknown_id=35, duplicate_id=234, validation_error=0, unrecovered=4)
  (unknown_id/duplicate_id: LLM output rejected; unrecovered: block yielded no record after retries)

## chunk retries

- 35 retried (bad_json=35, bad_shape=0)
  (bad_json: response not valid JSON, usually output truncated at the token cap; bad_shape: JSON parsed but failed the schema)

## Field scores (measured mean — vacuous empty×empty pairs excluded)

```
field                     exact  set_f1  set_f1_ids  rouge_l  token_f1
-----                     -----  ------  ----------  -------  --------
name                      -      -       -           0.983    0.983   
description               -      -       -           0.766    0.766   
solution                  -      -       -           0.742    0.742   
impact                    -      -       -           0.610    0.610   
references                -      0.696   0.698       -        -       
severity                  0.925  -       -           -        -       
port                      0.955  -       -           -        -       
protocol                  0.965  -       -           -        -       
cvss                      0.320  -       -           -        -       
insight                   -      -       -           0.186    0.186   
detection_result          -      -       -           0.542    0.542   
detection_method          -      -       -           0.687    0.688   
product_detection_result  -      -       -           0.887    0.887   
log_method                -      -       -           0.000    0.000   
```

`n/a` = every matched pair was empty on both sides for that field (nothing to measure). Inclusive means and per-pair detail live in `evaluation.json`.

## Worst pairs per field

- **name**: Oracle MySQL Server <= 5.7.39 / 8.0 <= 8.0.30 Security Update (cpuoct2022) - Linux (0.6); PHP < 5.4.45, 5.5.x < 5.5.29, 5.6.x < 5.6.13 RCE Vulnerability (Mar 2016) - Linux (0.682); Oracle MySQL Server <= 5.7.38 / 8.0 <= 8.0.29 Security Update (cpujul2022) - Linux (0.686); Oracle MySQL Server <= 5.7.33 / 8.0 <= 8.0.23 Security Update (cpuapr2021) - Linux (0.686); Oracle MySQL Server <= 5.7.32 / 8.0 <= 8.0.22 Security Update (cpuapr2021) - Linux (0.686)
- **description**: Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.37, 5.6.x < 5.6.23 Multiple Vulnerabilities (Aug 2016) - Linux (0.0); PHP < 5.4.40, 5.5.x < 5.5.24, 5.6.x < 5.6.8 Multiple Vulnerabilities - Linux (0.0); Oracle MySQL Server <= 5.7.35 / 8.0 <= 8.0.26 Security Update (cpuoct2021) - Linux (0.0); PHP CVE-2019-13224 Use-After-Free Vulnerability - Linux (0.0)
- **solution**: PHP < 5.5.37, 5.6.x < 5.6.23 Multiple Vulnerabilities (Aug 2016) - Linux (0.0); Oracle MySQL Server <= 5.7.35 / 8.0 <= 8.0.26 Security Update (cpuoct2021) - Linux (0.0); PHP CVE-2019-13224 Use-After-Free Vulnerability - Linux (0.0); PHP < 7.0.12 RCE / DoS Vulnerability - Linux (0.0); Apache HTTP Server <= 2.4.52 Multiple Vulnerabilities - Linux (0.0)
- **impact**: Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.6.28, 7.x < 7.0.13 Multiple Vulnerabilities (Nov 2016) - Linux (0.0); Apache HTTP Server <= 2.4.51 Buffer Overflow Vulnerability - Linux (0.0); PHP < 5.5.37, 5.6.x < 5.6.23 Multiple Vulnerabilities (Aug 2016) - Linux (0.0); PHP < 5.6.29, 7.0.x < 7.0.14 DoS Vulnerability - Linux (0.0)
- **references**: Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.37, 5.6.x < 5.6.23 Multiple Vulnerabilities (Aug 2016) - Linux (0.0); Oracle MySQL Server <= 5.7.35 / 8.0 <= 8.0.26 Security Update (cpuoct2021) - Linux (0.0); PHP CVE-2019-13224 Use-After-Free Vulnerability - Linux (0.0); PHP < 7.0.12 RCE / DoS Vulnerability - Linux (0.0)
- **severity**: Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.4.44, 5.5.x < 5.5.28, 5.6.x < 5.6.12 Multiple Vulnerabilities (Jul 2016) - Linux (0.0); PHP < 5.4.40, 5.5.x < 5.5.24, 5.6.x < 5.6.8 Multiple Vulnerabilities - Linux (0.0); Oracle MySQL Server <= 5.7.35 / 8.0 <= 8.0.26 Security Update (cpuoct2021) - Linux (0.0); Apache HTTP Server < 2.4.55 Multiple Vulnerabilities - Linux (0.0)
- **port**: TCP Timestamps Information Disclosure (0.0); ICMP Timestamp Reply Information Disclosure (0.0); Traceroute (0.0); CPE Inventory (0.0); PHP Detection Consolidation (0.0)
- **protocol**: TCP Timestamps Information Disclosure (0.0); Traceroute (0.0); PHP Detection Consolidation (0.0); Hostname Determination Reporting (0.0); OS Detection Consolidation and Reporting (0.0)
- **cvss**: PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0); PHP < 5.5.27, 5.6.x < 5.6.11 Arbitrary Code Execution Vulnerability (Aug 2016) - Linux (0.0); PHP < 5.6.30, 7.x < 7.0.15, 7.1.x < 7.1.1 Multiple Vulnerabilities (Jan 2017) - Linux (0.0)
- **insight**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.32, 8.2.x < 8.2.28 Multiple Vulnerabilities - Linux (0.0); PHP < 8.1.31, 8.2.x < 8.2.26, 8.3.x < 8.3.14 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server Multiple Vulnerabilities (Jun 2017) - Linux (0.0)
- **detection_result**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.32, 8.2.x < 8.2.28 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.27, 5.6.x < 5.6.11 Arbitrary Code Execution Vulnerability (Aug 2016) - Linux (0.0); PHP < 5.6.30, 7.x < 7.0.15, 7.1.x < 7.1.1 Multiple Vulnerabilities (Jan 2017) - Linux (0.0); PHP < 5.6.28, 7.x < 7.0.13 Multiple Vulnerabilities (Nov 2016) - Linux (0.0)
- **detection_method**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.32, 8.2.x < 8.2.28 Multiple Vulnerabilities - Linux (0.0); Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.27, 5.6.x < 5.6.11 Arbitrary Code Execution Vulnerability (Aug 2016) - Linux (0.0); PHP < 5.6.30, 7.x < 7.0.15, 7.1.x < 7.1.1 Multiple Vulnerabilities (Jan 2017) - Linux (0.0)
- **product_detection_result**: PHP End of Life (EOL) Detection - Linux (0.0); PHP < 8.1.32, 8.2.x < 8.2.28 Multiple Vulnerabilities - Linux (0.0); PHP CVE-2017-7189 Improper Input Validation Vulnerability - Linux (0.0); PHP < 7.2.30, 7.3 < 7.3.17, 7.4 < 7.4.5 DoS Vulnerability (Apr 2020) - Linux (0.0); PHP < 7.2.28 Multiple Vulnerabilities (Feb 2020) - Linux (0.0)
- **log_method**: Apache HTTP Server < 2.4.54 Multiple Vulnerabilities - Linux (0.0); PHP < 5.5.27, 5.6.x < 5.6.11 Arbitrary Code Execution Vulnerability (Aug 2016) - Linux (0.0); PHP < 5.6.30, 7.x < 7.0.15, 7.1.x < 7.1.1 Multiple Vulnerabilities (Jan 2017) - Linux (0.0); PHP < 5.6.28, 7.x < 7.0.13 Multiple Vulnerabilities (Nov 2016) - Linux (0.0); Oracle MySQL Server <= 5.7.40, 8.x <= 8.0.31 Security Update (cpujan2023) - Linux (0.0)

## False negatives (in baseline, not extracted)

- PHP < 5.5.33, 5.6.x < 5.6.19 Multiple Vulnerabilities (Apr 2016) - Linux
- PHP < 5.5.32, 5.6.x < 5.6.18, 7.x < 7.0.3 Multiple Vulnerabilities (Jul 2016) - Linux
- PHP < 8.1.29, 8.2.x < 8.2.20, 8.3.x < 8.3.8 Multiple Vulnerabilities - Linux
- Apache HTTP Server < 2.4.49 Multiple Vulnerabilities - Linux
- PHP < 5.5.34, 5.6.x < 5.6.20, 7.x < 7.0.5 Multiple Vulnerabilities (Jul 2016) - Linux
- Apache HTTP Server 2.4.0 - 2.4.46 Multiple Vulnerabilities - Linux
- PHP < 5.5.22, 5.6.x < 5.6.6 XXE Vulnerability - Linux
- Apache HTTP Server mod_auth_digest Multiple Vulnerabilities - Linux
- PHP < 8.1.30, 8.2.x < 8.2.24, 8.3.x < 8.3.12 Multiple Vulnerabilities - Linux
- PHP < 5.6.18, 7.x < 7.0.3 DoS Vulnerability (Jul 2016) - Linux
- Apache HTTP Server Whitespace Defects Multiple Vulnerabilities
- EasyPHP Webserver <= 12.1 Multiple Vulnerabilities - Active Check
- Oracle Mysql Security Updates (jan2017-2881727) 02 - Linux
- Oracle MySQL Security Update (cpujul2018 - 04) - Linux

## False positives (extracted, not in baseline)

- BLOCK 1 (host: 192.168.1.10, port: 5000)
- BLOCK 4 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 5 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 6 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 7 (host: 172.30.9.2, port: 80/tcp)
- PHP 5.x < 5.6.34, 7.x < 7.0.28, 7.1.x < 7.1.15, 7.2.x < 7.2.3 Stack Buffer Overflow (Vulnerability (Mar 2018) - Linux)
- Critical (CVSS: 9.8)
- Critical (CVSS: 9.8)
- Unauthenticated Remote Code Execution via Uninitialized Local Buffer
- Critical (CVSS: 9.6)
- PHP < 5.5.31, 5.6.x < 5.6.17, 7.x < 7.0.2 Out of Bounds Read Memory Corruption
- Oracle MySQL Server <= 5.5.52 / 5.6 <= 5.6.33 / 5.7 <= 5.7.15 Security Update (cpuoct2016) - Linux
- BLOCK 58 (host: 172.30.9.2, port: 80/tcp)
- BLOCK 59 (host: 172.30.9.2, port: 80/tcp)
- PHP < 5.6.36, 7.x < 7.0.30, 7.1.x < 7.1.17, 7.2.x < 7.2.5 Multiple Vulnerabilities (May 2018) - Linux
- PHP Multiple Heap Buffer Overflow and Information Disclosure Vulnerabilities (Aug 2018) - Linux
- PHP < 7.3.27, 7.4.x < 7.4.15, 8.0.x < 8.0.2 NULL Deference Vulnerability (Feb 2021) - Linux
- PHP < 5.6.32, 7.x < 7.0.24, 7.1.x < 7.1.11 Heap Based Buffer Overflow Vulnerability - Linux
- DFN-CERT-2015-0223
- DFN-CERT-2015-0223
- Apache HTTP Server < 2.4.39 mod_auth_digest Access Control Bypass Vulnerability - Linux
- Apache HTTP Server OPTIONS Memory Leak Vulnerability (Optionsbleed) - Version C.
- PHP < 5.4.44, 5.5.x < 5.5.28, 5.6.x < 5.6.12, 7.x < 7.0.4 DoS and Information Disclosure Vulnerability - Linux
- PHP < 5.4.44, 5.5.x < 5.5.28, 5.6.x < 5.6.12, 7.x < 7.0.4 DoS and Information Disclosure Vulnerability - Windows
- PHP < 5.4.44, 5.5.x < 5.5.28, 5.6.x < 5.6.12, 7.x < 7.0.4 DoS and Information Disclosure Vulnerability - Linux
- Oracle MySQL Server <= 8.0.39, 8.1 <= 8.4.2, 9.0 <= 9.0.1 Security Update (cpuc...)
- Oracle MySQL Server <= 5.5.51 / 5.6 <= 5.6.32 / 5.7 <= 5.7.14 Security Update (cpuoct2016) - Linux
- Medium (CVSS: 6.8)
- PHP < 8.1.28, 8.2.x < 8.2.18, 8.3.x < 8.3.6 Security Update (GHSA-h746-cjrr-wfmr) - Linux
- PHP 5.3.x < 5.3.29, 5.4.x < 5.4.30, 5.5.x < 5.5.14, 5.6.0alpha1 < 5.6.0 Heap Based Buffer Overflow Vulnerability - Linux
- PHP < 5.6.35, 7.x < 7.0.29, 7.1.x < 7.1.16, 7.2.x < 7.2.4 Security Bypass Vulnerability (May 2018) - Linux
- BLOCK 178 (host: 172.30.9.2, port: 3306/tcp)
- BLOCK 179 (host: 172.30.9.2, port: 3306/tcp)
- Oracle MySQL Server <= 8.0.41, 8.1 <= 8.4.4, 9.0 <= 9.2.0 Security Update (cpua..)
- Oracle MySQL Server <= 5.5.50 / 5.6 <= 5.6.31 / 5.7 <= 5.7.13 Security Update (cpuoct2016) - Linux
- Oracle MySQL Server <= 8.0.43, 8.1.x <= 8.4.7, 9.0.0 <= 9.4.0 Security Update (cpuoct2025) - Linux
- BLOCK 205 (host: 172.30.9.2, port: 3306/tcp)
- Oracle MySQL Server <= 8.0.38, 8.1 <= 8.4.1, 9.0 <= 9.0.1 Security Update (cpuoct2024) - Linux
- Oracle MySQL <= 5.5.60 and earlier
- Low (CVSS: 3.7)
- Low (CVSS: 3.7)
- Low (CVSS: 2.7)

## Notes

- baseline never fills `log_method` — scores there only measure presence agreement: 1.0 means the extraction also left the field empty; low values mean it filled a field the ground truth does not annotate.
